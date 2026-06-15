import { Navigate, Outlet, Route, Routes } from 'react-router-dom';

import LoadingSpinner from '@/components/common/LoadingSpinner';
import Layout from '@/components/layout/Layout';
import AdminPage from '@/pages/AdminPage';
import AlertsPage from '@/pages/AlertsPage';
import CopilotPage from '@/pages/CopilotPage';
import DashboardPage from '@/pages/DashboardPage';
import LoginPage from '@/pages/LoginPage';
import OpportunityDetailPage from '@/pages/OpportunityDetailPage';
import OpportunityExplorerPage from '@/pages/OpportunityExplorerPage';
import ReportsPage from '@/pages/ReportsPage';
import SearchPage from '@/pages/SearchPage';
import SourcesPage from '@/pages/SourcesPage';
import { useAuth } from '@/store/AuthContext';

const ProtectedRoute = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner label="Loading workspace..." />;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

const AdminRoute = () => {
  const { user } = useAuth();

  return user?.role === 'admin' ? <Outlet /> : <Navigate to="/" replace />;
};

const AppShell = () => (
  <Layout>
    <Outlet />
  </Layout>
);

const App = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />

    <Route element={<ProtectedRoute />}>
      <Route element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="/opportunities" element={<OpportunityExplorerPage />} />
        <Route path="/opportunities/:id" element={<OpportunityDetailPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/copilot" element={<CopilotPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/sources" element={<SourcesPage />} />
        <Route element={<AdminRoute />}>
          <Route path="/admin" element={<AdminPage />} />
        </Route>
      </Route>
    </Route>

    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;
