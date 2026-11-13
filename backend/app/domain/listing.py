"""Small query helpers shared by the list endpoints."""
from collections.abc import Callable
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Query

from app.models import Order, OrderStage


def page_of(query: Query, page: int, page_size: int, convert: Callable[[Any], Any] | None = None) -> dict:
    """Slice ``query`` into one page and wrap it in the standard pagination envelope."""
    total = query.order_by(None).count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    if convert is not None:
        rows = [convert(row) for row in rows]
    page_count = -(-total // page_size) or 1  # ceil division, but never report zero pages
    return {"items": rows, "total": total, "page": page, "page_size": page_size, "pages": page_count}


def _midnight_utc(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=timezone.utc)


def filter_orders(
    query: Query, stage: OrderStage | None, since: date | None, until: date | None
) -> Query:
    """Apply the optional status / date-range filters. ``until`` is inclusive of that whole day."""
    conditions = []
    if stage:
        conditions.append(Order.status == stage)
    if since:
        conditions.append(Order.created_at >= _midnight_utc(since))
    if until:
        conditions.append(Order.created_at < _midnight_utc(until + timedelta(days=1)))
    return query.filter(*conditions) if conditions else query


def newest_first(query: Query) -> Query:
    return query.order_by(Order.created_at.desc(), Order.id.desc())
