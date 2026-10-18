import { useState } from "react";
import { Link } from "react-router";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";
import Logo from "../components/Logo";

function LoginPage() {
  const { signIn, sessionExpired } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault(); // stop the browser from reloading the page
    setError("");
    setLoading(true);
    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });
      // Saving the user makes PublicOnlyRoute redirect to the dashboard.
      await signIn(data.access_token);
    } catch (err) {
      if (err.status === 401) {
        setError("Incorrect email or password.");
      } else if (err.status) {
        setError(err.message);
      } else {
        setError("Can't reach the server. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-center">
      <div className="card auth-card">
        <div>
          <Link to="/" aria-label="LexFlow home">
            <Logo />
          </Link>
          <h1 className="auth-title">Welcome back</h1>
          <p className="subtitle">Sign in to manage your firm's cases.</p>
        </div>

        {sessionExpired && (
          <p className="alert-info">Your session expired. Please sign in again.</p>
        )}

        <form className="form" onSubmit={handleSubmit}>
          <div>
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              className="input"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              className="input"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <p className="alert-error">{error}</p>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="auth-switch">
          New to LexFlow?{" "}
          <Link to="/register" className="link-button">
            Register your firm
          </Link>
        </p>
      </div>
    </main>
  );
}

export default LoginPage;
