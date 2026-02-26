import os
import pathlib
import importlib
from dotenv import load_dotenv

from botcore.core import BotCore


load_dotenv()


def _load_event_listeners(bot):
    events_dir = pathlib.Path(__file__).parent / "events"
    if not events_dir.exists():
        return
    for py in events_dir.glob("*.py"):
        if py.name.startswith("__"):
            continue
        mod_name = f"events.{py.stem}"
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "setup"):
                maybe = mod.setup(bot)
                if hasattr(maybe, "__await__"):
                    bot.loop.run_until_complete(maybe)
        except Exception:
            print(f"Failed to load event module {mod_name}")


def _load_cogs(bot):
    # load legacy cogs from cogs/commands before starting the bot
    cogs_dir = pathlib.Path(__file__).parent / "cogs" / "commands"
    if not cogs_dir.exists():
        return
    for py in cogs_dir.glob("*.py"):
        if py.name.startswith("__"):
            continue
        mod_name = f"cogs.commands.{py.stem}"
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "setup"):
                maybe = mod.setup(bot)
                if hasattr(maybe, "__await__"):
                    bot.loop.run_until_complete(maybe)
                print(f"Loaded cog {mod_name}")
        except Exception as e:
            print(f"Failed to load cog {mod_name}: {e}")


def _load_plugins(bot):
    # use ExtensionManager to load plugin modules synchronously
    try:
        bot.loop.run_until_complete(bot.loader.load_all())
    except Exception as e:
        print("Failed to load plugins:", e)


def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN environment variable not set")

    # Force dashboard to start automatically when running main.py
    os.environ["START_DASHBOARD"] = "true"


    intents = BotCore.default_intents()
    shard_count = int(os.environ.get("BOT_SHARD_COUNT", 1))

    bot = BotCore(intents=intents, shard_count=shard_count)

    # pre-load event listeners, cogs and plugins so commands are available immediately
    _load_event_listeners(bot)
    _load_cogs(bot)
    _load_plugins(bot)

    bot.run(token)


if __name__ == "__main__":
    main()
