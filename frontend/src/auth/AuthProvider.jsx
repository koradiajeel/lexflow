import { useCallback, useEffect, useMemo, useState } from "react";
import { apiFetch, clearToken, getToken, setToken, setUnauthorizedHandler } from "../api/client";
import { AuthContext } from "./authContext";

function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // { id, email, role, law_firm_id } from /auth/me
  const [loading, setLoading] = useState(Boolean(getToken())); // only wait if there is a token to check
  // True after clicking "Sign out", so the next login starts at the dashboard
  // instead of the page the previous user was on.
  const [signedOut, setSignedOut] = useState(false);
  // True when the server rejected our token mid-session; LoginPage shows a notice.
  const [sessionExpired, setSessionExpired] = useState(false);

  // If any request finds the login expired, sign out here too. ProtectedRoute then sends the
  // user to /login, remembering the page so they come back to it after signing in again.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      setSessionExpired(true);
      setUser(null);
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  // On app start: if a token is saved, ask the backend who it belongs to.
  useEffect(() => {
    if (!getToken()) return;
    apiFetch("/auth/me")
      .then(setUser)
      .catch(() => {
        clearToken(); // token is invalid or expired
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  // Called by Login/Register with the token the backend returned.
  const signIn = useCallback(async (token) => {
    setToken(token);
    const me = await apiFetch("/auth/me");
    setSignedOut(false);
    setSessionExpired(false);
    setUser(me);
    return me;
  }, []);

  const signOut = useCallback(() => {
    clearToken();
    setSignedOut(true);
    setSessionExpired(false);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, signedOut, sessionExpired, signIn, signOut }),
    [user, loading, signedOut, sessionExpired, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export default AuthProvider;
