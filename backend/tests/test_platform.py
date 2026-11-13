"""App-level behaviour: health check, tracing headers, and the demo seed."""
from app import demo_data
from app.core.db import SessionFactory
from app.domain.stale_order_watcher import raise_stale_alerts


def test_health(api):
    assert api.get("/health").json() == {"status": "ok"}


def test_responses_carry_timing_and_request_id(api):
    resp = api.get("/health")
    assert resp.headers["X-Process-Time"].endswith("ms")
    assert len(resp.headers["X-Request-ID"]) == 12


def test_incoming_request_id_is_echoed(api):
    assert api.get("/health", headers={"X-Request-ID": "trace-me"}).headers["X-Request-ID"] == "trace-me"


def test_demo_seed_is_idempotent_and_loginable(api):
    assert demo_data.populate() is True
    assert demo_data.populate() is False

    resp = api.post("/api/auth/login", json={"email": "customer@campusbite.app", "password": "password123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    history = api.get("/api/orders/my?page_size=100", headers={"Authorization": f"Bearer {token}"}).json()
    stages = {order["status"] for order in history["items"]}
    assert {"PLACED", "ACCEPTED", "PREPARING", "READY", "ASSIGNED", "OUT_FOR_DELIVERY", "DELIVERED"} <= stages


def test_demo_seed_has_exactly_one_stale_order():
    demo_data.populate()
    with SessionFactory() as db:
        assert raise_stale_alerts(db) == 1
