import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


async def get_or_fetch_user(
    bot: commands.Bot, user_id: int, guild: discord.Guild | None = None
) -> discord.User | discord.Member | None:
    """Get the user from a cache, and if it's not there, fetch it from the API."""
    if guild:
        member = guild.get_member(user_id)
        if member:
            return member

    user = bot.get_user(user_id)
    if user:
        return user

    try:
        return await bot.fetch_user(user_id)
    except discord.NotFound:
        logger.warning(f"User {user_id} not found in cache nor API.")
        return None
