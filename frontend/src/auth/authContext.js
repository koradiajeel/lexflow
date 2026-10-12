import { createContext } from "react";

// Shared "who is logged in" box. AuthProvider fills it, useAuth() reads it.
export const AuthContext = createContext(null);
