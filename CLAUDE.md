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

## Backend API (65 passing tests)
| Area | Routes | Who |
|---|---|---|
| Auth | `POST /auth/register` (firm + Owner, returns token), `POST /auth/login` (JSON), `GET /auth/me` (incl. `lawyer_id`), `POST /auth/change-password` | public / any |
| Users | `GET /users/`, `POST /users/` (Lawyer/Staff only, firm from token) | Owner |
| Law firms | `GET/PATCH/DELETE /law-firms/{id}` | GET any; write Owner |
| Lawyers | `GET /lawyers/`, `POST /lawyers/`, `GET/PATCH/DELETE /lawyers/{id}`, `POST /lawyers/{id}/create-login` | GET any; write Owner |
| Clients | `GET /clients/`, `POST /clients/`, `GET/PATCH/DELETE /clients/{id}` | GET any; create/update Owner+Lawyer; delete Owner |
| Cases | `GET /cases/` (`status`, `client_id`, `lawyer_id`, `limit` 1-100, `offset`), `POST /cases/`, `GET/PATCH /cases/{id}` | GET any (Lawyer: own cases only); write Owner+Lawyer |
| Documents | `POST/GET /cases/{id}/documents`, `GET /documents/{id}`, `GET /documents/{id}/download`, `DELETE /documents/{id}` | upload/download any; delete Owner+Lawyer |

Rules:
- JWT payload: `sub` (user UUID), `law_firm_id`, `role`. Roles `Owner` / `Lawyer` / `Staff` (case-sensitive).
- Firm isolation: every query limited to `current_user.law_firm_id`; other firm's record -> 404. A case's firm comes from its lawyer.
- Case visibility (`app/services/case_access.py`, used by case AND document routes): Owner/Staff see every case in the firm;
  a **Lawyer sees only cases assigned to their own lawyer profile** (`lawyers.user_id == user.id`); other cases and their
  documents -> 404. Unlinked Lawyer logins see no cases. A Lawyer may only create cases assigned to themselves (else 403).
- `law_firm_id` is never accepted from the request body.
- Lawyer profile vs login: `lawyers` (name/email/phone, assigned to cases) and `users` (email/password/role, for login) are
  separate tables linked by optional `lawyers.user_id` (unique FK, ON DELETE SET NULL; migration `a7c3e91b4d20`).
  `POST /lawyers/{id}/create-login {password}` creates a Lawyer user with the lawyer's email and links it (409 if already
  linked or email taken). PATCH of a linked lawyer's email also updates the login email. `/auth/me` returns `lawyer_id`.
- Deleting a firm/lawyer/client with cases -> 409. Cases have no DELETE (closed via status).
- Upload: 20 MB max, pdf/png/jpeg/doc/docx, magic-byte check (`app/services/file_validation.py`),
  stored in `backend/uploads/cases/<case_id>/<uuid>` (git-ignored).
- Errors: `{"detail": "..."}`; 401 no/expired token, 403 wrong role, 404 not found/other firm, 409 conflict, 415 bad file type, 422 validation.
- Tests: `tests/test_auth_users.py`, `tests/test_permissions.py`, `tests/test_lawyer_login.py`, `tests/test_case_visibility.py`. Must keep passing after any backend change.

## Frontend status
- `frontend/src/api/client.js`: `getToken`, `setToken`, `clearToken`, `apiFetch(path, options)`
  (Bearer token, JSON header unless FormData, clears token on 401, throws Error with `detail` + `status`, null on 204),
  plus `apiFetchBlob(path)` for file downloads (same auth + errors, returns a Blob).
  A 401 on a request that carried a token calls the handler set via `setUnauthorizedHandler()`; AuthProvider uses it to
  sign the user out with `sessionExpired = true` -> ProtectedRoute sends them to /login (remembering the page) and
  LoginPage shows "Your session expired". A 401 without a token (wrong password) doesn't trigger it.
