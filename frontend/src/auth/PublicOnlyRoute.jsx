import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "./useAuth";

// Wraps /login and /register. Already logged in (or just logged in) -> go to the page
// the user originally asked for, or the Home page.
function PublicOnlyRoute() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return null;
  }

  if (user) {
    return <Navigate to={location.state?.from || "/home"} replace />;
  }

  return <Outlet />;
}

export default PublicOnlyRoute;
