import { useCallback, useEffect, useRef, useState } from "react";
import { apiFetch, apiFetchBlob } from "../api/client";
import DocumentPreview from "./DocumentPreview";

const MAX_SIZE = 20 * 1024 * 1024; // same 20 MB limit as the backend
const ACCEPT = ".pdf,.png,.jpg,.jpeg,.doc,.docx";
// Types the browser can show by itself. Word files can only be downloaded.
const PREVIEWABLE = ["application/pdf", "image/png", "image/jpeg"];

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

// Start a download from an in-memory file link by clicking a temporary <a download>.
function saveFile(url, filename) {
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
}

function EyeIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

// Short label for the file icon, e.g. "PDF" or "DOCX".
function fileLabel(filename) {
  const ext = filename.includes(".") ? filename.split(".").pop() : "";
  return ext.slice(0, 4).toUpperCase() || "FILE";
}

function DocumentsPanel({ caseId }) {
  const [state, setState] = useState({ key: null, documents: [], error: "" });
  const [uploading, setUploading] = useState(false);
  const [busyId, setBusyId] = useState(null); // document currently downloading/deleting
  const [message, setMessage] = useState({ type: "", text: "" });
  const [preview, setPreview] = useState(null); // { doc, url } while the preview popup is open
  const fileInput = useRef(null);

  useEffect(() => {
    let ignore = false;
    apiFetch(`/cases/${caseId}/documents`)
      .then((documents) => {
        if (!ignore) setState({ key: caseId, documents, error: "" });
      })
      .catch((err) => {
        if (!ignore) setState({ key: caseId, documents: [], error: err.message });
      });
    return () => {
      ignore = true;
    };
  }, [caseId]);

  const loading = state.key !== caseId;

  async function handleFileChosen(event) {
    const file = event.target.files[0];
    event.target.value = ""; // so choosing the same file again still triggers a change
    if (!file) return;

    setMessage({ type: "", text: "" });
    if (file.size > MAX_SIZE) {
      setMessage({ type: "error", text: "File is larger than 20 MB." });
      return;
    }

    const formData = new FormData();
    formData.append("file", file); // "file" must match the backend parameter name

    setUploading(true);
    try {
      const doc = await apiFetch(`/cases/${caseId}/documents`, {
        method: "POST",
        body: formData,
      });
      setState((prev) => ({ ...prev, documents: [doc, ...prev.documents] }));
      setMessage({ type: "success", text: `Uploaded ${doc.filename}.` });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(doc) {
    setBusyId(doc.id);
    setMessage({ type: "", text: "" });
    try {
      const blob = await apiFetchBlob(`/documents/${doc.id}/download`);
      const url = URL.createObjectURL(blob); // temporary in-memory link to the file
      saveFile(url, doc.filename);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setBusyId(null);
    }
  }

  async function handleView(doc) {
    setBusyId(doc.id);
    setMessage({ type: "", text: "" });
    try {
      const blob = await apiFetchBlob(`/documents/${doc.id}/download`);
      setPreview({ doc, url: URL.createObjectURL(blob) });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setBusyId(null);
    }
  }

  const closePreview = useCallback(() => {
    setPreview((current) => {
      if (current) URL.revokeObjectURL(current.url); // free the memory used by the file
      return null;
    });
  }, []);

  async function handleDelete(doc) {
    if (!window.confirm(`Delete "${doc.filename}"? This cannot be undone.`)) return;

    setBusyId(doc.id);
    setMessage({ type: "", text: "" });
    try {
      await apiFetch(`/documents/${doc.id}`, { method: "DELETE" });
      setState((prev) => ({
        ...prev,
        documents: prev.documents.filter((d) => d.id !== doc.id),
      }));
      setMessage({ type: "success", text: `Deleted ${doc.filename}.` });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="card">
      <div className="section-header">
        <div>
          <h2 className="section-title">Documents</h2>
          <p className="hint-inline">PDF, PNG, JPEG or Word · up to 20 MB</p>
        </div>
        <input
          ref={fileInput}
          type="file"
          accept={ACCEPT}
          hidden
          onChange={handleFileChosen}
        />
        <button
          type="button"
          className="btn btn-primary btn-sm"
          disabled={uploading}
          onClick={() => fileInput.current.click()}
        >
          {uploading ? "Uploading..." : "Upload document"}
        </button>
      </div>

      {message.text && (
        <p className={message.type === "error" ? "alert-error" : "alert-success"}>
          {message.text}
        </p>
      )}

      {loading && <p className="cases-empty">Loading documents...</p>}
      {!loading && state.error && <p className="alert-error">{state.error}</p>}
      {!loading && !state.error && state.documents.length === 0 && (
        <p className="cases-empty">No documents yet.</p>
      )}

      {!loading && state.documents.length > 0 && (
        <ul className="doc-list">
          {state.documents.map((doc) => (
            <li key={doc.id} className="doc-row">
              <span className="doc-icon">{fileLabel(doc.filename)}</span>
              <div className="doc-info">
                <span className="doc-name">{doc.filename}</span>
                <span className="doc-meta">
                  {formatSize(doc.size)} · {formatDate(doc.created_at)}
                </span>
              </div>
              <div className="doc-actions">
                {PREVIEWABLE.includes(doc.content_type) && (
                  <button
                    type="button"
                    className="icon-button"
                    aria-label={`View ${doc.filename}`}
                    title="View"
                    disabled={busyId === doc.id}
                    onClick={() => handleView(doc)}
                  >
                    <EyeIcon />
                  </button>
                )}
                <button
                  type="button"
                  className="btn btn-outline btn-sm"
                  disabled={busyId === doc.id}
                  onClick={() => handleDownload(doc)}
                >
                  Download
                </button>
                <button
                  type="button"
                  className="btn btn-danger btn-sm"
                  disabled={busyId === doc.id}
                  onClick={() => handleDelete(doc)}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {preview && (
        <DocumentPreview
          doc={preview.doc}
          url={preview.url}
          onClose={closePreview}
          onDownload={() => saveFile(preview.url, preview.doc.filename)}
        />
      )}
    </section>
  );
}

export default DocumentsPanel;
