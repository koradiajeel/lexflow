import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { apiFetch } from "../api/client";
import Modal from "./Modal";
import PersonForm from "./PersonForm";

const PAGE_SIZE = 10;

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

// One list page for "people" records. Used by ClientsPage and LawyersPage.
// config: { title, singular, endpoint, description, limits, extraColumn? }
// extraColumn: { header, render(item, { reload, showMessage }) } adds one more column.
function PeopleManager({ config }) {
  const { title, singular, endpoint, description, limits, extraColumn } = config;

  const [searchParams, setSearchParams] = useSearchParams();
  const page = Math.max(1, Number(searchParams.get("page")) || 1);
  const [reloadCount, setReloadCount] = useState(0); // bump to load the list again
  const requestKey = `${endpoint}|${page}|${reloadCount}`;

  const [result, setResult] = useState({ key: null, items: [], hasNext: false, error: "" });
  const [editing, setEditing] = useState(null); // null = closed, {} = adding, item = editing
  const [message, setMessage] = useState({ type: "", text: "" });
  const [busyId, setBusyId] = useState(null);

  useEffect(() => {
    let ignore = false;
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE + 1), // one extra tells us if there is a next page
      offset: String((page - 1) * PAGE_SIZE),
    });
    apiFetch(`${endpoint}?${params}`)
      .then((items) => {
        if (ignore) return;
        setResult({
          key: requestKey,
          items: items.slice(0, PAGE_SIZE),
          hasNext: items.length > PAGE_SIZE,
          error: "",
        });
      })
      .catch((err) => {
        if (!ignore) setResult({ key: requestKey, items: [], hasNext: false, error: err.message });
      });
    return () => {
      ignore = true;
    };
  }, [endpoint, page, requestKey]);

  const loading = result.key !== requestKey;
  const closeForm = useCallback(() => setEditing(null), []);
  const reload = useCallback(() => setReloadCount((n) => n + 1), []);
  const showMessage = useCallback((text) => setMessage({ type: "success", text }), []);

  function goToPage(newPage) {
    setSearchParams(newPage === 1 ? {} : { page: String(newPage) });
  }

  // Called by PersonForm. Throws on error so the form can show it.
  async function handleSave(data) {
    const isNew = !editing.id;
    const saved = await apiFetch(isNew ? endpoint : `${endpoint}${editing.id}`, {
      method: isNew ? "POST" : "PATCH",
      body: JSON.stringify(data),
    });
    setEditing(null);
    setMessage({ type: "success", text: `${isNew ? "Added" : "Updated"} ${saved.name}.` });
    if (isNew && page !== 1) {
      goToPage(1); // new records appear first (newest first)
    } else {
      reload();
    }
  }

  async function handleDelete(item) {
    if (!window.confirm(`Delete ${singular.toLowerCase()} "${item.name}"? This cannot be undone.`)) {
      return;
    }
    setBusyId(item.id);
    setMessage({ type: "", text: "" });
    try {
      await apiFetch(`${endpoint}${item.id}`, { method: "DELETE" });
      setMessage({ type: "success", text: `Deleted ${item.name}.` });
      // If that was the last item on this page, go back one page.
      if (result.items.length === 1 && page > 1) goToPage(page - 1);
      else reload();
    } catch (err) {
      setMessage({ type: "error", text: err.message }); // e.g. 409 "existing cases reference..."
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="card cases-card">
      <div className="cases-header">
        <div>
          <h1 className="page-title">{title}</h1>
          <p className="subtitle">{description}</p>
        </div>
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={() => {
            setMessage({ type: "", text: "" });
            setEditing({});
          }}
        >
          + Add {singular.toLowerCase()}
        </button>
      </div>

      {message.text && (
        <p className={`list-message ${message.type === "error" ? "alert-error" : "alert-success"}`}>
          {message.text}
        </p>
      )}

      {loading && <p className="cases-empty">Loading {title.toLowerCase()}...</p>}
      {!loading && result.error && <p className="alert-error">{result.error}</p>}
      {!loading && !result.error && result.items.length === 0 && (
        <p className="cases-empty">No {title.toLowerCase()} yet.</p>
      )}

      {!loading && result.items.length > 0 && (
        <table className="cases-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Added</th>
              {extraColumn && <th>{extraColumn.header}</th>}
              <th className="col-actions">
                <span className="visually-hidden">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {result.items.map((item) => (
              <tr key={item.id}>
                <td data-label="Name">
                  <span className="case-title-plain">{item.name}</span>
                </td>
                <td data-label="Email">{item.email}</td>
                <td data-label="Phone">{item.phone}</td>
                <td data-label="Added">{formatDate(item.created_at)}</td>
                {extraColumn && (
                  <td data-label={extraColumn.header}>
                    {extraColumn.render(item, { reload, showMessage })}
                  </td>
                )}
                <td className="col-actions">
                  <div className="row-actions">
                    <button
                      type="button"
                      className="btn btn-outline btn-sm"
                      disabled={busyId === item.id}
                      onClick={() => {
                        setMessage({ type: "", text: "" });
                        setEditing(item);
                      }}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="btn btn-danger btn-sm"
                      disabled={busyId === item.id}
                      onClick={() => handleDelete(item)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && (page > 1 || result.hasNext) && (
        <div className="pagination">
          <button
            type="button"
            className="btn btn-outline btn-sm"
            disabled={page === 1}
            onClick={() => goToPage(page - 1)}
          >
            Previous
          </button>
          <span className="pagination-label">Page {page}</span>
          <button
            type="button"
            className="btn btn-outline btn-sm"
            disabled={!result.hasNext}
            onClick={() => goToPage(page + 1)}
          >
            Next
          </button>
        </div>
      )}

      {editing && (
        <Modal
          title={editing.id ? `Edit ${singular.toLowerCase()}` : `Add ${singular.toLowerCase()}`}
          onClose={closeForm}
        >
          <PersonForm
            initial={editing}
            limits={limits}
            submitLabel={editing.id ? "Save changes" : `Add ${singular.toLowerCase()}`}
            onSubmit={handleSave}
            onCancel={closeForm}
          />
        </Modal>
      )}
    </div>
  );
}

export default PeopleManager;
