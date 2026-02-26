import os
from typing import Optional

import aiosqlite

try:
    import asyncpg
except Exception:
    asyncpg = None


class Database:
    """Simple DB abstraction supporting SQLite and optionally Postgres.

    Use DATABASE_URL env var for Postgres (asyncpg), otherwise a local `data.db` SQLite file is used.
    """

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.environ.get("DATABASE_URL")
        self._conn = None
        self._is_postgres = bool(self.dsn and self.dsn.startswith("postgres"))

    async def connect(self):
        if self._is_postgres and asyncpg:
            self._conn = await asyncpg.connect(self.dsn)
        else:
            self._conn = await aiosqlite.connect("data.db")
            await self._conn.execute("PRAGMA foreign_keys = ON")
            await self._conn.commit()

    async def close(self):
        if not self._conn:
            return
        await self._conn.close()

    async def fetchrow(self, query: str, *args):
        if self._is_postgres and asyncpg:
            return await self._conn.fetchrow(query, *args)
        cur = await self._conn.execute(query, args)
        row = await cur.fetchone()
        return row

    async def fetch(self, query: str, *args):
        if self._is_postgres and asyncpg:
            return await self._conn.fetch(query, *args)
        cur = await self._conn.execute(query, args)
        rows = await cur.fetchall()
        return rows

    async def execute(self, query: str, *args):
        if self._is_postgres and asyncpg:
            return await self._conn.execute(query, *args)
        cur = await self._conn.execute(query, args)
        await self._conn.commit()
        return cur
