import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { EmployeeItem } from '../types';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { Users, UserCheck, ShieldCheck, Clock, ArrowRight } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const EmployeesPage: React.FC = () => {
  const [employees, setEmployees] = useState<EmployeeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmp, setSelectedEmp] = useState<EmployeeItem | null>(null);

  useEffect(() => {
    async function loadEmp() {
      try {
        const eList = await api.getEmployees();
        setEmployees(eList);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadEmp();
  }, []);

  if (loading) return <div className="p-6"><LoadingSkeleton type="table" rows={4} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold font-heading text-obsidian">Employee Onboarding Roster</h2>
          <p className="text-xs text-obsidian-400">Track active onboarding progress, assigned reviewers, and ground-truth verification status</p>
        </div>

        <NavLink to="/generation">
          <Button variant="primary" leftIcon={<UserCheck className="h-4 w-4" />}>
            New Employee Onboarding Plan
          </Button>
        </NavLink>
      </div>

      {/* Roster Table */}
      <div className="bg-white border border-cloud-200 rounded-xl overflow-hidden shadow-subtle">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-cloud-100 border-b border-cloud-200 text-obsidian-500 font-mono text-[10px] uppercase">
              <th className="p-3">Employee Name</th>
              <th className="p-3">Role & Dept</th>
              <th className="p-3">Experience</th>
              <th className="p-3">Current Stage</th>
              <th className="p-3">Progress</th>
              <th className="p-3">Verification Status</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cloud-200">
            {employees.map(emp => (
              <tr key={emp.id} className="hover:bg-cloud-50 transition-colors">
                <td className="p-3 font-bold text-obsidian">
                  <span>{emp.name}</span>
                  <span className="block text-[10px] font-mono text-obsidian-400">{emp.email}</span>
                </td>
                <td className="p-3">
                  <span className="font-semibold text-obsidian block">{emp.role_title}</span>
                  <span className="text-[11px] text-obsidian-400">{emp.department}</span>
                </td>
                <td className="p-3 font-mono text-obsidian-600">{emp.experience_level}</td>
                <td className="p-3 font-mono text-obsidian-600">{emp.current_stage}</td>
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 bg-cloud-200 rounded-full overflow-hidden">
                      <div className="h-full bg-electric-600 rounded-full" style={{ width: `${emp.progress_percentage}%` }} />
                    </div>
                    <span className="font-mono font-bold text-xs">{emp.progress_percentage}%</span>
                  </div>
                </td>
                <td className="p-3">
                  <Badge variant={emp.onboarding_status === 'VERIFIED' ? 'success' : emp.onboarding_status === 'IN_PROGRESS' ? 'info' : 'warning'} size="sm">
                    {emp.onboarding_status}
                  </Badge>
                </td>
                <td className="p-3 text-right">
                  <Button onClick={() => setSelectedEmp(emp)} variant="outline" size="sm">
                    Profile Detail
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Employee Detail Modal */}
      {selectedEmp && (
        <Modal
          isOpen={!!selectedEmp}
          onClose={() => setSelectedEmp(null)}
          title={`Employee Profile: ${selectedEmp.name}`}
          subtitle={`${selectedEmp.role_title} • ${selectedEmp.department}`}
        >
          <div className="space-y-4 text-xs">
            <div className="p-4 rounded-xl bg-cloud-100 border border-cloud-200 grid grid-cols-2 gap-4">
              <div>
                <span className="text-[10px] font-mono text-obsidian-400 uppercase block">EMPLOYEE ID</span>
                <span className="font-mono font-bold text-obsidian">{selectedEmp.employee_id}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-obsidian-400 uppercase block">EXPERIENCE LEVEL</span>
                <span className="font-semibold text-obsidian">{selectedEmp.experience_level}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-obsidian-400 uppercase block">ASSIGNED PLAN</span>
                <span className="font-mono text-electric-600 font-bold">{selectedEmp.plan_id || 'plan-cse-9042'}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-obsidian-400 uppercase block">ASSIGNED REVIEWER</span>
                <span className="font-semibold text-obsidian">{selectedEmp.assigned_reviewer}</span>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-cloud-200">
              <NavLink to="/employee-portal">
                <Button variant="ai" size="sm" rightIcon={<ArrowRight className="h-3.5 w-3.5" />}>
                  Open Employee Portal Experience
                </Button>
              </NavLink>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
