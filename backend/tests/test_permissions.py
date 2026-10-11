"""Permission and firm-isolation tests for lawyers, clients, cases,
law firms, users and documents.

Every test uses its own freshly registered firms and users (unique emails),
so the existing Firm A / Firm B test data is never touched.
"""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import CaseStatus

PASSWORD = "testpass123"
PDF_BYTES = b"%PDF-1.4\n% LexFlow test file\n"
FAKE_PDF_BYTES = b"hello, I am not really a pdf"


# ---------- helpers ----------

def unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@test.com"


def unique_phone() -> str:
    return "9" + str(uuid4().int)[:9]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register(client) -> tuple[str, str]:
    """Register a new firm + Owner. Returns (owner_token, law_firm_id)."""
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
    token = res.json()["access_token"]
    me = client.get("/auth/me", headers=auth(token))
    assert me.status_code == 200, me.text
    return token, me.json()["law_firm_id"]


def add_user(client, owner_token: str, role: str) -> str:
    """Owner creates a Lawyer/Staff user. Returns that user's token."""
    email = unique(role.lower())
    res = client.post(
        "/users/",
        json={"email": email, "password": PASSWORD, "role": role},
        headers=auth(owner_token),
    )
    assert res.status_code == 201, res.text
    login = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def add_lawyer(client, token: str, **extra) -> dict:
    res = client.post(
        "/lawyers/",
        json={"name": "Test Lawyer", "email": unique("lawyer-rec"), "phone": unique_phone(), **extra},
        headers=auth(token),
    )
    assert res.status_code == 201, res.text
    return res.json()


def add_client(client, token: str, **extra) -> dict:
    res = client.post(
        "/clients/",
        json={"name": "Test Client", "email": unique("client-rec"), "phone": unique_phone(), **extra},
        headers=auth(token),
    )
    assert res.status_code == 201, res.text
    return res.json()


def add_case(client, token: str, client_id: str, lawyer_id: str):
    return client.post(
        "/cases/",
        json={
            "title": "Test Case",
            "description": "Permission test",
            "client_id": client_id,
            "lawyer_id": lawyer_id,
        },
        headers=auth(token),
    )


def upload(client, token: str, case_id: str, content: bytes = PDF_BYTES, name: str = "test.pdf"):
    return client.post(
        f"/cases/{case_id}/documents",
        files={"file": (name, content, "application/pdf")},
        headers=auth(token),
    )


# ---------- shared setup: two firms with users, a lawyer, a client and a case ----------

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def world(client):
    owner_x, firm_x = register(client)
    owner_y, firm_y = register(client)

    lawyer_user_x = add_user(client, owner_x, "Lawyer")
    staff_user_x = add_user(client, owner_x, "Staff")

    lawyer_x = add_lawyer(client, owner_x)
    client_x = add_client(client, owner_x)
    lawyer_y = add_lawyer(client, owner_y)
    client_y = add_client(client, owner_y)

    case_res = add_case(client, owner_x, client_x["id"], lawyer_x["id"])
    assert case_res.status_code == 201, case_res.text

    return {
        "owner_x": owner_x, "firm_x": firm_x,
        "owner_y": owner_y, "firm_y": firm_y,
        "lawyer_user_x": lawyer_user_x, "staff_user_x": staff_user_x,
        "lawyer_x": lawyer_x, "client_x": client_x,
        "lawyer_y": lawyer_y, "client_y": client_y,
        "case_x": case_res.json(),
    }


# ---------- firm comes from the token, not the body ----------

def test_p1_lawyer_body_firm_ignored(client, world):
    lawyer = add_lawyer(client, world["owner_x"], law_firm_id=world["firm_y"])
    assert lawyer["law_firm_id"] == world["firm_x"]


def test_p2_client_body_firm_ignored(client, world):
    record = add_client(client, world["owner_x"], law_firm_id=world["firm_y"])
    assert record["law_firm_id"] == world["firm_x"]


