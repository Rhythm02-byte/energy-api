from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.auth import require_token
from app.db import SCHEMA, connect

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create the table on startup if it does not exist yet.
    with connect() as conn:
        conn.execute(SCHEMA)
    yield


app = FastAPI(title="Energy Data API", lifespan=lifespan)


class ReadingIn(BaseModel):
    device_id: str = Field(min_length=1)
    kwh: Annotated[float, Field(ge=0)]
    timestamp: datetime


class Reading(ReadingIn):
    pass


def get_conn() -> Iterator[psycopg.Connection]:
    with connect() as conn:
        yield conn


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/readings",
    status_code=status.HTTP_201_CREATED,
    response_model=Reading,
    dependencies=[Depends(require_token)],
)
def create_reading(payload: ReadingIn, conn: psycopg.Connection = Depends(get_conn)) -> Reading:
    conn.execute(
        "INSERT INTO readings (device_id, kwh, recorded_at) VALUES (%s, %s, %s)",
        (payload.device_id, payload.kwh, payload.timestamp),
    )
    conn.commit()
    return Reading(**payload.model_dump())


@app.get("/readings", response_model=list[Reading], dependencies=[Depends(require_token)])
def list_readings(conn: psycopg.Connection = Depends(get_conn)) -> list[Reading]:
    rows = conn.execute(
        "SELECT device_id, kwh, recorded_at FROM readings ORDER BY id"
    ).fetchall()
    return [Reading(device_id=d, kwh=k, timestamp=t) for d, k, t in rows]
