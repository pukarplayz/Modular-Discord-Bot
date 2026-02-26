import asyncio
import logging
import os
import subprocess
import pathlib
from typing import Optional

import discord
from discord.ext import commands

from .logging_config import setup_logging
from .db import Database
from .config import GuildConfigManager
from .loader import ExtensionManager
from .pubsub import PubSub
from .errors import ExceptionManager

logger = setup_logging("botcore")


class BotCore(commands.Bot):
    def __init__(
        self,
        intents: discord.Intents = discord.Intents.default(),
        shard_count: int = 1,
        **kwargs,
    ):
        super().__init__(command_prefix=os.environ.get("COMMAND_PREFIX", "!"), intents=intents, **kwargs)
        self.loop = asyncio.get_event_loop()
        self.db = Database()
        self.config = GuildConfigManager(self.db)
        self.loader = ExtensionManager(self, path="plugins")
        self.exception_manager = ExceptionManager(self)
        self.shard_count = shard_count

        # register handlers
        self.add_listener(self._on_ready)
        self.add_listener(self._on_error)

    @staticmethod
    def default_intents() -> discord.Intents:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        return intents

    async def _on_ready(self):
        logger.info("Bot ready: %s (shards=%s)", self.user, self.shard_count)

        # connect DB
        await self.db.connect()
        await self.config.ensure_table()

        # start pubsub if configured
        try:
            redis_url = os.environ.get("REDIS_URL")
            if redis_url:
                self.pubsub = PubSub(redis_url)
                await self.pubsub.connect()
                async def _handle_config_update(payload: dict):
                    logger.info("Received config update: %s", payload)
                    # payload expected: {"guild_id": "123", "config": {...}}
                    # bots should react to this message (e.g., refresh cache)
                    # placeholder: no-op for now
                    return
                await self.pubsub.subscribe("guild_config_updates", _handle_config_update)
        except Exception:
            logger.exception("Failed to initialize PubSub")

        # register global error handlers
        self.add_listener(self.exception_manager.on_command_error, "on_command_error")
        self.add_listener(self.exception_manager.on_app_command_error, "on_application_command_error")

        # load plugins
        await self.loader.load_all()

        # load legacy cogs from cogs/commands
        try:
            import pathlib
            p = pathlib.Path(__file__).parents[1] / "cogs" / "commands"
            if p.exists():
                for py in p.glob("*.py"):
                    if py.name.startswith("__"):
                        continue
                    mod_name = f"cogs.commands.{py.stem}"
                    try:
                        mod = __import__(mod_name, fromlist=["*"])
                        if hasattr(mod, "setup"):
                            maybe = mod.setup(self)
                            if asyncio.iscoroutine(maybe):
                                await maybe
                            logger.info("Loaded cog %s", mod_name)
                    except Exception:
                        logger.exception("Failed loading cog %s", mod_name)
        except Exception:
            logger.exception("Error while loading legacy cogs")

        # optionally start the dashboard in the same process (useful for development)
        try:
            if os.environ.get("START_DASHBOARD", "false").lower() in ("1", "true", "yes"):
                # import the FastAPI app and run uvicorn server in background
                try:
                    cfg_val = os.environ.get("START_DASHBOARD", "false").lower()
                    dashboard_path = pathlib.Path(__file__).parents[1] / "dashboard" / "backend" / "app" / "main.py"
                    should_auto_start = cfg_val in ("1", "true", "yes") or (cfg_val == "auto" and dashboard_path.exists())
                    if not should_auto_start:
                        logger.info("Dashboard not configured to start (set START_DASHBOARD=1 to enable)")
                    else:
                        cfg_host = os.environ.get("DASHBOARD_HOST", "0.0.0.0")
                        cfg_port = int(os.environ.get("DASHBOARD_PORT", "8000"))

                        # Prefer launching uvicorn as a subprocess to avoid event-loop conflicts
                        try:
                            cmd = ["uvicorn", "dashboard.backend.app.main:app", "--host", cfg_host, "--port", str(cfg_port)]
                            proc = subprocess.Popen(cmd)
                            logger.info("Started dashboard subprocess (pid=%s) on %s:%s", proc.pid, cfg_host, cfg_port)
                        except Exception:
                            # fallback: try in-process uvicorn server
                            try:
                                import uvicorn
                                from importlib import import_module

                                mod = import_module("dashboard.backend.app.main")
                                app = getattr(mod, "app", None)
                                if app is not None:
                                    server = uvicorn.Server(uvicorn.Config(app, host=cfg_host, port=cfg_port, loop="asyncio", log_level="info"))
                                    # run server in background task
                                    self.loop.create_task(server.serve())
                                    logger.info("Dashboard started in-process on %s:%s", cfg_host, cfg_port)
                            except Exception:
                                logger.exception("Failed to start dashboard in subprocess or in-process")
                except Exception:
                    logger.exception("Failed to initialize dashboard startup sequence")
        except Exception:
            logger.exception("Error in dashboard startup check")

        # dev-only file watcher for hot-reloading cogs/plugins
        try:
            if os.environ.get("DEV_HOT_RELOAD", "false").lower() in ("1", "true", "yes"):
                async def _watcher():
                    import pathlib
                    import time

                    paths = [pathlib.Path(__file__).parents[1] / "cogs" / "commands", pathlib.Path(__file__).parents[1] / "plugins"]
                    mtimes = {}
                    while True:
                        try:
                            for base in paths:
                                if not base.exists():
                                    continue
                                for py in base.glob("*.py"):
                                    key = str(py.resolve())
                                    try:
                                        m = py.stat().st_mtime
                                    except Exception:
                                        continue
                                    if key not in mtimes:
                                        mtimes[key] = m
                                        continue
                                    if m != mtimes[key]:
                                        mtimes[key] = m
                                        # determine module name
                                        if "cogs" in str(py.parents[0]):
                                            mod = f"cogs.commands.{py.stem}"
                                        else:
                                            mod = f"plugins.{py.stem}"
                                        try:
                                            await self.loader.reload(mod)
                                            logger.info("Hot-reloaded %s", mod)
                                        except Exception:
                                            logger.exception("Failed to hot-reload %s", mod)
                        except Exception:
                            logger.exception("Error in dev hot-reload watcher")
                        await asyncio.sleep(1.0)

                self.loop.create_task(_watcher())
                logger.info("Dev hot-reload watcher started")
        except Exception:
            logger.exception("Failed to start dev hot-reload watcher")

    async def _on_error(self, event_method, *args, **kwargs):
        logger.exception("Unhandled exception in %s", event_method)

    async def on_command_error(self, ctx, error):
        # suppress CommandNotFound to avoid noisy logs for non-commands
        from discord.ext import commands

        if isinstance(error, commands.CommandNotFound):
            return
        # delegate to exception manager for other errors
        try:
            await self.exception_manager.on_command_error(ctx, error)
        except Exception:
            logger.exception("Error in exception manager on_command_error")

    async def on_application_command_error(self, interaction, error):
        # delegate to exception manager
        try:
            await self.exception_manager.on_app_command_error(interaction, error)
        except Exception:
            logger.exception("Error in exception manager on_app_command_error")

    def run(self, token: str, **kwargs):
        super().run(token, **kwargs)
