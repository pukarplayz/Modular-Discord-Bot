import asyncio
import importlib
import logging
import pathlib
from typing import List

logger = logging.getLogger("bot.loader")


class ExtensionManager:
    def __init__(self, bot, path: str = "plugins"):
        self.bot = bot
        self.path = pathlib.Path(path)
        self.loaded: List[str] = []

    def discover(self) -> List[str]:
        mods = []
        if not self.path.exists():
            return mods
        for py in self.path.glob("*.py"):
            if py.name.startswith("__"):
                continue
            mods.append(f"{self.path.name}.{py.stem}")
        return mods

    async def load_all(self):
        for mod in self.discover():
            await self.load(mod)

    async def load(self, module: str):
        try:
            importlib.import_module(module)
            mod = importlib.import_module(module)
            if hasattr(mod, "setup"):
                maybe = mod.setup(self.bot)
                if asyncio.iscoroutine(maybe):
                    await maybe
            self.loaded.append(module)
            logger.info("Loaded extension %s", module)
        except Exception:
            logger.exception("Failed to load %s", module)

    async def unload(self, module: str):
        try:
            mod = importlib.import_module(module)
            if hasattr(mod, "teardown"):
                maybe = mod.teardown(self.bot)
                if asyncio.iscoroutine(maybe):
                    await maybe
            # remove from sys.modules to allow reload
            import sys

            if module in sys.modules:
                del sys.modules[module]
            if module in self.loaded:
                self.loaded.remove(module)
            logger.info("Unloaded extension %s", module)
        except Exception:
            logger.exception("Failed to unload %s", module)

    async def reload(self, module: str):
        await self.unload(module)
        await self.load(module)
