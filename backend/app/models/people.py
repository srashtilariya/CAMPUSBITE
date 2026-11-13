from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import now_utc
from app.core.db import ModelBase
from app.models.enums import Role, enum_column

if TYPE_CHECKING:
    from app.models.catalog import Restaurant
    from app.models.orders import Order


class Account(ModelBase):
    """Anyone who can sign in: customers, restaurant owners and delivery partners."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(enum_column(Role))
    phone: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    owned_restaurants: Mapped[list["Restaurant"]] = relationship(back_populates="owner")
    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer", foreign_keys="Order.customer_id"
    )
    courier_jobs: Mapped[list["Order"]] = relationship(
        back_populates="delivery_partner", foreign_keys="Order.delivery_partner_id"
    )
