"""Redis pub/sub wrapper using redis.asyncio with aioredis fallback."""
import asyncio
import json
import logging
from typing import Callable, Optional

logger = logging.getLogger("bot.pubsub")


class PubSub:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis = None
        self._tasks = []
        self._client_lib = None

    async def connect(self):
        if not self.redis_url:
            logger.warning("No REDIS_URL configured for PubSub")
            return
        # prefer redis.asyncio (redis-py) for asyncio support
        try:
            import redis.asyncio as redis

            self._redis = redis.from_url(self.redis_url)
            self._client_lib = "redis"
            # test connection
            await self._redis.ping()
            return
        except Exception:
            logger.debug("redis.asyncio not available or connection failed, falling back to aioredis")

        try:
            import aioredis

            self._redis = await aioredis.from_url(self.redis_url)
            self._client_lib = "aioredis"
            return
        except Exception:
            logger.exception("Failed to initialize any redis client for PubSub")

    async def publish(self, channel: str, payload: dict):
        if not self._redis:
            logger.warning("PubSub not connected; cannot publish")
            return
        data = json.dumps(payload)
        if self._client_lib == "redis":
            await self._redis.publish(channel, data)
        else:
            await self._redis.publish(channel, data)

    async def subscribe(self, channel: str, handler: Callable[[dict], None]):
        if not self._redis:
            logger.warning("PubSub not connected; cannot subscribe")
            return

        if self._client_lib == "redis":
            pubsub = self._redis.pubsub()
            await pubsub.subscribe(channel)

            async def _reader():
                logger.info("Subscribed (redis) to %s", channel)
                while True:
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message is None:
                        await asyncio.sleep(0.1)
                        continue
                    data = message.get("data")
                    try:
                        if isinstance(data, bytes):
                            data = data.decode()
                        payload = json.loads(data)
                    except Exception:
                        payload = {"raw": data}
                    try:
                        await handler(payload)
                    except Exception:
                        logger.exception("Handler error for channel %s", channel)

        else:
            # aioredis fallback
            pubsub = self._redis.pubsub()
            await pubsub.subscribe(channel)

            async def _reader():
                logger.info("Subscribed (aioredis) to %s", channel)
                async for message in pubsub.listen():
                    if message is None:
                        continue
                    if message.get("type") != "message":
                        continue
                    data = message.get("data")
                    try:
                        payload = json.loads(data)
                    except Exception:
                        payload = {"raw": data}
                    try:
                        await handler(payload)
                    except Exception:
                        logger.exception("Handler error for channel %s", channel)

        task = asyncio.create_task(_reader())
        self._tasks.append(task)

    async def close(self):
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass
        for t in self._tasks:
            t.cancel()
