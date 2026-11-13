import pytest

from tests.support import assign, deliver, hand_to_rider, make_ready, owner_sets, place_order, rider_sets


@pytest.fixture
def order_id(api, campus):
    return place_order(api, campus)["id"]


# --- owner side -------------------------------------------------------------------
def test_cannot_assign_rider_before_ready(api, campus, order_id):
    assert assign(api, campus.chef, order_id, campus.rider.id).status_code == 400


@pytest.mark.parametrize("target", ["READY", "DELIVERED"])
def test_owner_cannot_skip_ahead_from_placed(api, campus, order_id, target):
    assert owner_sets(api, campus.chef, order_id, target).status_code == 400


def test_owner_walks_order_to_ready(api, campus, order_id):
    make_ready(api, campus, order_id)
    assert api.get(f"/api/owner/orders/{order_id}", headers=campus.chef.auth).json()["status"] == "READY"


def test_assigning_a_ready_order_sets_partner(api, campus, order_id):
    make_ready(api, campus, order_id)
    resp = assign(api, campus.chef, order_id, campus.rider.id)
    assert resp.json()["status"] == "ASSIGNED"
    assert resp.json()["delivery_partner_id"] == campus.rider.id


# --- rider side -------------------------------------------------------------------
def test_unassigned_rider_sees_nothing(api, campus, order_id):
    hand_to_rider(api, campus, order_id)
    assert api.get("/api/delivery/orders", headers=campus.other_rider.auth).json()["total"] == 0


def test_unassigned_rider_cannot_update(api, campus, order_id):
    hand_to_rider(api, campus, order_id)
    assert rider_sets(api, campus.other_rider, order_id, "OUT_FOR_DELIVERY").status_code == 404


def test_rider_cannot_skip_out_for_delivery(api, campus, order_id):
    hand_to_rider(api, campus, order_id)
    assert rider_sets(api, campus.rider, order_id, "DELIVERED").status_code == 400


def test_rider_sees_customer_address(api, campus, order_id):
    hand_to_rider(api, campus, order_id)
    jobs = api.get("/api/delivery/orders", headers=campus.rider.auth).json()
    assert jobs["items"][0]["customer"]["address"] == "Hostel 1"


def test_delivery_completes_and_lands_in_history(api, campus, order_id):
    final = deliver(api, campus, order_id)
    assert final["status"] == "DELIVERED"
    assert api.get("/api/delivery/history", headers=campus.rider.auth).json()["total"] == 1


# --- cancellation -----------------------------------------------------------------
def test_customer_can_cancel_placed_order(api, campus, order_id):
    resp = api.post(f"/api/orders/{order_id}/cancel", headers=campus.shopper.auth)
    assert resp.json()["status"] == "CANCELLED"
    assert resp.json()["payment_status"] == "refunded"


def test_cannot_cancel_once_accepted(api, campus, order_id):
    owner_sets(api, campus.chef, order_id, "ACCEPTED")
    assert api.post(f"/api/orders/{order_id}/cancel", headers=campus.shopper.auth).status_code == 400


def test_cannot_cancel_delivered_order(api, campus, order_id):
    deliver(api, campus, order_id)
    assert api.post(f"/api/orders/{order_id}/cancel", headers=campus.shopper.auth).status_code == 400
