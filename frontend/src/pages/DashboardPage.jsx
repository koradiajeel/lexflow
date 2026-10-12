import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";
import StatusBadge from "../components/StatusBadge";

const PAGE_SIZE = 10;
const STATUS_FILTERS = ["All", "Open", "In Progress", "Closed"];

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

// Turn a list like [{id, name}, ...] into { id: name } for quick lookups.
function namesById(items) {
  return Object.fromEntries(items.map((item) => [item.id, item.name]));
}

function DashboardPage() {
  const { user } = useAuth();
  const myLawyerId = user.lawyer_id; // set only when this login is linked to a lawyer profile

  // Filters and page live in the URL (?mine=1&status=Open&page=2), so refresh and Back keep them.
  const [searchParams, setSearchParams] = useSearchParams();
  const status = searchParams.get("status") || "All";
  const mine = Boolean(myLawyerId) && searchParams.get("mine") === "1";
  const page = Math.max(1, Number(searchParams.get("page")) || 1);
  const requestKey = `${mine}|${status}|${page}`;

  const [result, setResult] = useState({ key: null, cases: [], hasNext: false, error: "" });
  const [names, setNames] = useState({ clients: {}, lawyers: {} });

  // Load client and lawyer names once, to show names instead of IDs in the table.
  useEffect(() => {
    Promise.all([apiFetch("/clients/?limit=100"), apiFetch("/lawyers/?limit=100")])
      .then(([clients, lawyers]) =>
        setNames({ clients: namesById(clients), lawyers: namesById(lawyers) }),
      )
      .catch(() => {}); // names are a nice extra; the table still works without them
  }, []);

  // Load one page of cases whenever the filter or page changes.
  useEffect(() => {
    let ignore = false; // set when a newer request starts, so an old reply can't overwrite it
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE + 1), // ask for one extra: if it comes back, there is a next page
      offset: String((page - 1) * PAGE_SIZE),
    });
    if (status !== "All") params.set("status", status);
    if (mine) params.set("lawyer_id", myLawyerId);

    apiFetch(`/cases/?${params}`)
      .then((cases) => {
        if (ignore) return;
        setResult({
          key: requestKey,
          cases: cases.slice(0, PAGE_SIZE),
          hasNext: cases.length > PAGE_SIZE,
          error: "",
        });
      })
      .catch((err) => {
        if (ignore) return;
        setResult({ key: requestKey, cases: [], hasNext: false, error: err.message });
      });

    return () => {
      ignore = true;
    };
  }, [status, page, mine, myLawyerId, requestKey]);

  const loading = result.key !== requestKey;

  // Changing a filter keeps the other filter and goes back to page 1.
  function setFilters({ newMine = mine, newStatus = status }) {
    const next = {};
    if (newMine) next.mine = "1";
    if (newStatus !== "All") next.status = newStatus;
    setSearchParams(next);
  }

  function goToPage(newPage) {
    const next = new URLSearchParams(searchParams);
    if (newPage === 1) next.delete("page");
    else next.set("page", String(newPage));
    setSearchParams(next);
  }

  return (
    <div className="card cases-card">
      <div className="cases-header">
        <div>
          <h1 className="page-title">Cases</h1>
          <p className="subtitle">
            {mine ? "Cases assigned to you, newest first." : "All cases in your firm, newest first."}
          </p>
        </div>

        <div className="cases-filters">
          {myLawyerId && (
            <div className="filter-tabs" role="group" aria-label="Whose cases">
              {[
                ["All cases", false],
                ["My cases", true],
              ].map(([label, value]) => (
                <button
                  key={label}
                  type="button"
                  className={`filter-tab ${mine === value ? "active" : ""}`}
                  aria-pressed={mine === value}
                  onClick={() => setFilters({ newMine: value })}
                >
                  {label}
                </button>
              ))}
            </div>
          )}

          <div className="filter-tabs" role="group" aria-label="Filter by status">
            {STATUS_FILTERS.map((option) => (
              <button
                key={option}
                type="button"
                className={`filter-tab ${status === option ? "active" : ""}`}
                aria-pressed={status === option}
                onClick={() => setFilters({ newStatus: option })}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      </div>

      {result.error && !loading && <p className="alert-error">{result.error}</p>}

      {loading && <p className="cases-empty">Loading cases...</p>}

      {!loading && !result.error && result.cases.length === 0 && (
        <p className="cases-empty">
          {status === "All" ? "No cases yet." : `No ${status.toLowerCase()} cases.`}
          {mine && " (only cases assigned to you are shown)"}
        </p>
      )}

      {!loading && result.cases.length > 0 && (
        <table className="cases-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Client</th>
              <th>Lawyer</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {result.cases.map((c) => (
              <tr key={c.id}>
                <td data-label="Title">
                  <Link to={`/cases/${c.id}`} className="case-title">
                    {c.title}
                  </Link>
                </td>
                <td data-label="Client">{names.clients[c.client_id] || "—"}</td>
                <td data-label="Lawyer">{names.lawyers[c.lawyer_id] || "—"}</td>
                <td data-label="Status">
                  <StatusBadge status={c.status} />
                </td>
                <td data-label="Created">{formatDate(c.created_at)}</td>
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
    </div>
  );
}

export default DashboardPage;
