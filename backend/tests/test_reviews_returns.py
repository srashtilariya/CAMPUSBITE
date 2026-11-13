import pytest

from tests.support import deliver, place_order


@pytest.fixture
def order_id(api, campus):
    return place_order(api, campus)["id"]


@pytest.fixture
def delivered_id(api, campus, order_id):
    deliver(api, campus, order_id)
    return order_id


def _review(api, campus, oid, **body):
    return api.post(f"/api/orders/{oid}/review", json=body, headers=campus.shopper.auth)


def _request_return(api, campus, oid, reason="Cold food"):
    return api.post(f"/api/orders/{oid}/return", json={"reason": reason}, headers=campus.shopper.auth)


def _decide(api, owner, claim_id, verdict, **body):
    return api.post(f"/api/owner/returns/{claim_id}/{verdict}", json=body or None, headers=owner.auth)


def _order(api, campus, oid):
    return api.get(f"/api/orders/{oid}", headers=campus.shopper.auth).json()


# --- reviews ----------------------------------------------------------------------
def test_cannot_review_undelivered_order(api, campus, order_id):
    assert _review(api, campus, order_id, rating=5).status_code == 400


def test_review_delivered_order(api, campus, delivered_id):
    assert _review(api, campus, delivered_id, rating=4, comment="ok").status_code == 201


def test_second_review_is_a_conflict(api, campus, delivered_id):
    _review(api, campus, delivered_id, rating=4)
    assert _review(api, campus, delivered_id, rating=4).status_code == 409


# --- returns ----------------------------------------------------------------------
def test_cannot_return_undelivered_order(api, campus, order_id):
    assert _request_return(api, campus, order_id).status_code == 400


def test_return_request_created(api, campus, delivered_id):
    assert _request_return(api, campus, delivered_id).status_code == 201
    assert _order(api, campus, delivered_id)["return_status"] == "requested"


def test_second_return_request_is_a_conflict(api, campus, delivered_id):
    _request_return(api, campus, delivered_id)
    assert _request_return(api, campus, delivered_id, "Again please").status_code == 409


def test_other_restaurant_cannot_decide_return(api, campus, delivered_id):
    claim_id = _request_return(api, campus, delivered_id).json()["id"]
    assert _decide(api, campus.rival_chef, claim_id, "approve").status_code == 404


def test_approving_return_refunds_order(api, campus, delivered_id):
    claim_id = _request_return(api, campus, delivered_id).json()["id"]
    resp = _decide(api, campus.chef, claim_id, "approve", note="Sorry")
    assert resp.json()["status"] == "approved"

    order = _order(api, campus, delivered_id)
    assert order["status"] == "REFUNDED"
    assert order["payment_status"] == "refunded"
    assert order["return_status"] == "approved"
    assert [p["entry_type"] for p in order["payments"]] == ["payment", "refund"]


def test_decided_return_cannot_be_decided_again(api, campus, delivered_id):
    claim_id = _request_return(api, campus, delivered_id).json()["id"]
    _decide(api, campus.chef, claim_id, "approve")
    assert _decide(api, campus.chef, claim_id, "reject").status_code == 409


def test_rejecting_return_keeps_payment(api, campus, delivered_id):
    claim_id = _request_return(api, campus, delivered_id, "Wrong item").json()["id"]
    _decide(api, campus.chef, claim_id, "reject")
    order = _order(api, campus, delivered_id)
    assert order["return_status"] == "rejected"
    assert order["payment_status"] == "mock_paid"
