from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.clock import now_utc
from app.core.db import ModelBase


class StaleOrderAlert(ModelBase):
    """Raised by the watcher when an order sits in PLACED/ACCEPTED for too long."""

    __tablename__ = "stale_order_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    order_status: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(String(255))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
