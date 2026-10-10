# LexFlow: Work Report (2026-10-11)

Branch: `lock-user-creation` (pushed to `origin`, **not merged into `main` yet**, so these commits will not count toward the GitHub streak until merged).
Commit author email: `koradiajeel1856@gmail.com` (matches the expected address).

## Summary of each task

| Task | What changed | Why |
|---|---|---|
| 1. Remove `POST /law-firms/` | Deleted the create route from `law_firm.py` and removed the `LawFirmCreate` and `IntegrityError` imports it no longer needed. | Firms are now created only through `POST /auth/register`, so the open route let anyone create a firm without an Owner. |
| 2. `UserCreate` schema | Removed `law_firm_id`, limited the password to 8 to 72 characters, and added a validator that rejects the `Owner` role. | The firm comes from the Owner's token. bcrypt only uses the first 72 bytes of a password. Only one Owner per firm, created at register. |
| 3. `POST /users/` | Only an Owner can call it (`require_role("Owner")`). The firm comes from `current_user`, and the email is trimmed and lowercased with a 409 if it already exists. | Stops users being created in other firms and stops anyone creating users without logging in. No circular import was found. |
| Fix (found during work) | Moved `RegisterRequest` from an uncommitted edit in `schemas/document.py` into `schemas/auth.py`, and discarded the document.py edit (the diff had only that class and a duplicate import). | Commit `15d430d` imported `RegisterRequest` from `app.schemas.auth`, where it did not exist, so the app could not start. |
| 4. Verify earlier fixes | `requirements.txt` re-saved as UTF-8 with `psycopg2-binary` removed and `pg8000`, `email-validator`, `pytest`, `httpx` added. Added `upload/` to `.gitignore`. Everything else checked out. | git cannot diff UTF-16 files. psycopg2 is blocked on this machine. `EmailStr` needs email-validator. |
| 5. Tests | Added `backend/tests/test_auth_users.py`: 18 tests, every one creates its own firms and users with unique emails. | Automated checks for register, user creation and firm isolation. |
| 6. Commit and push | 6 commits, each pushed. | Small, logical commits. |

## Task 4 checks

| Check | Result |
|---|---|
| `database.py` uses `postgresql+pg8000://` | OK |
| `requirements.txt` has pg8000 and email-validator, no psycopg2 | Fixed (it was UTF-16, had psycopg2-binary, and lacked both) |
| `storage.py` (`UPLOAD_ROOT`, single `get_file_path`, `exists()` before `unlink()`) | OK |
| `document.py` DELETE (role check, firm scoping, commit before deleting the file) | OK |
| `.gitignore` | `upload/` added. `git check-ignore` confirms `backend/uploads` and `backend/.env` are ignored |
| Server start (`python -m uvicorn app.main:app`) | Starts without errors, `/docs` returns 200 |

## Commits (branch `lock-user-creation`)

1. `17cbb60` Remove open POST /law-firms/; firms are created via /auth/register
2. `8c06031` Lock create-user to Owner: firm from token, role Lawyer/Staff only
3. `842f5fc` Move RegisterRequest to schemas/auth.py (fixes import error from 15d430d)
4. `0512258` requirements.txt: save as UTF-8, drop psycopg2-binary, add pg8000, email-validator, pytest, httpx
5. `6d04964` Ignore upload/ alongside uploads/
6. `3e46468` Add pytest tests for register, user creation and firm isolation

## Files changed

- `.gitignore`
- `backend/app/api/routes/law_firm.py`
- `backend/app/api/routes/user.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/user.py`
- `backend/requirements.txt`
- `backend/tests/test_auth_users.py` (new)

## Test results

`python -m pytest -v tests/test_auth_users.py`: **18 passed** in 12 s.

