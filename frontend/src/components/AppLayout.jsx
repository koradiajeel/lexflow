import { Link, Outlet, useNavigate } from "react-router";
import { useAuth } from "../auth/useAuth";
import Logo from "./Logo";

// Frame for every logged-in page: top bar + the page below it.
function AppLayout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  function handleSignOut() {
    signOut();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/dashboard" aria-label="LexFlow home">
          <Logo />
        </Link>
        <div className="topbar-user">
          <span className="topbar-email">{user.email}</span>
          <span className="badge">{user.role}</span>
          <button type="button" className="btn btn-outline btn-sm" onClick={handleSignOut}>
            Sign out
          </button>
        </div>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}

export default AppLayout;
