"""Mock payment ledger. No real money moves; every entry 'succeeds' immediately."""
import uuid

from app.models import LedgerEntry, LedgerKind, Order, PaymentState


def _reference(tag: str) -> str:
    return f"MOCK-{tag}-{uuid.uuid4().hex[:10].upper()}"


def _entry(order: Order, kind: LedgerKind, tag: str) -> LedgerEntry:
    return LedgerEntry(
        entry_type=kind,
        amount=order.total_amount,
        status="success",
        reference=_reference(tag),
    )


def charge(order: Order, method: str) -> None:
    order.payments.append(_entry(order, LedgerKind.PAYMENT, method.upper()))
    order.payment_status = PaymentState.MOCK_PAID


def refund(order: Order, tag: str) -> None:
    order.payments.append(_entry(order, LedgerKind.REFUND, tag))
    order.payment_status = PaymentState.REFUNDED


def refund_on_cancel(order: Order) -> None:
    """Cancelling a paid order reverses the charge; unpaid orders have nothing to give back."""
    if order.payment_status is PaymentState.MOCK_PAID:
        refund(order, "CANCEL")
