"""Delivery-partner endpoints. A courier only ever sees orders assigned to them."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Query as SAQuery
from sqlalchemy.orm import Session, selectinload

from app.api.auth_guards import courier_only
from app.core.db import db_session
from app.domain import lifecycle
from app.domain.listing import page_of
from app.domain.presenters import present_order_full
from app.models import Account, Order, OrderStage, Role
from app.schemas.common import Paginated
from app.schemas.orders import OrderFull, StageChange

router = APIRouter(prefix="/delivery", tags=["Delivery Partner"])

ON_THE_ROAD = (OrderStage.ASSIGNED, OrderStage.OUT_FOR_DELIVERY)
FINISHED = (OrderStage.DELIVERED, OrderStage.REFUNDED)


def _my_jobs(db: Session, courier: Account) -> SAQuery:
    return (
        db.query(Order)
        .options(selectinload(Order.items), selectinload(Order.customer), selectinload(Order.restaurant))
        .filter(Order.delivery_partner_id == courier.id)
    )


@router.get("/orders", response_model=Paginated[OrderFull])
def current_jobs(
    status: OrderStage | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    me: Account = Depends(courier_only),
    db: Session = Depends(db_session),
):
    stage_filter = Order.status == status if status else Order.status.in_(ON_THE_ROAD)
    query = _my_jobs(db, me).filter(stage_filter).order_by(Order.updated_at.desc())
    return page_of(query, page, page_size, present_order_full)


@router.get("/history", response_model=Paginated[OrderFull])
def past_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    me: Account = Depends(courier_only),
    db: Session = Depends(db_session),
):
    query = _my_jobs(db, me).filter(Order.status.in_(FINISHED)).order_by(Order.updated_at.desc())
    return page_of(query, page, page_size, present_order_full)


@router.patch("/orders/{order_id}/status", response_model=OrderFull)
def update_job(
    order_id: int, change: StageChange, me: Account = Depends(courier_only), db: Session = Depends(db_session)
):
    order = db.get(Order, order_id)
    if order is None or order.delivery_partner_id != me.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if change.status not in lifecycle.COURIER_SETTABLE:
        raise HTTPException(status_code=400, detail=f"Delivery partners cannot set status {change.status.value}")

    lifecycle.advance(order, change.status, Role.DELIVERY_PARTNER)
    db.commit()
    db.refresh(order)
    return present_order_full(order)
