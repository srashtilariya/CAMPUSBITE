"""Customer-facing order endpoints: checkout, history, cancel, review, return."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.api.auth_guards import current_account, customer_only
from app.core.clock import now_utc
from app.core.db import db_session
from app.domain import checkout, lifecycle, payments
from app.domain.listing import filter_orders, newest_first, page_of
from app.domain.presenters import present_order, present_order_full, present_review
from app.domain.stale_order_watcher import settle_alerts
from app.models import Account, Order, OrderStage, ReturnClaim, ReturnState, Review, Role
from app.schemas.catalog import ReviewView
from app.schemas.common import Paginated
from app.schemas.orders import CheckoutForm, OrderFull, OrderSummary, ReturnForm, ReturnView, ReviewForm

router = APIRouter(prefix="/orders", tags=["Customer Orders"])

REVIEWABLE = (OrderStage.DELIVERED, OrderStage.REFUNDED)


def _own_order(db: Session, order_id: int, customer: Account) -> Order:
    order = db.get(Order, order_id)
    # Someone else's order looks exactly like a missing one - no id probing.
    if order is None or order.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def _can_view(account: Account, order: Order) -> bool:
    if account.role is Role.CUSTOMER:
        return order.customer_id == account.id
    if account.role is Role.RESTAURANT_OWNER:
        return order.restaurant.owner_id == account.id
    if account.role is Role.DELIVERY_PARTNER:
        return order.delivery_partner_id == account.id
    return False


@router.post("", response_model=OrderFull, status_code=status.HTTP_201_CREATED)
def checkout_basket(form: CheckoutForm, me: Account = Depends(customer_only), db: Session = Depends(db_session)):
    return present_order_full(checkout.place_order(db, me, form))


@router.get("/my", response_model=Paginated[OrderSummary])
def order_history(
    status: OrderStage | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    me: Account = Depends(customer_only),
    db: Session = Depends(db_session),
):
    query = db.query(Order).options(selectinload(Order.items)).filter(Order.customer_id == me.id)
    query = newest_first(filter_orders(query, status, date_from, date_to))
    return page_of(query, page, page_size, present_order)


@router.get("/{order_id}", response_model=OrderFull)
def order_details(order_id: int, me: Account = Depends(current_account), db: Session = Depends(db_session)):
    order = db.get(Order, order_id)
    if order is None or not _can_view(me, order):
        raise HTTPException(status_code=404, detail="Order not found")
    return present_order_full(order)


@router.post("/{order_id}/cancel", response_model=OrderFull)
def cancel_order(order_id: int, me: Account = Depends(customer_only), db: Session = Depends(db_session)):
    order = _own_order(db, order_id, me)
    if order.status is not OrderStage.PLACED:
        raise HTTPException(
            status_code=400,
            detail=f"Order can only be cancelled while PLACED (current: {order.status.value})",
        )
    lifecycle.advance(order, OrderStage.CANCELLED, me.role)
    payments.refund_on_cancel(order)
    settle_alerts(db, order.id)
    db.commit()
    db.refresh(order)
    return present_order_full(order)


@router.post("/{order_id}/review", response_model=ReviewView, status_code=status.HTTP_201_CREATED)
def leave_review(
    order_id: int, form: ReviewForm, me: Account = Depends(customer_only), db: Session = Depends(db_session)
):
    order = _own_order(db, order_id, me)
    if order.status not in REVIEWABLE:
        raise HTTPException(status_code=400, detail="Only delivered orders can be reviewed")
    if order.review is not None:
        raise HTTPException(status_code=409, detail="This order has already been reviewed")

    review = Review(
        order_id=order.id,
        customer_id=me.id,
        restaurant_id=order.restaurant_id,
        rating=form.rating,
        comment=form.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return present_review(review)


@router.post("/{order_id}/return", response_model=ReturnView, status_code=status.HTTP_201_CREATED)
def open_return(
    order_id: int, form: ReturnForm, me: Account = Depends(customer_only), db: Session = Depends(db_session)
):
    order = _own_order(db, order_id, me)
    # Duplicate check comes first: a refunded order should say "already exists", not "not delivered".
    if order.return_request is not None or order.return_status is not ReturnState.NONE:
        raise HTTPException(status_code=409, detail="A return request already exists for this order")
    if order.status is not OrderStage.DELIVERED:
        raise HTTPException(status_code=400, detail="Returns can only be requested after delivery")

    claim = ReturnClaim(
        order_id=order.id,
        customer_id=me.id,
        restaurant_id=order.restaurant_id,
        reason=form.reason.strip(),
    )
    order.return_status = ReturnState.REQUESTED
    order.updated_at = now_utc()
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim
