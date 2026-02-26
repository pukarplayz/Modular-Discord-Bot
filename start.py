import os
from dotenv import load_dotenv

from botcore.core import BotCore


load_dotenv()


def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN environment variable not set")

    intents = BotCore.default_intents()
    shard_count = int(os.environ.get("BOT_SHARD_COUNT", 1))

    bot = BotCore(intents=intents, shard_count=shard_count)
    bot.run(token)


if __name__ == "__main__":
    main()
