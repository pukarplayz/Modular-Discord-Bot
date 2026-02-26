"""FastAPI backend entrypoint for the Dashboard service."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, settings
from app.core.middleware import register_middlewares
from app.routes import auth, guilds


def create_app() -> FastAPI:
    app = FastAPI(title="Discord Bot Dashboard API", version="0.1.0")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register custom middlewares (logging, error handling, rate limiting)
    register_middlewares(app)

    # Include routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(guilds.router, prefix="/api/v1/guilds", tags=["guilds"])

    @app.get("/api/v1/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