| # | Case | Expected | Result |
|---|---|---|---|
| R1 | Valid register | 201 with `access_token` | PASS |
| R2 | `GET /auth/me` | 200, Owner, new firm | PASS |
| R3 | Same firm email | 409 | PASS |
| R4 | Same owner email | 409 | PASS |
| R5 | Password `"123"` | 422 | PASS |
| R6 | Owner email differs only by case or spaces | 409 | PASS |
| L1 | `POST /law-firms/` | 405 | PASS |
| L2 | Own firm | 200 | PASS |
| L3 | Other firm | 404 | PASS |
| U1 | Owner creates Lawyer | 201, Owner's firm | PASS |
| U2 | Duplicate email | 409 | PASS |
| U3 | `role: "Owner"` | 422 | PASS |
| U4 | Other firm's `law_firm_id` in the body | 201, still the Owner's firm | PASS |
| U5 | Password `"123"` | 422 | PASS |
| U6 | Lawyer token | 403 | PASS |
| U7 | No token | 401 | PASS (installed FastAPI returns **401**) |
| U8 | Lawyer login, then `/auth/me` | 200 | PASS |
| F1 | `GET /cases/` | n/a | SKIPPED (route does not exist) |
| F2 | Firm Y reads firm X's case and its documents | 404 for both | PASS |

## Didn't match expectations, or follow-ups

- **`GET /cases/` list route missing** (F1 skipped).
- Commit `15d430d` on `main` could not start the app (the `RegisterRequest` import error). This is fixed on the branch, but `main` stays broken until the branch is merged.
- `law_firm.py` has no PUT or PATCH route.
- In `RegisterRequest`, `max_length=225` and `226` look like typos for 255 (copied as they were).
- In `schemas/lawyer.py`, `class Config` sits outside `LawyerResponse` because of its indentation, so it has no effect.
- `app/api/routes/law_firm.py` still imports `Client`, which it never used (this was the case before these changes).
- Pytest warns that Starlette's test client wants `httpx2` instead of `httpx`. It doesn't affect the results.
- The tests leave test firms and users (`*@test.com`) in the dev database.

## Final `backend/requirements.txt`

```text
alembic==1.18.5
annotated-doc==0.0.4
annotated-types==0.8.0
anyio==4.14.2
bcrypt==5.0.0
cffi==2.1.1
click==8.4.2
colorama==0.4.6
cryptography==50.0.2
ecdsa==0.19.2
email-validator==2.3.0
fastapi==0.140.0
greenlet==3.5.3
h11==0.16.0
httpx==0.28.1
idna==3.18
Mako==1.3.12
MarkupSafe==3.0.3
passlib==1.7.4
pg8000==1.31.5
pyasn1==0.6.4
pycparser==3.0
pydantic-settings==2.14.2
pydantic==2.13.5
pydantic_core==2.46.5
pytest==9.1.1
python-dotenv==1.2.2
python-jose==3.5.0
rsa==4.9.1
six==1.17.0
SQLAlchemy==2.0.51
starlette==1.3.1
typing-inspection==0.4.4
typing_extensions==4.16.0
uvicorn==0.51.0
```

## Full code diff (`15d430d..3e46468`, excluding requirements.txt)

