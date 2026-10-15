// Who may do what. Mirrors the backend's require_role(...) checks, so the UI only shows
// buttons that will actually work. The backend still enforces every rule (403 otherwise);
// this file just keeps people from clicking things that would fail.
const RULES = {
  "case.update": ["Owner", "Lawyer"], // change status (PATCH /cases/{id})
  "document.delete": ["Owner", "Lawyer"], // DELETE /documents/{id} (upload/download: everyone)
  "client.create": ["Owner", "Lawyer"],
  "client.update": ["Owner", "Lawyer"],
  "client.delete": ["Owner"],
  "lawyer.create": ["Owner"],
  "lawyer.update": ["Owner"],
  "lawyer.delete": ["Owner"],
  "lawyer.createLogin": ["Owner"],
  "user.manage": ["Owner"], // Users page: list logins, add staff
};

// can(user, "client.delete") -> true / false
export function can(user, action) {
  const allowed = RULES[action];
  if (!allowed) {
    throw new Error(`Unknown permission: ${action}`); // catches typos while developing
  }
  return Boolean(user) && allowed.includes(user.role);
}
