import time

from fastapi import APIRouter
from sqlalchemy import text

from ..config import settings
from ..database import engine
from ..schemas.schemas import HealthResponse

router = APIRouter()
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
def health_check():
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        database=db_status,
        uptime_seconds=round(time.time() - start_time, 1),
    )
