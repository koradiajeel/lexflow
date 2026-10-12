import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router";
import { useAuth } from "../auth/useAuth";
import Logo from "./Logo";

// Frame for every logged-in page: top bar + the page below it.
function AppLayout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const onCasePage = pathname.startsWith("/cases/");

  function handleSignOut() {
    signOut();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-left">
          <Link to="/dashboard" aria-label="LexFlow home">
            <Logo />
          </Link>
          {/* NavLink adds the "active" class when its page is open */}
          <nav className="topnav" aria-label="Main">
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `topnav-link ${isActive || onCasePage ? "active" : ""}`
              }
            >
              Cases
            </NavLink>
            <NavLink to="/clients" className="topnav-link">
              Clients
            </NavLink>
            <NavLink to="/lawyers" className="topnav-link">
              Lawyers
            </NavLink>
          </nav>
        </div>
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
