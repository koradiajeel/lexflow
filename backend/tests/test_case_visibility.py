"""Lawyers see only the cases assigned to them; Owner and Staff see every case in the firm.

Setup (one firm): lawyers A and B, each with a login; one case for each; a Staff user;
and a Lawyer login that isn't linked to any lawyer profile.
"""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "testpass123"
PDF_BYTES = b"%PDF-1.4\n% LexFlow test file\n"


# ---------- helpers ----------

def unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@test.com"


def unique_phone() -> str:
    return "9" + str(uuid4().int)[:9]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login(client, email: str, password: str = PASSWORD) -> str:
    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def register(client) -> str:
    res = client.post(
        "/auth/register",
        json={
            "firm_name": "Visibility Firm",
            "firm_email": unique("firm"),
            "firm_phone": unique_phone(),
            "firm_address": "1 Test Street",
            "owner_email": unique("owner"),
            "password": PASSWORD,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


def lawyer_with_login(client, owner: str) -> tuple[dict, str]:
    """Create a lawyer profile + its login. Returns (lawyer, lawyer_token)."""
    res = client.post(
        "/lawyers/",
        json={"name": "Lawyer", "email": unique("lawyer"), "phone": unique_phone()},
        headers=auth(owner),
    )
    assert res.status_code == 201, res.text
    lawyer = res.json()
    res = client.post(
        f"/lawyers/{lawyer['id']}/create-login", json={"password": PASSWORD}, headers=auth(owner)
    )
    assert res.status_code == 201, res.text
    return lawyer, login(client, lawyer["email"])


def add_user(client, owner: str, role: str) -> str:
    email = unique(role.lower())
    res = client.post(
        "/users/", json={"email": email, "password": PASSWORD, "role": role}, headers=auth(owner)
    )
    assert res.status_code == 201, res.text
    return login(client, email)


def new_case(client, token: str, client_id: str, lawyer_id: str):
    return client.post(
        "/cases/",
        json={"title": "Case", "description": "Visibility test", "client_id": client_id, "lawyer_id": lawyer_id},
        headers=auth(token),
    )


def upload(client, token: str, case_id: str):
    return client.post(
        f"/cases/{case_id}/documents",
        files={"file": ("test.pdf", PDF_BYTES, "application/pdf")},
        headers=auth(token),
    )


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def firm(client):
    owner = register(client)
    lawyer_a, token_a = lawyer_with_login(client, owner)
    lawyer_b, token_b = lawyer_with_login(client, owner)
    staff = add_user(client, owner, "Staff")
    unlinked_lawyer = add_user(client, owner, "Lawyer")  # Lawyer login with no lawyer profile

    res = client.post(
        "/clients/",
        json={"name": "Client", "email": unique("client"), "phone": unique_phone()},
        headers=auth(owner),
    )
    assert res.status_code == 201, res.text
    client_id = res.json()["id"]

    case_a = new_case(client, owner, client_id, lawyer_a["id"]).json()
    case_b = new_case(client, owner, client_id, lawyer_b["id"]).json()
    doc_b = upload(client, owner, case_b["id"])
    assert doc_b.status_code == 201, doc_b.text

    return {
        "owner": owner, "staff": staff, "unlinked_lawyer": unlinked_lawyer,
        "lawyer_a": lawyer_a, "token_a": token_a,
        "lawyer_b": lawyer_b, "token_b": token_b,
        "client_id": client_id, "case_a": case_a, "case_b": case_b, "doc_b": doc_b.json(),
    }


def case_ids(client, token: str, query: str = "") -> set[str]:
    res = client.get(f"/cases/{query}", headers=auth(token))
    assert res.status_code == 200, res.text
    return {c["id"] for c in res.json()}


# ---------- case list ----------

def test_lawyer_lists_only_own_cases(client, firm):
    assert case_ids(client, firm["token_a"]) == {firm["case_a"]["id"]}
    assert case_ids(client, firm["token_b"]) == {firm["case_b"]["id"]}


def test_owner_and_staff_list_all_firm_cases(client, firm):
    both = {firm["case_a"]["id"], firm["case_b"]["id"]}
    assert case_ids(client, firm["owner"]) == both
    assert case_ids(client, firm["staff"]) == both


def test_lawyer_filtering_by_another_lawyer_gets_nothing(client, firm):
    assert case_ids(client, firm["token_a"], f"?lawyer_id={firm['lawyer_b']['id']}") == set()


def test_unlinked_lawyer_login_sees_no_cases(client, firm):
    assert case_ids(client, firm["unlinked_lawyer"]) == set()
    res = client.get(f"/cases/{firm['case_a']['id']}", headers=auth(firm["unlinked_lawyer"]))
    assert res.status_code == 404


# ---------- single case ----------

def test_lawyer_can_open_and_update_own_case(client, firm):
    case_id = firm["case_a"]["id"]
    assert client.get(f"/cases/{case_id}", headers=auth(firm["token_a"])).status_code == 200
    res = client.patch(f"/cases/{case_id}", json={"status": "In Progress"}, headers=auth(firm["token_a"]))
    assert res.status_code == 200, res.text


def test_lawyer_cannot_open_or_update_other_lawyers_case(client, firm):
    case_id = firm["case_b"]["id"]
    assert client.get(f"/cases/{case_id}", headers=auth(firm["token_a"])).status_code == 404
    res = client.patch(f"/cases/{case_id}", json={"status": "Closed"}, headers=auth(firm["token_a"]))
    assert res.status_code == 404


# ---------- documents ----------

def test_lawyer_can_upload_to_own_case(client, firm):
    assert upload(client, firm["token_a"], firm["case_a"]["id"]).status_code == 201


def test_lawyer_cannot_touch_other_lawyers_documents(client, firm):
    case_id = firm["case_b"]["id"]
    doc_id = firm["doc_b"]["id"]
    token = firm["token_a"]
    assert client.get(f"/cases/{case_id}/documents", headers=auth(token)).status_code == 404
    assert upload(client, token, case_id).status_code == 404
    assert client.get(f"/documents/{doc_id}", headers=auth(token)).status_code == 404
    assert client.get(f"/documents/{doc_id}/download", headers=auth(token)).status_code == 404
    assert client.delete(f"/documents/{doc_id}", headers=auth(token)).status_code == 404
    # ...while the assigned lawyer can still see it
    assert client.get(f"/documents/{doc_id}", headers=auth(firm["token_b"])).status_code == 200


# ---------- creating cases ----------

def test_lawyer_can_create_case_for_self(client, firm):
    res = new_case(client, firm["token_a"], firm["client_id"], firm["lawyer_a"]["id"])
    assert res.status_code == 201, res.text


def test_lawyer_cannot_create_case_for_another_lawyer(client, firm):
    res = new_case(client, firm["token_a"], firm["client_id"], firm["lawyer_b"]["id"])
    assert res.status_code == 403
    assert res.json()["detail"] == "Lawyers can only create cases assigned to themselves"


def test_owner_can_create_case_for_any_lawyer(client, firm):
    res = new_case(client, firm["owner"], firm["client_id"], firm["lawyer_b"]["id"])
    assert res.status_code == 201, res.text
