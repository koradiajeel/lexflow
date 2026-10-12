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
  const headers = authHeaders(options.headers);

  // FormData sets its own multipart Content-Type (with boundary), so leave it alone.
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (response.status === 401) {
    clearToken();
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
  const response = await fetch(`${API_URL}${path}`, { headers: authHeaders() });

  if (response.status === 401) {
    clearToken();
  }

  if (!response.ok) {
    await throwApiError(response);
  }

  return response.blob();
}
