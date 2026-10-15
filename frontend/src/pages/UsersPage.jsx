import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { apiFetch } from "../api/client";
import { can } from "../auth/permissions";
import { useAuth } from "../auth/useAuth";
import Modal from "../components/Modal";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 10;

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

// Popup form: Owner creates a Staff login (POST /users/ with role "Staff").
function AddStaffForm({ onCreated, onCancel }) {
  const [form, setForm] = useState({ email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSaving(true);
    try {
      const user = await apiFetch("/users/", {
        method: "POST",
        body: JSON.stringify({
          email: form.email.trim(),
          password: form.password,
          role: "Staff",
        }),
      });
      onCreated(user);
    } catch (err) {
      setError(
        err.status === 422 ? "Check the email and use a password of 8 to 72 characters." : err.message,
      );
      setSaving(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <p className="modal-intro">
        Staff can view cases, clients and lawyers and upload documents, but can't change them.
        Share the temporary password privately; they can change it under My account.
      </p>
      <div>
        <label className="label" htmlFor="staff-email">
          Email
        </label>
        <input
          id="staff-email"
          name="email"
          className="input"
          type="email"
          required
          maxLength={255}
          value={form.email}
          onChange={handleChange}
          autoFocus
        />
      </div>
      <div>
        <label className="label" htmlFor="staff-password">
          Temporary password
        </label>
        <input
          id="staff-password"
          name="password"
          className="input"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          maxLength={72}
          value={form.password}
          onChange={handleChange}
        />
      </div>
      <div>
        <label className="label" htmlFor="staff-confirm">
          Confirm password
        </label>
        <input
          id="staff-confirm"
          name="confirm"
          className="input"
          type="password"
          autoComplete="new-password"
          required
          value={form.confirm}
          onChange={handleChange}
        />
      </div>
      <p className="hint">At least 8 characters.</p>

      {error && <p className="alert-error">{error}</p>}

      <div className="form-buttons">
        <button type="button" className="btn btn-outline" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Creating..." : "Create staff login"}
        </button>
      </div>
    </form>
  );
}

function UsersPage() {
  const { user: me } = useAuth();
  const isOwner = can(me, "user.manage");

  const [searchParams, setSearchParams] = useSearchParams();
  const page = Math.max(1, Number(searchParams.get("page")) || 1);
  const [reloadCount, setReloadCount] = useState(0);
  const requestKey = `${page}|${reloadCount}`;

  const [result, setResult] = useState({ key: null, users: [], hasNext: false, error: "" });
  const [lawyerNames, setLawyerNames] = useState({}); // login user_id -> lawyer profile name
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState("");

  // Which logins belong to which lawyer profile (lawyers carry user_id).
  useEffect(() => {
    if (!isOwner) return;
    apiFetch("/lawyers/?limit=100")
      .then((lawyers) =>
        setLawyerNames(
          Object.fromEntries(lawyers.filter((l) => l.user_id).map((l) => [l.user_id, l.name])),
        ),
      )
      .catch(() => {});
  }, [isOwner, reloadCount]);

  useEffect(() => {
    if (!isOwner) return; // GET /users/ is Owner-only; don't even ask
    let ignore = false;
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE + 1),
      offset: String((page - 1) * PAGE_SIZE),
    });
    apiFetch(`/users/?${params}`)
      .then((users) => {
        if (ignore) return;
        setResult({
          key: requestKey,
          users: users.slice(0, PAGE_SIZE),
          hasNext: users.length > PAGE_SIZE,
          error: "",
        });
      })
      .catch((err) => {
        if (!ignore) setResult({ key: requestKey, users: [], hasNext: false, error: err.message });
      });
    return () => {
      ignore = true;
    };
  }, [isOwner, page, requestKey]);

  const closeForm = useCallback(() => setAdding(false), []);

  if (!isOwner) {
    return (
      <div className="card">
        <h1 className="page-title">Users</h1>
        <p className="alert-error users-denied">Only the firm's Owner can manage user logins.</p>
      </div>
    );
  }

  const loading = result.key !== requestKey;

  function goToPage(newPage) {
    setSearchParams(newPage === 1 ? {} : { page: String(newPage) });
  }

  function handleCreated(user) {
    setAdding(false);
    setMessage(`Staff login created for ${user.email}.`);
    if (page !== 1) goToPage(1); // newest first, so it appears on page 1
    else setReloadCount((n) => n + 1);
  }

  return (
    <div className="card cases-card">
      <div className="cases-header">
        <div>
          <h1 className="page-title">Users</h1>
          <p className="subtitle">
            Everyone who can sign in to your firm. Lawyer logins are created from the{" "}
            <Link to="/lawyers" className="link-button">
              Lawyers
            </Link>{" "}
            page.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={() => {
            setMessage("");
            setAdding(true);
          }}
        >
          + Add staff
        </button>
      </div>

      {message && <p className="list-message alert-success">{message}</p>}

      {loading && <p className="cases-empty">Loading users...</p>}
      {!loading && result.error && <p className="alert-error">{result.error}</p>}

      {!loading && result.users.length > 0 && (
        <table className="cases-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Lawyer profile</th>
              <th>Added</th>
            </tr>
          </thead>
          <tbody>
            {result.users.map((u) => (
              <tr key={u.id}>
                <td data-label="Email">
                  <span className="case-title-plain">{u.email}</span>
                  {u.id === me.id && <span className="you-tag">You</span>}
                </td>
                <td data-label="Role">
                  <span className={`badge role-${u.role.toLowerCase()}`}>{u.role}</span>
                </td>
                <td data-label="Lawyer profile">
                  {u.role === "Lawyer" ? lawyerNames[u.id] || "Not linked" : "—"}
                </td>
                <td data-label="Added">{formatDate(u.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && <Pagination page={page} hasNext={result.hasNext} onChange={goToPage} />}

      {adding && (
        <Modal title="Add staff login" onClose={closeForm}>
          <AddStaffForm onCreated={handleCreated} onCancel={closeForm} />
        </Modal>
      )}
    </div>
  );
}

export default UsersPage;
