"""Aggregate numbers for the restaurant-owner dashboard."""
from datetime import datetime, time, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.clock import now_utc
from app.models import (
    LedgerEntry,
    LedgerKind,
    Order,
    OrderLine,
    OrderStage,
    PaymentState,
    ReturnClaim,
    ReturnState,
    Review,
    StaleOrderAlert,
)
from app.schemas.dashboard import BestSeller, KitchenStats

TOP_DISH_LIMIT = 5


def _count_by_stage(db: Session, restaurant_id: int) -> dict[str, int]:
    counts = dict.fromkeys((stage.value for stage in OrderStage), 0)
    grouped = (
        db.query(Order.status, func.count(Order.id))
        .filter(Order.restaurant_id == restaurant_id)
        .group_by(Order.status)
    )
    counts.update({stage.value: n for stage, n in grouped})
    return counts


def _best_sellers(db: Session, restaurant_id: int) -> list[BestSeller]:
    units = func.sum(OrderLine.quantity)
    rows = (
        db.query(OrderLine.name, units)
        .join(Order, Order.id == OrderLine.order_id)
        .filter(Order.restaurant_id == restaurant_id, Order.status != OrderStage.CANCELLED)
        .group_by(OrderLine.name)
        .order_by(units.desc())
        .limit(TOP_DISH_LIMIT)
    )
    return [BestSeller(name=name, quantity=int(qty)) for name, qty in rows]


def build_stats(db: Session, restaurant_id: int) -> KitchenStats:
    mine = Order.restaurant_id == restaurant_id
    by_stage = _count_by_stage(db, restaurant_id)

    start_of_day = datetime.combine(now_utc().date(), time.min, tzinfo=timezone.utc)
    today = db.query(func.count(Order.id)).filter(mine, Order.created_at >= start_of_day).scalar()

    revenue = (
        db.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(mine, Order.payment_status == PaymentState.MOCK_PAID)
        .scalar()
    )
    refunded = (
        db.query(func.coalesce(func.sum(LedgerEntry.amount), 0))
        .join(Order, Order.id == LedgerEntry.order_id)
        .filter(mine, LedgerEntry.entry_type == LedgerKind.REFUND)
        .scalar()
    )
    mean_rating, reviews = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.restaurant_id == restaurant_id)
        .one()
    )
    open_returns = (
        db.query(func.count(ReturnClaim.id))
        .filter(ReturnClaim.restaurant_id == restaurant_id, ReturnClaim.status == ReturnState.REQUESTED)
        .scalar()
    )
    open_alerts = (
        db.query(func.count(StaleOrderAlert.id))
        .filter(StaleOrderAlert.restaurant_id == restaurant_id, StaleOrderAlert.resolved.is_(False))
        .scalar()
    )

    return KitchenStats(
        total_orders=sum(by_stage.values()),
        orders_today=today or 0,
        total_revenue=Decimal(revenue or 0),
        refunded_amount=Decimal(refunded or 0),
        avg_rating=None if mean_rating is None else round(float(mean_rating), 2),
        review_count=reviews,
        status_counts=by_stage,
        top_dishes=_best_sellers(db, restaurant_id),
        pending_returns=open_returns or 0,
        open_reminders=open_alerts or 0,
    )
