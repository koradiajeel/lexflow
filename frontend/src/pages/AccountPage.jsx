import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router";
import { apiFetch } from "../api/client";
import { can } from "../auth/permissions";
import { useAuth } from "../auth/useAuth";
import FirmCard from "../components/FirmCard";

function ChangePasswordForm() {
  const [form, setForm] = useState({ current: "", next: "", confirm: "" });
  const [message, setMessage] = useState({ type: "", text: "" });
  const [saving, setSaving] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage({ type: "", text: "" });
    if (form.next !== form.confirm) {
      setMessage({ type: "error", text: "New passwords do not match." });
      return;
    }
    setSaving(true);
    try {
      await apiFetch("/auth/change-password", {
        method: "POST",
        body: JSON.stringify({ current_password: form.current, new_password: form.next }),
      });
      setForm({ current: "", next: "", confirm: "" });
      setMessage({ type: "success", text: "Password changed." });
    } catch (err) {
      setMessage({
        type: "error",
        text: err.status === 422 ? "New password must be 8 to 72 characters." : err.message,
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="form account-form" onSubmit={handleSubmit}>
      <div>
        <label className="label" htmlFor="current">
          Current password
        </label>
        <input
          id="current"
          name="current"
          className="input"
          type="password"
          autoComplete="current-password"
          required
          value={form.current}
          onChange={handleChange}
        />
      </div>
      <div className="grid-2">
        <div>
          <label className="label" htmlFor="next">
            New password
          </label>
          <input
            id="next"
            name="next"
            className="input"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            maxLength={72}
            value={form.next}
            onChange={handleChange}
          />
        </div>
        <div>
          <label className="label" htmlFor="confirm">
            Confirm new password
          </label>
          <input
            id="confirm"
            name="confirm"
            className="input"
            type="password"
            autoComplete="new-password"
            required
            value={form.confirm}
            onChange={handleChange}
          />
        </div>
      </div>
      <p className="hint">At least 8 characters.</p>

      {message.text && (
        <p className={message.type === "error" ? "alert-error" : "alert-success"}>
          {message.text}
        </p>
      )}

      <div>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Saving..." : "Change password"}
        </button>
      </div>
    </form>
  );
}

function AccountPage() {
  const { hash } = useLocation();

  // /account#firm (from the Home "Firm settings" tile): scroll to that section.
  useEffect(() => {
    if (!hash) return;
    const timer = setTimeout(() => {
      document.querySelector(hash)?.scrollIntoView({ block: "start" });
    }, 300); // give the firm card a moment to load
    return () => clearTimeout(timer);
  }, [hash]);

  const { user } = useAuth();
  const lawyerId = user.lawyer_id;
  // The linked lawyer profile (name, phone), if this login belongs to a lawyer.
  const [profile, setProfile] = useState({ key: null, data: null });

  useEffect(() => {
    if (!lawyerId) return;
    let ignore = false;
    apiFetch(`/lawyers/${lawyerId}`)
      .then((data) => {
        if (!ignore) setProfile({ key: lawyerId, data });
      })
      .catch(() => {
        if (!ignore) setProfile({ key: lawyerId, data: null });
      });
    return () => {
      ignore = true;
    };
  }, [lawyerId]);

  const lawyer = profile.key === lawyerId ? profile.data : null;
  const hasFooter = Boolean(lawyerId) || user.role === "Lawyer"; // "View my cases" or the unlinked hint

  return (
    <div className="detail-stack">
      <section className="card">
        <h1 className="page-title">My account</h1>
        {/* Drop the bottom divider when nothing follows the details (Owner/Staff without a lawyer profile). */}
        <dl className={`detail-grid ${hasFooter ? "" : "detail-grid-last"}`}>
          <div>
            <dt>Email</dt>
            <dd>{user.email}</dd>
          </div>
          <div>
            <dt>Role</dt>
            <dd>
              <span className="badge">{user.role}</span>
            </dd>
          </div>
          {lawyerId && (
            <div>
              <dt>Lawyer profile</dt>
              <dd>{lawyer ? lawyer.name : "—"}</dd>
              {lawyer && <dd className="detail-sub">{lawyer.phone}</dd>}
            </div>
          )}
        </dl>
        {lawyerId && (
          <Link
            to={can(user, "case.viewAll") ? "/dashboard?mine=1" : "/dashboard"}
            className="btn btn-outline btn-sm"
          >
            View my cases
          </Link>
        )}
        {user.role === "Lawyer" && !lawyerId && (
          <p className="hint account-hint">
            This login isn't linked to a lawyer profile yet. Ask your firm's Owner to create
            your login from the Lawyers page.
          </p>
        )}
      </section>

      <FirmCard />

      <section className="card">
        <h2 className="section-title">Change password</h2>
        <p className="hint-inline">If the Owner gave you a temporary password, replace it here.</p>
        <ChangePasswordForm />
      </section>
    </div>
  );
}

export default AccountPage;
