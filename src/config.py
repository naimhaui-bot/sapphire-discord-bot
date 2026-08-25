import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    token: str
    client_id: int | None
    client_secret: str | None
    database_url: str
    log_level: str
    command_sync_guild_id: int | None


def _optional_int(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    return int(value) if value else None


def _database_url() -> str:
    return "sqlite+aiosqlite:///sapphire.sqlite3"


settings = Settings(
    token=os.getenv("DISCORD_TOKEN", "").strip(),
    client_id=_optional_int("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET") or None,
    database_url=_database_url(),
    log_level="INFO",
    command_sync_guild_id=None,
)