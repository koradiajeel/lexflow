import { useAuth } from "../auth/useAuth";

// Placeholder: the case list arrives in roadmap step 4.
function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="card">
      <h1 className="page-title">Dashboard</h1>
      <p className="subtitle">Signed in as {user.email}</p>
      <p className="hint dashboard-hint">
        Your cases will appear here in the next step.
      </p>
    </div>
  );
}

export default DashboardPage;
