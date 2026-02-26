from discord.ext import commands
from discord import Member
import asyncio


class Moderation(commands.Cog):
    """Moderation commands requiring Manage Guild or kick/ban permissions."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        # only allow in guilds
        return ctx.guild is not None

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: Member, *, reason: str = None):
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: Member, *, reason: str = None):
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member}")


async def setup(bot: commands.Bot):
    maybe = bot.add_cog(Moderation(bot))
    if asyncio.iscoroutine(maybe):
        await maybe
