import { useCallback, useState } from "react";
import { getToken } from "./api/client";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

// Simple page switcher until react-router is added (roadmap step 3).
function App() {
  const [page, setPage] = useState(getToken() ? "home" : "login");

  const goToLogin = useCallback(() => setPage("login"), []);
  const goToRegister = useCallback(() => setPage("register"), []);
  const goToHome = useCallback(() => setPage("home"), []);

  if (page === "home") {
    return <HomePage onLogout={goToLogin} />;
  }
  if (page === "register") {
    return <RegisterPage onSuccess={goToHome} onGoToLogin={goToLogin} />;
  }
  return <LoginPage onSuccess={goToHome} onGoToRegister={goToRegister} />;
}

export default App;
