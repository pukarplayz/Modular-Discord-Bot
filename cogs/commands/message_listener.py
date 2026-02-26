from discord.ext import commands
import asyncio


class MessageListener(commands.Cog):
    """Handle raw message events inside a cog so behavior is modular and reloadable."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: commands.Context):
        # ignore bot messages
        if message.author.bot:
            return

        content = message.content.strip()

        # simple keyword responses
        if content.lower() == "panda":
            await message.channel.send("Panda says hello 🐼")
            return

        if content.startswith("!hello"):
            await message.channel.send(f"Hello {message.author.mention}!")
            return

        # ensure commands are still processed
        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    maybe = bot.add_cog(MessageListener(bot))
    if asyncio.iscoroutine(maybe):
        await maybe
