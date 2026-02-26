import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from botcore.permissions import has_any_role


class ExampleCog(commands.Cog):
    """Example plugin demonstrating hybrid and slash commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="greet", with_app_command=True, description="Greet the user")
    @has_any_role("Admin", "Moderator")
    async def greet(self, ctx: commands.Context):
        """Hybrid command: works as prefix and slash command."""
        await ctx.respond(f"Hello, {ctx.author.display_name}!")

    @app_commands.command(name="whoami", description="Show your info")
    async def whoami(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You are {interaction.user} (id: {interaction.user.id})", ephemeral=True)


async def setup(bot: commands.Bot):
    maybe = bot.add_cog(ExampleCog(bot))
    if asyncio.iscoroutine(maybe):
        await maybe