def test_p3_case_with_other_firms_lawyer(client, world):
    res = add_case(client, world["owner_x"], world["client_x"]["id"], world["lawyer_y"]["id"])
    assert res.status_code == 404


def test_p4_case_with_other_firms_client(client, world):
    res = add_case(client, world["owner_x"], world["client_y"]["id"], world["lawyer_x"]["id"])
    assert res.status_code == 404


# ---------- roles ----------

def test_p5_staff_cannot_create_lawyer(client, world):
    res = client.post(
        "/lawyers/",
        json={"name": "X", "email": unique("l"), "phone": unique_phone()},
        headers=auth(world["staff_user_x"]),
    )
    assert res.status_code == 403


def test_p6_lawyer_cannot_create_lawyer(client, world):
    res = client.post(
        "/lawyers/",
        json={"name": "X", "email": unique("l"), "phone": unique_phone()},
        headers=auth(world["lawyer_user_x"]),
    )
    assert res.status_code == 403


def test_p7_lawyer_can_create_client(client, world):
    record = add_client(client, world["lawyer_user_x"])
    assert record["law_firm_id"] == world["firm_x"]


def test_p8_lawyer_cannot_delete_client(client, world):
    res = client.delete(f"/clients/{world['client_x']['id']}", headers=auth(world["lawyer_user_x"]))
    assert res.status_code == 403


def test_p9_staff_cannot_create_case(client, world):
    res = add_case(client, world["staff_user_x"], world["client_x"]["id"], world["lawyer_x"]["id"])
    assert res.status_code == 403


def test_p10_staff_cannot_change_case(client, world):
    res = client.patch(
        f"/cases/{world['case_x']['id']}",
        json={"title": "Changed by staff"},
        headers=auth(world["staff_user_x"]),
    )
    assert res.status_code == 403


def test_missing_lawyer_is_404_not_500(client, world):
    res = client.get(f"/lawyers/{uuid4()}", headers=auth(world["owner_x"]))
    assert res.status_code == 404


# ---------- list routes ----------

def test_p11_case_list_is_firm_scoped(client, world):
    case_id = world["case_x"]["id"]
    ids_x = [c["id"] for c in client.get("/cases/", headers=auth(world["owner_x"])).json()]
    ids_y = [c["id"] for c in client.get("/cases/", headers=auth(world["owner_y"])).json()]
    assert case_id in ids_x
    assert case_id not in ids_y


def test_p12_case_status_filter(client, world):
    other_status = next(s for s in CaseStatus if s != CaseStatus.OPEN)

    open_ids = [c["id"] for c in client.get(
        "/cases/", params={"status": CaseStatus.OPEN.value}, headers=auth(world["owner_x"])
    ).json()]
    other_ids = [c["id"] for c in client.get(
        "/cases/", params={"status": other_status.value}, headers=auth(world["owner_x"])
    ).json()]

    assert world["case_x"]["id"] in open_ids
    assert world["case_x"]["id"] not in other_ids


def test_p13_case_list_limit(client, world):
    add_case(client, world["owner_x"], world["client_x"]["id"], world["lawyer_x"]["id"])
    res = client.get("/cases/", params={"limit": 1}, headers=auth(world["owner_x"]))
    assert res.status_code == 200
    assert len(res.json()) <= 1
    assert client.get("/cases/", params={"limit": 500}, headers=auth(world["owner_x"])).status_code == 422


def test_p14_lawyer_and_client_lists_are_firm_scoped(client, world):
    lawyers_y = client.get("/lawyers/", headers=auth(world["owner_y"])).json()
    clients_y = client.get("/clients/", headers=auth(world["owner_y"])).json()
    assert all(l["law_firm_id"] == world["firm_y"] for l in lawyers_y)
    assert all(c["law_firm_id"] == world["firm_y"] for c in clients_y)
    assert world["lawyer_x"]["id"] not in [l["id"] for l in lawyers_y]
    assert world["client_x"]["id"] not in [c["id"] for c in clients_y]


