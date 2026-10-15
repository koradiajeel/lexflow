import { useState } from "react";
import { Link } from "react-router";
import { apiFetch } from "../api/client";

// Form for POST /cases/. Length rules match backend/app/schemas/case.py.
// clients / lawyers: lists for the dropdowns (null while still loading).
// defaultLawyerId: pre-selects the signed-in lawyer, if any.
function NewCaseForm({ clients, lawyers, defaultLawyerId, onCreated, onCancel }) {
  const [form, setForm] = useState({
    title: "",
    description: "",
    client_id: "",
    lawyer_id: defaultLawyerId || "",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  if (!clients || !lawyers) {
    return <p className="cases-empty">Loading clients and lawyers...</p>;
  }

  // A case needs a client and a lawyer, so explain where to add them first.
  if (clients.length === 0 || lawyers.length === 0) {
    return (
      <div className="form">
        <p className="alert-error">
          A case needs a client and a lawyer. Add{" "}
          {clients.length === 0 && (
            <Link to="/clients" className="link-button">
              a client
            </Link>
          )}
          {clients.length === 0 && lawyers.length === 0 && " and "}
          {lawyers.length === 0 && (
            <Link to="/lawyers" className="link-button">
              a lawyer
            </Link>
          )}{" "}
          first.
        </p>
        <div className="form-buttons">
          <button type="button" className="btn btn-outline" onClick={onCancel}>
            Close
          </button>
        </div>
      </div>
    );
  }

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      const created = await apiFetch("/cases/", {
        method: "POST",
        body: JSON.stringify({
          title: form.title.trim(),
          description: form.description.trim(),
          client_id: form.client_id,
          lawyer_id: form.lawyer_id,
        }),
      });
      onCreated(created);
    } catch (err) {
      setError(
        err.status === 422
          ? "Title needs at least 2 characters and a description is required."
          : err.message,
      );
      setSaving(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div>
        <label className="label" htmlFor="case-title">
          Title
        </label>
        <input
          id="case-title"
          name="title"
          className="input"
          required
          minLength={2}
          maxLength={255}
          placeholder="e.g. Property boundary dispute"
          value={form.title}
          onChange={handleChange}
          autoFocus
        />
      </div>

      <div>
        <label className="label" htmlFor="case-description">
          Description
        </label>
        <textarea
          id="case-description"
          name="description"
          className="input textarea"
          required
          maxLength={1000}
          rows={4}
          placeholder="What is this case about?"
          value={form.description}
          onChange={handleChange}
        />
        <p className="hint-inline char-count">{form.description.length} / 1000</p>
      </div>

      <div className="grid-2">
        <div>
          <label className="label" htmlFor="case-client">
            Client
          </label>
          <select
            id="case-client"
            name="client_id"
            className="input"
            required
            value={form.client_id}
            onChange={handleChange}
          >
            <option value="" disabled>
              Choose a client
            </option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="case-lawyer">
            Lawyer
          </label>
          <select
            id="case-lawyer"
            name="lawyer_id"
            className="input"
            required
            value={form.lawyer_id}
            onChange={handleChange}
          >
            <option value="" disabled>
              Choose a lawyer
            </option>
            {lawyers.map((l) => (
              <option key={l.id} value={l.id}>
                {l.name}
                {l.id === defaultLawyerId ? " (you)" : ""}
              </option>
            ))}
          </select>
        </div>
      </div>

      <p className="hint">New cases start as Open.</p>

      {error && <p className="alert-error">{error}</p>}

      <div className="form-buttons">
        <button type="button" className="btn btn-outline" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Creating..." : "Create case"}
        </button>
      </div>
    </form>
  );
}

export default NewCaseForm;
