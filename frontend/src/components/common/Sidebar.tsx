import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  ListCheck,
  ShieldCheck,
  Users,
  Sparkles,
  CheckCircle2,
  ClipboardList,
  GitPullRequest,
  BarChart3,
  FileSpreadsheet,
  UserCheck,
  ChevronLeft,
  ChevronRight,
  LogOut
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const { user, logout } = useAuth();

  const navItems = [
    { label: 'Executive Dashboard', path: '/', icon: LayoutDashboard, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Document Inventory', path: '/documents', icon: FileText, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Requirement Matrix', path: '/requirements', icon: ListCheck, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Role Architecture', path: '/roles', icon: ShieldCheck, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Employee Roster', path: '/employees', icon: Users, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'GenAI Plan Generator', path: '/generation', icon: Sparkles, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Verification Center', path: '/verification', icon: CheckCircle2, flagship: true, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Manual Review Queue', path: '/review', icon: ClipboardList, badge: '3', roleAccess: ['ADMIN', 'REVIEWER'] },
    { label: 'Policy Impact Analysis', path: '/policy-impact', icon: GitPullRequest, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'System Analytics', path: '/analytics', icon: BarChart3, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Compliance Reports', path: '/reports', icon: FileSpreadsheet, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER'] },
    { label: 'Employee Portal', path: '/employee-portal', icon: UserCheck, employeeHighlight: true, roleAccess: ['ADMIN', 'REVIEWER', 'MANAGER', 'TRAINING_MANAGER', 'EMPLOYEE'] }
  ];

  const userRole = user?.role || 'EMPLOYEE';
  const filteredItems = navItems.filter(item => item.roleAccess.includes(userRole));

  return (
    <aside
      className={`fixed top-0 left-0 bottom-0 z-40 bg-obsidian text-cloud flex flex-col transition-all duration-300 border-r border-obsidian-700 shadow-xl ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-obsidian-700 shrink-0">
        {!collapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="h-8 w-8 rounded-lg bg-electric-600 flex items-center justify-center text-white font-heading font-extrabold text-lg shadow-subtle shrink-0">
              S
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-heading font-bold text-sm tracking-tight text-white truncate">
                SkillSprint <span className="text-electric-500 font-extrabold">AI</span>
              </span>
              <span className="text-[10px] text-cloud-400 font-mono tracking-wider uppercase truncate">
                Verified Intelligence
              </span>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="mx-auto h-8 w-8 rounded-lg bg-electric-600 flex items-center justify-center text-white font-heading font-bold text-lg">
            S
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1 rounded-md text-cloud-400 hover:text-white hover:bg-obsidian-700 transition-colors hidden md:block"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {filteredItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 group relative ${
                isActive
                  ? 'bg-electric-600 text-white font-semibold shadow-subtle'
                  : item.flagship
                  ? 'text-teal-400 hover:bg-obsidian-700 hover:text-teal-300'
                  : item.employeeHighlight
                  ? 'text-ai-300 hover:bg-obsidian-700 hover:text-ai-200'
                  : 'text-cloud-300 hover:bg-obsidian-700 hover:text-white'
              }`
            }
          >
            <item.icon
              className={`h-4 w-4 shrink-0 transition-transform duration-150 ${
                item.flagship ? 'text-teal-400 group-hover:scale-110' : ''
              }`}
            />
            {!collapsed && (
              <span className="truncate flex-1 font-sans">{item.label}</span>
            )}

            {!collapsed && item.flagship && (
              <span className="px-1.5 py-0.5 text-[9px] font-mono font-bold uppercase rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                Core
              </span>
            )}

            {!collapsed && item.badge && (
              <span className="px-1.5 py-0.5 text-[10px] font-mono font-bold rounded-full bg-rose-500 text-white">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </div>

      {/* Footer Logout Action */}
      <div className="p-2 border-t border-obsidian-700 shrink-0">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-rose-400 hover:bg-rose-950/40 hover:text-rose-300 transition-colors"
          title="Sign Out / Logout"
        >
          <LogOut className="h-4 w-4 shrink-0 text-rose-400" />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  );
};
