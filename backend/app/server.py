"""ASGI entrypoint:  uvicorn app.server:app"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401  (registers tables before create_all)
from app.api import api_router
from app.core.db import ModelBase, engine
from app.core.request_tracing import RequestTracer
from app.core.settings import load_config
from app.domain import stale_order_watcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def _lifespan(_: FastAPI):
    ModelBase.metadata.create_all(bind=engine)
    stop = asyncio.Event()
    watcher = asyncio.create_task(stale_order_watcher.watch(stop)) if load_config().run_watcher else None
    try:
        yield
    finally:
        stop.set()
        if watcher is not None:
            await watcher


def create_app() -> FastAPI:
    cfg = load_config()
    application = FastAPI(
        title="CampusBite API",
        description="Order food on campus: customers order, restaurants cook, delivery partners deliver.",
        version="1.0.0",
        lifespan=_lifespan,
    )
    application.add_middleware(RequestTracer)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Request-ID"],
    )
    application.include_router(api_router)

    @application.get("/health", tags=["Health"])
    def health():
        return {"status": "ok"}

    return application


app = create_app()
