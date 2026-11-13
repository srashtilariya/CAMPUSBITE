"""Shared fixtures.

The environment must be configured *before* anything under ``app`` is imported,
because the engine and settings are created at import time.
"""
import os
import tempfile

_TEST_DB = os.path.join(tempfile.gettempdir(), "campusbite-tests.sqlite3")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ["ENABLE_BACKGROUND_TASKS"] = "false"
os.environ["OPENAI_API_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.db import ModelBase, engine  # noqa: E402
from app.domain import insights_engine  # noqa: E402
from app.server import app  # noqa: E402
from tests.support import Campus, add_dish, sign_up  # noqa: E402


@pytest.fixture(autouse=True)
def clean_schema():
    ModelBase.metadata.drop_all(bind=engine)
    ModelBase.metadata.create_all(bind=engine)
    yield
    ModelBase.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def fresh_throttle():
    # The AI throttle is process-global and ids restart every test, so wipe it.
    insights_engine.throttle.reset()
    yield
    insights_engine.throttle.reset()


@pytest.fixture
def api():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def campus(api) -> Campus:
    """Two of each role, plus a restaurant (owned by ``chef``) with two dishes."""
    chef = sign_up(api, "chef@uni.example.org", role="restaurant_owner", restaurant_name="Testaurant")
    pizza = add_dish(api, chef, "Pizza", "100.00")
    cola = add_dish(api, chef, "Cola", "40.00")
    return Campus(
        shopper=sign_up(api, "shopper@uni.example.org", address="Hostel 1"),
        other_shopper=sign_up(api, "other.shopper@uni.example.org"),
        chef=chef,
        rival_chef=sign_up(api, "rival.chef@uni.example.org", role="restaurant_owner"),
        rider=sign_up(api, "rider@uni.example.org", role="delivery_partner"),
        other_rider=sign_up(api, "other.rider@uni.example.org", role="delivery_partner"),
        pizza=pizza,
        cola=cola,
        restaurant_id=pizza["restaurant_id"],
    )