- `frontend/.env.development`: `VITE_API_URL=http://localhost:8000`
- Backend CORS allows `http://localhost:5173` and `http://localhost:5174`.
- Routing: `react-router` v8 (import from `"react-router"`, not `react-router-dom`). `BrowserRouter` + `AuthProvider` wrap `<App />` in `main.jsx`.
- `frontend/src/App.jsx`: route map. `/login`, `/register` inside `PublicOnlyRoute` (logged in -> redirect to `state.from` or `/home`);
  `/home`, `/dashboard`, `/cases/:caseId`, `/clients`, `/lawyers`, `/account`, `/users` inside `ProtectedRoute` (not logged in -> `/login`) and `AppLayout` (top bar: logo -> /home, nav links Home/Cases/Clients/Lawyers (+ Users for Owner only) via `NavLink`, email = link to /account ("Account" on phones), role badge (hidden on phones), Sign out); `*` -> `/home`.
- `frontend/src/auth/`: `AuthProvider.jsx` (`user` incl. `lawyer_id`, `loading`, `signedOut`, `signIn(token)`, `signOut()`; checks `/auth/me` on start;
  after a deliberate sign-out `ProtectedRoute` doesn't remember the last page, so the next user starts at /dashboard),
  `useAuth.js` hook, `authContext.js`, `ProtectedRoute.jsx`, `PublicOnlyRoute.jsx`. Add new logged-in pages as child routes of `AppLayout`.
- `frontend/src/pages/`: `LoginPage`, `RegisterPage` (firm + Owner), `DashboardPage` (case table: status filter tabs + Previous/Next,
  state in URL `?mine=1&status=&page=`; "All cases / My cases" toggle only for roles with `case.viewAll` that also have a `lawyer_id` (Lawyers get only their own cases from the API, so no toggle); asks `limit=PAGE_SIZE+1` to know if a next page exists; client/lawyer names from `/clients/` + `/lawyers/` `?limit=100`).
- `frontend/src/pages/CaseDetailPage.jsx`: case info + client/lawyer names, status change (PATCH, segmented buttons), renders `DocumentsPanel`.
  Case titles in the dashboard table link here.
- `frontend/src/components/`: `Logo.jsx`, `AppLayout.jsx`, `StatusBadge.jsx` (Open blue, In Progress amber, Closed gray),
  `DocumentsPanel.jsx` (list, upload via hidden file input + FormData field `file`, download via blob link, delete with confirm,
  eye button for PDF/PNG/JPEG -> `DocumentPreview.jsx` popup: iframe for PDF, img for images; Word = download only).
- `Modal.jsx`: shared popup (title bar, optional `actions`, ✕, Esc and backdrop click close; `wide` for previews). Use it for any new popup.
- `ClientsPage` / `LawyersPage` are thin configs for `PeopleManager.jsx` (paginated table, Add/Edit in a Modal with `PersonForm.jsx`,
  Delete with confirm; backend 409s shown as messages). `config.limits` mirrors the backend schema min/max lengths.
  Optional `config.extraColumn` adds a column: LawyersPage uses it for `CreateLoginButton.jsx` ("Has login" badge or Create login popup).
- `HomePage.jsx` (/home, landing page after login): welcome strip (avatar letter, email, role, firm name), "Search sections"
  filter, and a grid of section tiles (`MODULES` list; each tile's `show(user)` uses `permissions.js`, so roles only see
  sections they can use). Icons in `components/ModuleIcon.jsx`. Tiles link to pages; "New case" -> `/dashboard?new=1`
  (Dashboard opens the New case popup and drops `new` on close); "Firm settings" -> `/account#firm` (AccountPage scrolls there).
- `AccountPage.jsx` (/account): email, role, linked lawyer profile + "View my cases", `FirmCard.jsx` ("Your firm": everyone
  sees name/email/phone/address from `GET /law-firms/{law_firm_id}`; Owner gets Edit -> PATCH), change password form.
- `CaseDetailPage` has "Edit details" (permission `case.update`) -> `EditCaseForm.jsx` popup (title + description, PATCH).
- `UsersPage.jsx` (/users, Owner only; others see a message and the page doesn't call the API): paginated logins with role badge,
  linked lawyer name (from `/lawyers/` `user_id`), "You" tag; "+ Add staff" popup -> `POST /users/` role Staff.
- `Pagination.jsx`: shared Previous / Page N / Next (hidden when only one page). Used by Dashboard, PeopleManager, Users.
- `NewCaseForm.jsx`: opened from the dashboard's "+ New case" (permission `case.create`) in a Modal; title, description
  (textarea + counter), client and lawyer dropdowns (lists from the dashboard's `?limit=100` fetch; signed-in lawyer
  pre-selected; for a Lawyer (`onlySelf`, no `case.assignAnyLawyer`) the lawyer select is fixed to themselves);
  explains if no clients/lawyers exist; on success navigates to `/cases/<new id>`.
- Role-based UI: `frontend/src/auth/permissions.js` has `can(user, "action")` with one RULES table mirroring the backend
  `require_role` checks (`case.viewAll`, `case.create`, `case.assignAnyLawyer`, `case.update`, `document.delete`, `client.create/update/delete`, `lawyer.create/update/delete/createLogin`,
  `firm.update`, `user.manage`). Pages hide buttons the role can't use; PeopleManager takes `config.permissions` and `extraColumn.permission`.
  When a backend permission changes, update RULES too. The backend still enforces everything (403).
- Pattern for loading data in effects: store `{ key, ...data }` in state and derive `loading = state.key !== currentKey`
  (avoids sync setState in effects, which the react-hooks lint rule flags); use an `ignore` flag against stale replies.

## Design system (white + blue)
- All theme colors are CSS variables in `frontend/src/index.css`: `--blue`, `--blue-dark`, `--blue-soft`,
  `--blue-softer`, `--ink`, `--text`, `--muted`, `--border`, `--bg`, `--red`/`--red-soft`, `--green`/`--green-soft`,
  plus `--radius`, `--shadow-sm`, `--shadow-lg`. Use only these; no new hex colors in components.
- Font: Plus Jakarta Sans (Google Fonts, loaded in `frontend/index.html`). Light theme only.
- Reusable classes: `.btn` + `.btn-primary` / `.btn-outline` / `.btn-danger` (+ `.btn-sm`), `.icon-button`, `.card`, `.label`, `.input`, `.badge`,
  `.alert-error`, `.alert-success`, `.alert-info`, `.page-center`, `.textarea`.
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
8. ~~Role-based UI (hide actions the role can't do)~~ (done)
9. ~~New case form (`+ New case` on the dashboard, Owner + Lawyer)~~ (done)
10. ~~Polish: expired-session handling, edit case details, firm settings~~ (done)
Next (not started, pick one): README with screenshots | Docker | deployment (needs production `VITE_API_URL` + CORS origin).
Later: S3 storage, monitoring.

## Known follow-ups
- Client email/phone are unique across the whole DB, not per firm (needs migration).
- Use a separate test database before deployment (tests write `@test.com` data into dev DB).
- Case list shows client/lawyer names only for the first 100 of each (fetched with `?limit=100`); a firm with more shows "—".
  Better fix later: include `client_name`/`lawyer_name` in `CaseResponse` on the backend.
- Lawyer-role users created earlier via `POST /users/` (e.g. Firm A's) aren't linked to a lawyer profile; create-login
  returns 409 for their email. Could add a "link existing account" option later.
- Deleting a lawyer keeps their login account (link becomes NULL). Decide later whether to also remove/disable the login.
- New case dropdowns only list the first 100 clients/lawyers (same `?limit=100` fetch as the table names).
- Delete `backend/test_db.py` (old psycopg2 script) - still present.

## Test data
Test accounts and IDs live in `CLAUDE.local.md` (git-ignored, auto-loaded by Claude Code).
