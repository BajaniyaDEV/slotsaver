"""Health check: is the API up, can it reach the database, is the model loaded?"""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import get_db

router = APIRouter(tags=["health"])
logger = logging.getLogger("slotsaver")


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:  # noqa: BLE001 - report any database failure
        logger.exception("Health check: database unreachable")
        database = "unreachable"

    # TODO (Amal): report "loaded" once ml/artifacts/model.joblib is served by the API.
    body = {"status": "ok" if database == "ok" else "degraded", "database": database, "model": "not_loaded"}
    return JSONResponse(status_code=200 if database == "ok" else 503, content=body)
