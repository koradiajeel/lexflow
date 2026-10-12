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

export async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

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

  return response.json();
}
