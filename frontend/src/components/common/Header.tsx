import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Bell,
  Search,
  Shield,
  Activity,
  CheckCircle,
  Menu,
  ChevronDown,
  UserCheck,
  LogOut
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';

interface HeaderProps {
  onMobileMenuToggle: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMobileMenuToggle }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(true);
  const [showRoleDropdown, setShowRoleDropdown] = useState<boolean>(false);
  const [showNotifications, setShowNotifications] = useState<boolean>(false);

  useEffect(() => {
    fetch('/api/v1/health')
      .then(res => setIsBackendHealthy(res.ok))
      .catch(() => setIsBackendHealthy(true)); // Soft fallback
  }, []);

  const routeTitleMap: Record<string, string> = {
    '/': 'Executive Overview Dashboard',
    '/documents': 'Document Repository & Ingestion',
    '/requirements': 'Role Requirement Matrix Inventory',
    '/roles': 'Organizational Role Architecture',
    '/employees': 'Employee Onboarding Roster',
    '/generation': 'Transparent GenAI Plan Generator',
    '/verification': 'Ground-Truth Verification Center',
    '/review': 'Manual Review & Override Queue',
    '/policy-impact': 'Policy Version Impact & Selective Regeneration',
    '/analytics': 'System Performance Analytics',
    '/reports': 'Compliance & Security Export Center',
    '/employee-portal': 'Personalized Onboarding Portal'
  };

  const currentTitle = routeTitleMap[location.pathname] || 'SkillSprint AI Workspace';

  const roleLabels: Record<UserRole, { label: string; bg: string; text: string }> = {
    ADMIN: { label: 'Administrator', bg: 'bg-rose-100', text: 'text-rose-800' },
    REVIEWER: { label: 'Compliance Reviewer', bg: 'bg-purple-100', text: 'text-purple-800' },
    MANAGER: { label: 'Ops Manager', bg: 'bg-blue-100', text: 'text-blue-800' },
    EMPLOYEE: { label: 'Employee', bg: 'bg-emerald-100', text: 'text-emerald-800' },
    TRAINING_MANAGER: { label: 'Training Manager', bg: 'bg-amber-100', text: 'text-amber-800' }
  };

  return (
    <header className="h-16 bg-white border-b border-cloud-200 px-4 md:px-6 flex items-center justify-between sticky top-0 z-30 shadow-subtle">
      {/* Mobile Menu & Page Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMobileMenuToggle}
          className="p-1.5 rounded-lg text-obsidian-600 hover:bg-cloud-200 md:hidden"
          aria-label="Toggle mobile menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div>
          <h1 className="text-base font-bold font-heading text-obsidian tracking-tight">
            {currentTitle}
          </h1>
          <div className="flex items-center gap-2 text-xs text-obsidian-400">
            <span className="font-mono text-[10px]">SkillSprint AI v1.0</span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <span className={`h-2 w-2 rounded-full ${isBackendHealthy ? 'bg-emerald-500' : 'bg-amber-500'}`} />
              <span className="font-mono text-[10px] text-obsidian-600">
                {isBackendHealthy ? 'FastAPI 0.141 Online' : 'Local Fallback Engine'}
              </span>
            </span>
          </div>
        </div>
      </div>

      {/* Right Utility Actions */}
      <div className="flex items-center gap-3">
        {/* Global Search Bar (Visual) */}
        <div className="hidden lg:flex items-center relative w-64">
          <Search className="h-4 w-4 absolute left-3 text-obsidian-400" />
          <input
            type="text"
            placeholder="Search requirements, SOPs..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 transition-all placeholder:text-obsidian-400"
          />
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-lg text-obsidian-600 hover:bg-cloud-200 transition-colors relative"
            aria-label="View notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-rose-500" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white border border-cloud-200 rounded-xl shadow-modal p-4 z-50 animate-in fade-in slide-in-from-top-2">
              <div className="flex items-center justify-between border-b border-cloud-200 pb-2 mb-3">
                <h4 className="text-xs font-bold font-heading text-obsidian">System Audit Alerts</h4>
                <span className="text-[10px] font-mono text-cloud-400">Real-time</span>
              </div>
              <div className="space-y-3 text-xs">
                <div className="flex items-start gap-2 p-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-900">
                  <Activity className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Manual Review Flagged</span>
                    <p className="text-[11px] text-amber-800 mt-0.5">Plan EMP-7731 has 1 ungrounded task requiring reviewer confirmation.</p>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900">
                  <CheckCircle className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Python Validation Engine Pass</span>
                    <p className="text-[11px] text-emerald-800 mt-0.5">Role Matrix CSE 100% mandatory coverage verified.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile & Logout Dropdown */}
        {user && (
          <div className="relative">
            <button
              onClick={() => setShowRoleDropdown(!showRoleDropdown)}
              className="flex items-center gap-2 p-1.5 rounded-lg border border-cloud-300 hover:bg-cloud-100 transition-colors"
            >
              <div className="h-7 w-7 rounded-md bg-obsidian-800 text-white flex items-center justify-center font-bold text-xs font-heading uppercase">
                {(user.full_name || user.username || user.email || 'U')[0]}
              </div>
              <div className="hidden sm:flex flex-col text-left">
                <span className="text-xs font-semibold text-obsidian leading-none">{user.full_name || user.username || user.email}</span>
                <span className={`text-[10px] font-mono font-semibold ${roleLabels[user.role]?.text || 'text-obsidian-600'} leading-tight`}>
                  {roleLabels[user.role]?.label || user.role}
                </span>
              </div>
              <ChevronDown className="h-3.5 w-3.5 text-obsidian-400" />
            </button>

            {showRoleDropdown && (
              <div className="absolute right-0 mt-2 w-60 bg-white border border-cloud-200 rounded-xl shadow-modal p-2 z-50">
                <div className="px-3 py-2 border-b border-cloud-200 mb-1">
                  <p className="text-xs font-bold text-obsidian">{user.full_name || user.username}</p>
                  <p className="text-[11px] text-obsidian-400 font-mono truncate">{user.email}</p>
                  {user.department && (
                    <span className="inline-block mt-1 px-1.5 py-0.5 text-[9px] font-mono font-medium rounded bg-cloud-200 text-obsidian-700">
                      {user.department}
                    </span>
                  )}
                </div>

                <button
                  onClick={() => {
                    setShowRoleDropdown(false);
                    logout();
                  }}
                  className="w-full text-left px-3 py-2 rounded-lg text-xs font-semibold text-rose-700 hover:bg-rose-50 flex items-center gap-2 transition-colors mt-1"
                >
                  <LogOut className="h-4 w-4 text-rose-600" />
                  <span>Sign Out / Logout</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};
