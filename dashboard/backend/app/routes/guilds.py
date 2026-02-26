"""Guild-related routes: list guilds and manage guild config."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.guilds import GuildItem, GuildConfigIn, GuildConfigOut
from app.database import get_db
from app.models import models
from app.services import bot_sync

router = APIRouter()


@router.get("/me", response_model=List[GuildItem])
async def list_user_guilds():
    """Return list of guilds for the authenticated user (frontend filters manage permission)."""
    # In real implementation, decode JWT, fetch user's guilds from DB or Discord
    # Here return a placeholder empty list for skeleton
    return []


@router.get("/{guild_id}/config", response_model=GuildConfigOut)
async def get_guild_config(guild_id: str, db: AsyncSession = Depends(get_db)):
    # fetch guild by discord id first
    gq = await db.execute(models.Guild.__table__.select().where(models.Guild.discord_id == guild_id))
    grow = gq.first()
    if not grow:
        raise HTTPException(status_code=404, detail="Guild not found")
    guild_db = grow[0]

    q = await db.execute(models.GuildConfig.__table__.select().where(models.GuildConfig.guild_id == guild_db.id))
    row = q.first()
    if not row:
        raise HTTPException(status_code=404, detail="Config not found")
    cfg = row[0]
    return GuildConfigOut(
        guild_id=str(guild_db.discord_id),
        prefix=cfg.prefix,
        automod_enabled=cfg.automod_enabled,
        logging_channel_id=cfg.logging_channel_id,
        raid_mode=cfg.raid_mode,
        settings=cfg.settings or {},
    )


@router.put("/{guild_id}/config", response_model=GuildConfigOut)
async def update_guild_config(guild_id: str, payload: GuildConfigIn, db: AsyncSession = Depends(get_db)):
    # TODO: enforce RBAC: ensure the caller can manage the guild
    # upsert guild and config
    # ensure guild exists
    gq = await db.execute(models.Guild.__table__.select().where(models.Guild.discord_id == guild_id))
    grow = gq.first()
    if not grow:
        # create minimal guild record
        ins = models.Guild(discord_id=guild_id, name=None)
        db.add(ins)
        await db.commit()
        await db.refresh(ins)
        guild_db = ins
    else:
        guild_db = grow[0]

    # upsert config
    cq = await db.execute(models.GuildConfig.__table__.select().where(models.GuildConfig.guild_id == guild_db.id))
    crow = cq.first()
    if not crow:
        cfg = models.GuildConfig(
            guild_id=guild_db.id,
            prefix=payload.prefix,
            automod_enabled=payload.automod_enabled,
            logging_channel_id=payload.logging_channel_id,
            raid_mode=payload.raid_mode,
            settings=payload.settings,
        )
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)
    else:
        cfg = crow[0]
        cfg.prefix = payload.prefix
        cfg.automod_enabled = payload.automod_enabled
        cfg.logging_channel_id = payload.logging_channel_id
        cfg.raid_mode = payload.raid_mode
        cfg.settings = payload.settings
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)

    # publish to Redis for bots
    try:
        await bot_sync.publish_config_update(str(guild_id), {
            "prefix": cfg.prefix,
            "automod_enabled": cfg.automod_enabled,
            "logging_channel_id": cfg.logging_channel_id,
            "raid_mode": cfg.raid_mode,
            "settings": cfg.settings,
        })
    except Exception:
        # ignore pubsub failures for now
        pass

    return GuildConfigOut(
        guild_id=str(guild_id),
        prefix=cfg.prefix,
        automod_enabled=cfg.automod_enabled,
        logging_channel_id=cfg.logging_channel_id,
        raid_mode=cfg.raid_mode,
        settings=cfg.settings or {},
    )
