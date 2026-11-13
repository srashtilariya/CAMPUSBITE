import pytest

from tests.support import place_order


@pytest.fixture
def three_orders(api, campus):
    return [place_order(api, campus) for _ in range(3)]


def test_order_history_paginates(api, campus, three_orders):
    page = api.get("/api/orders/my?page=1&page_size=2", headers=campus.shopper.auth).json()
    assert page["total"] == 3
    assert page["pages"] == 2
    assert len(page["items"]) == 2


@pytest.mark.parametrize(("stage", "expected"), [("ACCEPTED", 0), ("PLACED", 3)])
def test_owner_filters_orders_by_status(api, campus, three_orders, stage, expected):
    listing = api.get(f"/api/owner/orders?status={stage}", headers=campus.chef.auth).json()
    assert listing["total"] == expected


def test_owner_stats_count_orders_and_revenue(api, campus, three_orders):
    stats = api.get("/api/owner/stats", headers=campus.chef.auth).json()
    assert stats["total_orders"] == 3
    assert float(stats["total_revenue"]) == 720.0
    assert stats["status_counts"]["PLACED"] == 3


def test_public_menu_search_and_price_cap(api, campus):
    menu = api.get(f"/api/restaurants/{campus.restaurant_id}/menu?search=piz&max_price=150").json()
    assert [dish["name"] for dish in menu["items"]] == ["Pizza"]


def test_public_menu_rejects_inverted_price_range(api, campus):
    resp = api.get(f"/api/restaurants/{campus.restaurant_id}/menu?min_price=50&max_price=10")
    assert resp.status_code == 400
