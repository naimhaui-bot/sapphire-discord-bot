import random
import time
from collections import defaultdict

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserXP
from src.services.settings import get_config

_last_award: dict[tuple[int, int], float] = defaultdict(float)


def xp_required(level: int) -> int:
    return 100 + (level * 50)


def level_for_xp(xp: int) -> int:
    level = 0
    while xp >= xp_required(level):
        xp -= xp_required(level)
        level += 1
    return level


async def get_user(database: AsyncSession, guild_id: int, user_id: int) -> UserXP:
    user = await database.get(UserXP, (guild_id, user_id))
    if user is None:
        user = UserXP(guild_id=guild_id, user_id=user_id)
        database.add(user)
        await database.flush()
    return user


async def award_message(database: AsyncSession, member) -> tuple[UserXP, bool, int] | None:
    config = await get_config(database, member.guild.id)
    key = (member.guild.id, member.id)
    now = time.monotonic()
    if now - _last_award[key] < config.xp_cooldown:
        return None
    _last_award[key] = now

    user = await get_user(database, member.guild.id, member.id)
    previous_level = user.level
    user.xp += max(1, round(random.randint(15, 25) * config.xp_rate))
    user.messages += 1
    user.level = level_for_xp(user.xp)
    await database.commit()
    return user, user.level > previous_level, user.level


async def leaderboard(database: AsyncSession, guild_id: int) -> list[UserXP]:
    result = await database.execute(
        select(UserXP)
        .where(UserXP.guild_id == guild_id)
        .order_by(desc(UserXP.xp))
        .limit(10)
    )
    return list(result.scalars())
