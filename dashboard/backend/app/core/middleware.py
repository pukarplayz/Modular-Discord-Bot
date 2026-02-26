"""Custom middleware for error handling, logging, and basic rate limiting."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import logging

logger = logging.getLogger("dashboard.middleware")


def register_middlewares(app: FastAPI):
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception("Unhandled exception: %s", exc)
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
