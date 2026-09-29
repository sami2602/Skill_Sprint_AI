import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { RequirementItem } from '../types';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { Search, Filter, ShieldAlert, FileText, CheckCircle2 } from 'lucide-react';

export const RequirementsPage: React.FC = () => {
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [mandatoryOnly, setMandatoryOnly] = useState(false);
  const [selectedReq, setSelectedReq] = useState<RequirementItem | null>(null);

  useEffect(() => {
    async function loadReqs() {
      try {
        const reqs = await api.getRequirements();
        setRequirements(reqs);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadReqs();
  }, []);

  const rolesList = Array.from(new Set(requirements.flatMap(r => r.target_roles)));
  const categoriesList = Array.from(new Set(requirements.map(r => r.category)));

  const filtered = requirements.filter(req => {
    const matchesSearch =
      req.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      req.requirement_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      req.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'ALL' || req.target_roles.includes(selectedRole);
    const matchesCategory = selectedCategory === 'ALL' || req.category === selectedCategory;
    const matchesMandatory = !mandatoryOnly || req.is_mandatory;
    return matchesSearch && matchesRole && matchesCategory && matchesMandatory;
  });

  if (loading) return <div className="p-6"><LoadingSkeleton type="table" rows={6} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-xl font-bold font-heading text-obsidian">Role Requirement Matrix Inventory</h2>
        <p className="text-xs text-obsidian-400">Database ground-truth requirement items extracted from validated corporate SOPs</p>
      </div>

      {/* Filter Controls Bar */}
      <div className="bg-white p-4 rounded-xl border border-cloud-200 shadow-subtle flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[240px]">
          <div className="relative flex-1">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-obsidian-400" />
            <input
              type="text"
              placeholder="Search by ID, title, or description..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian focus:ring-2 focus:ring-electric-600 outline-none"
            />
          </div>

          <select
            value={selectedRole}
            onChange={e => setSelectedRole(e.target.value)}
            className="p-1.5 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian font-medium"
          >
            <option value="ALL">All Roles ({rolesList.length})</option>
            {rolesList.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>

          <select
            value={selectedCategory}
            onChange={e => setSelectedCategory(e.target.value)}
            className="p-1.5 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian font-medium"
          >
            <option value="ALL">All Categories</option>
            {categoriesList.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <label className="flex items-center gap-2 text-xs font-semibold text-obsidian cursor-pointer select-none">
          <input
            type="checkbox"
            checked={mandatoryOnly}
            onChange={e => setMandatoryOnly(e.target.checked)}
            className="rounded text-electric-600 focus:ring-electric-600 h-4 w-4"
          />
          <span>Show Mandatory Items Only</span>
        </label>
      </div>

      {/* Requirement Inventory Table */}
      <div className="bg-white border border-cloud-200 rounded-xl overflow-hidden shadow-subtle">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-cloud-100 border-b border-cloud-200 text-obsidian-500 font-mono text-[10px] uppercase">
              <th className="p-3">Req ID</th>
              <th className="p-3">Title & Category</th>
              <th className="p-3">Type</th>
              <th className="p-3">Target Roles</th>
              <th className="p-3">Priority</th>
              <th className="p-3">Due Stage</th>
              <th className="p-3">Source Citation</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cloud-200">
            {filtered.map(req => (
              <tr key={req.id} className="hover:bg-cloud-50 transition-colors">
                <td className="p-3 font-mono font-bold text-electric-600">{req.requirement_id}</td>
                <td className="p-3">
                  <span className="font-bold text-obsidian block">{req.title}</span>
                  <span className="text-[11px] text-obsidian-400">{req.category}</span>
                </td>
                <td className="p-3">
                  <Badge variant={req.is_mandatory ? 'danger' : 'neutral'} size="sm">
                    {req.is_mandatory ? 'Mandatory' : 'Optional'}
                  </Badge>
                </td>
                <td className="p-3 text-obsidian-600 max-w-[180px] truncate">{req.target_roles.join(', ')}</td>
                <td className="p-3">
                  <Badge variant={req.priority === 'CRITICAL' ? 'danger' : req.priority === 'HIGH' ? 'warning' : 'info'} size="sm">
                    {req.priority}
                  </Badge>
                </td>
                <td className="p-3 font-mono text-obsidian-600">{req.due_stage}</td>
                <td className="p-3 font-mono text-[11px] text-obsidian-500">
                  {req.source_document_id} ({req.source_section_id})
                </td>
                <td className="p-3 text-right">
                  <Button onClick={() => setSelectedReq(req)} variant="outline" size="sm">
                    Inspect
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {selectedReq && (
        <Modal
          isOpen={!!selectedReq}
          onClose={() => setSelectedReq(null)}
          title={`Requirement: ${selectedReq.requirement_id}`}
          subtitle={selectedReq.title}
          maxWidth="2xl"
        >
          <div className="space-y-4 text-xs">
            <div className="p-4 rounded-xl bg-cloud-100 border border-cloud-200 space-y-2">
              <p className="text-obsidian-700 leading-relaxed font-sans">{selectedReq.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg border border-cloud-200 bg-white">
                <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Mandatory Status</span>
                <Badge variant={selectedReq.is_mandatory ? 'danger' : 'neutral'} size="sm" className="mt-1">
                  {selectedReq.is_mandatory ? 'Mandatory Requirement' : 'Optional Requirement'}
                </Badge>
              </div>

              <div className="p-3 rounded-lg border border-cloud-200 bg-white">
                <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Assessment Method</span>
                <span className="font-semibold text-obsidian mt-1 block">{selectedReq.assessment_type}</span>
              </div>
            </div>

            {/* Citation Metadata */}
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-2">
              <div className="flex items-center gap-2 text-emerald-800 font-bold font-heading text-xs">
                <FileText className="h-4 w-4 text-emerald-600" />
                Source Traceability Citation
              </div>
              <div className="font-mono text-[11px] text-emerald-900 space-y-1">
                <p>Document ID: {selectedReq.source_document_id} (Version {selectedReq.version})</p>
                <p>Section Reference: {selectedReq.source_section_id}</p>
                <p>Page / Paragraph: {selectedReq.page_number ? `Page ${selectedReq.page_number}` : selectedReq.paragraph_ref}</p>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
