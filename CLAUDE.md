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

## Backend API (54 passing tests)
| Area | Routes | Who |
|---|---|---|
| Auth | `POST /auth/register` (firm + Owner, returns token), `POST /auth/login` (JSON), `GET /auth/me` (incl. `lawyer_id`), `POST /auth/change-password` | public / any |
| Users | `GET /users/`, `POST /users/` (Lawyer/Staff only, firm from token) | Owner |
| Law firms | `GET/PATCH/DELETE /law-firms/{id}` | GET any; write Owner |
| Lawyers | `GET /lawyers/`, `POST /lawyers/`, `GET/PATCH/DELETE /lawyers/{id}`, `POST /lawyers/{id}/create-login` | GET any; write Owner |
| Clients | `GET /clients/`, `POST /clients/`, `GET/PATCH/DELETE /clients/{id}` | GET any; create/update Owner+Lawyer; delete Owner |
| Cases | `GET /cases/` (`status`, `client_id`, `lawyer_id`, `limit` 1-100, `offset`), `POST /cases/`, `GET/PATCH /cases/{id}` | GET any; write Owner+Lawyer |
| Documents | `POST/GET /cases/{id}/documents`, `GET /documents/{id}`, `GET /documents/{id}/download`, `DELETE /documents/{id}` | upload/download any; delete Owner+Lawyer |

Rules:
- JWT payload: `sub` (user UUID), `law_firm_id`, `role`. Roles `Owner` / `Lawyer` / `Staff` (case-sensitive).
- Firm isolation: every query limited to `current_user.law_firm_id`; other firm's record -> 404. A case's firm comes from its lawyer.
- `law_firm_id` is never accepted from the request body.
- Lawyer profile vs login: `lawyers` (name/email/phone, assigned to cases) and `users` (email/password/role, for login) are
  separate tables linked by optional `lawyers.user_id` (unique FK, ON DELETE SET NULL; migration `a7c3e91b4d20`).
  `POST /lawyers/{id}/create-login {password}` creates a Lawyer user with the lawyer's email and links it (409 if already
  linked or email taken). PATCH of a linked lawyer's email also updates the login email. `/auth/me` returns `lawyer_id`.
- Deleting a firm/lawyer/client with cases -> 409. Cases have no DELETE (closed via status).
- Upload: 20 MB max, pdf/png/jpeg/doc/docx, magic-byte check (`app/services/file_validation.py`),
  stored in `backend/uploads/cases/<case_id>/<uuid>` (git-ignored).
- Errors: `{"detail": "..."}`; 401 no/expired token, 403 wrong role, 404 not found/other firm, 409 conflict, 415 bad file type, 422 validation.
- Tests: `tests/test_auth_users.py`, `tests/test_permissions.py`, `tests/test_lawyer_login.py`. Must keep passing after any backend change.

## Frontend status
- `frontend/src/api/client.js`: `getToken`, `setToken`, `clearToken`, `apiFetch(path, options)`
  (Bearer token, JSON header unless FormData, clears token on 401, throws Error with `detail` + `status`, null on 204),
  plus `apiFetchBlob(path)` for file downloads (same auth + errors, returns a Blob).
- `frontend/.env.development`: `VITE_API_URL=http://localhost:8000`
- Backend CORS allows `http://localhost:5173` and `http://localhost:5174`.
- Routing: `react-router` v8 (import from `"react-router"`, not `react-router-dom`). `BrowserRouter` + `AuthProvider` wrap `<App />` in `main.jsx`.
- `frontend/src/App.jsx`: route map. `/login`, `/register` inside `PublicOnlyRoute` (logged in -> redirect to `state.from` or `/dashboard`);
  `/dashboard`, `/cases/:caseId`, `/clients`, `/lawyers`, `/account`, `/users` inside `ProtectedRoute` (not logged in -> `/login`) and `AppLayout` (top bar: logo, nav links Cases/Clients/Lawyers (+ Users for Owner only) via `NavLink`, email = link to /account ("Account" on phones), role badge, Sign out); `*` -> `/dashboard`.
