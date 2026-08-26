import logging
from datetime import timedelta

import discord
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ModerationCase, Warning
from src.services.settings import get_config

log = logging.getLogger(__name__)


async def record_case(
    database: AsyncSession,
    guild: discord.Guild,
    target_id: int,
    moderator_id: int,
    action: str,
    reason: str,
) -> ModerationCase:
    case = ModerationCase(
        guild_id=guild.id,
        target_id=target_id,
        moderator_id=moderator_id,
        action=action,
        reason=reason,
    )
    database.add(case)
    await database.commit()
    await database.refresh(case)
    config = await get_config(database, guild.id)
    if config.moderation_log_channel_id:
        channel = guild.get_channel(config.moderation_log_channel_id)
        if isinstance(channel, discord.TextChannel):
            message = discord.Embed(
                title=f"Case #{case.id} · {action.title()}",
                description=reason,
                colour=discord.Colour.red(),
            )
            message.add_field(name="Target", value=f"<@{target_id}> (`{target_id}`)")
            message.add_field(name="Moderator", value=f"<@{moderator_id}>")
            try:
                await channel.send(embed=message)
            except discord.HTTPException:
                log.warning("Unable to send moderation log for guild %s", guild.id)
    return case


async def add_warning(
    database: AsyncSession, guild: discord.Guild, target: discord.Member, moderator: discord.Member, reason: str
) -> Warning:
    warning = Warning(
        guild_id=guild.id, user_id=target.id, moderator_id=moderator.id, reason=reason
    )
    database.add(warning)
    await database.commit()
    await database.refresh(warning)
    await record_case(database, guild, target.id, moderator.id, "warning", reason)
    return warning


async def timeout_member(member: discord.Member, duration: int, reason: str) -> None:
    await member.timeout(timedelta(minutes=max(1, min(duration, 40320))), reason=reason)