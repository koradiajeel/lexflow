import { useCallback, useState } from "react";
import { apiFetch } from "../api/client";
import Modal from "./Modal";

// Shows "Has login" for lawyers with an account, or a "Create login" button that
// lets the Owner set a temporary password (POST /lawyers/{id}/create-login).
function CreateLoginButton({ lawyer, onCreated }) {
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const close = useCallback(() => {
    setOpen(false);
    setPassword("");
    setConfirm("");
    setError("");
  }, []);

  if (lawyer.user_id) {
    return <span className="badge badge-success">Has login</span>;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSaving(true);
    try {
      await apiFetch(`/lawyers/${lawyer.id}/create-login`, {
        method: "POST",
        body: JSON.stringify({ password }),
      });
      close();
      onCreated(lawyer);
    } catch (err) {
      setError(err.status === 422 ? "Password must be 8 to 72 characters." : err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <button type="button" className="btn btn-outline btn-sm" onClick={() => setOpen(true)}>
        Create login
      </button>

      {open && (
        <Modal title={`Create login for ${lawyer.name}`} onClose={close}>
          <form className="form" onSubmit={handleSubmit}>
            <p className="modal-intro">
              {lawyer.name} will sign in with <strong>{lawyer.email}</strong> and this
              temporary password. Share it with them privately; they can change it under
              My account.
            </p>
            <div>
              <label className="label" htmlFor="login-password">
                Temporary password
              </label>
              <input
                id="login-password"
                className="input"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                maxLength={72}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoFocus
              />
            </div>
            <div>
              <label className="label" htmlFor="login-confirm">
                Confirm password
              </label>
              <input
                id="login-confirm"
                className="input"
                type="password"
                autoComplete="new-password"
                required
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </div>
            <p className="hint">At least 8 characters.</p>

            {error && <p className="alert-error">{error}</p>}

            <div className="form-buttons">
              <button type="button" className="btn btn-outline" onClick={close}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Creating..." : "Create login"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}

export default CreateLoginButton;