- `frontend/src/auth/`: `AuthProvider.jsx` (`user` incl. `lawyer_id`, `loading`, `signedOut`, `signIn(token)`, `signOut()`; checks `/auth/me` on start;
  after a deliberate sign-out `ProtectedRoute` doesn't remember the last page, so the next user starts at /dashboard),
  `useAuth.js` hook, `authContext.js`, `ProtectedRoute.jsx`, `PublicOnlyRoute.jsx`. Add new logged-in pages as child routes of `AppLayout`.
- `frontend/src/pages/`: `LoginPage`, `RegisterPage` (firm + Owner), `DashboardPage` (case table: status filter tabs + Previous/Next,
  state in URL `?mine=1&status=&page=`; "All cases / My cases" toggle only when `user.lawyer_id` (adds `lawyer_id=` filter); asks `limit=PAGE_SIZE+1` to know if a next page exists; client/lawyer names from `/clients/` + `/lawyers/` `?limit=100`).
- `frontend/src/pages/CaseDetailPage.jsx`: case info + client/lawyer names, status change (PATCH, segmented buttons), renders `DocumentsPanel`.
  Case titles in the dashboard table link here.
- `frontend/src/components/`: `Logo.jsx`, `AppLayout.jsx`, `StatusBadge.jsx` (Open blue, In Progress amber, Closed gray),
  `DocumentsPanel.jsx` (list, upload via hidden file input + FormData field `file`, download via blob link, delete with confirm,
  eye button for PDF/PNG/JPEG -> `DocumentPreview.jsx` popup: iframe for PDF, img for images; Word = download only).
- `Modal.jsx`: shared popup (title bar, optional `actions`, ✕, Esc and backdrop click close; `wide` for previews). Use it for any new popup.
- `ClientsPage` / `LawyersPage` are thin configs for `PeopleManager.jsx` (paginated table, Add/Edit in a Modal with `PersonForm.jsx`,
  Delete with confirm; backend 409s shown as messages). `config.limits` mirrors the backend schema min/max lengths.
  Optional `config.extraColumn` adds a column: LawyersPage uses it for `CreateLoginButton.jsx` ("Has login" badge or Create login popup).
- `AccountPage.jsx` (/account): email, role, linked lawyer profile + "View my cases", change password form.
- `UsersPage.jsx` (/users, Owner only; others see a message and the page doesn't call the API): paginated logins with role badge,
  linked lawyer name (from `/lawyers/` `user_id`), "You" tag; "+ Add staff" popup -> `POST /users/` role Staff.
- `Pagination.jsx`: shared Previous / Page N / Next (hidden when only one page). Used by Dashboard, PeopleManager, Users.
- Pattern for loading data in effects: store `{ key, ...data }` in state and derive `loading = state.key !== currentKey`
  (avoids sync setState in effects, which the react-hooks lint rule flags); use an `ignore` flag against stale replies.

## Design system (white + blue)
- All theme colors are CSS variables in `frontend/src/index.css`: `--blue`, `--blue-dark`, `--blue-soft`,
  `--blue-softer`, `--ink`, `--text`, `--muted`, `--border`, `--bg`, `--red`/`--red-soft`, `--green`/`--green-soft`,
  plus `--radius`, `--shadow-sm`, `--shadow-lg`. Use only these; no new hex colors in components.
- Font: Plus Jakarta Sans (Google Fonts, loaded in `frontend/index.html`). Light theme only.
- Reusable classes: `.btn` + `.btn-primary` / `.btn-outline` / `.btn-danger` (+ `.btn-sm`), `.icon-button`, `.card`, `.label`, `.input`, `.badge`,
  `.alert-error`, `.alert-success`, `.page-center`.
- Look: modern SaaS style - white background, one blue accent, soft blue tints, rounded corners,
  soft shadows, generous spacing. Must work at 375px phone width with no horizontal scroll.
- No fake marketing content (made-up customer counts, stats, testimonials).

## Frontend roadmap
1. ~~CORS connection test~~ + ~~white/blue theme~~ (done)
2. ~~Login page and Register page (store token, redirect)~~ (done)
3. ~~Routing (react-router) + protected routes + logout~~ (done)
4. ~~Case list (dashboard): `GET /cases/` with status filter + pagination~~ (done)
5. ~~Case detail: info, status change, documents (upload via FormData, download, delete, in-page preview)~~ (done)
6. ~~Clients and Lawyers pages~~ (done)
7. ~~Users page (Owner only): list all logins, create **Staff** logins (lawyer logins are created from the Lawyers page)~~ (done)
8. Role-based UI (hide actions the role can't do)  <- next
Later: Docker, deployment, README with screenshots, S3 storage, monitoring.

## Known follow-ups
- Client email/phone are unique across the whole DB, not per firm (needs migration).
- Use a separate test database before deployment (tests write `@test.com` data into dev DB).
- Case list shows client/lawyer names only for the first 100 of each (fetched with `?limit=100`); a firm with more shows "—".
  Better fix later: include `client_name`/`lawyer_name` in `CaseResponse` on the backend.
- Staff can see status buttons, document Delete, and Add/Edit/Delete on clients and lawyers, but the backend returns 403
  (shown as an error). Lawyers can't write lawyers or delete clients either. Hide these in step 8.
- Lawyer-role users created earlier via `POST /users/` (e.g. Firm A's) aren't linked to a lawyer profile; create-login
  returns 409 for their email. Could add a "link existing account" option later.
- Deleting a lawyer keeps their login account (link becomes NULL). Decide later whether to also remove/disable the login.
- Delete `backend/test_db.py` (old psycopg2 script) - still present.

## Test data
Test accounts and IDs live in `CLAUDE.local.md` (git-ignored, auto-loaded by Claude Code).
