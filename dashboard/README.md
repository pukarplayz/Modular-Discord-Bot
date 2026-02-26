# Discord Bot Dashboard

This repository contains a production-oriented dashboard for managing Discord bots.

This folder currently has the backend skeleton (FastAPI). Frontend is recommended to be built with Next.js.

Quickstart (development):

1. Copy the example env file and set required values:

```bash
cp dashboard/backend/.env.example dashboard/backend/.env
# edit .env to add DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, JWT_SECRET
```

2. Start services with Docker Compose:

```bash
docker compose -f dashboard/docker-compose.yml up --build
```

3. Backend will be available at http://localhost:8000

Next steps:
- Implement full OAuth persistence and JWT refresh flow.
- Add Alembic migrations and run initial schema.
- Implement frontend in Next.js and integrate with backend endpoints.
