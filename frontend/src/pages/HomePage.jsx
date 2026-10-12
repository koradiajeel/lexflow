import { useEffect, useState } from "react";
import { apiFetch, clearToken } from "../api/client";
import Logo from "../components/Logo";

// Temporary page shown after login. The real dashboard comes with routing (roadmap step 3-4).
function HomePage({ onLogout }) {
  const [me, setMe] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadMe() {
      try {
        setMe(await apiFetch("/auth/me"));
      } catch (err) {
        if (err.status === 401) {
          onLogout(); // token expired or invalid: apiFetch already cleared it
        } else {
          setError(err.message);
        }
      }
    }
    loadMe();
  }, [onLogout]);

  function handleLogout() {
    clearToken();
    onLogout();
  }

  return (
    <main className="page-center">
      <div className="card auth-card">
        <Logo />

        {!me && !error && <p className="subtitle">Loading your account...</p>}
        {error && <p className="alert-error">{error}</p>}

        {me && (
          <>
            <div>
              <h1 className="auth-title">You're signed in</h1>
              <p className="subtitle">{me.email}</p>
            </div>
            <div>
              <span className="badge">{me.role}</span>
            </div>
            <p className="hint">
              The dashboard with your cases is coming in the next steps.
            </p>
          </>
        )}

        <button type="button" className="btn btn-outline" onClick={handleLogout}>
          Sign out
        </button>
      </div>
    </main>
  );
}

export default HomePage;
