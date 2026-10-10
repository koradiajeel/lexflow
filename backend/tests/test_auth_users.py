"""Tests for register, law firm access, user creation and firm isolation.

These run against the dev database, so every test creates its own data
with unique emails and never touches existing firms.
"""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "testpass123"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@test.com"


def unique_phone() -> str:
    return "9" + str(uuid4().int)[:9]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_body(firm_email=None, owner_email=None, password=PASSWORD) -> dict:
    return {
        "firm_name": "Test Firm",
        "firm_email": firm_email or unique("firm"),
        "firm_phone": unique_phone(),
        "firm_address": "1 Test Street",
        "owner_email": owner_email or unique("owner"),
        "password": password,
    }


def register(client) -> tuple[str, str]:
    """Register a new firm + Owner and return (token, law_firm_id)."""
    res = client.post("/auth/register", json=register_body())
    assert res.status_code == 201, res.text
    token = res.json()["access_token"]
    me = client.get("/auth/me", headers=auth(token))
    assert me.status_code == 200, me.text
    return token, me.json()["law_firm_id"]


# ---------- Register ----------

def test_r1_register_valid(client):
    res = client.post("/auth/register", json=register_body())
    assert res.status_code == 201
    assert "access_token" in res.json()


def test_r2_me_is_owner_of_new_firm(client):
    res = client.post("/auth/register", json=register_body())
    token = res.json()["access_token"]
    me = client.get("/auth/me", headers=auth(token))
    assert me.status_code == 200
    assert me.json()["role"] == "Owner"
    assert me.json()["law_firm_id"]


def test_r3_same_firm_email_conflict(client):
    firm_email = unique("firm")
    assert client.post("/auth/register", json=register_body(firm_email=firm_email)).status_code == 201
    assert client.post("/auth/register", json=register_body(firm_email=firm_email)).status_code == 409


def test_r4_same_owner_email_conflict(client):
    owner_email = unique("owner")
    assert client.post("/auth/register", json=register_body(owner_email=owner_email)).status_code == 201
    assert client.post("/auth/register", json=register_body(owner_email=owner_email)).status_code == 409


def test_r5_short_password(client):
    assert client.post("/auth/register", json=register_body(password="123")).status_code == 422


def test_r6_owner_email_case_and_whitespace(client):
    email = unique("owner")
    first = client.post("/auth/register", json=register_body(owner_email=f"  {email.upper()}"))
    assert first.status_code == 201
    second = client.post("/auth/register", json=register_body(owner_email=email))
    assert second.status_code == 409


# ---------- Law firms ----------

def test_l1_post_law_firms_removed(client):
    res = client.post("/law-firms/", json={"name": "x", "email": unique("firm"), "phone": "12345", "address": "x"})
    assert res.status_code == 405


def test_l2_owner_reads_own_firm(client):
    token, firm_id = register(client)
    assert client.get(f"/law-firms/{firm_id}", headers=auth(token)).status_code == 200


def test_l3_owner_cannot_read_other_firm(client):
    token_x, _ = register(client)
    _, firm_y = register(client)
    assert client.get(f"/law-firms/{firm_y}", headers=auth(token_x)).status_code == 404


# ---------- Create user ----------

@pytest.fixture(scope="module")
def owner(client):
    return register(client)


@pytest.fixture(scope="module")
def lawyer_user(client, owner):
    token, _ = owner
    email = unique("lawyer")
    res = client.post("/users/", json={"email": email, "password": PASSWORD, "role": "Lawyer"}, headers=auth(token))
    assert res.status_code == 201, res.text
    return email, res.json()


def test_u1_owner_creates_lawyer(owner, lawyer_user):
    _, firm_id = owner
    _, body = lawyer_user
    assert body["role"] == "Lawyer"
    assert body["law_firm_id"] == firm_id


def test_u2_duplicate_email(client, owner, lawyer_user):
    token, _ = owner
    email, _ = lawyer_user
    res = client.post("/users/", json={"email": email, "password": PASSWORD, "role": "Staff"}, headers=auth(token))
    assert res.status_code == 409


def test_u3_cannot_create_owner(client, owner):
    token, _ = owner
    res = client.post("/users/", json={"email": unique("user"), "password": PASSWORD, "role": "Owner"}, headers=auth(token))
    assert res.status_code == 422


def test_u4_body_law_firm_id_ignored(client, owner):
    token, firm_id = owner
    _, other_firm = register(client)
    res = client.post(
        "/users/",
        json={"email": unique("user"), "password": PASSWORD, "role": "Staff", "law_firm_id": other_firm},
        headers=auth(token),
    )
    assert res.status_code == 201
    assert res.json()["law_firm_id"] == firm_id


def test_u5_short_password(client, owner):
    token, _ = owner
    res = client.post("/users/", json={"email": unique("user"), "password": "123", "role": "Staff"}, headers=auth(token))
    assert res.status_code == 422


def _login(client, email: str) -> str:
    res = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_u6_lawyer_cannot_create_user(client, lawyer_user):
    email, _ = lawyer_user
    token = _login(client, email)
    res = client.post("/users/", json={"email": unique("user"), "password": PASSWORD}, headers=auth(token))
    assert res.status_code == 403


def test_u7_no_token(client):
    res = client.post("/users/", json={"email": unique("user"), "password": PASSWORD})
    assert res.status_code == 401


def test_u8_lawyer_login_and_me(client, lawyer_user):
    email, body = lawyer_user
    token = _login(client, email)
    me = client.get("/auth/me", headers=auth(token))
    assert me.status_code == 200
    assert me.json()["role"] == "Lawyer"
    assert me.json()["law_firm_id"] == body["law_firm_id"]


# ---------- Firm isolation ----------
# F1 skipped: there is no GET /cases/ list route yet.

def test_f2_other_firm_cannot_see_case(client):
    token_x, firm_x = register(client)
    token_y, _ = register(client)

    lawyer = client.post(
        "/Lawyers/",
        json={"name": "Test Lawyer", "email": unique("lawyer"), "phone": unique_phone(), "law_firm_id": firm_x},
        headers=auth(token_x),
    )
    assert lawyer.status_code == 201, lawyer.text

    test_client = client.post(
        "/clients/",
        json={"name": "Test Client", "email": unique("client"), "phone": unique_phone(), "law_firm_id": firm_x},
        headers=auth(token_x),
    )
    assert test_client.status_code == 201, test_client.text

    case = client.post(
        "/cases/",
        json={
            "title": "Test Case",
            "description": "Isolation test",
            "client_id": test_client.json()["id"],
            "lawyer_id": lawyer.json()["id"],
        },
        headers=auth(token_x),
    )
    assert case.status_code == 201, case.text
    case_id = case.json()["id"]

    # Firm X can see its own case, firm Y gets 404
    assert client.get(f"/cases/{case_id}", headers=auth(token_x)).status_code == 200
    assert client.get(f"/cases/{case_id}", headers=auth(token_y)).status_code == 404
    assert client.get(f"/cases/{case_id}/documents", headers=auth(token_y)).status_code == 404
