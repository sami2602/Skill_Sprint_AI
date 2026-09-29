import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { ShieldAlert, Lock, ArrowLeft } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';

interface ProtectedRouteProps {
  allowedRoles?: UserRole[];
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles, children }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-cloud flex items-center justify-center p-6">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-electric-600 animate-pulse flex items-center justify-center text-white font-bold font-heading">
            S
          </div>
          <span className="text-xs font-mono text-obsidian-400">Verifying session token...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    if (user.role === 'EMPLOYEE') {
      return <Navigate to="/employee-portal" replace />;
    }
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-md w-full bg-white p-8 rounded-2xl border border-rose-200 shadow-modal space-y-4">
          <div className="h-14 w-14 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center mx-auto">
            <ShieldAlert className="h-8 w-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-bold font-heading text-obsidian">403 Access Forbidden</h3>
            <p className="text-xs text-obsidian-400">
              Your assigned role <span className="font-mono font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">{user.role}</span> does not have authorization to view this protected resource.
            </p>
          </div>

          <div className="pt-2 text-xs text-obsidian-400 font-mono bg-cloud-100 p-3 rounded-xl">
            Required Role Level: {allowedRoles.join(', ')}
          </div>

          <button
            onClick={() => window.history.back()}
            className="w-full py-2 px-4 bg-obsidian hover:bg-obsidian-800 text-white font-semibold text-xs rounded-xl flex items-center justify-center gap-2 transition-all"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Return to Previous Page</span>
          </button>
        </div>
      </div>
    );
  }

  return children ? <>{children}</> : <Outlet />;
};
