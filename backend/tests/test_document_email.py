"""Tests for POST /documents/{id}/email ("Email" button on a document).

No real emails are sent: a fake send_message catches each email so the tests can
look at it. conftest.py also empties the Gmail login, so nothing can leak out.
"""
import smtplib
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.document_email import DocumentEmail
from app.services import email as email_service

PASSWORD = "testpass123"
PDF_BYTES = b"%PDF-1.4\n% LexFlow email test file\n"


# ---------- helpers ----------

def unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@test.com"


def unique_phone() -> str:
    return "9" + str(uuid4().int)[:9]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login(client, email: str) -> str:
    res = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def register(client, firm_name: str) -> tuple[str, str]:
    """New firm + Owner. Returns (owner_token, owner_email)."""
    owner_email = unique("owner")
    res = client.post(
        "/auth/register",
        json={
            "firm_name": firm_name,
            "firm_email": unique("firm"),
            "firm_phone": unique_phone(),
            "firm_address": "1 Test Street",
            "owner_email": owner_email,
            "password": PASSWORD,
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["access_token"], owner_email


def lawyer_with_login(client, owner: str, name: str) -> tuple[dict, str]:
    """Lawyer profile + its login. Returns (lawyer, lawyer_token)."""
    res = client.post(
        "/lawyers/",
        json={"name": name, "email": unique("lawyer"), "phone": unique_phone()},
        headers=auth(owner),
    )
    assert res.status_code == 201, res.text
    lawyer = res.json()
    res = client.post(
        f"/lawyers/{lawyer['id']}/create-login", json={"password": PASSWORD}, headers=auth(owner)
    )
    assert res.status_code == 201, res.text
    return lawyer, login(client, lawyer["email"])


def send(client, token: str, doc_id: str, to: str = "client@example.com", message: str = ""):
    return client.post(
        f"/documents/{doc_id}/email", json={"to": to, "message": message}, headers=auth(token)
    )


def log_rows(doc_id: str) -> list[DocumentEmail]:
    """Sent-log rows for one document, read straight from the database."""
    with SessionLocal() as db:
        return list(db.scalars(select(DocumentEmail).where(DocumentEmail.document_id == UUID(doc_id))))


# ---------- setup ----------

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def firm(client):
    owner, owner_email = register(client, "Mehta & Rao Associates")
    lawyer_a, token_a = lawyer_with_login(client, owner, "Asha Rao")
    lawyer_b, token_b = lawyer_with_login(client, owner, "Ben Kumar")

    staff_email = unique("staff")
    res = client.post(
        "/users/", json={"email": staff_email, "password": PASSWORD, "role": "Staff"}, headers=auth(owner)
    )
    assert res.status_code == 201, res.text

    res = client.post(
        "/clients/",
        json={"name": "Client", "email": unique("client"), "phone": unique_phone()},
        headers=auth(owner),
    )
    client_id = res.json()["id"]
    case = client.post(
        "/cases/",
        json={"title": "Email case", "description": "Email test", "client_id": client_id, "lawyer_id": lawyer_a["id"]},
        headers=auth(owner),
    ).json()

    def upload(name: str) -> str:
        res = client.post(
            f"/cases/{case['id']}/documents",
            files={"file": (name, PDF_BYTES, "application/pdf")},
            headers=auth(owner),
        )
        assert res.status_code == 201, res.text
        return res.json()["id"]

    other_owner, _ = register(client, "Other Firm")

    return {
        "owner": owner, "owner_email": owner_email,
        "lawyer_a": lawyer_a, "token_a": token_a,
        "token_b": token_b,
        "staff": login(client, staff_email),
        "other_owner": other_owner,
        "upload": upload,
    }


@pytest.fixture
def outbox(monkeypatch):
    """Replace the real sender: every 'sent' email lands in this list instead."""
    sent = []
    monkeypatch.setattr(email_service, "send_message", sent.append)
    return sent


# ---------- who can send ----------

def test_lawyer_sends_email_as_themselves(client, firm, outbox):
    doc_id = firm["upload"]("agreement draft.pdf")

    res = send(client, firm["token_a"], doc_id, to="client@example.com", message="Please review.")
    assert res.status_code == 200, res.text
    assert res.json() == {"sent_to": "client@example.com", "filename": "agreement draft.pdf"}

    assert len(outbox) == 1
    msg = outbox[0]
    assert msg["To"] == "client@example.com"
    assert "Asha Rao (Mehta & Rao Associates) via LexFlow" in msg["From"]
    assert msg["Reply-To"] == firm["lawyer_a"]["email"]  # replies go to the lawyer, not LexFlow
    assert msg["Subject"] == 'Asha Rao shared "agreement draft.pdf" with you'
    assert "Please review." in msg.get_body().get_content()

    attachments = list(msg.iter_attachments())
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "agreement draft.pdf"
    assert attachments[0].get_content_type() == "application/pdf"
    assert attachments[0].get_content() == PDF_BYTES


def test_owner_without_lawyer_profile_sends_with_their_email(client, firm, outbox):
    doc_id = firm["upload"]("owner.pdf")
    assert send(client, firm["owner"], doc_id).status_code == 200
    assert f'{firm["owner_email"]} (Mehta & Rao Associates) via LexFlow' in outbox[0]["From"]
    assert outbox[0]["Reply-To"] == firm["owner_email"]


def test_staff_cannot_send(client, firm, outbox):
    doc_id = firm["upload"]("staff.pdf")
    assert send(client, firm["staff"], doc_id).status_code == 403
    assert outbox == []
    assert log_rows(doc_id) == []


def test_other_lawyer_cannot_send_this_case(client, firm, outbox):
    doc_id = firm["upload"]("not-yours.pdf")
    assert send(client, firm["token_b"], doc_id).status_code == 404  # B can't even see the case
    assert outbox == []


def test_other_firm_cannot_send(client, firm, outbox):
    doc_id = firm["upload"]("other-firm.pdf")
    assert send(client, firm["other_owner"], doc_id).status_code == 404
    assert outbox == []


def test_unknown_document_is_404(client, firm, outbox):
    assert send(client, firm["owner"], str(uuid4())).status_code == 404


def test_needs_login(client, firm, outbox):
    doc_id = firm["upload"]("no-login.pdf")
    res = client.post(f"/documents/{doc_id}/email", json={"to": "client@example.com"})
    assert res.status_code in (401, 403)
    assert outbox == []


# ---------- input checks ----------

def test_invalid_email_address_is_422(client, firm, outbox):
    doc_id = firm["upload"]("bad-address.pdf")
    assert send(client, firm["owner"], doc_id, to="not-an-email").status_code == 422
    assert outbox == []


def test_message_too_long_is_422(client, firm, outbox):
    doc_id = firm["upload"]("long-message.pdf")
    assert send(client, firm["owner"], doc_id, message="x" * 2001).status_code == 422


def test_file_too_large_is_413(client, firm, outbox, monkeypatch):
    doc_id = firm["upload"]("big.pdf")
    # Pretend the limit is tiny instead of uploading an 18 MB file.
    monkeypatch.setattr(email_service, "MAX_ATTACHMENT_BYTES", 10)
    res = send(client, firm["owner"], doc_id)
    assert res.status_code == 413
    assert "too large" in res.json()["detail"]
    assert outbox == []


# ---------- sent log ----------

def test_successful_send_is_logged(client, firm, outbox):
    doc_id = firm["upload"]("logged.pdf")
    assert send(client, firm["token_a"], doc_id, to="someone@example.com").status_code == 200

    rows = log_rows(doc_id)
    assert len(rows) == 1
    assert rows[0].to_email == "someone@example.com"
    assert rows[0].filename == "logged.pdf"


def test_failed_send_is_502_and_not_logged(client, firm, monkeypatch):
    def gmail_refuses(msg):
        raise smtplib.SMTPException("Gmail said no")

    monkeypatch.setattr(email_service, "send_message", gmail_refuses)
    doc_id = firm["upload"]("fails.pdf")
    res = send(client, firm["owner"], doc_id)
    assert res.status_code == 502
    assert log_rows(doc_id) == []  # the log never claims an email went out when it didn't


def test_email_not_configured_is_503(client, firm):
    # No outbox fixture: the real send_message runs, but conftest.py emptied the Gmail login.
    doc_id = firm["upload"]("no-smtp.pdf")
    res = send(client, firm["owner"], doc_id)
    assert res.status_code == 503
    assert log_rows(doc_id) == []
