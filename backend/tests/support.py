"""Test helpers: tiny wrappers over the HTTP API so tests read like user stories."""
from dataclasses import dataclass

from fastapi.testclient import TestClient

PASSWORD = "secret123"


@dataclass
class Actor:
    token: str
    profile: dict

    @property
    def auth(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    @property
    def id(self) -> int:
        return self.profile["id"]


@dataclass
class Campus:
    shopper: Actor
    other_shopper: Actor
    chef: Actor
    rival_chef: Actor
    rider: Actor
    other_rider: Actor
    pizza: dict
    cola: dict
    restaurant_id: int


def sign_up(api: TestClient, email: str, role: str = "customer", **extra) -> Actor:
    payload = {"name": email.split("@")[0], "email": email, "password": PASSWORD, "role": role, **extra}
    resp = api.post("/api/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return Actor(token=data["access_token"], profile=data["user"])


def add_dish(api: TestClient, owner: Actor, name: str, price: str) -> dict:
    resp = api.post("/api/owner/menu", json={"name": name, "price": price}, headers=owner.auth)
    assert resp.status_code == 201, resp.text
    return resp.json()


def place_order(api: TestClient, campus: Campus, pizzas: int = 2) -> dict:
    """Order ``pizzas`` x Pizza (100) + 1 x Cola (40) as the main shopper."""
    resp = api.post(
        "/api/orders",
        json={
            "restaurant_id": campus.restaurant_id,
            "items": [
                {"menu_item_id": campus.pizza["id"], "quantity": pizzas},
                {"menu_item_id": campus.cola["id"], "quantity": 1},
            ],
            "delivery_address": "Hostel 1",
        },
        headers=campus.shopper.auth,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def owner_sets(api: TestClient, owner: Actor, order_id: int, stage: str):
    return api.patch(f"/api/owner/orders/{order_id}/status", json={"status": stage}, headers=owner.auth)


def rider_sets(api: TestClient, rider: Actor, order_id: int, stage: str):
    return api.patch(f"/api/delivery/orders/{order_id}/status", json={"status": stage}, headers=rider.auth)


def assign(api: TestClient, owner: Actor, order_id: int, partner_id: int):
    return api.post(
        f"/api/owner/orders/{order_id}/assign", json={"delivery_partner_id": partner_id}, headers=owner.auth
    )


def make_ready(api: TestClient, campus: Campus, order_id: int) -> None:
    for stage in ("ACCEPTED", "PREPARING", "READY"):
        resp = owner_sets(api, campus.chef, order_id, stage)
        assert resp.status_code == 200, resp.text


def hand_to_rider(api: TestClient, campus: Campus, order_id: int) -> None:
    make_ready(api, campus, order_id)
    resp = assign(api, campus.chef, order_id, campus.rider.id)
    assert resp.status_code == 200, resp.text


def deliver(api: TestClient, campus: Campus, order_id: int) -> dict:
    hand_to_rider(api, campus, order_id)
    for stage in ("OUT_FOR_DELIVERY", "DELIVERED"):
        resp = rider_sets(api, campus.rider, order_id, stage)
        assert resp.status_code == 200, resp.text
    return resp.json()
