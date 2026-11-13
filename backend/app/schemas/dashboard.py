"""Shapes used only by the restaurant-owner dashboard."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import FromORM


class AlertView(FromORM):
    id: int
    order_id: int
    order_status: str
    message: str
    resolved: bool
    created_at: datetime


class BestSeller(BaseModel):
    name: str
    quantity: int


class KitchenStats(BaseModel):
    total_orders: int
    orders_today: int
    total_revenue: Decimal
    refunded_amount: Decimal
    avg_rating: float | None
    review_count: int
    status_counts: dict[str, int]
    top_dishes: list[BestSeller]
    pending_returns: int
    open_reminders: int
