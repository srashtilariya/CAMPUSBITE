"""An order plus everything that hangs off it: lines, ledger, review and return claim."""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import now_utc
from app.core.db import ModelBase
from app.models.enums import LedgerKind, OrderStage, PaymentState, ReturnState, enum_column

if TYPE_CHECKING:
    from app.models.catalog import Restaurant
    from app.models.people import Account


def _timestamp(**kwargs) -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), default=now_utc, **kwargs)


class Order(ModelBase):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    delivery_partner_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), index=True)
    status: Mapped[OrderStage] = mapped_column(
        enum_column(OrderStage), default=OrderStage.PLACED, index=True
    )
    payment_status: Mapped[PaymentState] = mapped_column(
        enum_column(PaymentState), default=PaymentState.PENDING
    )
    return_status: Mapped[ReturnState] = mapped_column(
        enum_column(ReturnState), default=ReturnState.NONE
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    delivery_address: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _timestamp(index=True)
    updated_at: Mapped[datetime] = _timestamp()

    # NB: the attribute names below double as API field names (schemas read them directly).
    customer: Mapped["Account"] = relationship(back_populates="orders", foreign_keys=[customer_id])
    delivery_partner: Mapped["Account | None"] = relationship(
        back_populates="courier_jobs", foreign_keys=[delivery_partner_id]
    )
    restaurant: Mapped["Restaurant"] = relationship(back_populates="orders")
    items: Mapped[list["OrderLine"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", order_by="OrderLine.id"
    )
    payments: Mapped[list["LedgerEntry"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", order_by="LedgerEntry.id"
    )
    review: Mapped["Review | None"] = relationship(back_populates="order", uselist=False)
    return_request: Mapped["ReturnClaim | None"] = relationship(back_populates="order", uselist=False)


class OrderLine(ModelBase):
    """Snapshot of a dish at checkout time - name and price are copied, not referenced."""

    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    menu_item_id: Mapped[int | None] = mapped_column(ForeignKey("menu_entries.id"))
    name: Mapped[str] = mapped_column(String(150))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int] = mapped_column(Integer)

    order: Mapped[Order] = relationship(back_populates="items")


class LedgerEntry(ModelBase):
    """One money movement (mock charge or refund) against an order."""

    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    entry_type: Mapped[LedgerKind] = mapped_column(enum_column(LedgerKind))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(32))
    reference: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = _timestamp()

    order: Mapped[Order] = relationship(back_populates="payments")


class Review(ModelBase):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("order_id", name="uq_reviews_one_per_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _timestamp()

    order: Mapped[Order] = relationship(back_populates="review")
    customer: Mapped["Account"] = relationship()


class ReturnClaim(ModelBase):
    __tablename__ = "return_claims"
    __table_args__ = (UniqueConstraint("order_id", name="uq_return_claims_one_per_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[ReturnState] = mapped_column(
        enum_column(ReturnState), default=ReturnState.REQUESTED
    )
    resolution_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _timestamp()
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order: Mapped[Order] = relationship(back_populates="return_request")
