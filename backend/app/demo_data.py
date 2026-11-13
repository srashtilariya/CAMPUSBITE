"""Populate an empty database with a believable demo campus.

    python -m app.demo_data

Safe to run on every boot: if any account already exists, nothing happens.
Every demo account uses the password below.
"""
from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal

import app.models  # noqa: F401
from app.core.clock import now_utc
from app.core.db import ModelBase, SessionFactory, engine
from app.core.passwords import make_hash
from app.domain import payments
from app.models import Account, MenuEntry, Order, OrderLine, OrderStage, Restaurant, Review, Role

DEMO_PASSWORD = "password123"
DOMAIN = "campusbite.app"


@dataclass
class Kitchen:
    owner_name: str
    owner_email: str
    name: str
    cuisine: str
    blurb: str
    address: str
    image_url: str
    dishes: list[tuple[str, str, str, str]] = field(default_factory=list)  # name, description, price, category


KITCHENS = [
    Kitchen(
        "Rohan Kapoor", f"owner@{DOMAIN}", "Tandoor Junction", "North Indian",
        "Smoky tandoor grills, slow-simmered curries and dum biryani.",
        "Food Court, Block C",
        "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800",
        [
            ("Chicken Tikka Masala", "Charred chicken tikka in a velvety masala", "270", "Mains"),
            ("Kadai Paneer", "Paneer and peppers tossed with kadai spices", "230", "Mains"),
            ("Mutton Biryani", "Dum-cooked basmati with tender mutton", "290", "Rice"),
            ("Chole Bhature", "Spiced chickpeas with two fluffy bhature", "150", "Mains"),
            ("Butter Naan", "Soft tandoor naan brushed with butter", "45", "Breads"),
            ("Rasmalai", "Saffron milk with soft cheese dumplings", "80", "Desserts"),
        ],
    ),
    Kitchen(
        "Giulia Bianchi", f"owner2@{DOMAIN}", "Forno Rosso", "Italian",
        "Stone-oven pizza and hand-rolled pasta.",
        "Main Quad, Shop 7",
        "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800",
        [
            ("Pizza Diavola", "Spicy salami, chilli oil, mozzarella", "329", "Pizza"),
            ("Quattro Formaggi", "Four-cheese white pizza", "359", "Pizza"),
            ("Spaghetti Aglio e Olio", "Garlic, chilli flakes, parsley", "239", "Pasta"),
            ("Mushroom Risotto", "Arborio rice with porcini and parmesan", "299", "Pasta"),
            ("Tomato Bruschetta", "Toasted sourdough, tomato, basil", "139", "Sides"),
            ("Panna Cotta", "Vanilla cream with berry compote", "179", "Desserts"),
        ],
    ),
    Kitchen(
        "Mei Lin", f"owner3@{DOMAIN}", "Bamboo Basket", "Asian",
        "Dumplings, wok noodles and bao from the hostel strip.",
        "Hostel Strip, Unit 5",
        "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800",
        [
            ("Schezwan Noodles", "Fiery wok-tossed noodles", "190", "Noodles"),
            ("Honey Chilli Potato", "Crispy potato in sticky honey chilli", "170", "Starters"),
            ("Chicken Dumplings", "Steamed dumplings with chilli dip (6 pcs)", "150", "Dim Sum"),
            ("Thai Basil Fried Rice", "Jasmine rice, holy basil, egg", "210", "Rice"),
            ("Veg Spring Rolls", "Golden rolls with sweet chilli (4 pcs)", "130", "Starters"),
        ],
    ),
    Kitchen(
        "Farah Siddiqui", f"owner4@{DOMAIN}", "Leaf & Ladle", "Healthy",
        "Grain bowls, wraps and cold-pressed drinks.",
        "Near the Athletics Track",
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
        [
            ("Mediterranean Bowl", "Couscous, falafel, hummus, greens", "230", "Bowls"),
            ("Grilled Paneer Wrap", "Paneer, mint chutney, crunchy slaw", "180", "Wraps"),
            ("Berry Smoothie Bowl", "Mixed berries, banana, granola", "240", "Bowls"),
            ("Hummus Platter", "Hummus, pita, crudites", "190", "Salads"),
            ("Fresh Lime Soda", "Sweet or salted", "80", "Drinks"),
        ],
    ),
]

COURIERS = [("Arjun Nair", f"partner@{DOMAIN}"), ("Kavya Reddy", f"partner2@{DOMAIN}")]
CUSTOMERS = [("Ishaan Verma", f"customer@{DOMAIN}"), ("Ananya Iyer", f"customer2@{DOMAIN}")]


@dataclass
class PastOrder:
    kitchen: str
    dishes: dict[str, int]
    stage: OrderStage
    days_ago: int = 0
    idle_minutes: int | None = None  # minutes since last update; None = closed out long ago
    review: tuple[int, str] | None = None


