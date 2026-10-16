import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "./useAuth";

// Wraps pages that need a login. Not logged in -> send to /login,
// and remember where the user wanted to go so Login can send them back
// (but not after a deliberate "Sign out": then the next login starts at Home).
function ProtectedRoute() {
  const { user, loading, signedOut } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <main className="page-center">
        <p className="subtitle">Loading...</p>
      </main>
    );
  }

  if (!user) {
    return (
      <Navigate to="/login" replace state={signedOut ? null : { from: location.pathname }} />
    );
  }

  return <Outlet />;
}

export default ProtectedRoute;
