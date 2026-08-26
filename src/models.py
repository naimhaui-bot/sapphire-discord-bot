from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class GuildConfig(Base):
    __tablename__ = "guild_configs"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    moderation_log_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    welcome_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    goodbye_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    goodbye_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    welcome_message: Mapped[str] = mapped_column(
        Text, default="Welcome {mention} to **{server}**! You are member #{memberCount}."
    )
    goodbye_message: Mapped[str] = mapped_column(
        Text, default="**{username}** has left {server}."
    )
    welcome_embed: Mapped[bool] = mapped_column(Boolean, default=True)
    dm_welcome: Mapped[bool] = mapped_column(Boolean, default=False)
    autorole_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    custom_commands: Mapped[dict] = mapped_column(JSON, default=dict)
    xp_rate: Mapped[float] = mapped_column(Float, default=1.0)
    xp_cooldown: Mapped[int] = mapped_column(Integer, default=60)
    levelup_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    levelup_message: Mapped[str] = mapped_column(
        Text, default="Congratulations {mention}, you reached level **{level}**!"
    )
    xp_rewards: Mapped[dict] = mapped_column(JSON, default=dict)
    role_rewards: Mapped[dict] = mapped_column(JSON, default=dict)
    honeypot_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    honeypot_punishment: Mapped[str] = mapped_column(String(12), default="timeout")
    raid_threshold: Mapped[int] = mapped_column(Integer, default=8)
    raid_window: Mapped[int] = mapped_column(Integer, default=20)
    raid_action: Mapped[str] = mapped_column(String(12), default="timeout")
    emergency_lockdown: Mapped[bool] = mapped_column(Boolean, default=False)
    whitelist: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ModerationCase(Base):
    __tablename__ = "moderation_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    target_id: Mapped[int] = mapped_column(BigInteger, index=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(24))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Warning(Base):
    __tablename__ = "warnings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserXP(Base):
    __tablename__ = "user_xp"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    messages: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AkinatorStat(Base):
    __tablename__ = "akinator_stats"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    games: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)