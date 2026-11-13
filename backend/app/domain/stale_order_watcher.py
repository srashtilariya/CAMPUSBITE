"""Background watcher that flags orders a restaurant seems to have forgotten about.

An order is "stale" when it has been PLACED or ACCEPTED for longer than the
configured threshold without any update. We raise at most one alert per
(order, stage) pair, so a dismissed alert stays dismissed and the periodic sweep
never piles up duplicates.
"""
import asyncio
import logging
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.clock import now_utc
from app.core.db import SessionFactory
from app.core.settings import load_config
from app.models import Order, OrderStage, StaleOrderAlert

log = logging.getLogger("campusbite.watcher")

WATCHED_STAGES = (OrderStage.PLACED, OrderStage.ACCEPTED)


def _alert_text(order: Order, minutes: int) -> str:
    return (
        f"Order #{order.id} has been {order.status.value} for more than "
        f"{minutes} minutes without an update."
    )


def raise_stale_alerts(db: Session, threshold_minutes: int | None = None) -> int:
    """Create alerts for newly-stale orders. Returns how many were created."""
    minutes = load_config().stale_after_minutes if threshold_minutes is None else threshold_minutes
    cutoff = now_utc() - timedelta(minutes=minutes)

    stale = (
        db.query(Order)
        .filter(Order.status.in_(WATCHED_STAGES), Order.updated_at < cutoff)
        .all()
    )
    already_flagged: set[tuple[int, str]] = set()
    if stale:
        existing = db.query(StaleOrderAlert.order_id, StaleOrderAlert.order_status).filter(
            StaleOrderAlert.order_id.in_([order.id for order in stale])
        )
        already_flagged = {(order_id, stage) for order_id, stage in existing}

    fresh = [order for order in stale if (order.id, order.status.value) not in already_flagged]
    db.add_all(
        StaleOrderAlert(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            order_status=order.status.value,
            message=_alert_text(order, minutes),
        )
        for order in fresh
    )
    db.commit()
    return len(fresh)


def settle_alerts(db: Session, order_id: int) -> None:
    """Mark an order's open alerts resolved (the caller commits)."""
    db.query(StaleOrderAlert).filter(
        StaleOrderAlert.order_id == order_id, StaleOrderAlert.resolved.is_(False)
    ).update({StaleOrderAlert.resolved: True}, synchronize_session=False)


def _sweep_once() -> int:
    with SessionFactory() as db:
        return raise_stale_alerts(db)


async def watch(stop: asyncio.Event) -> None:
    """Run a sweep every REMINDER_INTERVAL_SECONDS until ``stop`` is set."""
    interval = load_config().sweep_every_seconds
    log.info("Stale-order watcher running every %ss", interval)
    while not stop.is_set():
        try:
            created = await asyncio.to_thread(_sweep_once)
        except Exception:  # a bad sweep must never kill the watcher
            log.exception("Stale-order sweep failed")
        else:
            if created:
                log.info("Raised %d stale-order alert(s)", created)
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue
