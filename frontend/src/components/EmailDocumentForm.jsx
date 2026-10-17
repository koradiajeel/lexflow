import { useState } from "react";
import { apiFetch } from "../api/client";

// Same limit as the backend (app/schemas/document.py).
const MAX_MESSAGE = 2000;

// Clear text for each way sending can fail (the backend's own detail is shown otherwise).
function errorText(err) {
  if (err.status === 422) return "Please enter a valid email address.";
  if (err.status === 503) return "Email isn't set up on the server yet. Ask your administrator.";
  if (err.status === 502) return "Couldn't send the email right now. Please try again in a minute.";
  if (!err.status) return "Can't reach the server. Is the backend running?";
  return err.message; // e.g. 413 "too large", 404, 403
}

// Popup form: email one document as an attachment (POST /documents/{id}/email).
// Two steps: fill in the address, then confirm, because a typo would send a
// confidential file to a stranger.
function EmailDocumentForm({ doc, onSent, onCancel }) {
  const [to, setTo] = useState("");
  const [message, setMessage] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  function handleReview(event) {
    event.preventDefault(); // the browser already checked the address format (type="email")
    setError("");
    setConfirming(true);
  }

  async function handleSend() {
    setError("");
    setSending(true);
    try {
      const result = await apiFetch(`/documents/${doc.id}/email`, {
        method: "POST",
        body: JSON.stringify({ to: to.trim(), message: message.trim() }),
      });
      onSent(result);
    } catch (err) {
      setError(errorText(err));
      setConfirming(false);
      setSending(false);
    }
  }

  if (confirming) {
    return (
      <div className="form">
        <p className="email-confirm">
          Send <strong>{doc.filename}</strong> to <strong>{to.trim()}</strong>?
        </p>
        <p className="hint-inline">
          They'll see it as coming from you via LexFlow, and their reply will come to your email.
        </p>
        <div className="form-buttons">
          <button
            type="button"
            className="btn btn-outline"
            disabled={sending}
            onClick={() => setConfirming(false)}
          >
            Back
          </button>
          <button type="button" className="btn btn-primary" disabled={sending} onClick={handleSend}>
            {sending ? "Sending..." : "Yes, send"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <form className="form" onSubmit={handleReview}>
      <p className="email-file">
        📎 {doc.filename}
      </p>

      <div>
        <label className="label" htmlFor="email-to">
          To
        </label>
        <input
          id="email-to"
          className="input"
          type="email"
          required
          maxLength={255}
          placeholder="client@example.com"
          value={to}
          onChange={(e) => setTo(e.target.value)}
          autoFocus
        />
      </div>

      <div>
        <label className="label" htmlFor="email-message">
          Message <span className="label-optional">(optional)</span>
        </label>
        <textarea
          id="email-message"
          className="input textarea"
          maxLength={MAX_MESSAGE}
          rows={4}
          placeholder="Please find the document attached."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <p className="hint-inline char-count">
          {message.length} / {MAX_MESSAGE}
        </p>
      </div>

      {error && <p className="alert-error">{error}</p>}

      <div className="form-buttons">
        <button type="button" className="btn btn-outline" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary">
          Next
        </button>
      </div>
    </form>
  );
}

export default EmailDocumentForm;