# History for the main demo customer: finished orders for the dashboards and AI
# insights, plus one live order sitting at every active stage. The PLACED one has
# been idle past the reminder threshold so the owner sees a stale-order alert.
HISTORY = [
    PastOrder("Tandoor Junction", {"Chicken Tikka Masala": 1, "Butter Naan": 2}, OrderStage.DELIVERED, 12,
              review=(5, "Best tikka masala on campus!")),
    PastOrder("Forno Rosso", {"Pizza Diavola": 1, "Tomato Bruschetta": 1}, OrderStage.DELIVERED, 9,
              review=(4, "Lovely pizza, arrived a little late.")),
    PastOrder("Tandoor Junction", {"Mutton Biryani": 2}, OrderStage.DELIVERED, 5),
    PastOrder("Bamboo Basket", {"Schezwan Noodles": 1, "Chicken Dumplings": 1}, OrderStage.DELIVERED, 3),
    PastOrder("Leaf & Ladle", {"Berry Smoothie Bowl": 1}, OrderStage.CANCELLED, 2),
    PastOrder("Tandoor Junction", {"Chicken Tikka Masala": 2}, OrderStage.PLACED, idle_minutes=25),
    PastOrder("Forno Rosso", {"Spaghetti Aglio e Olio": 1}, OrderStage.ACCEPTED, idle_minutes=3),
    PastOrder("Tandoor Junction", {"Chole Bhature": 1, "Rasmalai": 2}, OrderStage.PREPARING, idle_minutes=4),
    PastOrder("Tandoor Junction", {"Kadai Paneer": 1, "Butter Naan": 1}, OrderStage.READY, idle_minutes=5),
    PastOrder("Tandoor Junction", {"Mutton Biryani": 1}, OrderStage.ASSIGNED, idle_minutes=7),
    PastOrder("Tandoor Junction", {"Kadai Paneer": 1, "Butter Naan": 2, "Rasmalai": 1},
              OrderStage.OUT_FOR_DELIVERY, idle_minutes=10),
]

COURIER_STAGES = {OrderStage.ASSIGNED, OrderStage.OUT_FOR_DELIVERY, OrderStage.DELIVERED}


def _people(pw_hash: str) -> tuple[list[Account], list[Account]]:
    customers = [
        Account(name=name, email=email, password_hash=pw_hash, role=Role.CUSTOMER,
                phone=f"+91 98100 1000{n}", address=f"Hostel {n + 1}, Room 20{n}")
        for n, (name, email) in enumerate(CUSTOMERS)
    ]
    couriers = [
        Account(name=name, email=email, password_hash=pw_hash, role=Role.DELIVERY_PARTNER,
                phone=f"+91 97100 2000{n}")
        for n, (name, email) in enumerate(COURIERS)
    ]
    return customers, couriers


def _restaurant(spec: Kitchen, pw_hash: str) -> Restaurant:
    owner = Account(name=spec.owner_name, email=spec.owner_email, password_hash=pw_hash,
                    role=Role.RESTAURANT_OWNER, phone="+91 96100 30000")
    return Restaurant(
        owner=owner, name=spec.name, cuisine=spec.cuisine, description=spec.blurb,
        address=spec.address, image_url=spec.image_url,
        menu=[MenuEntry(name=n, description=d, price=Decimal(p), category=c) for n, d, p, c in spec.dishes],
    )


def _order(past: PastOrder, restaurant: Restaurant, customer: Account, courier: Account) -> Order:
    now = now_utc()
    placed_at = now - timedelta(days=past.days_ago, minutes=(past.idle_minutes or 0) + 5)
    touched_at = placed_at + timedelta(minutes=40) if past.idle_minutes is None else now - timedelta(minutes=past.idle_minutes)

    by_name = {dish.name: dish for dish in restaurant.menu}
    lines = [
        OrderLine(menu_item_id=by_name[name].id, name=name, unit_price=by_name[name].price, quantity=qty)
        for name, qty in past.dishes.items()
    ]
    order = Order(
        customer_id=customer.id, restaurant_id=restaurant.id, status=past.stage, items=lines,
        total_amount=sum((line.unit_price * line.quantity for line in lines), Decimal("0")),
        delivery_address=customer.address, created_at=placed_at, updated_at=touched_at,
        delivery_partner_id=courier.id if past.stage in COURIER_STAGES else None,
    )
    payments.charge(order, "DUMMY_CARD")
    if past.stage is OrderStage.CANCELLED:
        payments.refund_on_cancel(order)
    return order


def populate() -> bool:
    """Seed the database. Returns False if it already had data."""
    ModelBase.metadata.create_all(bind=engine)
    with SessionFactory() as db:
        if db.query(Account.id).first() is not None:
            return False

        pw_hash = make_hash(DEMO_PASSWORD)
        customers, couriers = _people(pw_hash)
        restaurants = {spec.name: _restaurant(spec, pw_hash) for spec in KITCHENS}
        db.add_all([*customers, *couriers, *restaurants.values()])
        db.flush()  # need ids for the order history below

        shopper, courier = customers[0], couriers[0]
        for past in HISTORY:
            restaurant = restaurants[past.kitchen]
            order = _order(past, restaurant, shopper, courier)
            if past.review:
                stars, text = past.review
                order.review = Review(customer_id=shopper.id, restaurant_id=restaurant.id, rating=stars, comment=text)
            db.add(order)
        db.commit()
    return True


if __name__ == "__main__":
    if populate():
        print(f"Demo data loaded. Every account's password is: {DEMO_PASSWORD}")
    else:
        print("Database already has data - demo seed skipped.")
