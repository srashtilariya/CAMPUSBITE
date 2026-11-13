import pytest

from tests.support import owner_sets, place_order


@pytest.mark.parametrize(
    ("who", "method", "path"),
    [
        ("shopper", "GET", "/api/owner/orders"),
        ("chef", "GET", "/api/delivery/orders"),
        ("chef", "POST", "/api/orders"),
        ("rider", "POST", "/api/ai/insights"),
    ],
)
def test_wrong_role_gets_403(api, campus, who, method, path):
    actor = getattr(campus, who)
    resp = api.request(method, path, json={}, headers=actor.auth)
    assert resp.status_code == 403


def test_customer_cannot_view_someone_elses_order(api, campus):
    order = place_order(api, campus)
    assert api.get(f"/api/orders/{order['id']}", headers=campus.other_shopper.auth).status_code == 404


def test_customer_cannot_cancel_someone_elses_order(api, campus):
    order = place_order(api, campus)
    assert api.post(f"/api/orders/{order['id']}/cancel", headers=campus.other_shopper.auth).status_code == 404


def test_owner_cannot_touch_another_restaurants_order(api, campus):
    order = place_order(api, campus)
    assert owner_sets(api, campus.rival_chef, order["id"], "ACCEPTED").status_code == 404


def test_order_history_only_lists_own_orders(api, campus):
    place_order(api, campus)
    assert api.get("/api/orders/my", headers=campus.other_shopper.auth).json()["total"] == 0


def test_owning_restaurant_can_view_order_detail(api, campus):
    order = place_order(api, campus)
    assert api.get(f"/api/orders/{order['id']}", headers=campus.chef.auth).status_code == 200
    assert api.get(f"/api/orders/{order['id']}", headers=campus.rival_chef.auth).status_code == 404
