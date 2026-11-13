"""String enums shared by the ORM and the API schemas.

The *values* are part of the public API contract - rename members freely, but
never change what they serialize to.
"""
import enum

from sqlalchemy import Enum as SAEnum


class Role(str, enum.Enum):
    CUSTOMER = "customer"
    RESTAURANT_OWNER = "restaurant_owner"
    DELIVERY_PARTNER = "delivery_partner"


class OrderStage(str, enum.Enum):
    PLACED = "PLACED"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY = "READY"
    ASSIGNED = "ASSIGNED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentState(str, enum.Enum):
    PENDING = "pending"
    MOCK_PAID = "mock_paid"
    REFUNDED = "refunded"


class ReturnState(str, enum.Enum):
    NONE = "none"
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"


class LedgerKind(str, enum.Enum):
    PAYMENT = "payment"
    REFUND = "refund"


def enum_column(enum_cls: type[enum.Enum]) -> SAEnum:
    """Store enums as plain VARCHARs holding the member *value* (portable across SQLite/Postgres)."""
    return SAEnum(
        enum_cls,
        values_callable=lambda members: [m.value for m in members],
        native_enum=False,
        length=32,
    )
