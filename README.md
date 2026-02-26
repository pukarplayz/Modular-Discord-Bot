# Modular Discord Bot Framework

A scalable, plugin-driven Discord bot framework built on `discord.py` with
production-focused features: slash & hybrid commands, role-based permissions,
config-per-guild, SQLite/Postgres support, logging, hot-reloadable plugins,
and Docker deployment.

**Core Goals**
- Clean, extendable architecture following SOLID principles.
- Plugins are drop-in Python modules (no framework recompilation required).
- Production-grade defaults (structured logging, DB-backed config, error handling).

**Suggested Folder Structure**

- `main.py` - application entrypoint.
- `botcore/` - core framework (Bot subclass, loader, DB, config, errors, permissions).
- `plugins/` - drop-in plugin modules (each exposes `setup(bot)`).
- `events/` - event listeners (optional registering via `setup`).
- `cogs/` - legacy cogs (optional).
- `requirements.txt` - Python dependencies.
- `Dockerfile`, `docker-compose.yml` - container deployment.
- `.env.example` - environment variables template.
- `DB_SCHEMA.md` - suggested DB schema and migrations.

See the code in the repository for concrete implementations: [main.py](main.py), [botcore](botcore), [plugins](plugins), and [DB_SCHEMA.md](DB_SCHEMA.md).

**Features**
- Slash and hybrid commands (via `discord.app_commands` and `commands.hybrid_command`).
- Role-based permission checks and decorators.
- Centralized exception manager handling command + app-command errors.
- SQLite by default, optional PostgreSQL support via `DATABASE_URL`.
- Per-guild configuration stored as JSON in the DB.
- Hot-reloadable plugins via admin commands; optional file-watcher for dev.
- Sharding-ready Bootstrapping via environment variables.
- Containerized with `Dockerfile` and `docker-compose.yml`.

Installation

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set `DISCORD_TOKEN` and `BOT_OWNER_ID`.

3. Run locally:

```bash
python main.py
```

Deployment

VPS
- Use systemd to run the bot as a service. Create a small wrapper script that activates the virtualenv and runs `python main.py`.

Docker
- Build and run with Docker Compose:

```bash
docker compose up --build -d
```

Environment Variables
- `DISCORD_TOKEN` (required)
- `BOT_OWNER_ID` (owner id for admin commands)
- `DATABASE_URL` (optional Postgres DSN; otherwise SQLite `data.db` is used)
- `COMMAND_PREFIX` (default: `!`)
- `BOT_SHARD_COUNT` (set for sharding)

Database Schema

See [DB_SCHEMA.md](DB_SCHEMA.md) for the suggested schema and migration notes.

Contributing

- Fork and open a PR with a clear description and tests for behavior changes.
- Keep plugins self-contained; add docs to `plugins/PLUGIN_NAME/README.md`.
- New features should include small migration scripts if they alter DB schema.

License

This project uses the MIT License — see [LICENSE](LICENSE).

Branding & Positioning Strategy (short)
- Name: "ModuBot" (modular + bot) or "ShardForge" (scalable/sharding focus).
- Tagline: "Plugin-first Discord bots for teams and communities." 
- Positioning: emphasize production-readiness, sharding, and DB-backed configs; target server ops and bot developers.
- Marketing: publish a demo, CI for tests, and example plugins (moderation, logging, economy). Share benchmarks and upgrade guides.
