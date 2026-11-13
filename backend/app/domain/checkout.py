"""Turning a customer's basket into a persisted, (mock-)paid order."""
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain import payments
from app.models import Account, MenuEntry, Order, OrderLine, OrderStage, PaymentState, Restaurant
from app.schemas.orders import CheckoutForm


def _load_dishes(db: Session, restaurant: Restaurant, wanted: list[int]) -> dict[int, MenuEntry]:
    rows = db.query(MenuEntry).filter(
        MenuEntry.restaurant_id == restaurant.id,
        MenuEntry.id.in_(wanted),
        MenuEntry.is_deleted.is_(False),
    )
    dishes = {dish.id: dish for dish in rows}

    unknown = [dish_id for dish_id in wanted if dish_id not in dishes]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Menu items not found in this restaurant: {unknown}")

    sold_out = [dishes[dish_id].name for dish_id in wanted if not dishes[dish_id].is_available]
    if sold_out:
        raise HTTPException(status_code=400, detail=f"Currently unavailable: {', '.join(sold_out)}")
    return dishes


def place_order(db: Session, customer: Account, form: CheckoutForm) -> Order:
    restaurant = db.get(Restaurant, form.restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    dishes = _load_dishes(db, restaurant, [line.menu_item_id for line in form.items])

    lines = []
    for wanted in form.items:
        dish = dishes[wanted.menu_item_id]
        lines.append(
            OrderLine(menu_item_id=dish.id, name=dish.name, unit_price=dish.price, quantity=wanted.quantity)
        )

    order = Order(
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        status=OrderStage.PLACED,
        payment_status=PaymentState.PENDING,
        delivery_address=form.delivery_address.strip(),
        notes=form.notes,
        items=lines,
        total_amount=sum((line.unit_price * line.quantity for line in lines), Decimal("0")),
    )
    payments.charge(order, form.payment_method)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
