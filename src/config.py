import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    token: str
    client_id: str
    client_secret: str
    database_url: str
    log_level: str
    command_sync_guild_id: int | None


def _database_url() -> str:
    return "sqlite+aiosqlite:///sapphire.sqlite3"


settings = Settings(
    token=os.getenv("DISCORD_TOKEN", "").strip(),
    client_id=os.getenv("CLIENT_ID", "").strip(),
    client_secret=os.getenv("CLIENT_SECRET", "").strip(),
    database_url=_database_url(),
    log_level="INFO",
    command_sync_guild_id=None,
)