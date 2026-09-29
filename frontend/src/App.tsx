import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Sidebar } from './components/common/Sidebar';
import { Header } from './components/common/Header';

import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { RequirementsPage } from './pages/RequirementsPage';
import { RolesPage } from './pages/RolesPage';
import { EmployeesPage } from './pages/EmployeesPage';
import { GenerationPage } from './pages/GenerationPage';
import { VerificationPage } from './pages/VerificationPage';
import { ReviewPage } from './pages/ReviewPage';
import { PolicyImpactPage } from './pages/PolicyImpactPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ReportsPage } from './pages/ReportsPage';
import { EmployeePortalPage } from './pages/EmployeePortalPage';
import { LearningModulePage } from './pages/LearningModulePage';

export const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-cloud flex text-obsidian">
      {/* Sidebar */}
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />

      {/* Main Container */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
        <Header onMobileMenuToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
        <main className="flex-1 overflow-y-auto pb-12">
          <Routes>
            <Route
              path="/"
              element={
                user?.role === 'EMPLOYEE' ? (
                  <Navigate to="/employee-portal" replace />
                ) : (
                  <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                    <DashboardPage />
                  </ProtectedRoute>
                )
              }
            />
            <Route
              path="/documents"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <DocumentsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/requirements"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <RequirementsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/roles"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <RolesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/employees"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <EmployeesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/generation"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <GenerationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/verification"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <VerificationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/review"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER']}>
                  <ReviewPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/policy-impact"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <PolicyImpactPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER']}>
                  <ReportsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/employee-portal"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER', 'EMPLOYEE']}>
                  <EmployeePortalPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/learning-module"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER', 'EMPLOYEE']}>
                  <LearningModulePage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to={user?.role === 'EMPLOYEE' ? '/employee-portal' : '/'} replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export const AppContent: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};

export default App;
