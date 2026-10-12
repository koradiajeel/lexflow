import { useState } from "react";
import { Link } from "react-router";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";
import Logo from "../components/Logo";

const EMPTY_FORM = {
  firm_name: "",
  firm_email: "",
  firm_phone: "",
  firm_address: "",
  owner_email: "",
  password: "",
  confirm_password: "",
};

function RegisterPage() {
  const { signIn } = useAuth();
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // One change handler for every field: the input's "name" says which key to update.
  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (form.password !== form.confirm_password) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const data = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          firm_name: form.firm_name.trim(),
          firm_email: form.firm_email.trim(),
          firm_phone: form.firm_phone.trim(),
          firm_address: form.firm_address.trim(),
          owner_email: form.owner_email.trim(),
          password: form.password,
        }),
      });
      // Saving the user makes PublicOnlyRoute redirect to the dashboard.
      await signIn(data.access_token);
    } catch (err) {
      if (err.status === 422) {
        setError("Some fields are invalid. Please check the form and try again.");
      } else if (err.status) {
        setError(err.message); // e.g. 409 "A firm with this email already exists"
      } else {
        setError("Can't reach the server. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-center">
      <div className="card auth-card auth-card-wide">
        <div>
          <Logo />
          <h1 className="auth-title">Register your firm</h1>
          <p className="subtitle">
            Create your law firm and your Owner account in one step.
          </p>
        </div>

        <form className="form" onSubmit={handleSubmit}>
          <p className="form-section-title">Firm details</p>

          <div>
            <label className="label" htmlFor="firm_name">
              Firm name
            </label>
            <input
              id="firm_name"
              name="firm_name"
              className="input"
              required
              maxLength={225}
              value={form.firm_name}
              onChange={handleChange}
            />
          </div>

          <div className="grid-2">
            <div>
              <label className="label" htmlFor="firm_email">
                Firm email
              </label>
              <input
                id="firm_email"
                name="firm_email"
                className="input"
                type="email"
                required
                value={form.firm_email}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="label" htmlFor="firm_phone">
                Firm phone
              </label>
              <input
                id="firm_phone"
                name="firm_phone"
                className="input"
                type="tel"
                required
                minLength={5}
                maxLength={20}
                value={form.firm_phone}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <label className="label" htmlFor="firm_address">
              Firm address
            </label>
            <input
              id="firm_address"
              name="firm_address"
              className="input"
              required
              maxLength={500}
              value={form.firm_address}
              onChange={handleChange}
            />
          </div>

          <p className="form-section-title">Your account (Owner)</p>

          <div>
            <label className="label" htmlFor="owner_email">
              Your email
            </label>
            <input
              id="owner_email"
              name="owner_email"
              className="input"
              type="email"
              autoComplete="email"
              required
              value={form.owner_email}
              onChange={handleChange}
            />
          </div>

          <div className="grid-2">
            <div>
              <label className="label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                name="password"
                className="input"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                maxLength={72}
                value={form.password}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="label" htmlFor="confirm_password">
                Confirm password
              </label>
              <input
                id="confirm_password"
                name="confirm_password"
                className="input"
                type="password"
                autoComplete="new-password"
                required
                value={form.confirm_password}
                onChange={handleChange}
              />
            </div>
          </div>
          <p className="hint">At least 8 characters.</p>

          {error && <p className="alert-error">{error}</p>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Creating your firm..." : "Create firm"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account?{" "}
          <Link to="/login" className="link-button">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}

export default RegisterPage;
