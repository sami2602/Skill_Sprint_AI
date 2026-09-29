import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ReviewQueueItem } from '../types';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ClipboardList, ShieldAlert, CheckCircle2, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const ReviewPage: React.FC = () => {
  const { user } = useAuth();
  const [reviews, setReviews] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState<ReviewQueueItem | null>(null);

  // Review Action Form State
  const [actionComments, setActionComments] = useState('');
  const [overrideReason, setOverrideReason] = useState('');
  const [isOverride, setIsOverride] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadQueue();
  }, []);

  async function loadQueue() {
    try {
      const q = await api.getReviewQueue();
      setReviews(q);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const handleActionSubmit = async (action: 'APPROVE' | 'REJECT' | 'REVISE') => {
    if (!selectedReview) return;
    if (isOverride && !overrideReason.trim()) {
      alert('Mandatory override reason is required when overriding system verification findings.');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.submitReviewAction(selectedReview.id, action, actionComments, isOverride ? overrideReason : undefined);
      setReviews(prev =>
        prev.map(r => (r.id === selectedReview.id ? { ...r, status: action === 'APPROVE' ? 'APPROVED' : 'REJECTED' } : r))
      );
      setSelectedReview(null);
      setActionComments('');
      setOverrideReason('');
      setIsOverride(false);
    } catch (err) {
      alert('Submission failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <div className="p-6"><LoadingSkeleton type="table" rows={4} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold font-heading text-obsidian">Manual Review & Override Queue</h2>
        <p className="text-xs text-obsidian-400">
          Human-in-the-loop review for flagged ungrounded content, warnings, or policy overrides with mandatory audit trailing
        </p>
      </div>

      {/* Review Queue Table */}
      <div className="bg-white border border-cloud-200 rounded-xl overflow-hidden shadow-subtle">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-cloud-100 border-b border-cloud-200 text-obsidian-500 font-mono text-[10px] uppercase">
              <th className="p-3">Plan & Employee</th>
              <th className="p-3">Flagged Requirement</th>
              <th className="p-3">Flagged Reason</th>
              <th className="p-3">Severity</th>
              <th className="p-3">Queue Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cloud-200">
            {reviews.map(rev => (
              <tr key={rev.id} className="hover:bg-cloud-50 transition-colors">
                <td className="p-3 font-bold text-obsidian">
                  <span>{rev.employee_name}</span>
                  <span className="block text-[10px] font-mono text-obsidian-400">{rev.role_title} ({rev.plan_id})</span>
                </td>
                <td className="p-3 font-mono font-semibold text-electric-600">
                  {rev.requirement_id}: {rev.requirement_title}
                </td>
                <td className="p-3 text-obsidian-600 max-w-xs truncate">{rev.flagged_reason}</td>
                <td className="p-3">
                  <Badge variant={rev.severity === 'CRITICAL' || rev.severity === 'HIGH' ? 'danger' : 'warning'} size="sm">
                    {rev.severity}
                  </Badge>
                </td>
                <td className="p-3">
                  <Badge variant={rev.status === 'APPROVED' ? 'success' : rev.status === 'PENDING' ? 'warning' : 'danger'} size="sm">
                    {rev.status}
                  </Badge>
                </td>
                <td className="p-3 text-right">
                  <Button onClick={() => setSelectedReview(rev)} variant="primary" size="sm">
                    Inspect & Decide
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Review Action Modal */}
      {selectedReview && (
        <Modal
          isOpen={!!selectedReview}
          onClose={() => setSelectedReview(null)}
          title={`Review Inspection: ${selectedReview.requirement_id}`}
          subtitle={`Employee: ${selectedReview.employee_name} • Plan: ${selectedReview.plan_id}`}
          maxWidth="2xl"
        >
          <div className="space-y-4 text-xs">
            {/* Side-By-Side: Requirement vs Generated vs Evidence */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 rounded-xl bg-cloud-100 border border-cloud-200 space-y-2">
                <span className="text-[10px] font-mono font-bold text-obsidian-500 uppercase">GENERATED PLAN CONTENT</span>
                <p className="text-obsidian-800 font-mono text-[11px] p-2 bg-white rounded border border-cloud-200">
                  "{selectedReview.generated_content}"
                </p>
              </div>

              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 space-y-2">
                <span className="text-[10px] font-mono font-bold text-rose-700 uppercase">PYTHON ENGINE EVIDENCE</span>
                <p className="text-rose-900 font-mono text-[11px] p-2 bg-white rounded border border-rose-200">
                  "{selectedReview.validation_evidence}"
                </p>
              </div>
            </div>

            {/* Reviewer Action Form */}
            <div className="border-t border-cloud-200 pt-4 space-y-3">
              <div>
                <label className="block font-semibold text-obsidian mb-1">Reviewer Comments</label>
                <textarea
                  value={actionComments}
                  onChange={e => setActionComments(e.target.value)}
                  placeholder="Provide justification or instructions..."
                  rows={2}
                  className="w-full p-2 border border-cloud-300 rounded-lg bg-white"
                />
              </div>

              {/* Mandatory Override Toggle & Reason Field */}
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 space-y-3">
                <label className="flex items-center gap-2 font-semibold text-amber-900 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={isOverride}
                    onChange={e => setIsOverride(e.target.checked)}
                    className="rounded text-amber-600 focus:ring-amber-600 h-4 w-4"
                  />
                  <span>Execute Reviewer Override (Bypass Ground-Truth Finding)</span>
                </label>

                {isOverride && (
                  <div className="space-y-1">
                    <label className="block text-[11px] font-bold text-amber-900 uppercase">
                      Mandatory Override Reason (Required for Immutable Audit Trail)
                    </label>
                    <textarea
                      value={overrideReason}
                      onChange={e => setOverrideReason(e.target.value)}
                      placeholder="Specify explicit operational rationale for overriding system compliance rules..."
                      rows={2}
                      className="w-full p-2 border border-amber-300 rounded-lg bg-white font-sans text-xs text-amber-950"
                      required
                    />
                  </div>
                )}
              </div>

              {/* Decision Buttons */}
              <div className="flex justify-end gap-2 pt-2">
                <Button onClick={() => handleActionSubmit('REVISE')} variant="outline" size="sm" isLoading={isSubmitting}>
                  Request Revision
                </Button>
                <Button onClick={() => handleActionSubmit('REJECT')} variant="danger" size="sm" isLoading={isSubmitting}>
                  Reject Item
                </Button>
                <Button onClick={() => handleActionSubmit('APPROVE')} variant="primary" size="sm" isLoading={isSubmitting}>
                  Approve Item
                </Button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
