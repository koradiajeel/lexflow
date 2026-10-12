"""Tests for lawyer login accounts (POST /lawyers/{id}/create-login),
the lawyer_id in /auth/me, and POST /auth/change-password.

Every test registers its own firms and users with unique emails.
"""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "testpass123"
LAWYER_PASSWORD = "lawyerpass123"


# ---------- helpers ----------

def unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@test.com"


def unique_phone() -> str:
    return "9" + str(uuid4().int)[:9]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register(client) -> str:
    """Register a new firm + Owner. Returns the owner token."""
    res = client.post(
        "/auth/register",
        json={
            "firm_name": "Test Firm",
            "firm_email": unique("firm"),
            "firm_phone": unique_phone(),
            "firm_address": "1 Test Street",
            "owner_email": unique("owner"),
            "password": PASSWORD,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


def add_lawyer(client, token: str, email: str | None = None) -> dict:
    res = client.post(
        "/lawyers/",
        json={"name": "Test Lawyer", "email": email or unique("lawyer-rec"), "phone": unique_phone()},
        headers=auth(token),
    )
    assert res.status_code == 201, res.text
    return res.json()


def create_login(client, token: str, lawyer_id: str, password: str = LAWYER_PASSWORD):
    return client.post(
        f"/lawyers/{lawyer_id}/create-login",
        json={"password": password},
        headers=auth(token),
    )


def login(client, email: str, password: str):
    return client.post("/auth/login", json={"email": email, "password": password})


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ---------- create-login ----------

def test_owner_creates_login_and_lawyer_can_sign_in(client):
    owner = register(client)
    lawyer = add_lawyer(client, owner)
    assert lawyer["user_id"] is None

    res = create_login(client, owner, lawyer["id"])
    assert res.status_code == 201, res.text
    assert res.json()["user_id"] is not None

    signed_in = login(client, lawyer["email"], LAWYER_PASSWORD)
    assert signed_in.status_code == 200, signed_in.text

    me = client.get("/auth/me", headers=auth(signed_in.json()["access_token"])).json()
    assert me["role"] == "Lawyer"
    assert me["lawyer_id"] == lawyer["id"]
    assert me["id"] == res.json()["user_id"]


def test_lawyer_list_shows_user_id(client):
    owner = register(client)
    lawyer = add_lawyer(client, owner)
    create_login(client, owner, lawyer["id"])

    listed = client.get("/lawyers/", headers=auth(owner)).json()
    assert listed[0]["id"] == lawyer["id"]
    assert listed[0]["user_id"] is not None


def test_create_login_twice_is_409(client):
    owner = register(client)
    lawyer = add_lawyer(client, owner)
    assert create_login(client, owner, lawyer["id"]).status_code == 201

    again = create_login(client, owner, lawyer["id"])
    assert again.status_code == 409
    assert again.json()["detail"] == "This lawyer already has a login"


def test_create_login_when_email_already_has_account_is_409(client):
    owner = register(client)
    email = unique("taken")
    res = client.post(
        "/users/",
        json={"email": email, "password": PASSWORD, "role": "Staff"},
        headers=auth(owner),
    )
    assert res.status_code == 201, res.text
    lawyer = add_lawyer(client, owner, email=email)

    conflict = create_login(client, owner, lawyer["id"])
    assert conflict.status_code == 409
    assert conflict.json()["detail"] == "A user with this email already exists"


def test_create_login_short_password_is_422(client):
    owner = register(client)
    lawyer = add_lawyer(client, owner)
    assert create_login(client, owner, lawyer["id"], password="short").status_code == 422


def test_only_owner_can_create_login(client):
    owner = register(client)
    lawyer = add_lawyer(client, owner)
    assert create_login(client, owner, lawyer["id"]).status_code == 201
    lawyer_token = login(client, lawyer["email"], LAWYER_PASSWORD).json()["access_token"]

    other = add_lawyer(client, owner)
    assert create_login(client, lawyer_token, other["id"]).status_code == 403


def test_create_login_for_other_firms_lawyer_is_404(client):
    owner_x = register(client)
    owner_y = register(client)
    lawyer_y = add_lawyer(client, owner_y)

    assert create_login(client, owner_x, lawyer_y["id"]).status_code == 404


def test_changing_lawyer_email_updates_login_email(client):
    owner = register(client)
    lawyer = add_lawyer(client, owner)
    create_login(client, owner, lawyer["id"])

    new_email = unique("renamed")
    res = client.patch(f"/lawyers/{lawyer['id']}", json={"email": new_email}, headers=auth(owner))
    assert res.status_code == 200, res.text

    assert login(client, new_email, LAWYER_PASSWORD).status_code == 200
    assert login(client, lawyer["email"], LAWYER_PASSWORD).status_code == 401


def test_owner_me_has_no_lawyer_id(client):
    owner = register(client)
    me = client.get("/auth/me", headers=auth(owner)).json()
    assert me["lawyer_id"] is None


# ---------- change-password ----------

def test_change_password(client):
    owner = register(client)
    lawyer = add_lawyer(client, owner)
    create_login(client, owner, lawyer["id"])
    token = login(client, lawyer["email"], LAWYER_PASSWORD).json()["access_token"]

    wrong = client.post(
        "/auth/change-password",
        json={"current_password": "not-my-password", "new_password": "brandnew123"},
        headers=auth(token),
    )
    assert wrong.status_code == 400
    assert wrong.json()["detail"] == "Current password is incorrect"

    same = client.post(
        "/auth/change-password",
        json={"current_password": LAWYER_PASSWORD, "new_password": LAWYER_PASSWORD},
        headers=auth(token),
    )
    assert same.status_code == 400

    ok = client.post(
        "/auth/change-password",
        json={"current_password": LAWYER_PASSWORD, "new_password": "brandnew123"},
        headers=auth(token),
    )
    assert ok.status_code == 204, ok.text

    assert login(client, lawyer["email"], LAWYER_PASSWORD).status_code == 401
    assert login(client, lawyer["email"], "brandnew123").status_code == 200


def test_change_password_needs_login(client):
    res = client.post(
        "/auth/change-password",
        json={"current_password": "a", "new_password": "brandnew123"},
    )
    assert res.status_code in (401, 403)
