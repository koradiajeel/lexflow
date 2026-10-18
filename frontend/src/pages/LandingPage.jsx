import { Link } from "react-router";
import { useAuth } from "../auth/useAuth";
import Logo from "../components/Logo";
import ModuleIcon from "../components/ModuleIcon";
import StatusBadge from "../components/StatusBadge";

// Public home page at "/". Only describes what LexFlow really does
// (no made-up numbers, customers or testimonials).

const FEATURES = [
  {
    icon: "cases",
    title: "Track every case",
    text: "Open, In Progress or Closed at a glance. Filter, page through and update cases in seconds.",
  },
  {
    icon: "cloud",
    title: "Documents in secure cloud storage",
    text: "Upload PDFs, images and Word files. Preview them in the browser; files are stored encrypted in Amazon S3.",
  },
  {
    icon: "mail",
    title: "Email a document in one click",
    text: "Sent in your name (“Priya Sharma via LexFlow”), replies come straight to you, and every send is logged.",
  },
  {
    icon: "lawyers",
    title: "Lawyers see their own cases",
    text: "Give each lawyer a login. They work on the cases assigned to them, and nothing else.",
  },
  {
    icon: "users",
    title: "The right access for every role",
    text: "Owners run the firm, lawyers handle their cases, staff help with documents. Buttons only appear when allowed.",
  },
  {
    icon: "lock",
    title: "Every firm’s data stays separate",
    text: "Each firm only ever sees its own lawyers, clients, cases and files. Passwords are hashed and sessions expire.",
  },
];

const STEPS = [
  { title: "Register your firm", text: "Create your firm and your Owner account in one form." },
  { title: "Add your team and clients", text: "Add lawyers and give them a login, add staff and clients." },
  { title: "Open cases and add documents", text: "Create cases, assign a lawyer, upload and share files." },
];

const ROLES = [
  {
    name: "Owner",
    points: ["Sees every case in the firm", "Adds lawyers, staff and their logins", "Manages firm settings"],
  },
  {
    name: "Lawyer",
    points: ["Sees only their own cases", "Opens cases and adds clients", "Uploads, previews and emails documents"],
  },
  {
    name: "Staff",
    points: ["Sees every case in the firm", "Uploads and downloads documents", "Read-only for everything else"],
  },
];

// Example rows for the product picture in the hero (an illustration, not real data).
const PREVIEW_CASES = [
  { title: "Property boundary dispute", lawyer: "Priya Sharma", status: "Open" },
  { title: "Commercial lease renewal", lawyer: "Arjun Mehta", status: "In Progress" },
  { title: "Trademark registration", lawyer: "Priya Sharma", status: "Closed" },
  { title: "Employment contract review", lawyer: "Arjun Mehta", status: "Open" },
];

function LandingPage() {
  const { user } = useAuth();

  const primaryCta = user ? (
    <Link to="/home" className="btn btn-primary">
      Open LexFlow
    </Link>
  ) : (
    <Link to="/register" className="btn btn-primary">
      Register your firm
    </Link>
  );

  return (
    <div className="landing">
      <header className="landing-header">
        <Link to="/" aria-label="LexFlow home">
          <Logo />
        </Link>
        <nav className="landing-nav" aria-label="Page sections">
          <a href="#features">Features</a>
          <a href="#how">How it works</a>
          <a href="#roles">Roles</a>
        </nav>
        <div className="landing-header-actions">
          {user ? (
            <Link to="/home" className="btn btn-primary btn-sm">
              Open LexFlow
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline btn-sm">
                Sign in
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm landing-hide-phone">
                Register
              </Link>
            </>
          )}
        </div>
      </header>

      <main>
        {/* ---------- Hero ---------- */}
        <section className="landing-hero">
          <div className="landing-hero-text">
            <span className="badge">Case &amp; document management for law firms</span>
            <h1 className="landing-title">
              Your firm&rsquo;s cases, clients and documents, <span className="landing-accent">in one place.</span>
            </h1>
            <p className="landing-lead">
              LexFlow keeps every case, client and file organised, and makes sure each person in
              your firm sees exactly what they should.
            </p>
            <div className="landing-ctas">
              {primaryCta}
              {!user && (
                <Link to="/login" className="btn btn-outline">
                  Sign in
                </Link>
              )}
            </div>
          </div>

          <div className="landing-preview" aria-hidden="true">
            <div className="landing-preview-bar">
              <span />
              <span />
              <span />
              <em>Preview</em>
            </div>
            <div className="landing-preview-body">
              <div className="landing-preview-head">
                <strong>Cases</strong>
                <span className="landing-preview-btn">+ New case</span>
              </div>
              {PREVIEW_CASES.map((c) => (
                <div key={c.title} className="landing-preview-row">
                  <div>
                    <span className="landing-preview-title">{c.title}</span>
                    <span className="landing-preview-lawyer">{c.lawyer}</span>
                  </div>
                  <StatusBadge status={c.status} />
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ---------- Features ---------- */}
        <section id="features" className="landing-section">
          <h2 className="landing-section-title">Everything a firm needs, nothing it doesn&rsquo;t</h2>
          <p className="landing-section-lead">The essentials of running cases, built simple.</p>
          <div className="landing-features">
            {FEATURES.map((f) => (
              <article key={f.title} className="landing-feature">
                <span className="landing-feature-icon">
                  <ModuleIcon name={f.icon} />
                </span>
                <h3>{f.title}</h3>
                <p>{f.text}</p>
              </article>
            ))}
          </div>
        </section>

        {/* ---------- How it works ---------- */}
        <section id="how" className="landing-section landing-section-tint">
          <h2 className="landing-section-title">Up and running in three steps</h2>
          <ol className="landing-steps">
            {STEPS.map((s, i) => (
              <li key={s.title} className="landing-step">
                <span className="landing-step-number">{i + 1}</span>
                <h3>{s.title}</h3>
                <p>{s.text}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* ---------- Roles ---------- */}
        <section id="roles" className="landing-section">
          <h2 className="landing-section-title">Built around how a firm really works</h2>
          <p className="landing-section-lead">Three roles, each with exactly the access it needs.</p>
          <div className="landing-roles">
            {ROLES.map((r) => (
              <article key={r.name} className="landing-role">
                <span className="badge">{r.name}</span>
                <ul>
                  {r.points.map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        {/* ---------- Final call to action ---------- */}
        <section className="landing-cta">
          <h2>Ready to organise your firm?</h2>
          <p>Set up your firm and invite your team today.</p>
          {primaryCta}
        </section>
      </main>

      <footer className="landing-footer">
        <Logo />
        <nav aria-label="Footer">
          <Link to="/login">Sign in</Link>
          <Link to="/register">Register your firm</Link>
        </nav>
        <span>&copy; {new Date().getFullYear()} LexFlow</span>
      </footer>
    </div>
  );
}

export default LandingPage;
