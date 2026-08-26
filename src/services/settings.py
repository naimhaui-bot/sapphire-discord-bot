from src.database import JsonDatabase
from src.models import GuildConfig


async def get_config(database: JsonDatabase, guild_id: int) -> GuildConfig:
    config = await database.get(GuildConfig, guild_id)
    if config is None:
        config = GuildConfig(guild_id=guild_id)
        database.add(config)
        await database.commit()
    return config


async def update_config(database: JsonDatabase, guild_id: int, **values) -> GuildConfig:
    config = await get_config(database, guild_id)
    for key, value in values.items():
        if hasattr(config, key):
            setattr(config, key, value)
    database.add(config)
    await database.commit()
    return config


async def top_custom_commands(database: JsonDatabase, guild_id: int) -> dict:
    return (await get_config(database, guild_id)).custom_commands or {}
