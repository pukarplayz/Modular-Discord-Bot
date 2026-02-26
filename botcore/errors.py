import logging
from typing import Optional

from discord.ext import commands
import discord

logger = logging.getLogger("bot.errors")


class ExceptionManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        # central place to handle command errors
        logger.exception("Command error: %s", error)
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("You do not have permission to run this command.")
            return
        if isinstance(error, commands.CommandNotFound):
            return
        await ctx.reply("An unexpected error occurred while processing the command.")

    async def on_app_command_error(self, interaction: discord.Interaction, error: Exception):
        logger.exception("App command error: %s", error)
        try:
            await interaction.response.send_message("An error occurred.", ephemeral=True)
        except Exception:
            pass
