from discord.ext import commands
import asyncio


class Ping(commands.Cog):
    """Simple ping command."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="pingcog")
    async def pingcog(self, ctx: commands.Context):
        """Responds with bot latency (from ping cog)."""
        ms = round(self.bot.latency * 1000)
        await ctx.send(f"PingCog Pong! {ms}ms")


async def setup(bot: commands.Bot):
    maybe = bot.add_cog(Ping(bot))
    if asyncio.iscoroutine(maybe):
        await maybe
