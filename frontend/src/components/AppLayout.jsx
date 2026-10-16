import { Link, NavLink, Outlet } from "react-router";
import { useAuth } from "../auth/useAuth";
import Logo from "./Logo";

// Frame for every logged-in page: top bar + the page below it.
// Sections (Cases, Clients, Lawyers, Users...) are opened from the tiles on Home,
// so the top bar only needs a way back there.
function AppLayout() {
  const { user, signOut } = useAuth();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-left">
          <Link to="/home" aria-label="LexFlow home">
            <Logo />
          </Link>
          {/* NavLink adds the "active" class when its page is open */}
          <nav className="topnav" aria-label="Main">
            <NavLink to="/home" className="topnav-link">
              Home
            </NavLink>
          </nav>
        </div>
        <div className="topbar-user">
          <NavLink to="/account" className="topbar-email" title="My account">
            <span className="topbar-email-full">{user.email}</span>
            <span className="topbar-email-short">Account</span>
          </NavLink>
          <span className="badge topbar-role">{user.role}</span>
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
