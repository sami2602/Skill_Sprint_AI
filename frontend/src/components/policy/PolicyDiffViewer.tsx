import React from 'react';
import { PolicyImpactItem } from '../../types';
import { Badge } from '../common/Badge';
import { GitCompare, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

interface PolicyDiffViewerProps {
  impact: PolicyImpactItem;
  onSelectiveRegenerate?: () => void;
  isRegenerating?: boolean;
}

export const PolicyDiffViewer: React.FC<PolicyDiffViewerProps> = ({
  impact,
  onSelectiveRegenerate,
  isRegenerating = false
}) => {
  return (
    <div className="bg-white border border-cloud-200 rounded-xl p-6 shadow-subtle space-y-6">
      {/* Header Comparison Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-cloud-200">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="warning" size="sm">Policy Transition Detected</Badge>
            <span className="text-xs font-mono text-obsidian-400">Doc ID: {impact.document_id}</span>
          </div>
          <h3 className="text-base font-bold font-heading text-obsidian mt-1 flex items-center gap-2">
            {impact.filename}
          </h3>
        </div>

        <div className="flex items-center gap-3 bg-cloud-100 px-4 py-2 rounded-xl border border-cloud-200 font-mono text-xs">
          <span className="text-rose-700 font-bold bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
            v{impact.old_version} (Obsolete)
          </span>
          <ArrowRight className="h-4 w-4 text-obsidian-400" />
          <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            v{impact.new_version} (Active)
          </span>
        </div>
      </div>

      {/* Impact Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-3 rounded-lg bg-cloud-100 border border-cloud-200">
          <span className="text-[10px] font-mono text-obsidian-400 uppercase">Requirements Affected</span>
          <p className="text-lg font-bold font-heading text-obsidian">{impact.affected_requirements_count}</p>
        </div>
        <div className="p-3 rounded-lg bg-cloud-100 border border-cloud-200">
          <span className="text-[10px] font-mono text-obsidian-400 uppercase">Roles Impacted</span>
          <p className="text-lg font-bold font-heading text-obsidian">{impact.affected_roles.length}</p>
        </div>
        <div className="p-3 rounded-lg bg-cloud-100 border border-cloud-200">
          <span className="text-[10px] font-mono text-obsidian-400 uppercase">Employees Affected</span>
          <p className="text-lg font-bold font-heading text-obsidian">{impact.affected_employees_count}</p>
        </div>
        <div className="p-3 rounded-lg bg-cloud-100 border border-cloud-200">
          <span className="text-[10px] font-mono text-obsidian-400 uppercase">Plans Requiring Update</span>
          <p className="text-lg font-bold font-heading text-obsidian">{impact.affected_plans_count}</p>
        </div>
      </div>

      {/* Policy Change Summary List */}
      <div>
        <h4 className="text-xs font-bold font-heading text-obsidian mb-2 flex items-center gap-1.5">
          <GitCompare className="h-4 w-4 text-electric-600" />
          Key Policy Modifications Summary
        </h4>
        <ul className="space-y-2 text-xs text-obsidian-700">
          {impact.changes_summary.map((change, idx) => (
            <li key={idx} className="flex items-start gap-2 p-2 rounded-lg bg-cloud-50 border border-cloud-200">
              <span className="h-1.5 w-1.5 rounded-full bg-electric-600 shrink-0 mt-1.5" />
              <span>{change}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Selective Regeneration Action Footer */}
      <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-start gap-2.5 max-w-xl">
          <AlertCircle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="text-xs text-amber-900">
            <span className="font-bold">Selective Regeneration Guarantee:</span>
            <p className="mt-0.5 text-amber-800">
              Only modules mapped to obsolete v{impact.old_version} will be updated. All unaffected training modules remain unchanged and preserved.
            </p>
          </div>
        </div>

        {onSelectiveRegenerate && (
          <button
            onClick={onSelectiveRegenerate}
            disabled={isRegenerating}
            className="px-4 py-2 rounded-lg bg-amber-600 text-white font-medium text-xs hover:bg-amber-700 active:bg-amber-800 transition-colors shadow-subtle flex items-center gap-2 disabled:opacity-50"
          >
            {isRegenerating ? (
              <>
                <span className="animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full" />
                <span>Regenerating Affected Modules...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="h-4 w-4" />
                <span>Execute Selective Regeneration</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};
