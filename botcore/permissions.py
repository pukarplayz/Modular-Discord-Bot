from typing import Iterable
from discord.ext import commands
import os


def has_any_role(*role_names: Iterable[str]):
    """Check factory that verifies the invoking user has any of the given role names."""

    def predicate(ctx: commands.Context):
        if not ctx.guild:
            return False
        member = ctx.author
        member_role_names = {r.name for r in member.roles}
        return any(r in member_role_names for r in role_names)

    return commands.check(predicate)


def is_owner():
    """Check that the invoking user is the configured BOT_OWNER_ID."""
    owner_id = int(os.environ.get("BOT_OWNER_ID", "0"))

    def predicate(ctx: commands.Context):
        return getattr(ctx.author, "id", None) == owner_id

    return commands.check(predicate)
