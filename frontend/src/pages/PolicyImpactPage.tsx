import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { PolicyImpactItem } from '../types';
import { PolicyDiffViewer } from '../components/policy/PolicyDiffViewer';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { GitPullRequest, AlertCircle } from 'lucide-react';

export const PolicyImpactPage: React.FC = () => {
  const [impacts, setImpacts] = useState<PolicyImpactItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [regenSuccessMsg, setRegenSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadImpact() {
      try {
        const data = await api.getPolicyImpact();
        setImpacts(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadImpact();
  }, []);

  const handleSelectiveRegenerate = async (docId: string) => {
    setIsRegenerating(true);
    setRegenSuccessMsg(null);
    try {
      const res = await api.triggerSelectiveRegenerate(docId);
      setRegenSuccessMsg(`Selective regeneration successfully completed for ${res.regenerated_plans_count} affected onboarding plans. Unchanged modules were preserved.`);
    } catch (e) {
      alert('Regeneration failed');
    } finally {
      setIsRegenerating(false);
    }
  };

  if (loading) return <div className="p-6"><LoadingSkeleton type="card" rows={2} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold font-heading text-obsidian">Policy Version Impact Analysis & Selective Regeneration</h2>
        <p className="text-xs text-obsidian-400">
          Identifies affected onboarding modules, tasks, and employees when policy versions update (e.g. SOP v1.0 → v2.0)
        </p>
      </div>

      {regenSuccessMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
          <GitPullRequest className="h-4 w-4 text-emerald-600 shrink-0" />
          <span className="font-semibold">{regenSuccessMsg}</span>
        </div>
      )}

      {/* Policy Transition Diff Viewer */}
      <div className="space-y-6">
        {impacts.map(imp => (
          <PolicyDiffViewer
            key={imp.document_id}
            impact={imp}
            onSelectiveRegenerate={() => handleSelectiveRegenerate(imp.document_id)}
            isRegenerating={isRegenerating}
          />
        ))}
      </div>
    </div>
  );
};
