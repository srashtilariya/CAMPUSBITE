"""SQLAlchemy engine, session factory and the declarative base for all models."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import load_config


def _make_engine(url: str) -> Engine:
    options: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        # FastAPI may hand the same connection to a different worker thread.
        options["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **options)


engine = _make_engine(load_config().db_url)
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class ModelBase(DeclarativeBase):
    pass


def db_session() -> Iterator[Session]:
    """FastAPI dependency: one session per request, always closed afterwards."""
    with SessionFactory() as session:
        yield session
