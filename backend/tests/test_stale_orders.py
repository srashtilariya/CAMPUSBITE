from datetime import timedelta

import pytest

from app.core.clock import now_utc
from app.core.db import SessionFactory
from app.domain.stale_order_watcher import raise_stale_alerts
from app.models import Order, StaleOrderAlert
from tests.support import owner_sets, place_order


@pytest.fixture
def stale_order_id(api, campus):
    oid = place_order(api, campus)["id"]
    with SessionFactory() as db:
        db.get(Order, oid).updated_at = now_utc() - timedelta(minutes=20)
        db.commit()
    return oid


@pytest.fixture
def db():
    with SessionFactory() as session:
        yield session


def _inbox(api, owner):
    return api.get("/api/owner/reminders", headers=owner.auth).json()


def test_sweep_flags_stale_order_once(db, stale_order_id):
    assert raise_stale_alerts(db) == 1
    assert raise_stale_alerts(db) == 0
    assert db.query(StaleOrderAlert).count() == 1


def test_fresh_orders_are_not_flagged(api, campus, db):
    place_order(api, campus)
    assert raise_stale_alerts(db) == 0


def test_alert_visible_only_to_owning_restaurant(api, campus, db, stale_order_id):
    raise_stale_alerts(db)
    assert _inbox(api, campus.chef)["total"] == 1
    assert _inbox(api, campus.rival_chef)["total"] == 0


def test_moving_the_order_clears_its_alert(api, campus, db, stale_order_id):
    raise_stale_alerts(db)
    owner_sets(api, campus.chef, stale_order_id, "ACCEPTED")
    assert _inbox(api, campus.chef)["total"] == 0


def test_manual_refresh_endpoint_runs_sweep(api, campus, stale_order_id):
    resp = api.post("/api/owner/reminders/refresh", headers=campus.chef.auth)
    assert resp.json() == {"created": 1}
