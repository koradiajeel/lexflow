# LexFlow - Project Context for Claude Code

## What this is
LexFlow is a multi-tenant law-firm case and document management system. Each firm sees only its own
lawyers, clients, cases and documents. Roles: Owner, Lawyer, Staff.
Learning + portfolio project by a B.Tech AI & Data Science student: build it like a real product.

## How to work with me
- I'm learning: after each change, explain in simple words what each file does and why.
- Work one step at a time; don't jump ahead to later roadmap items unless asked.
- Commit directly to `main` (no branches) after each step and push (daily GitHub streak).
- Never commit: `backend/uploads/`, `venv/`, `node_modules/`, secret `.env` files, `LIVE.png`,
  or a stray `package-lock.json` in the repo root.
- End with exact manual test steps for me.

## Layout
- Git root: `D:\lexflow`
- Backend: `D:\lexflow\backend` (FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, Pydantic v2, python-jose, passlib bcrypt)
- Frontend: `D:\lexflow\frontend` (Vite + React, JavaScript, ESLint, plain CSS - no Tailwind)

## Windows rules (important)
- Application Control blocks `pip.exe` and compiled DLLs. Always use:
  `python -m pip`, `python -m alembic`, `python -m uvicorn app.main:app --reload`, `python -m pytest -v tests`
- DB driver is **pg8000** (`postgresql+pg8000://`). Do not switch to psycopg2 (its DLL is blocked).
- Activate venv first: `cd D:\lexflow\backend` then `.\venv\Scripts\Activate.ps1`.
- `requirements.txt`: use `python -m pip freeze | Out-File -Encoding utf8 requirements.txt` (not `>`, it writes UTF-16).
- npm works normally. Vite may run on 5174 if 5173 is busy.

## Backend API (complete, 43 passing tests)
| Area | Routes | Who |
|---|---|---|
| Auth | `POST /auth/register` (firm + Owner, returns token), `POST /auth/login` (JSON), `GET /auth/me` | public / any |
| Users | `GET /users/`, `POST /users/` (Lawyer/Staff only, firm from token) | Owner |
| Law firms | `GET/PATCH/DELETE /law-firms/{id}` | GET any; write Owner |
| Lawyers | `GET /lawyers/`, `POST /lawyers/`, `GET/PATCH/DELETE /lawyers/{id}` | GET any; write Owner |
| Clients | `GET /clients/`, `POST /clients/`, `GET/PATCH/DELETE /clients/{id}` | GET any; create/update Owner+Lawyer; delete Owner |
| Cases | `GET /cases/` (`status`, `client_id`, `lawyer_id`, `limit` 1-100, `offset`), `POST /cases/`, `GET/PATCH /cases/{id}` | GET any; write Owner+Lawyer |
| Documents | `POST/GET /cases/{id}/documents`, `GET /documents/{id}`, `GET /documents/{id}/download`, `DELETE /documents/{id}` | upload/download any; delete Owner+Lawyer |

Rules:
- JWT payload: `sub` (user UUID), `law_firm_id`, `role`. Roles `Owner` / `Lawyer` / `Staff` (case-sensitive).
- Firm isolation: every query limited to `current_user.law_firm_id`; other firm's record -> 404. A case's firm comes from its lawyer.
- `law_firm_id` is never accepted from the request body.
- Deleting a firm/lawyer/client with cases -> 409. Cases have no DELETE (closed via status).
- Upload: 20 MB max, pdf/png/jpeg/doc/docx, magic-byte check (`app/services/file_validation.py`),
  stored in `backend/uploads/cases/<case_id>/<uuid>` (git-ignored).
- Errors: `{"detail": "..."}`; 401 no/expired token, 403 wrong role, 404 not found/other firm, 409 conflict, 415 bad file type, 422 validation.
- Tests: `tests/test_auth_users.py`, `tests/test_permissions.py`. Must keep passing after any backend change.

## Frontend status
- `frontend/src/api/client.js`: `getToken`, `setToken`, `clearToken`, `apiFetch(path, options)`
  (Bearer token, JSON header unless FormData, clears token on 401, throws Error with `detail` + `status`, null on 204).
- `frontend/.env.development`: `VITE_API_URL=http://localhost:8000`
- Backend CORS allows `http://localhost:5173` and `http://localhost:5174`.
- `frontend/src/App.jsx`: simple `page` state switcher (login / register / home) - replace with react-router in step 3.
- `frontend/src/pages/`: `LoginPage`, `RegisterPage` (firm + Owner), `HomePage` (temporary: shows `/auth/me`, Sign out).
- `frontend/src/components/Logo.jsx`: shared logo.

## Design system (white + blue)
- All theme colors are CSS variables in `frontend/src/index.css`: `--blue`, `--blue-dark`, `--blue-soft`,
  `--blue-softer`, `--ink`, `--text`, `--muted`, `--border`, `--bg`, `--red`/`--red-soft`, `--green`/`--green-soft`,
  plus `--radius`, `--shadow-sm`, `--shadow-lg`. Use only these; no new hex colors in components.
- Font: Plus Jakarta Sans (Google Fonts, loaded in `frontend/index.html`). Light theme only.
- Reusable classes: `.btn` + `.btn-primary` / `.btn-outline`, `.card`, `.label`, `.input`, `.badge`,
  `.alert-error`, `.alert-success`, `.page-center`.
- Look: modern SaaS style - white background, one blue accent, soft blue tints, rounded corners,
  soft shadows, generous spacing. Must work at 375px phone width with no horizontal scroll.
- No fake marketing content (made-up customer counts, stats, testimonials).

## Frontend roadmap
1. ~~CORS connection test~~ + ~~white/blue theme~~ (done)
2. Login page and Register page (store token, redirect)  <- next
3. Routing (react-router) + protected routes + logout
4. Case list (dashboard): `GET /cases/` with status filter + pagination
5. Case detail: info, status change, documents (upload via FormData, download, delete)
6. Clients and Lawyers pages
7. Users page (Owner only)
8. Role-based UI (hide actions the role can't do)
Later: Docker, deployment, README with screenshots, S3 storage, monitoring.

## Known follow-ups
- Client email/phone are unique across the whole DB, not per firm (needs migration).
- Use a separate test database before deployment (tests write `@test.com` data into dev DB).
- Delete `backend/test_db.py` (old psycopg2 script) - still present.

## Test data
Test accounts and IDs live in `CLAUDE.local.md` (git-ignored, auto-loaded by Claude Code).
