"""Restaurant-owner endpoints: profile, menu, incoming orders, returns, alerts and stats.

Every route here requires the restaurant_owner role (enforced at router level);
routes that touch restaurant data additionally resolve the caller's restaurant.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, selectinload

from app.api.auth_guards import owned_restaurant, owner_only
from app.core.clock import now_utc
from app.core.db import db_session
from app.domain import lifecycle, payments
from app.domain.kitchen_stats import build_stats
from app.domain.listing import filter_orders, newest_first, page_of
from app.domain.presenters import present_order, present_order_full, present_return
from app.domain.stale_order_watcher import raise_stale_alerts, settle_alerts
from app.models import (
    Account,
    MenuEntry,
    Order,
    OrderStage,
    Restaurant,
    ReturnClaim,
    ReturnState,
    Role,
    StaleOrderAlert,
)
from app.schemas.accounts import Contact
from app.schemas.catalog import AvailabilityToggle, DishForm, DishPatch, DishView, RestaurantCard, RestaurantPatch
from app.schemas.common import Paginated
from app.schemas.dashboard import AlertView, KitchenStats
from app.schemas.orders import CourierPick, OrderFull, OrderSummary, ReturnQueueItem, ReturnVerdict, StageChange

router = APIRouter(prefix="/owner", tags=["Restaurant Owner"], dependencies=[Depends(owner_only)])


# --- lookups scoped to the caller's restaurant -------------------------------
def _dish(db: Session, dish_id: int, restaurant: Restaurant) -> MenuEntry:
    dish = db.get(MenuEntry, dish_id)
    if dish is None or dish.is_deleted or dish.restaurant_id != restaurant.id:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return dish


def _incoming(db: Session, order_id: int, restaurant: Restaurant) -> Order:
    order = db.get(Order, order_id)
    if order is None or order.restaurant_id != restaurant.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def _undecided_claim(db: Session, claim_id: int, restaurant: Restaurant) -> ReturnClaim:
    claim = db.get(ReturnClaim, claim_id)
    if claim is None or claim.restaurant_id != restaurant.id:
        raise HTTPException(status_code=404, detail="Return request not found")
    if claim.status is not ReturnState.REQUESTED:
        raise HTTPException(status_code=409, detail=f"Return request already {claim.status.value}")
    return claim


def _apply_patch(target, patch) -> None:
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(target, field, value)


def _save(db: Session, obj):
    db.commit()
    db.refresh(obj)
    return obj


# --- restaurant profile -------------------------------------------------------
@router.get("/restaurant", response_model=RestaurantCard)
def view_profile(restaurant: Restaurant = Depends(owned_restaurant)):
    return restaurant


@router.put("/restaurant", response_model=RestaurantCard)
def edit_profile(
    patch: RestaurantPatch, restaurant: Restaurant = Depends(owned_restaurant), db: Session = Depends(db_session)
):
    _apply_patch(restaurant, patch)
    return _save(db, restaurant)


# --- menu -----------------------------------------------------------------------
@router.get("/menu", response_model=Paginated[DishView])
def menu_overview(
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    query = db.query(MenuEntry).filter(MenuEntry.restaurant_id == restaurant.id, MenuEntry.is_deleted.is_(False))
    if search:
        query = query.filter(MenuEntry.name.ilike(f"%{search.strip()}%"))
    return page_of(query.order_by(MenuEntry.category, MenuEntry.name), page, page_size)


@router.post("/menu", response_model=DishView, status_code=status.HTTP_201_CREATED)
def add_dish(form: DishForm, restaurant: Restaurant = Depends(owned_restaurant), db: Session = Depends(db_session)):
    dish = MenuEntry(restaurant_id=restaurant.id, **form.model_dump())
    db.add(dish)
    return _save(db, dish)


@router.put("/menu/{item_id}", response_model=DishView)
def edit_dish(
    item_id: int,
    patch: DishPatch,
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    dish = _dish(db, item_id, restaurant)
    _apply_patch(dish, patch)
    return _save(db, dish)


@router.patch("/menu/{item_id}/availability", response_model=DishView)
def toggle_availability(
    item_id: int,
    toggle: AvailabilityToggle,
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    dish = _dish(db, item_id, restaurant)
    dish.is_available = toggle.is_available
    return _save(db, dish)


@router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_dish(item_id: int, restaurant: Restaurant = Depends(owned_restaurant), db: Session = Depends(db_session)):
    dish = _dish(db, item_id, restaurant)
    # Soft delete: past order lines still point at this row.
    dish.is_deleted = True
    dish.is_available = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- incoming orders ------------------------------------------------------------
@router.get("/orders", response_model=Paginated[OrderSummary])
def incoming_orders(
    status: OrderStage | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    query = db.query(Order).options(selectinload(Order.items)).filter(Order.restaurant_id == restaurant.id)
    query = newest_first(filter_orders(query, status, date_from, date_to))
    return page_of(query, page, page_size, present_order)


@router.get("/orders/{order_id}", response_model=OrderFull)
def incoming_order(order_id: int, restaurant: Restaurant = Depends(owned_restaurant), db: Session = Depends(db_session)):
    return present_order_full(_incoming(db, order_id, restaurant))


@router.patch("/orders/{order_id}/status", response_model=OrderFull)
def set_order_stage(
    order_id: int,
    change: StageChange,
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    order = _incoming(db, order_id, restaurant)
    target = change.status
    if target not in lifecycle.OWNER_SETTABLE:
        hint = " (use the assign endpoint)" if target is OrderStage.ASSIGNED else ""
        raise HTTPException(status_code=400, detail=f"Owners cannot set status {target.value} here{hint}")

    lifecycle.advance(order, target, Role.RESTAURANT_OWNER)
    if target is OrderStage.CANCELLED:
        payments.refund_on_cancel(order)
    # Any movement means the restaurant is on it - clear outstanding alerts.
    settle_alerts(db, order.id)
    return present_order_full(_save(db, order))


@router.get("/delivery-partners", response_model=list[Contact])
def available_couriers(db: Session = Depends(db_session)):
    return db.query(Account).filter(Account.role == Role.DELIVERY_PARTNER).order_by(Account.name).all()


@router.post("/orders/{order_id}/assign", response_model=OrderFull)
def hand_to_courier(
    order_id: int,
    pick: CourierPick,
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    order = _incoming(db, order_id, restaurant)
    courier = db.get(Account, pick.delivery_partner_id)
    if courier is None or courier.role is not Role.DELIVERY_PARTNER:
        raise HTTPException(status_code=400, detail="Selected user is not a delivery partner")
    if order.status is not OrderStage.READY:
        raise HTTPException(
            status_code=400,
            detail=f"Delivery partners can only be assigned to READY orders (current: {order.status.value})",
        )

    lifecycle.advance(order, OrderStage.ASSIGNED, Role.RESTAURANT_OWNER)
    order.delivery_partner_id = courier.id
    return present_order_full(_save(db, order))


# --- stats ------------------------------------------------------------------------
@router.get("/stats", response_model=KitchenStats)
def dashboard_stats(restaurant: Restaurant = Depends(owned_restaurant), db: Session = Depends(db_session)):
    return build_stats(db, restaurant.id)


# --- returns ----------------------------------------------------------------------
@router.get("/returns", response_model=Paginated[ReturnQueueItem])
def return_queue(
    status: ReturnState | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    query = db.query(ReturnClaim).filter(ReturnClaim.restaurant_id == restaurant.id)
    if status:
        query = query.filter(ReturnClaim.status == status)
    return page_of(query.order_by(ReturnClaim.created_at.desc()), page, page_size, present_return)


def _close_claim(claim: ReturnClaim, outcome: ReturnState, verdict: ReturnVerdict | None) -> None:
    stamp = now_utc()
    claim.status = outcome
    claim.resolution_note = verdict.note if verdict else None
    claim.resolved_at = stamp
    claim.order.return_status = outcome
    claim.order.updated_at = stamp


@router.post("/returns/{return_id}/approve", response_model=ReturnQueueItem)
def approve_return(
    return_id: int,
    verdict: ReturnVerdict | None = None,
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    claim = _undecided_claim(db, return_id, restaurant)
    _close_claim(claim, ReturnState.APPROVED, verdict)
    claim.order.status = OrderStage.REFUNDED
    payments.refund(claim.order, "REFUND")
    return present_return(_save(db, claim))


@router.post("/returns/{return_id}/reject", response_model=ReturnQueueItem)
def reject_return(
    return_id: int,
    verdict: ReturnVerdict | None = None,
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    claim = _undecided_claim(db, return_id, restaurant)
    _close_claim(claim, ReturnState.REJECTED, verdict)
    return present_return(_save(db, claim))


# --- stale-order alerts -----------------------------------------------------------
@router.get("/reminders", response_model=Paginated[AlertView])
def alert_inbox(
    include_resolved: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    restaurant: Restaurant = Depends(owned_restaurant),
    db: Session = Depends(db_session),
):
    query = db.query(StaleOrderAlert).filter(StaleOrderAlert.restaurant_id == restaurant.id)
    if not include_resolved:
        query = query.filter(StaleOrderAlert.resolved.is_(False))
    return page_of(query.order_by(StaleOrderAlert.created_at.desc()), page, page_size)


@router.post("/reminders/refresh", response_model=dict)
def sweep_now(db: Session = Depends(db_session)):
    """Run the stale-order sweep on demand instead of waiting for the background watcher."""
    return {"created": raise_stale_alerts(db)}


@router.post("/reminders/{reminder_id}/dismiss", response_model=AlertView)
def dismiss_alert(reminder_id: int, restaurant: Restaurant = Depends(owned_restaurant), db: Session = Depends(db_session)):
    alert = db.get(StaleOrderAlert, reminder_id)
    if alert is None or alert.restaurant_id != restaurant.id:
        raise HTTPException(status_code=404, detail="Reminder not found")
    alert.resolved = True
    return _save(db, alert)
