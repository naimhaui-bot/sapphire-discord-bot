import time
from collections import defaultdict, deque
from datetime import timedelta

import discord
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.moderation import record_case
from src.services.settings import get_config

_join_times: dict[int, deque[float]] = defaultdict(deque)


async def is_staff_or_whitelisted(database: AsyncSession, member: discord.Member) -> bool:
    config = await get_config(database, member.guild.id)
    return (
        member.id in (config.whitelist or [])
        or member.guild_permissions.administrator
        or member.guild.owner_id == member.id
    )


async def register_join(database: AsyncSession, member: discord.Member) -> bool:
    config = await get_config(database, member.guild.id)
    now = time.monotonic()
    joins = _join_times[member.guild.id]
    joins.append(now)
    while joins and now - joins[0] > config.raid_window:
        joins.popleft()
    return len(joins) >= config.raid_threshold


async def punish(
    database: AsyncSession,
    member: discord.Member,
    action: str,
    reason: str,
) -> bool:
    if await is_staff_or_whitelisted(database, member):
        return False
    bot_member = member.guild.me
    if bot_member is None or member.top_role >= bot_member.top_role:
        return False
    try:
        if action == "ban":
            await member.ban(reason=reason, delete_message_seconds=0)
        elif action == "kick":
            await member.kick(reason=reason)
        else:
            await member.timeout(timedelta(minutes=10), reason=reason)
    except (discord.Forbidden, discord.HTTPException):
        return False
    await record_case(database, member.guild, member.id, bot_member.id, action, reason)
    return True