"""SQLAlchemy models for the dashboard service."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    owner_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class GuildConfig(Base):
    __tablename__ = "guild_config"

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    prefix = Column(String, default="!")
    automod_enabled = Column(Boolean, default=False)
    logging_channel_id = Column(String, nullable=True)
    raid_mode = Column(Boolean, default=False)
    settings = Column(JSON, default={})
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    guild = relationship("Guild", backref="config")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    key_hash = Column(String, nullable=False)
    owner_id = Column(Integer, nullable=True)
    revoked = Column(Boolean, default=False)
    scopes = Column(JSON, default=[])  # simple scope list


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, nullable=True)
    actor_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    payload = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())
