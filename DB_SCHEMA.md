Database schema (SQLite/Postgres)

-- guild_config: stores per-guild JSON configuration
CREATE TABLE IF NOT EXISTS guild_config (
  guild_id TEXT PRIMARY KEY,
  config TEXT NOT NULL
);

-- audit_logs: optional logging for moderation actions
CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id TEXT,
  actor_id TEXT,
  action TEXT,
  payload TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- extensions: optional table to track enabled/disabled plugins per guild
CREATE TABLE IF NOT EXISTS extensions (
  guild_id TEXT,
  extension TEXT,
  enabled INTEGER DEFAULT 1,
  PRIMARY KEY (guild_id, extension)
);
