const TOKEN_KEY = "lexflow_token";
const API_URL = import.meta.env.VITE_API_URL;

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// AuthProvider registers a function here so it hears about expired logins.
let unauthorizedHandler = null;

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

// A request that carried a token got 401: the login expired or became invalid.
// (A 401 without a token, like a wrong password on /auth/login, is not a session ending.)
function handleUnauthorized(hadToken) {
  clearToken();
  if (hadToken && unauthorizedHandler) {
    unauthorizedHandler();
  }
}

function authHeaders(extra = {}) {
  const headers = { ...extra };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

// Turn a non-OK response into an Error with the backend's `detail` message and the status code.
async function throwApiError(response) {
  let message = response.statusText;
  try {
    const data = await response.json();
    if (data && data.detail !== undefined) {
      message =
        typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail);
    }
  } catch {
    // Body was not JSON; keep the status text.
  }
  const err = new Error(message);
  err.status = response.status;
  throw err;
}

export async function apiFetch(path, options = {}) {
  const hadToken = Boolean(getToken());
  const headers = authHeaders(options.headers);

  // FormData sets its own multipart Content-Type (with boundary), so leave it alone.
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (response.status === 401) {
    handleUnauthorized(hadToken);
  }

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    await throwApiError(response);
  }

  return response.json();
}

// Like apiFetch, but returns the raw file (a Blob) instead of JSON. Used for downloads.
export async function apiFetchBlob(path) {
  const hadToken = Boolean(getToken());
  const response = await fetch(`${API_URL}${path}`, { headers: authHeaders() });

  if (response.status === 401) {
    handleUnauthorized(hadToken);
  }

  if (!response.ok) {
    await throwApiError(response);
  }

  return response.blob();
}
