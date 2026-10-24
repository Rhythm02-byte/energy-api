from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, status
from pydantic import BaseModel, Field

from app.db import SCHEMA, connect


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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/readings", status_code=status.HTTP_201_CREATED, response_model=Reading)
def create_reading(payload: ReadingIn, conn: psycopg.Connection = Depends(get_conn)) -> Reading:
    conn.execute(
        "INSERT INTO readings (device_id, kwh, recorded_at) VALUES (%s, %s, %s)",
        (payload.device_id, payload.kwh, payload.timestamp),
    )
    conn.commit()
    return Reading(**payload.model_dump())


@app.get("/readings", response_model=list[Reading])
def list_readings(conn: psycopg.Connection = Depends(get_conn)) -> list[Reading]:
    rows = conn.execute(
        "SELECT device_id, kwh, recorded_at FROM readings ORDER BY id"
    ).fetchall()
    return [Reading(device_id=d, kwh=k, timestamp=t) for d, k, t in rows]
