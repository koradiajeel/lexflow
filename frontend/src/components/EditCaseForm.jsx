import { useState } from "react";
import { apiFetch } from "../api/client";

// Edit a case's title and description (PATCH /cases/{id}).
// Length rules match backend/app/schemas/case.py.
function EditCaseForm({ caseData, onSaved, onCancel }) {
  const [form, setForm] = useState({
    title: caseData.title,
    description: caseData.description,
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
      const updated = await apiFetch(`/cases/${caseData.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          title: form.title.trim(),
          description: form.description.trim(),
        }),
      });
      onSaved(updated);
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
        <label className="label" htmlFor="edit-title">
          Title
        </label>
        <input
          id="edit-title"
          name="title"
          className="input"
          required
          minLength={2}
          maxLength={255}
          value={form.title}
          onChange={handleChange}
          autoFocus
        />
      </div>
      <div>
        <label className="label" htmlFor="edit-description">
          Description
        </label>
        <textarea
          id="edit-description"
          name="description"
          className="input textarea"
          required
          maxLength={1000}
          rows={5}
          value={form.description}
          onChange={handleChange}
        />
        <p className="hint-inline char-count">{form.description.length} / 1000</p>
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

export default EditCaseForm;
