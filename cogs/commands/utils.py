from discord.ext import commands
import time
import asyncio


class Utils(commands.Cog):
    """Utility commands: ping, echo, uptime."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._start = time.time()

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Respond with latency."""
        ms = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! {ms}ms")

    @commands.command(name="echo")
    async def echo(self, ctx: commands.Context, *, text: str):
        """Echo back the provided text."""
        await ctx.send(text)

    @commands.command(name="uptime")
    async def uptime(self, ctx: commands.Context):
        """Show bot uptime."""
        secs = int(time.time() - self._start)
        await ctx.send(f"Uptime: {secs}s")


async def setup(bot: commands.Bot):
    maybe = bot.add_cog(Utils(bot))
    if asyncio.iscoroutine(maybe):
        await maybe
