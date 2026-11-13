import pytest

from tests.support import place_order


@pytest.fixture
def order(api, campus):
    return place_order(api, campus)


def test_new_order_starts_placed(order):
    assert order["status"] == "PLACED"


def test_new_order_is_mock_paid(order):
    assert order["payment_status"] == "mock_paid"


def test_total_is_sum_of_lines(order):
    # 2 x 100 + 1 x 40
    assert float(order["total_amount"]) == 240.0


def test_one_payment_entry_is_recorded(order):
    assert len(order["payments"]) == 1
    assert order["payments"][0]["entry_type"] == "payment"
    assert order["payments"][0]["reference"].startswith("MOCK-DUMMY_CARD-")


def test_sold_out_dish_blocks_checkout(api, campus):
    api.patch(
        f"/api/owner/menu/{campus.pizza['id']}/availability",
        json={"is_available": False},
        headers=campus.chef.auth,
    )
    resp = api.post(
        "/api/orders",
        json={
            "restaurant_id": campus.restaurant_id,
            "items": [{"menu_item_id": campus.pizza["id"], "quantity": 1}],
            "delivery_address": "x y z",
        },
        headers=campus.shopper.auth,
    )
    assert resp.status_code == 400


def test_repeated_dish_in_basket_fails_validation(api, campus):
    line = {"menu_item_id": campus.pizza["id"], "quantity": 1}
    resp = api.post(
        "/api/orders",
        json={"restaurant_id": campus.restaurant_id, "items": [line, line], "delivery_address": "Hostel 1"},
        headers=campus.shopper.auth,
    )
    assert resp.status_code == 422


def test_unknown_restaurant_is_404(api, campus):
    resp = api.post(
        "/api/orders",
        json={"restaurant_id": 9999, "items": [{"menu_item_id": 1, "quantity": 1}], "delivery_address": "Hostel 1"},
        headers=campus.shopper.auth,
    )
    assert resp.status_code == 404
