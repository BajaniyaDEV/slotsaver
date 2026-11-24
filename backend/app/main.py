"""SlotSaver API entry point.

Run from the repo root:  uvicorn backend.app.main:app --reload
Interactive docs:        http://localhost:8000/docs
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import CORS_ORIGINS, LOG_DIR
from .database import Base, engine
from .routers import appointments, health

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(LOG_DIR, "app.log"))],
)
logger = logging.getLogger("slotsaver")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates any missing tables. Fine for the capstone; Alembic can replace this later.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SlotSaver API",
    description="No-show prediction and waitlist filling for community clinics.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Every error uses the same shape: {"error": "...", "detail": ...}
@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    logger.warning("%s %s -> %s: %s", request.method, request.url.path, exc.status_code, exc.detail)
    error = "not_found" if exc.status_code == 404 else "request_error"
    return JSONResponse(status_code=exc.status_code, content={"error": error, "detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    messages = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err["loc"] if part not in ("query", "body", "path"))
        messages.append(f"{field}: {err['msg']}")
    logger.warning("%s %s -> 422: %s", request.method, request.url.path, messages)
    return JSONResponse(
        status_code=422,
        content={"error": "invalid_input", "detail": messages},
    )


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "server_error", "detail": "Something went wrong. Check logs/app.log."},
    )


app.include_router(health.router)
app.include_router(appointments.router)
