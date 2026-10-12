import { useState } from "react";
import { apiFetch } from "./api/client";

function App() {
  const [message, setMessage] = useState("");

  async function testBackend() {
    setMessage("Checking...");
    try {
      const me = await apiFetch("/auth/me");
      setMessage(`Logged in as ${me.email}`);
    } catch (err) {
      if (err.status) {
        setMessage(`Backend replied: ${err.status} ${err.message}`);
      } else {
        setMessage(`Error: ${err.message}`);
      }
    }
  }

  return (
    <div>
      <h1>LexFlow</h1>
      <button type="button" onClick={testBackend}>
        Test backend
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default App;
