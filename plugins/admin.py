import os
from discord.ext import commands


class AdminCog(commands.Cog):
    """Administrative plugin: load/unload/reload extensions and simple health checks."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.owner_id = int(os.environ.get("BOT_OWNER_ID", "0"))

    def cog_check(self, ctx: commands.Context):
        return ctx.author.id == self.owner_id

    @commands.command(name="reload")
    async def reload_cmd(self, ctx: commands.Context, module: str):
        await ctx.send(f"Reloading {module}...")
        await self.bot.loader.reload(module)
        await ctx.send("Done")

    @commands.command(name="load")
    async def load_cmd(self, ctx: commands.Context, module: str):
        await ctx.send(f"Loading {module}...")
        await self.bot.loader.load(module)
        await ctx.send("Done")

    @commands.command(name="unload")
    async def unload_cmd(self, ctx: commands.Context, module: str):
        await ctx.send(f"Unloading {module}...")
        await self.bot.loader.unload(module)
        await ctx.send("Done")


import asyncio


async def setup(bot: commands.Bot):
    maybe = bot.add_cog(AdminCog(bot))
    if asyncio.iscoroutine(maybe):
        await maybe
