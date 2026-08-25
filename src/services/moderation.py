from datetime import timedelta

import discord
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ModerationCase, Warning


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
    return case


async def add_warning(
    database: AsyncSession,
    guild: discord.Guild,
    member: discord.Member,
    moderator: discord.Member,
    reason: str,
) -> ModerationCase:
    warning = Warning(
        guild_id=guild.id,
        user_id=member.id,
        moderator_id=moderator.id,
        reason=reason,
    )
    database.add(warning)
    case = ModerationCase(
        guild_id=guild.id,
        target_id=member.id,
        moderator_id=moderator.id,
        action="warn",
        reason=reason,
    )
    database.add(case)
    await database.commit()
    await database.refresh(case)
    return case


async def timeout_member(member: discord.Member, minutes: int, reason: str) -> None:
    await member.timeout(timedelta(minutes=minutes), reason=reason)
