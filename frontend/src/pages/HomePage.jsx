import { useEffect, useState } from "react";
import { Link } from "react-router";
import { apiFetch } from "../api/client";
import { can } from "../auth/permissions";
import { useAuth } from "../auth/useAuth";
import ModuleIcon from "../components/ModuleIcon";

// Every section of the app. `show(user)` decides who sees the tile, using the same
// rules as the buttons inside each page (auth/permissions.js).
const MODULES = [
  {
    title: "Cases",
    description: (user) =>
      can(user, "case.viewAll") ? "All cases in your firm" : "Cases assigned to you",
    to: "/dashboard",
    icon: "cases",
    show: () => true,
  },
  {
    title: "New case",
    description: () => "Open a new case",
    to: "/dashboard?new=1",
    icon: "newCase",
    show: (user) =>
      can(user, "case.create") && (can(user, "case.assignAnyLawyer") || Boolean(user.lawyer_id)),
  },
  {
    title: "My cases",
    description: () => "Only cases where you are the lawyer",
    to: "/dashboard?mine=1",
    icon: "myCases",
    // Owner/Staff linked to a lawyer profile; a Lawyer's "Cases" tile is already only theirs.
    show: (user) => can(user, "case.viewAll") && Boolean(user.lawyer_id),
  },
  {
    title: "Clients",
    description: () => "People and companies you represent",
    to: "/clients",
    icon: "clients",
    show: () => true,
  },
  {
    title: "Lawyers",
    description: (user) =>
      can(user, "lawyer.createLogin") ? "Lawyers and their logins" : "Lawyers in your firm",
    to: "/lawyers",
    icon: "lawyers",
    show: () => true,
  },
  {
    title: "Users",
    description: () => "Logins and staff accounts",
    to: "/users",
    icon: "users",
    show: (user) => can(user, "user.manage"),
  },
  {
    title: "Firm settings",
    description: (user) => (can(user, "firm.update") ? "Name, email, phone, address" : "Your firm's details"),
    to: "/account#firm",
    icon: "firm",
    show: () => true,
  },
  {
    title: "My account",
    description: () => "Profile and password",
    to: "/account",
    icon: "account",
    show: () => true,
  },
];

function HomePage() {
  const { user } = useAuth();
  const [search, setSearch] = useState("");
  const [firmName, setFirmName] = useState("");

  useEffect(() => {
    let ignore = false;
    apiFetch(`/law-firms/${user.law_firm_id}`)
      .then((firm) => {
        if (!ignore) setFirmName(firm.name);
      })
      .catch(() => {}); // the firm name is just a nice extra in the welcome strip
    return () => {
      ignore = true;
    };
  }, [user.law_firm_id]);

  const query = search.trim().toLowerCase();
  const tiles = MODULES.filter((m) => m.show(user))
    .map((m) => ({ ...m, text: m.description(user) }))
    .filter((m) => !query || `${m.title} ${m.text}`.toLowerCase().includes(query));

  return (
    <div className="home">
      <section className="card welcome-strip">
        <span className="welcome-avatar" aria-hidden="true">
          {user.email[0].toUpperCase()}
        </span>
        <div className="welcome-text">
          <span className="welcome-email">{user.email}</span>
          <span className="badge">{user.role}</span>
        </div>
        {firmName && <span className="welcome-firm">{firmName}</span>}
      </section>

      <div className="module-search">
        <input
          className="module-search-input"
          type="search"
          placeholder="Search sections"
          aria-label="Search sections"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <svg
          className="module-search-icon"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-4-4" />
        </svg>
      </div>

      {tiles.length === 0 ? (
        <p className="cases-empty">No sections match “{search}”.</p>
      ) : (
        <div className="module-grid">
          {tiles.map((m) => (
            <Link key={m.title} to={m.to} className="module-tile">
              <span className="module-title">{m.title}</span>
              <span className="module-icon">
                <ModuleIcon name={m.icon} />
              </span>
              <span className="module-description">{m.text}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default HomePage;
