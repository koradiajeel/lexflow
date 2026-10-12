import { useState } from "react";
import { apiFetch } from "./api/client";

function ScaleIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 3v18M7 21h10M5 7h14M12 5l-7 2M12 5l7 2" />
      <path d="M5 7l-3 7a3.5 3.5 0 0 0 6 0L5 7zM19 7l-3 7a3.5 3.5 0 0 0 6 0l-3-7z" />
    </svg>
  );
}

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function testBackend() {
    setLoading(true);
    setResult(null);
    try {
      const me = await apiFetch("/auth/me");
      setResult({ ok: true, text: `Logged in as ${me.email}` });
    } catch (err) {
      const text = err.status
        ? `Backend replied: ${err.status} ${err.message}`
        : `Error: ${err.message}`;
      setResult({ ok: false, text });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-center">
      <div className="card test-card">
        <div>
          <div className="logo">
            <span className="logo-icon">
              <ScaleIcon />
            </span>
            LexFlow
          </div>
          <p className="subtitle">Backend connection check</p>
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={testBackend}
          disabled={loading}
        >
          {loading ? "Checking..." : "Test backend"}
        </button>

        {result && (
          <p className={result.ok ? "alert-success" : "alert-error"}>
            {result.text}
          </p>
        )}
      </div>
    </main>
  );
}

export default App;
