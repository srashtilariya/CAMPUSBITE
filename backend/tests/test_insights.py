from unittest.mock import patch

from tests.support import place_order

ENDPOINT = "/api/ai/insights"


def test_missing_api_key_is_503(api, campus):
    place_order(api, campus)
    assert api.post(ENDPOINT, json={}, headers=campus.shopper.auth).status_code == 503


def test_customer_without_orders_gets_canned_reply(api, campus):
    resp = api.post(ENDPOINT, json={}, headers=campus.other_shopper.auth)
    assert resp.status_code == 200
    assert resp.json()["orders_considered"] == 0


def test_model_only_sees_callers_orders(api, campus):
    place_order(api, campus)
    seen = {}

    def fake_model(orders, question, today):
        seen["customers"] = {o.customer_id for o in orders}
        seen["question"] = question
        return "summary"

    with patch("app.domain.insights_engine.ask_model", side_effect=fake_model):
        resp = api.post(ENDPOINT, json={"question": "How much did I spend?"}, headers=campus.shopper.auth)

    assert resp.json()["answer"] == "summary"
    assert resp.json()["orders_considered"] == 1
    assert seen == {"customers": {campus.shopper.id}, "question": "How much did I spend?"}


def test_throttle_kicks_in_with_retry_after(api, campus):
    for _ in range(5):
        assert api.post(ENDPOINT, json={}, headers=campus.other_shopper.auth).status_code == 200
    resp = api.post(ENDPOINT, json={}, headers=campus.other_shopper.auth)
    assert resp.status_code == 429
    assert int(resp.headers["Retry-After"]) > 0
