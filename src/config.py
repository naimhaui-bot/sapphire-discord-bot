import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    token: str
    client_id: int | None
    client_secret: str | None
    database_url: str = "sqlite+aiosqlite:///sapphire.sqlite3"


def _optional_int(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    return int(value) if value else None


settings = Settings(
    token=os.getenv("DISCORD_TOKEN", "").strip(),
    client_id=_optional_int("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET") or None,
)