```diff
diff --git a/.gitignore b/.gitignore
index db6d36e..df59d96 100644
--- a/.gitignore
+++ b/.gitignore
@@ -6,4 +6,5 @@ backend/venv/
 *.db
 .pytest_cache/
 .vscode/
-uploads/
\ No newline at end of file
+uploads/
+upload/
diff --git a/backend/app/api/routes/law_firm.py b/backend/app/api/routes/law_firm.py
index 05ba597..148d52e 100644
--- a/backend/app/api/routes/law_firm.py
+++ b/backend/app/api/routes/law_firm.py
@@ -1,13 +1,12 @@
 from fastapi import APIRouter, Depends, status, HTTPException
 
 from sqlalchemy.orm import Session
-from sqlalchemy.exc import IntegrityError
 from sqlalchemy import select
 
 from app.models.law_firm import LawFirm
 from app.models.lawyer import Lawyer
 from app.core.database import get_db
-from app.schemas.law_firm import LawFirmCreate, LawFirmResponse
+from app.schemas.law_firm import LawFirmResponse
 from app.models.client import Client
 from app.models.case import Case
 from app.models.user import User
@@ -18,35 +17,6 @@ from uuid import UUID
 router = APIRouter()
 
 
-@router.post(
-    "/",
-    response_model=LawFirmResponse,
-    status_code=status.HTTP_201_CREATED,
-)
-def creat_law_firm(
-    data: LawFirmCreate,
-    db: Session = Depends(get_db),
-):
-    law_firm = LawFirm(
-        name=data.name,
-        email=data.email,
-        phone=data.phone,
-        address=data.address,
-    )
-    try:
-        db.add(law_firm)
-        db.commit()
-        db.refresh(law_firm)
-    except IntegrityError:
-        db.rollback()
-        raise HTTPException(
-            status_code=status.HTTP_409_CONFLICT,
-            detail="lawfarm with this email already exists",
-        )
-
-    return law_firm
-
-
 @router.get("/{law_firm_id}", response_model=LawFirmResponse)
 def get_law_firm(
     law_firm_id: UUID,
diff --git a/backend/app/api/routes/user.py b/backend/app/api/routes/user.py
index f664816..16fec1f 100644
--- a/backend/app/api/routes/user.py
+++ b/backend/app/api/routes/user.py
@@ -1,12 +1,12 @@
-from fastapi import APIRouter, status, Depends, HTTPException
-from sqlalchemy.orm import Session
+from fastapi import APIRouter, Depends, HTTPException, status
 from sqlalchemy import select
 from sqlalchemy.exc import IntegrityError
+from sqlalchemy.orm import Session
 
+from app.api.routes.auth import require_role
 from app.core.database import get_db
 from app.core.security import hash_password
 from app.models.user import User
-from app.models.law_firm import LawFirm
 from app.schemas.user import UserCreate, UserResponse
 
 router = APIRouter()
@@ -16,18 +16,24 @@ router = APIRouter()
 def create_user(
     data: UserCreate,
     db: Session = Depends(get_db),
+    current_user: User = Depends(require_role("Owner")),
 ):
-    law_firm = db.scalar(select(LawFirm).where(LawFirm.id == data.law_firm_id))
-    if law_firm is None:
-        raise HTTPException(status_code=404, detail="law firm not found")
+    email = data.email.strip().lower()
+
+    if db.scalar(select(User).where(User.email == email)):
+        raise HTTPException(
+            status_code=status.HTTP_409_CONFLICT,
+            detail="user with this email already exists",
+        )
 
     user = User(
-        law_firm_id=data.law_firm_id,
-        email=data.email,
+        law_firm_id=current_user.law_firm_id,
+        email=email,
         hashed_password=hash_password(data.password),
         role=data.role,
     )
     db.add(user)
+
     try:
         db.commit()
     except IntegrityError:
@@ -36,5 +42,6 @@ def create_user(
             status_code=status.HTTP_409_CONFLICT,
             detail="user with this email already exists",
         )
+
     db.refresh(user)
-    return user
\ No newline at end of file
+    return user
diff --git a/backend/app/schemas/auth.py b/backend/app/schemas/auth.py
index 35b1b55..0a6f8c1 100644
--- a/backend/app/schemas/auth.py
+++ b/backend/app/schemas/auth.py
@@ -1,4 +1,4 @@
-from pydantic import BaseModel
+from pydantic import BaseModel, Field
 
 
 class LoginRequest(BaseModel):
@@ -8,4 +8,16 @@ class LoginRequest(BaseModel):
 
 class TokenResponse(BaseModel):
     access_token: str
-    token_type: str = "bearer"
\ No newline at end of file
+    token_type: str = "bearer"
+
+
+class RegisterRequest(BaseModel):
+    # Law firm details
+    firm_name: str = Field(min_length=1, max_length=225)
+    firm_email: str = Field(min_length=3, max_length=226)
+    firm_phone: str = Field(min_length=5, max_length=20)
+    firm_address: str = Field(min_length=1, max_length=500)
+
+    # First user of the firm (becomes Owner)
+    owner_email: str = Field(min_length=3, max_length=255)
+    password: str = Field(min_length=8, max_length=72)
diff --git a/backend/app/schemas/user.py b/backend/app/schemas/user.py
index 66a70ab..7ed3fa9 100644
--- a/backend/app/schemas/user.py
+++ b/backend/app/schemas/user.py
@@ -1,17 +1,23 @@
 from datetime import datetime
 from uuid import UUID
 
-from pydantic import BaseModel, ConfigDict, EmailStr, Field
+from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
 
 from app.models.enums import UserRole
 
 
 class UserCreate(BaseModel):
-    law_firm_id: UUID
     email: EmailStr
-    password: str = Field(min_length=8)
+    password: str = Field(min_length=8, max_length=72)
     role: UserRole = UserRole.STAFF
 
+    @field_validator("role")
+    @classmethod
+    def role_cannot_be_owner(cls, value: UserRole) -> UserRole:
+        if value == UserRole.OWNER:
+            raise ValueError("Only Lawyer or Staff users can be created")
+        return value
+
 
 class UserResponse(BaseModel):
     id: UUID
diff --git a/backend/tests/test_auth_users.py b/backend/tests/test_auth_users.py
new file mode 100644
index 0000000..32579e7
--- /dev/null
+++ b/backend/tests/test_auth_users.py
@@ -0,0 +1,232 @@
+"""Tests for register, law firm access, user creation and firm isolation.
+
+These run against the dev database, so every test creates its own data
+with unique emails and never touches existing firms.
+"""
+from uuid import uuid4
+
+import pytest
+from fastapi.testclient import TestClient
+
+from app.main import app
+
+PASSWORD = "testpass123"
+
+
+@pytest.fixture(scope="module")
+def client():
+    with TestClient(app) as c:
+        yield c
+
+
+def unique(prefix: str) -> str:
+    return f"{prefix}-{uuid4().hex[:8]}@test.com"
+
+
+def unique_phone() -> str:
+    return "9" + str(uuid4().int)[:9]
+
+
+def auth(token: str) -> dict:
+    return {"Authorization": f"Bearer {token}"}
+
+
+def register_body(firm_email=None, owner_email=None, password=PASSWORD) -> dict:
+    return {
+        "firm_name": "Test Firm",
+        "firm_email": firm_email or unique("firm"),
+        "firm_phone": unique_phone(),
+        "firm_address": "1 Test Street",
+        "owner_email": owner_email or unique("owner"),
+        "password": password,
+    }
+
+
+def register(client) -> tuple[str, str]:
+    """Register a new firm + Owner and return (token, law_firm_id)."""
+    res = client.post("/auth/register", json=register_body())
+    assert res.status_code == 201, res.text
+    token = res.json()["access_token"]
+    me = client.get("/auth/me", headers=auth(token))
+    assert me.status_code == 200, me.text
+    return token, me.json()["law_firm_id"]
+
+
+# ---------- Register ----------
+
+def test_r1_register_valid(client):
+    res = client.post("/auth/register", json=register_body())
+    assert res.status_code == 201
+    assert "access_token" in res.json()
+
+
+def test_r2_me_is_owner_of_new_firm(client):
+    res = client.post("/auth/register", json=register_body())
+    token = res.json()["access_token"]
+    me = client.get("/auth/me", headers=auth(token))
+    assert me.status_code == 200
+    assert me.json()["role"] == "Owner"
+    assert me.json()["law_firm_id"]
+
+
+def test_r3_same_firm_email_conflict(client):
+    firm_email = unique("firm")
+    assert client.post("/auth/register", json=register_body(firm_email=firm_email)).status_code == 201
+    assert client.post("/auth/register", json=register_body(firm_email=firm_email)).status_code == 409
+
+
+def test_r4_same_owner_email_conflict(client):
+    owner_email = unique("owner")
+    assert client.post("/auth/register", json=register_body(owner_email=owner_email)).status_code == 201
+    assert client.post("/auth/register", json=register_body(owner_email=owner_email)).status_code == 409
+
+
+def test_r5_short_password(client):
+    assert client.post("/auth/register", json=register_body(password="123")).status_code == 422
+
+
+def test_r6_owner_email_case_and_whitespace(client):
+    email = unique("owner")
+    first = client.post("/auth/register", json=register_body(owner_email=f"  {email.upper()}"))
+    assert first.status_code == 201
+    second = client.post("/auth/register", json=register_body(owner_email=email))
+    assert second.status_code == 409
+
+
+# ---------- Law firms ----------
+
+def test_l1_post_law_firms_removed(client):
+    res = client.post("/law-firms/", json={"name": "x", "email": unique("firm"), "phone": "12345", "address": "x"})
+    assert res.status_code == 405
+
+
+def test_l2_owner_reads_own_firm(client):
+    token, firm_id = register(client)
+    assert client.get(f"/law-firms/{firm_id}", headers=auth(token)).status_code == 200
+
+
+def test_l3_owner_cannot_read_other_firm(client):
+    token_x, _ = register(client)
+    _, firm_y = register(client)
+    assert client.get(f"/law-firms/{firm_y}", headers=auth(token_x)).status_code == 404
+
+
+# ---------- Create user ----------
+
+@pytest.fixture(scope="module")
+def owner(client):
+    return register(client)
+
+
+@pytest.fixture(scope="module")
+def lawyer_user(client, owner):
+    token, _ = owner
+    email = unique("lawyer")
+    res = client.post("/users/", json={"email": email, "password": PASSWORD, "role": "Lawyer"}, headers=auth(token))
+    assert res.status_code == 201, res.text
+    return email, res.json()
+
+
+def test_u1_owner_creates_lawyer(owner, lawyer_user):
+    _, firm_id = owner
+    _, body = lawyer_user
+    assert body["role"] == "Lawyer"
+    assert body["law_firm_id"] == firm_id
+
+
+def test_u2_duplicate_email(client, owner, lawyer_user):
+    token, _ = owner
+    email, _ = lawyer_user
+    res = client.post("/users/", json={"email": email, "password": PASSWORD, "role": "Staff"}, headers=auth(token))
+    assert res.status_code == 409
+
+
+def test_u3_cannot_create_owner(client, owner):
+    token, _ = owner
+    res = client.post("/users/", json={"email": unique("user"), "password": PASSWORD, "role": "Owner"}, headers=auth(token))
+    assert res.status_code == 422
+
+
+def test_u4_body_law_firm_id_ignored(client, owner):
+    token, firm_id = owner
+    _, other_firm = register(client)
+    res = client.post(
+        "/users/",
+        json={"email": unique("user"), "password": PASSWORD, "role": "Staff", "law_firm_id": other_firm},
+        headers=auth(token),
+    )
+    assert res.status_code == 201
+    assert res.json()["law_firm_id"] == firm_id
+
+
+def test_u5_short_password(client, owner):
+    token, _ = owner
+    res = client.post("/users/", json={"email": unique("user"), "password": "123", "role": "Staff"}, headers=auth(token))
+    assert res.status_code == 422
+
+
+def _login(client, email: str) -> str:
+    res = client.post("/auth/login", json={"email": email, "password": PASSWORD})
+    assert res.status_code == 200, res.text
+    return res.json()["access_token"]
+
+
+def test_u6_lawyer_cannot_create_user(client, lawyer_user):
+    email, _ = lawyer_user
+    token = _login(client, email)
+    res = client.post("/users/", json={"email": unique("user"), "password": PASSWORD}, headers=auth(token))
+    assert res.status_code == 403
+
+
+def test_u7_no_token(client):
+    res = client.post("/users/", json={"email": unique("user"), "password": PASSWORD})
+    assert res.status_code == 401
+
+
+def test_u8_lawyer_login_and_me(client, lawyer_user):
+    email, body = lawyer_user
+    token = _login(client, email)
+    me = client.get("/auth/me", headers=auth(token))
+    assert me.status_code == 200
+    assert me.json()["role"] == "Lawyer"
+    assert me.json()["law_firm_id"] == body["law_firm_id"]
+
+
+# ---------- Firm isolation ----------
+# F1 skipped: there is no GET /cases/ list route yet.
+
+def test_f2_other_firm_cannot_see_case(client):
+    token_x, firm_x = register(client)
+    token_y, _ = register(client)
+
+    lawyer = client.post(
+        "/Lawyers/",
+        json={"name": "Test Lawyer", "email": unique("lawyer"), "phone": unique_phone(), "law_firm_id": firm_x},
+        headers=auth(token_x),
+    )
+    assert lawyer.status_code == 201, lawyer.text
+
+    test_client = client.post(
+        "/clients/",
+        json={"name": "Test Client", "email": unique("client"), "phone": unique_phone(), "law_firm_id": firm_x},
+        headers=auth(token_x),
+    )
+    assert test_client.status_code == 201, test_client.text
+
+    case = client.post(
+        "/cases/",
+        json={
+            "title": "Test Case",
+            "description": "Isolation test",
+            "client_id": test_client.json()["id"],
+            "lawyer_id": lawyer.json()["id"],
+        },
+        headers=auth(token_x),
+    )
+    assert case.status_code == 201, case.text
+    case_id = case.json()["id"]
+
+    # Firm X can see its own case, firm Y gets 404
+    assert client.get(f"/cases/{case_id}", headers=auth(token_x)).status_code == 200
+    assert client.get(f"/cases/{case_id}", headers=auth(token_y)).status_code == 404
+    assert client.get(f"/cases/{case_id}/documents", headers=auth(token_y)).status_code == 404
```
