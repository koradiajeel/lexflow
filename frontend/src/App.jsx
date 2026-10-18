import { Navigate, Route, Routes } from "react-router";
import ProtectedRoute from "./auth/ProtectedRoute";
import PublicOnlyRoute from "./auth/PublicOnlyRoute";
import AppLayout from "./components/AppLayout";
import AccountPage from "./pages/AccountPage";
import CaseDetailPage from "./pages/CaseDetailPage";
import ClientsPage from "./pages/ClientsPage";
import DashboardPage from "./pages/DashboardPage";
import HomePage from "./pages/HomePage";
import LandingPage from "./pages/LandingPage";
import LawyersPage from "./pages/LawyersPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import UsersPage from "./pages/UsersPage";

// The map of URLs -> pages.
function App() {
  return (
    <Routes>
      {/* Public home page: open to everyone, logged in or not */}
      <Route path="/" element={<LandingPage />} />

      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/home" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/cases/:caseId" element={<CaseDetailPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/lawyers" element={<LawyersPage />} />
          <Route path="/account" element={<AccountPage />} />
          <Route path="/users" element={<UsersPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/home" replace />} />
    </Routes>
  );
}

export default App;
