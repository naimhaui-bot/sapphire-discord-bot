from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import GuildConfig


async def get_config(database: AsyncSession, guild_id: int) -> GuildConfig:
    config = await database.get(GuildConfig, guild_id)
    if config is None:
        config = GuildConfig(guild_id=guild_id)
        database.add(config)
        await database.commit()
        await database.refresh(config)
    return config


async def update_config(database: AsyncSession, guild_id: int, **values) -> GuildConfig:
    config = await get_config(database, guild_id)
    for key, value in values.items():
        setattr(config, key, value)
    await database.commit()
    await database.refresh(config)
    return config


async def top_custom_commands(database: AsyncSession, guild_id: int) -> dict:
    return (await get_config(database, guild_id)).custom_commands or {}