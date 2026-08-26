import json
import logging
from contextlib import asynccontextmanager
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, TypeVar

from src.models import GuildConfig, ModerationCase, Warning, UserXP, AkinatorStat

log = logging.getLogger(__name__)
DATA_PATH = Path("sapphire-data.json")
T = TypeVar("T")


def _encode(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {key: _encode(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _encode(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    return value


def _decode_config(data: dict[str, Any]) -> GuildConfig:
    data = dict(data)
    data["updated_at"] = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else GuildConfig(0).updated_at
    return GuildConfig(**data)


class JsonDatabase:
    def __init__(self) -> None:
        self.data: dict[str, Any] = self._load()
        self._pending: list[Any] = []

    def _load(self) -> dict[str, Any]:
        try:
            if DATA_PATH.exists():
                return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            log.warning("Unable to read %s; starting with empty data", DATA_PATH)
        return {"guild_configs": {}, "moderation_cases": [], "warnings": [], "user_xp": {}, "akinator_stats": {}}

    async def get(self, model: type[T], key: Any) -> T | None:
        if model is GuildConfig:
            raw = self.data.setdefault("guild_configs", {}).get(str(key))
            return _decode_config(raw) if raw else None
        return None

    def add(self, value: Any) -> None:
        self._pending.append(value)

    async def commit(self) -> None:
        for value in self._pending:
            if isinstance(value, GuildConfig):
                self.data.setdefault("guild_configs", {})[str(value.guild_id)] = _encode(value)
            elif isinstance(value, ModerationCase):
                value.id = max([item.get("id", 0) for item in self.data.setdefault("moderation_cases", [])] or [0]) + 1
                self.data["moderation_cases"].append(_encode(value))
            elif isinstance(value, Warning):
                value.id = max([item.get("id", 0) for item in self.data.setdefault("warnings", [])] or [0]) + 1
                self.data["warnings"].append(_encode(value))
        self._pending.clear()
        temporary = DATA_PATH.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(DATA_PATH)

    async def refresh(self, value: Any) -> None:
        return None


@asynccontextmanager
async def SessionLocal() -> AsyncIterator[JsonDatabase]:
    database = JsonDatabase()
    try:
        yield database
    finally:
        await database.commit()


async def init_database() -> None:
    if not DATA_PATH.exists():
        await JsonDatabase().commit()
    log.info("Local JSON storage initialized")


async def session() -> AsyncIterator[JsonDatabase]:
    async with SessionLocal() as database:
        yield database


async def close_database() -> None:
    return None
