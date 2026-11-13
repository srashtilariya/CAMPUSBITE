from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.enums import OrderStage, PaymentState, ReturnState
from app.schemas.accounts import Contact
from app.schemas.catalog import ReviewView
from app.schemas.common import FromORM


# ----- inbound -----------------------------------------------------------------
class BasketLine(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1, le=50)


class CheckoutForm(BaseModel):
    restaurant_id: int
    items: list[BasketLine] = Field(min_length=1)
    delivery_address: str = Field(min_length=3, max_length=255)
    notes: str | None = Field(default=None, max_length=500)
    payment_method: str = Field(default="dummy_card", max_length=32)

    @field_validator("items")
    @classmethod
    def _no_repeated_dishes(cls, lines: list[BasketLine]) -> list[BasketLine]:
        seen: set[int] = set()
        for line in lines:
            if line.menu_item_id in seen:
                raise ValueError("Duplicate menu items in cart; merge quantities instead")
            seen.add(line.menu_item_id)
        return lines


class StageChange(BaseModel):
    status: OrderStage


class CourierPick(BaseModel):
    delivery_partner_id: int


class ReviewForm(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class ReturnForm(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)


class ReturnVerdict(BaseModel):
    note: str | None = Field(default=None, max_length=500)


# ----- outbound ----------------------------------------------------------------
class LineView(FromORM):
    id: int
    menu_item_id: int | None
    name: str
    unit_price: Decimal
    quantity: int


class LedgerView(FromORM):
    id: int
    entry_type: str
    amount: Decimal
    status: str
    reference: str
    created_at: datetime


class ReturnView(FromORM):
    id: int
    order_id: int
    reason: str
    status: ReturnState
    resolution_note: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None


class ReturnQueueItem(ReturnView):
    customer_name: str | None = None
    order_total: Decimal | None = None


class OrderSummary(FromORM):
    id: int
    customer_id: int
    restaurant_id: int
    restaurant_name: str | None = None
    delivery_partner_id: int | None = None
    status: OrderStage
    payment_status: PaymentState
    return_status: ReturnState
    total_amount: Decimal
    delivery_address: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[LineView] = []
    has_review: bool = False


class OrderFull(OrderSummary):
    customer: Contact | None = None
    delivery_partner: Contact | None = None
    payments: list[LedgerView] = []
    review: ReviewView | None = None
    return_request: ReturnView | None = None
