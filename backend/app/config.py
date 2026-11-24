"""App settings, read from environment variables (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

# PostgreSQL by default (see docker-compose.yml). For a quick start without Docker,
# set DATABASE_URL=sqlite:///./slotsaver.db in .env.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://slotsaver:slotsaver@localhost:5432/slotsaver",
)

# Comma-separated list of frontend origins allowed to call the API.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

LOG_DIR = os.getenv("LOG_DIR", "logs")
