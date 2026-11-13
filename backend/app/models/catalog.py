from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import now_utc
from app.core.db import ModelBase

if TYPE_CHECKING:
    from app.models.orders import Order
    from app.models.people import Account


class Restaurant(ModelBase):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    cuisine: Mapped[str | None] = mapped_column(String(80))
    address: Mapped[str | None] = mapped_column(String(255))
    image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    owner: Mapped["Account"] = relationship(back_populates="owned_restaurants")
    menu: Mapped[list["MenuEntry"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan", order_by="MenuEntry.id"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="restaurant")


class MenuEntry(ModelBase):
    """A dish on a restaurant's menu. Deleting one only flags it, so old orders still make sense."""

    __tablename__ = "menu_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str | None] = mapped_column(String(80))
    image_url: Mapped[str | None] = mapped_column(String(500))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    restaurant: Mapped[Restaurant] = relationship(back_populates="menu")