def test_p15_lawyer_cannot_list_users(client, world):
    assert client.get("/users/", headers=auth(world["lawyer_user_x"])).status_code == 403


def test_p16_owner_lists_own_users_without_password(client, world):
    res = client.get("/users/", headers=auth(world["owner_x"]))
    assert res.status_code == 200
    users = res.json()
    assert len(users) >= 3  # owner + lawyer user + staff user
    assert all(u["law_firm_id"] == world["firm_x"] for u in users)
    assert all("hashed_password" not in u for u in users)


# ---------- PATCH /law-firms ----------

def test_p17_owner_updates_only_phone(client, world):
    before = client.get(f"/law-firms/{world['firm_x']}", headers=auth(world["owner_x"])).json()
    new_phone = unique_phone()
    res = client.patch(
        f"/law-firms/{world['firm_x']}",
        json={"phone": new_phone},
        headers=auth(world["owner_x"]),
    )
    assert res.status_code == 200
    after = res.json()
    assert after["phone"] == new_phone
    assert after["name"] == before["name"]
    assert after["email"] == before["email"]
    assert after["address"] == before["address"]


def test_p18_owner_cannot_update_other_firm(client, world):
    res = client.patch(
        f"/law-firms/{world['firm_y']}",
        json={"phone": unique_phone()},
        headers=auth(world["owner_x"]),
    )
    assert res.status_code == 404


def test_p19_lawyer_cannot_update_firm(client, world):
    res = client.patch(
        f"/law-firms/{world['firm_x']}",
        json={"phone": unique_phone()},
        headers=auth(world["lawyer_user_x"]),
    )
    assert res.status_code == 403


def test_p20_lawyers_path_is_lowercase(client, world):
    assert client.get("/lawyers/", headers=auth(world["owner_x"])).status_code == 200
    assert client.get("/Lawyers/", headers=auth(world["owner_x"])).status_code == 404


# ---------- documents ----------

def test_d1_real_pdf_upload_then_delete(client, world):
    res = upload(client, world["owner_x"], world["case_x"]["id"])
    assert res.status_code == 201, res.text
    doc_id = res.json()["id"]

    download = client.get(f"/documents/{doc_id}/download", headers=auth(world["owner_x"]))
    assert download.status_code == 200
    assert download.content == PDF_BYTES

    assert client.delete(f"/documents/{doc_id}", headers=auth(world["owner_x"])).status_code == 204
    assert client.get(f"/documents/{doc_id}", headers=auth(world["owner_x"])).status_code == 404


def test_d2_fake_pdf_rejected(client, world):
    res = upload(client, world["owner_x"], world["case_x"]["id"], content=FAKE_PDF_BYTES, name="fake.pdf")
    assert res.status_code == 415


def test_d3_staff_can_upload_but_not_delete(client, world):
    res = upload(client, world["staff_user_x"], world["case_x"]["id"])
    assert res.status_code == 201, res.text
    doc_id = res.json()["id"]

    assert client.delete(f"/documents/{doc_id}", headers=auth(world["staff_user_x"])).status_code == 403

    # clean up as Owner
    assert client.delete(f"/documents/{doc_id}", headers=auth(world["owner_x"])).status_code == 204


def test_d4_other_firm_cannot_touch_document(client, world):
    res = upload(client, world["owner_x"], world["case_x"]["id"])
    assert res.status_code == 201, res.text
    doc_id = res.json()["id"]

    headers_y = auth(world["owner_y"])
    assert client.get(f"/documents/{doc_id}", headers=headers_y).status_code == 404
    assert client.get(f"/documents/{doc_id}/download", headers=headers_y).status_code == 404
    assert client.delete(f"/documents/{doc_id}", headers=headers_y).status_code == 404

    # clean up as Owner of firm X
    assert client.delete(f"/documents/{doc_id}", headers=auth(world["owner_x"])).status_code == 204