import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { can } from "../auth/permissions";
import { useAuth } from "../auth/useAuth";
import Modal from "./Modal";

// Edit form for the firm (PATCH /law-firms/{id}). Length rules match backend/app/schemas/law_firm.py.
function FirmForm({ firm, onSaved, onCancel }) {
  const [form, setForm] = useState({
    name: firm.name,
    email: firm.email,
    phone: firm.phone,
    address: firm.address,
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      const updated = await apiFetch(`/law-firms/${firm.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name: form.name.trim(),
          email: form.email.trim(),
          phone: form.phone.trim(),
          address: form.address.trim(),
        }),
      });
      onSaved(updated);
    } catch (err) {
      setError(err.status === 422 ? "Some fields are invalid. Please check them." : err.message);
      setSaving(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div>
        <label className="label" htmlFor="firm-name">
          Firm name
        </label>
        <input
          id="firm-name"
          name="name"
          className="input"
          required
          minLength={2}
          maxLength={225}
          value={form.name}
          onChange={handleChange}
          autoFocus
        />
      </div>
      <div className="grid-2">
        <div>
          <label className="label" htmlFor="firm-email">
            Firm email
          </label>
          <input
            id="firm-email"
            name="email"
            className="input"
            type="email"
            required
            minLength={3}
            maxLength={226}
            value={form.email}
            onChange={handleChange}
          />
        </div>
        <div>
          <label className="label" htmlFor="firm-phone">
            Firm phone
          </label>
          <input
            id="firm-phone"
            name="phone"
            className="input"
            type="tel"
            required
            minLength={5}
            maxLength={20}
            value={form.phone}
            onChange={handleChange}
          />
        </div>
      </div>
      <div>
        <label className="label" htmlFor="firm-address">
          Address
        </label>
        <input
          id="firm-address"
          name="address"
          className="input"
          required
          maxLength={500}
          value={form.address}
          onChange={handleChange}
        />
      </div>

      {error && <p className="alert-error">{error}</p>}

      <div className="form-buttons">
        <button type="button" className="btn btn-outline" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Saving..." : "Save changes"}
        </button>
      </div>
    </form>
  );
}

// "Your firm" card on the My account page. Everyone can see it; only the Owner can edit.
function FirmCard() {
  const { user } = useAuth();
  const firmId = user.law_firm_id;
  const canEdit = can(user, "firm.update");

  const [state, setState] = useState({ key: null, firm: null, error: "" });
  const [editing, setEditing] = useState(false);
  const [message, setMessage] = useState("");
  const closeEdit = useCallback(() => setEditing(false), []);

  useEffect(() => {
    let ignore = false;
    apiFetch(`/law-firms/${firmId}`)
      .then((firm) => {
        if (!ignore) setState({ key: firmId, firm, error: "" });
      })
      .catch((err) => {
        if (!ignore) setState({ key: firmId, firm: null, error: err.message });
      });
    return () => {
      ignore = true;
    };
  }, [firmId]);

  const loading = state.key !== firmId;
  const firm = state.firm;

  return (
    <section className="card">
      <div className="section-header">
        <h2 className="section-title">Your firm</h2>
        {canEdit && firm && (
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => {
              setMessage("");
              setEditing(true);
            }}
          >
            Edit
          </button>
        )}
      </div>

      {loading && <p className="hint-inline">Loading firm details...</p>}
      {!loading && state.error && <p className="alert-error">{state.error}</p>}
      {message && <p className="alert-success">{message}</p>}

      {firm && (
        <dl className="detail-grid detail-grid-last firm-grid">
          <div>
            <dt>Name</dt>
            <dd>{firm.name}</dd>
          </div>
          <div>
            <dt>Email</dt>
            <dd>{firm.email}</dd>
          </div>
          <div>
            <dt>Phone</dt>
            <dd>{firm.phone}</dd>
          </div>
          <div>
            <dt>Address</dt>
            <dd>{firm.address}</dd>
          </div>
        </dl>
      )}

      {editing && firm && (
        <Modal title="Edit firm details" onClose={closeEdit}>
          <FirmForm
            firm={firm}
            onSaved={(updated) => {
              setState((prev) => ({ ...prev, firm: updated }));
              setEditing(false);
              setMessage("Firm details saved.");
            }}
            onCancel={closeEdit}
          />
        </Modal>
      )}
    </section>
  );
}

export default FirmCard;
