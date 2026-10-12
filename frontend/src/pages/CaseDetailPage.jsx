import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { apiFetch } from "../api/client";
import DocumentsPanel from "../components/DocumentsPanel";
import StatusBadge from "../components/StatusBadge";

const STATUSES = ["Open", "In Progress", "Closed"];

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function CaseDetailPage() {
  const { caseId } = useParams(); // the :caseId part of /cases/:caseId
  const [state, setState] = useState({ key: null, data: null, client: null, lawyer: null, error: "" });
  const [saving, setSaving] = useState(false);
  const [statusError, setStatusError] = useState("");

  // Load the case, then its client and lawyer (for their names).
  useEffect(() => {
    let ignore = false;
    async function load() {
      try {
        const data = await apiFetch(`/cases/${caseId}`);
        const [client, lawyer] = await Promise.all([
          apiFetch(`/clients/${data.client_id}`).catch(() => null),
          apiFetch(`/lawyers/${data.lawyer_id}`).catch(() => null),
        ]);
        if (!ignore) setState({ key: caseId, data, client, lawyer, error: "" });
      } catch (err) {
        if (!ignore) {
          const error = err.status === 404 || err.status === 422 ? "Case not found." : err.message;
          setState({ key: caseId, data: null, client: null, lawyer: null, error });
        }
      }
    }
    load();
    return () => {
      ignore = true;
    };
  }, [caseId]);

  async function changeStatus(newStatus) {
    if (newStatus === state.data.status) return;
    setSaving(true);
    setStatusError("");
    try {
      const updated = await apiFetch(`/cases/${caseId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
      setState((prev) => ({ ...prev, data: updated }));
    } catch (err) {
      setStatusError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const loading = state.key !== caseId;
  const c = state.data;

  return (
    <div className="detail-stack">
      <Link to="/dashboard" className="back-link">
        ← All cases
      </Link>

      {loading && <p className="cases-empty">Loading case...</p>}
      {!loading && state.error && <p className="alert-error">{state.error}</p>}

      {!loading && c && (
        <>
          <section className="card">
            <div className="detail-title-row">
              <h1 className="page-title">{c.title}</h1>
              <StatusBadge status={c.status} />
            </div>
            <p className="detail-description">{c.description}</p>

            <dl className="detail-grid">
              <div>
                <dt>Client</dt>
                <dd>{state.client ? state.client.name : "—"}</dd>
                {state.client && <dd className="detail-sub">{state.client.email}</dd>}
              </div>
              <div>
                <dt>Lawyer</dt>
                <dd>{state.lawyer ? state.lawyer.name : "—"}</dd>
                {state.lawyer && <dd className="detail-sub">{state.lawyer.email}</dd>}
              </div>
              <div>
                <dt>Created</dt>
                <dd>{formatDate(c.created_at)}</dd>
              </div>
            </dl>

            <div className="status-changer">
              <span className="label">Change status</span>
              <div className="filter-tabs" role="group" aria-label="Change status">
                {STATUSES.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className={`filter-tab ${c.status === s ? "active" : ""}`}
                    aria-pressed={c.status === s}
                    disabled={saving}
                    onClick={() => changeStatus(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
              {statusError && <p className="alert-error">{statusError}</p>}
            </div>
          </section>

          <DocumentsPanel caseId={caseId} />
        </>
      )}
    </div>
  );
}

export default CaseDetailPage;
