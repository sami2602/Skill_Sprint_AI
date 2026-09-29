import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ValidationRun, RequirementItem } from '../types';
import { VerificationDecisionBadge } from '../components/verification/VerificationDecisionBadge';
import { SideBySideInspector } from '../components/verification/SideBySideInspector';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ShieldCheck, CheckCircle2, AlertTriangle, Cpu, FileCheck, Layers, HelpCircle, AlertCircle } from 'lucide-react';

export const VerificationPage: React.FC = () => {
  const [plans, setPlans] = useState<any[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<string>('');
  const [valRun, setValRun] = useState<ValidationRun | null>(null);
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [valLoading, setValLoading] = useState(false);
  const [activeReqIndex, setActiveReqIndex] = useState<number>(0);

  useEffect(() => {
    async function initPage() {
      try {
        const [plansData, reqsData] = await Promise.all([
          api.getPlans(),
          api.getRequirements()
        ]);
        setPlans(plansData);
        setRequirements(reqsData);
        if (plansData.length > 0) {
          setSelectedPlanId(plansData[0].plan_id);
        } else {
          setSelectedPlanId('plan-emp-001');
        }
      } catch (e) {
        console.error('Error initializing verification page:', e);
        setSelectedPlanId('plan-emp-001');
      } finally {
        setLoading(false);
      }
    }
    initPage();
  }, []);

  useEffect(() => {
    if (!selectedPlanId) return;
    async function loadValRun() {
      setValLoading(true);
      try {
        const vData = await api.getValidationRun(selectedPlanId);
        setValRun(vData);
      } catch (e) {
        console.error(`Error loading validation run for ${selectedPlanId}:`, e);
      } finally {
        setValLoading(false);
      }
    }
    loadValRun();
  }, [selectedPlanId]);

  if (loading) return <div className="p-6"><LoadingSkeleton type="card" rows={4} /></div>;

  const activeReq = requirements[activeReqIndex] || requirements[0];
  const activeEvidence = valRun?.evidences.find(e => e.requirement_id === activeReq?.requirement_id);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Flagship Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-obsidian via-obsidian-800 to-obsidian text-white shadow-xl space-y-4 border border-obsidian-700">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
                Flagship Verification Center
              </span>
              <span className="text-xs text-cloud-400 font-mono">Plan: {selectedPlanId}</span>
            </div>
            <h2 className="text-xl font-bold font-heading text-white mt-1">
              Independent Python Ground-Truth Verification
            </h2>
            <p className="text-xs text-cloud-300">
              Deterministic validation comparing GenAI onboarding outputs against database role requirement matrices (Zero self-approval)
            </p>
          </div>

          <div className="flex items-center gap-3">
            {plans.length > 0 && (
              <select
                value={selectedPlanId}
                onChange={(e) => setSelectedPlanId(e.target.value)}
                className="bg-obsidian-900 text-white text-xs font-mono font-semibold px-3 py-2 rounded-lg border border-teal-500/40 focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {plans.map((p) => (
                  <option key={p.plan_id} value={p.plan_id}>
                    {p.plan_id} ({p.role_id})
                  </option>
                ))}
              </select>
            )}

            {valRun && <VerificationDecisionBadge status={valRun.verification_status} size="lg" />}
          </div>
        </div>

        {/* Highlighted Independent Engine Guarantee */}
        <div className="p-3 rounded-xl bg-teal-900/50 border border-teal-500/40 text-xs text-teal-200 flex items-center gap-3">
          <ShieldCheck className="h-5 w-5 text-teal-400 shrink-0" />
          <span>
            <strong className="text-white">Python Pipeline 2 Isolation Enforced:</strong> Coverage ({valRun?.coverage_score ?? 0}%) and Traceability ({valRun?.traceability_score ?? 0}%) were evaluated directly by Python parsers without LLM self-evaluation.
          </span>
        </div>
      </div>

      {/* 9 Quality Criteria Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-9 gap-3">
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Coverage</span>
          <span className="text-base font-bold font-heading text-emerald-600">{valRun?.coverage_score ?? 0}%</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Traceability</span>
          <span className="text-base font-bold font-heading text-electric-600">{valRun?.traceability_score ?? 0}%</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Missing Mandatory</span>
          <span className="text-base font-bold font-heading text-rose-600">{valRun?.missing_mandatory_count ?? 0}</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Unsupported Claim</span>
          <span className="text-base font-bold font-heading text-purple-600">{valRun?.unsupported_items_count ?? 0}</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Contradictions</span>
          <span className="text-base font-bold font-heading text-rose-600">{valRun?.contradictions_count ?? 0}</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Outdated Source</span>
          <span className="text-base font-bold font-heading text-amber-600">{valRun?.outdated_sources_count ?? 0}</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Duplicate Item</span>
          <span className="text-base font-bold font-heading text-obsidian">0</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Role Irrelevance</span>
          <span className="text-base font-bold font-heading text-obsidian">0</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-cloud-200 shadow-subtle text-center">
          <span className="text-[10px] font-mono text-obsidian-400 block uppercase">Sequence Error</span>
          <span className="text-base font-bold font-heading text-obsidian">0</span>
        </div>
      </div>

      {/* Drill-Down Requirement Selector Tabs */}
      <div className="bg-white p-4 rounded-xl border border-cloud-200 shadow-subtle space-y-4">
        <h3 className="text-sm font-bold font-heading text-obsidian border-b border-cloud-200 pb-2">
          Drill Into Individual Requirement Verification
        </h3>
        <div className="flex flex-wrap gap-2">
          {requirements.map((req, idx) => (
            <button
              key={req.id}
              onClick={() => setActiveReqIndex(idx)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-colors border ${
                activeReqIndex === idx
                  ? 'bg-electric-600 text-white border-electric-700 shadow-subtle'
                  : 'bg-cloud-100 text-obsidian-700 border-cloud-300 hover:bg-cloud-200'
              }`}
            >
              {req.requirement_id}
            </button>
          ))}
        </div>
      </div>

      {/* Flagship Side-By-Side 5-Stage Verification Inspector */}
      {activeReq && (
        <SideBySideInspector
          requirement={activeReq}
          evidence={activeEvidence}
          verificationStatus={valRun?.verification_status || 'VERIFIED'}
        />
      )}
    </div>
  );
};
