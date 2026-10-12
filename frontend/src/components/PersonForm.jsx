import { useState } from "react";

// Add/Edit form for a client or lawyer (both have name, email, phone).
// `limits` holds the same min/max lengths the backend checks.
function PersonForm({ initial, limits, submitLabel, onSubmit, onCancel }) {
  const [form, setForm] = useState({
    name: initial?.name ?? "",
    email: initial?.email ?? "",
    phone: initial?.phone ?? "",
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
      await onSubmit({
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
      });
    } catch (err) {
      setError(
        err.status === 422 ? "Some fields are invalid. Please check them." : err.message,
      );
      setSaving(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div>
        <label className="label" htmlFor="person-name">
          Name
        </label>
        <input
          id="person-name"
          name="name"
          className="input"
          required
          minLength={limits.name[0]}
          maxLength={limits.name[1]}
          value={form.name}
          onChange={handleChange}
          autoFocus
        />
      </div>
      <div>
        <label className="label" htmlFor="person-email">
          Email
        </label>
        <input
          id="person-email"
          name="email"
          className="input"
          type="email"
          required
          maxLength={255}
          value={form.email}
          onChange={handleChange}
        />
      </div>
      <div>
        <label className="label" htmlFor="person-phone">
          Phone
        </label>
        <input
          id="person-phone"
          name="phone"
          className="input"
          type="tel"
          required
          minLength={limits.phone[0]}
          maxLength={limits.phone[1]}
          value={form.phone}
          onChange={handleChange}
        />
      </div>

      {error && <p className="alert-error">{error}</p>}

      <div className="form-buttons">
        <button type="button" className="btn btn-outline" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}

export default PersonForm;
