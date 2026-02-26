"""Bot sync helpers: publish config updates to Redis for bots to consume."""
import json
import logging
from typing import Any, Dict

from app.config import settings

logger = logging.getLogger("dashboard.bot_sync")


async def publish_config_update(guild_id: str, config: Dict[str, Any]):
    url = settings.REDIS_URL
    if not url:
        logger.warning("REDIS_URL not configured; skipping publish")
        return
    try:
        # prefer redis.asyncio
        try:
            import redis.asyncio as redis

            r = redis.from_url(url)
            await r.publish("guild_config_updates", json.dumps({"guild_id": guild_id, "config": config}))
            await r.close()
            return
        except Exception:
            pass

        # fallback to aioredis if needed
        import aioredis

        redis = aioredis.from_url(url)
        await redis.publish("guild_config_updates", json.dumps({"guild_id": guild_id, "config": config}))
        await redis.close()
    except Exception:
        logger.exception("Failed to publish config update for %s", guild_id)
