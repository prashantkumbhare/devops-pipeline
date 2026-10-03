"""Synthetic trading lab with PostgreSQL storage; no broker connection."""
import json
import logging
import time
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
import psycopg
from psycopg.rows import dict_row
from fastapi.responses import JSONResponse

def connect():
    return psycopg.connect(
        host=os.environ["DB_HOST"], dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
        connect_timeout=3, options="-c statement_timeout=3000", row_factory=dict_row,
    )


@asynccontextmanager
async def lifespan(app):
    # Initial lab schema only. Versioned migrations will replace this later.
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id UUID PRIMARY KEY,
                symbol VARCHAR(10) NOT NULL,
                side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
                quantity INTEGER NOT NULL CHECK (quantity > 0 AND quantity <= 1000000),
                limit_price NUMERIC(12,2) NOT NULL CHECK (limit_price > 0),
                status TEXT NOT NULL CHECK (status = 'ACCEPTED'),
                created_at TIMESTAMPTZ NOT NULL
            )
        """)
    yield


app = FastAPI(title="Trading API Lab", version="0.2.0", lifespan=lifespan)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("trading")


class OrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    symbol: str = Field(pattern=r"^[A-Z][A-Z0-9.]{0,9}$", examples=["DEMO"])
    side: Literal["BUY", "SELL"]
    quantity: int = Field(gt=0, le=1000000, strict=True)
    limit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class Order(OrderRequest):
    id: UUID
    status: Literal["ACCEPTED"] = "ACCEPTED"
    created_at: datetime


@app.exception_handler(psycopg.OperationalError)
async def database_unavailable(request: Request, exc):
    logger.error(json.dumps({"event": "database_unavailable"}))
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = str(uuid4())
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.error(json.dumps({"event": "request_failed", "request_id": request_id}))
        raise
    response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({
        "event": "request_completed", "request_id": request_id,
        "method": request.method, "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
    }))
    return response


@app.get("/health/live")
async def live():
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    with connect() as conn:
        conn.execute("SELECT id FROM orders LIMIT 1")
    return {"status": "ready", "storage": "postgresql", "persistent": True}


@app.post("/orders", response_model=Order, status_code=201)
def create_order(body: OrderRequest):
    order = Order(**body.model_dump(), id=uuid4(), created_at=datetime.now(timezone.utc))
    # The connection context commits on success, or rolls back on failure.
    with connect() as conn:
        conn.execute(
            "INSERT INTO orders (id, symbol, side, quantity, limit_price, status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (order.id, order.symbol, order.side, order.quantity,
             order.limit_price, order.status, order.created_at),
        )
    return order


@app.get("/orders", response_model=list[Order])
def list_orders():
    with connect() as conn:
        return conn.execute("SELECT * FROM orders ORDER BY created_at, id").fetchall()


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: UUID):
    with connect() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = %s", (order_id,)).fetchone()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
