import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { RoleItem } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ShieldCheck, CheckCircle2, ListCheck } from 'lucide-react';

export const RolesPage: React.FC = () => {
  const [roles, setRoles] = useState<RoleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [matrixLoading, setMatrixLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState<RoleItem | null>(null);
  const [matrixItems, setMatrixItems] = useState<any[]>([]);

  useEffect(() => {
    async function loadRoles() {
      try {
        const rList = await api.getRoles();
        setRoles(rList);
        if (rList.length > 0) {
          setSelectedRole(rList[0]);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadRoles();
  }, []);

  useEffect(() => {
    if (!selectedRole?.role_id) return;
    const roleId = selectedRole.role_id;
    async function fetchMatrix() {
      setMatrixLoading(true);
      try {
        const detail = await api.getRoleDetail(roleId);
        setMatrixItems(detail.requirement_matrix || []);
      } catch (e) {
        console.error(`Error fetching matrix for ${roleId}:`, e);
        setMatrixItems([]);
      } finally {
        setMatrixLoading(false);
      }
    }
    fetchMatrix();
  }, [selectedRole?.role_id]);

  if (loading) return <div className="p-6"><LoadingSkeleton type="card" rows={3} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-xl font-bold font-heading text-obsidian">Organizational Role Architecture & Requirement Matrix</h2>
        <p className="text-xs text-obsidian-400">Database Role Requirement Matrix definitions mapping mandatory policy standards per job function</p>
      </div>

      {/* Main Grid: Left Role List & Right Role Matrix Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Role List Selection */}
        <div className="space-y-3">
          {roles.map(role => (
            <div
              key={role.id}
              onClick={() => setSelectedRole(role)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                selectedRole?.id === role.id
                  ? 'bg-white border-electric-600 shadow-md ring-2 ring-electric-600/20'
                  : 'bg-white border-cloud-200 hover:border-cloud-300 shadow-subtle'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] text-electric-600 font-bold">{role.role_id}</span>
                <Badge variant={role.coverage_percentage === 100 ? 'success' : 'warning'} size="sm">
                  {role.coverage_percentage}% Coverage
                </Badge>
              </div>
              <h3 className="text-sm font-bold font-heading text-obsidian mt-1">{role.title}</h3>
              <p className="text-xs text-obsidian-400 mt-0.5">{role.department}</p>

              <div className="mt-3 flex items-center justify-between text-xs pt-2 border-t border-cloud-200">
                <span className="text-obsidian-500 font-mono text-[11px]">
                  <span className="font-bold text-obsidian">{role.mandatory_requirements_count}</span> Mandatory / {role.total_requirements_count} Total
                </span>
                <span className="text-electric-600 text-xs font-semibold">Inspect Matrix →</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right: Selected Role Matrix Breakdown */}
        {selectedRole && (
          <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-cloud-200 shadow-subtle space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-cloud-200">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-electric-600 font-bold">{selectedRole.role_id}</span>
                  <Badge variant="info" size="sm">{selectedRole.department}</Badge>
                </div>
                <h3 className="text-lg font-bold font-heading text-obsidian mt-1">{selectedRole.title}</h3>
                <p className="text-xs text-obsidian-400">{selectedRole.description}</p>
              </div>

              <div className="text-right bg-cloud-100 p-3 rounded-xl border border-cloud-200">
                <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Matrix Coverage</span>
                <span className="text-xl font-bold font-heading text-emerald-600">{selectedRole.coverage_percentage}%</span>
              </div>
            </div>

            {/* Required Skills & Competencies */}
            <div>
              <h4 className="text-xs font-bold font-heading text-obsidian mb-2">Required Skills & Policy Domain Competencies</h4>
              <div className="flex flex-wrap gap-2">
                {(selectedRole.required_skills || []).map((skill, idx) => (
                  <span key={idx} className="px-2.5 py-1 rounded-md bg-cloud-100 border border-cloud-200 text-obsidian-700 text-xs font-medium">
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Matrix Rule Summary */}
            <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 space-y-2">
              <div className="flex items-center gap-2 text-teal-900 font-bold text-xs font-heading">
                <ShieldCheck className="h-4 w-4 text-teal-600" />
                Python Engine Requirement Matrix Rule Standard
              </div>
              <p className="text-xs text-teal-800 leading-relaxed">
                All onboarding plans generated for {selectedRole.title} must include all {selectedRole.mandatory_requirements_count} mandatory policy items. Failure to include any mandatory item triggers an automatic <span className="font-mono font-bold">INCOMPLETE</span> verification status.
              </p>
            </div>

            {/* Detailed Requirement Matrix Table */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold font-heading text-obsidian flex items-center gap-2">
                  <ListCheck className="h-4 w-4 text-electric-600" />
                  Role Requirement Matrix Mapping ({matrixItems.length} Requirements)
                </h4>
                {matrixLoading && <span className="text-xs text-cloud-400 animate-pulse font-mono">Loading matrix...</span>}
              </div>

              {matrixItems.length > 0 ? (
                <div className="overflow-x-auto border border-cloud-200 rounded-xl">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-cloud-50 text-obsidian-600 font-mono border-b border-cloud-200 uppercase text-[10px]">
                      <tr>
                        <th className="p-3">Req ID</th>
                        <th className="p-3">Requirement Title</th>
                        <th className="p-3">Compliance Type</th>
                        <th className="p-3">Priority</th>
                        <th className="p-3">Due Stage</th>
                        <th className="p-3">Source Citation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-cloud-100">
                      {matrixItems.map((item, idx) => (
                        <tr key={item.mapping_id || idx} className="hover:bg-cloud-50/60 transition-colors">
                          <td className="p-3 font-mono font-bold text-electric-600">{item.requirement_id}</td>
                          <td className="p-3 font-medium text-obsidian max-w-xs truncate" title={item.title}>
                            {item.title}
                          </td>
                          <td className="p-3">
                            {item.is_mandatory ? (
                              <Badge variant="success" size="sm">Mandatory</Badge>
                            ) : (
                              <Badge variant="neutral" size="sm">Optional</Badge>
                            )}
                          </td>
                          <td className="p-3">
                            <span className={`font-mono text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                              item.priority === 'CRITICAL' ? 'bg-rose-100 text-rose-700' :
                              item.priority === 'HIGH' ? 'bg-amber-100 text-amber-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {item.priority || 'MEDIUM'}
                            </span>
                          </td>
                          <td className="p-3 font-mono text-obsidian-600">{item.due_stage || 'Day 1'}</td>
                          <td className="p-3 font-mono text-cloud-500 text-[11px]">
                            {item.doc_id || 'DOC-POL01'} {item.section_ref ? `§ ${item.section_ref}` : ''}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                !matrixLoading && (
                  <div className="p-4 rounded-xl bg-cloud-50 border border-cloud-200 text-center text-xs text-cloud-500">
                    No requirement matrix items mapped for this role yet.
                  </div>
                )
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
