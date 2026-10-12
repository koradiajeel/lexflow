import { useState } from "react";
import { apiFetch, setToken } from "../api/client";
import Logo from "../components/Logo";

function LoginPage({ onSuccess, onGoToRegister }) {
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
      setToken(data.access_token);
      onSuccess();
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
          <Logo />
          <h1 className="auth-title">Welcome back</h1>
          <p className="subtitle">Sign in to manage your firm's cases.</p>
        </div>

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
          <button type="button" className="link-button" onClick={onGoToRegister}>
            Register your firm
          </button>
        </p>
      </div>
    </main>
  );
}

export default LoginPage;
