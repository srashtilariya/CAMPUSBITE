"""The order state machine.

Each stage lists the stages it may move to and which roles are allowed to make
that move. Anything not listed is an invalid transition.
"""
from fastapi import HTTPException

from app.core.clock import now_utc
from app.models import Order, OrderStage, Role

_OWNER = frozenset({Role.RESTAURANT_OWNER})
_COURIER = frozenset({Role.DELIVERY_PARTNER})

FLOW: dict[OrderStage, dict[OrderStage, frozenset[Role]]] = {
    OrderStage.PLACED: {
        OrderStage.ACCEPTED: _OWNER,
        OrderStage.CANCELLED: frozenset({Role.CUSTOMER, Role.RESTAURANT_OWNER}),
    },
    OrderStage.ACCEPTED: {OrderStage.PREPARING: _OWNER},
    OrderStage.PREPARING: {OrderStage.READY: _OWNER},
    OrderStage.READY: {OrderStage.ASSIGNED: _OWNER},
    OrderStage.ASSIGNED: {OrderStage.OUT_FOR_DELIVERY: _COURIER},
    OrderStage.OUT_FOR_DELIVERY: {OrderStage.DELIVERED: _COURIER},
}

# What each role may request through its generic "set status" endpoint.
# (Owners reach ASSIGNED through the dedicated assign endpoint instead.)
OWNER_SETTABLE = frozenset(
    {OrderStage.ACCEPTED, OrderStage.PREPARING, OrderStage.READY, OrderStage.CANCELLED}
)
COURIER_SETTABLE = frozenset({OrderStage.OUT_FOR_DELIVERY, OrderStage.DELIVERED})


def check_move(current: OrderStage, target: OrderStage, actor: Role) -> None:
    """400 if the move doesn't exist at all, 403 if it exists but not for this role."""
    permitted = FLOW.get(current, {}).get(target)
    if permitted is None:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current.value} to {target.value}",
        )
    if actor not in permitted:
        raise HTTPException(
            status_code=403,
            detail=f"Role {actor.value} cannot move an order from {current.value} to {target.value}",
        )


def advance(order: Order, target: OrderStage, actor: Role) -> None:
    check_move(order.status, target, actor)
    order.status = target
    order.updated_at = now_utc()
