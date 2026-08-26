from dataclasses import dataclass, field
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base:
    """Compatibility marker retained for modules that import the old model base."""


@dataclass
class GuildConfig:
    guild_id: int
    moderation_log_channel_id: int | None = None
    welcome_channel_id: int | None = None
    goodbye_channel_id: int | None = None
    welcome_enabled: bool = False
    goodbye_enabled: bool = False
    welcome_message: str = "Welcome {mention} to **{server}**! You are member #{memberCount}."
    goodbye_message: str = "**{username}** has left {server}."
    welcome_embed: bool = True
    dm_welcome: bool = False
    autorole_id: int | None = None
    custom_commands: dict[str, str] = field(default_factory=dict)
    xp_rate: float = 1.0
    xp_cooldown: int = 60
    levelup_channel_id: int | None = None
    levelup_message: str = "Congratulations {mention}, you reached level **{level}**!"
    xp_rewards: dict = field(default_factory=dict)
    role_rewards: dict = field(default_factory=dict)
    honeypot_channel_id: int | None = None
    honeypot_punishment: str = "timeout"
    raid_threshold: int = 8
    raid_window: int = 20
    raid_action: str = "timeout"
    emergency_lockdown: bool = False
    whitelist: list[int] = field(default_factory=list)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class ModerationCase:
    guild_id: int
    target_id: int
    moderator_id: int
    action: str
    reason: str
    id: int = 0
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class Warning:
    guild_id: int
    user_id: int
    moderator_id: int
    reason: str
    id: int = 0
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class UserXP:
    guild_id: int
    user_id: int
    xp: int = 0
    level: int = 0
    messages: int = 0
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class AkinatorStat:
    guild_id: int
    user_id: int
    wins: int = 0
    losses: int = 0
    games: int = 0
    updated_at: datetime = field(default_factory=utcnow)
