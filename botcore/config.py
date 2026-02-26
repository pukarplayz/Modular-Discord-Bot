import json
from typing import Any, Dict, Optional

from .db import Database


class GuildConfigManager:
    """Per-guild configuration backed by the Database.

    Stores JSON in `guild_config` table: (guild_id TEXT PRIMARY KEY, config TEXT)
    """

    def __init__(self, db: Database):
        self.db = db

    async def ensure_table(self):
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id TEXT PRIMARY KEY,
                config TEXT NOT NULL
            )
            """
        )

    async def get(self, guild_id: int) -> Dict[str, Any]:
        row = await self.db.fetchrow("SELECT config FROM guild_config WHERE guild_id = $1" if self.db._is_postgres else "SELECT config FROM guild_config WHERE guild_id = ?", str(guild_id))
        if not row:
            return {}
        raw = row[0] if not self.db._is_postgres else row[0]
        return json.loads(raw)

    async def set(self, guild_id: int, config: Dict[str, Any]):
        raw = json.dumps(config)
        if self.db._is_postgres:
            await self.db.execute("INSERT INTO guild_config (guild_id, config) VALUES ($1,$2) ON CONFLICT (guild_id) DO UPDATE SET config = EXCLUDED.config", str(guild_id), raw)
        else:
            await self.db.execute("INSERT OR REPLACE INTO guild_config (guild_id, config) VALUES (?,?)", str(guild_id), raw)
