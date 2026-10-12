import { Link, NavLink, Outlet, useLocation } from "react-router";
import { useAuth } from "../auth/useAuth";
import Logo from "./Logo";

// Frame for every logged-in page: top bar + the page below it.
function AppLayout() {
  const { user, signOut } = useAuth();
  const { pathname } = useLocation();
  const onCasePage = pathname.startsWith("/cases/");

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
          <NavLink to="/account" className="topbar-email" title="My account">
            <span className="topbar-email-full">{user.email}</span>
            <span className="topbar-email-short">Account</span>
          </NavLink>
          <span className="badge">{user.role}</span>
          <button type="button" className="btn btn-outline btn-sm" onClick={signOut}>
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
