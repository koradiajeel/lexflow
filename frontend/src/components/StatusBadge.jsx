// Colored pill for a case status: Open (blue), In Progress (amber), Closed (gray).
const STATUS_CLASS = {
  Open: "status-open",
  "In Progress": "status-progress",
  Closed: "status-closed",
};

function StatusBadge({ status }) {
  return (
    <span className={`status-badge ${STATUS_CLASS[status] || ""}`}>
      {status}
    </span>
  );
}

export default StatusBadge;
