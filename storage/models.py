"""SQLAlchemy models matching the existing VLMB SQLite schema."""
from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Float,
    Index,
    Integer,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for VLMB database models."""


class AdminSettings(Base):
    __tablename__ = "admin_settings"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[str] = mapped_column(Text, nullable=False)


class Bans(Base):
    __tablename__ = "bans"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    reason: Mapped[str | None] = mapped_column(Text)
    banned_by: Mapped[int | None] = mapped_column(BigInteger)
    banned_at: Mapped[str] = mapped_column(Text, nullable=False)

class Chats(Base):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    chat_type: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    username: Mapped[str | None] = mapped_column(Text)
    last_seen: Mapped[str] = mapped_column(Text, nullable=False)
    bot_is_admin: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    bot_status: Mapped[str | None] = mapped_column(Text)
    can_post_messages: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    can_send_messages: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

class ForwardedFileIds(Base):
    __tablename__ = "forwarded_file_ids"
    __table_args__ = (
        Index("idx_forwarded_file_ids_added_at", "added_at"),
        Index("idx_forwarded_file_ids_type", "file_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    file_unique_id: Mapped[str | None] = mapped_column(Text)
    file_type: Mapped[str | None] = mapped_column(Text)
    file_name: Mapped[str | None] = mapped_column(Text)
    mime_type: Mapped[str | None] = mapped_column(Text)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    added_by: Mapped[int | None] = mapped_column(BigInteger)
    added_at: Mapped[str] = mapped_column(Text, nullable=False)


class GroupDigestSentTracks(Base):
    __tablename__ = "group_digest_sent_tracks"
    __table_args__ = (
        Index("idx_digest_sent_at", "sent_at"),
    )

    subscription_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    track_key: Mapped[str] = mapped_column(Text, primary_key=True)
    sent_at: Mapped[float] = mapped_column(Float, nullable=False)


class GroupDigestSubscriptions(Base):
    __tablename__ = "group_digest_subscriptions"
    __table_args__ = (
        Index("idx_digest_chat", "chat_id"),
        Index("idx_digest_due", "next_run_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    thread_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, server_default=text("0")
    )
    genre_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    genre_name: Mapped[str] = mapped_column(Text, nullable=False)
    schedule_key: Mapped[str] = mapped_column(Text, nullable=False)
    track_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("5")
    )
    enabled: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    next_run_at: Mapped[float] = mapped_column(Float, nullable=False)
    last_run_at: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[str] = mapped_column(Text, nullable=False)


class GroupTopics(Base):
    __tablename__ = "group_topics"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    thread_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str | None] = mapped_column(Text)
    last_seen: Mapped[float] = mapped_column(Float, nullable=False)


class StatsDaily(Base):
    __tablename__ = "stats_daily"

    day: Mapped[str] = mapped_column(Text, primary_key=True)
    searches: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    downloads: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    ym_searches: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    vk_searches: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    errors: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    yt_searches: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )


class StatsEvents(Base):
    __tablename__ = "stats_events"
    __table_args__ = (
        Index("idx_stats_events_user", "user_id"),
        Index("idx_stats_events_ts", "ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[str] = mapped_column(Text, nullable=False)
    event: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    chat_id: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(Text)
    extra: Mapped[str | None] = mapped_column(Text)


class TgAudioCache(Base):
    __tablename__ = "tg_audio_cache"
    __table_args__ = (
        Index("idx_tg_audio_cache_created_at", "created_at"),
    )

    query_key: Mapped[str] = mapped_column(Text, primary_key=True)
    file_id: Mapped[str | None] = mapped_column(Text)
    artist: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[int | None] = mapped_column(Integer)
    unique_id: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[int | None] = mapped_column(Integer)


class UserActions(Base):
    __tablename__ = "user_actions"
    __table_args__ = (
        Index("idx_user_actions_user", "user_id"),
        Index("idx_user_actions_ts", "ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    chat_id: Mapped[int | None] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[str | None] = mapped_column(Text)


class UserFavorites(Base):
    __tablename__ = "user_favorites"
    __table_args__ = (
        Index("idx_user_favorites_user_ts", "user_id", "ts"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    uid: Mapped[str] = mapped_column(Text, primary_key=True)
    track_json: Mapped[str] = mapped_column(Text, nullable=False)
    ts: Mapped[float] = mapped_column(Float, nullable=False)


class UserHistory(Base):
    __tablename__ = "user_history"
    __table_args__ = (
        Index("idx_user_history_user_uid_ts", "user_id", "uid", "ts"),
        Index("idx_user_history_user_ts", "user_id", "ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    uid: Mapped[str | None] = mapped_column(Text)
    track_json: Mapped[str | None] = mapped_column(Text)
    ts: Mapped[float | None] = mapped_column(Float)


class UserLast(Base):
    __tablename__ = "user_last"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    uid: Mapped[str | None] = mapped_column(Text)
    track_json: Mapped[str | None] = mapped_column(Text)
    ts: Mapped[float | None] = mapped_column(Float)

class UserPendingFavorite(Base):
    __tablename__ = "user_pending_favorite"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    uid: Mapped[str] = mapped_column(Text, nullable=False)
    track_json: Mapped[str] = mapped_column(Text, nullable=False)
    ts: Mapped[float] = mapped_column(Float, nullable=False)

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    prefer_source: Mapped[str | None] = mapped_column(Text)
    artist_only_default: Mapped[int | None] = mapped_column(Integer)
    prefer_bitrate_kbps: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[float | None] = mapped_column(Float)

class UserUsageContext(Base):
    __tablename__ = "user_usage_context"
    __table_args__ = (
        CheckConstraint(
            "context IN ('private', 'group')",
            name="ck_user_usage_context_context",
        ),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    context: Mapped[str] = mapped_column(Text, primary_key=True)
    first_seen: Mapped[str] = mapped_column(Text, nullable=False)
    last_seen: Mapped[str] = mapped_column(Text, nullable=False)


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    username: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    last_seen: Mapped[str] = mapped_column(Text, nullable=False)

class VkTokens(Base):
    __tablename__ = "vk_tokens"
    __table_args__ = (
        Index("idx_tokens_expires", "expires_at"),
        Index("idx_tokens_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    added_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    added_at: Mapped[str | None] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    is_active: Mapped[int | None] = mapped_column(
        Integer, server_default=text("1")
    )
    last_used: Mapped[str | None] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    expires_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    description: Mapped[str | None] = mapped_column(Text)
