import pytest

from tests.support import PASSWORD, sign_up

EMAIL = "alice@uni.example.org"


@pytest.fixture
def alice(api):
    return sign_up(api, EMAIL)


def _login(api, email, password):
    return api.post("/api/auth/login", json={"email": email, "password": password})


def test_signup_returns_bearer_token_and_customer_profile(alice):
    assert alice.token
    assert alice.profile["role"] == "customer"
    assert alice.profile["email"] == EMAIL


def test_signup_lowercases_email(api):
    actor = sign_up(api, "Mixed.Case@Uni.Example.org")
    assert actor.profile["email"] == "mixed.case@uni.example.org"


def test_duplicate_email_is_a_conflict(api, alice):
    resp = api.post("/api/auth/register", json={"name": "aa", "email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 409


def test_login_with_wrong_password_is_rejected(api, alice):
    assert _login(api, EMAIL, "wrong").status_code == 401


def test_login_with_unknown_email_is_rejected(api):
    assert _login(api, "ghost@uni.example.org", PASSWORD).status_code == 401


def test_login_token_identifies_the_user(api, alice):
    token = _login(api, EMAIL, PASSWORD).json()["access_token"]
    me = api.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == alice.id
    assert me.json()["role"] == "customer"


def test_me_requires_a_token(api):
    assert api.get("/api/auth/me").status_code == 401


def test_me_rejects_a_garbage_token(api):
    assert api.get("/api/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_owner_signup_creates_named_restaurant(api):
    owner = sign_up(api, "ola@uni.example.org", role="restaurant_owner", restaurant_name="Ola's Diner")
    assert api.get("/api/owner/restaurant", headers=owner.auth).json()["name"] == "Ola's Diner"


def test_owner_signup_without_name_gets_default_kitchen(api):
    owner = sign_up(api, "ben@uni.example.org", role="restaurant_owner")
    assert api.get("/api/owner/restaurant", headers=owner.auth).json()["name"] == "ben's Kitchen"
