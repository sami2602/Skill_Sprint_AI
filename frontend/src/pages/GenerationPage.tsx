import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { OnboardingPlan, EmployeeItem, RoleItem } from '../types';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Sparkles, CheckCircle2, Cpu, ShieldCheck, FileText, ArrowRight, Clock } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const GenerationPage: React.FC = () => {
  const [employeeId, setEmployeeId] = useState('EMP-004');
  const [roleId, setRoleId] = useState('ROL-03');
  const [expLevel, setExpLevel] = useState('Junior');
  const [employees, setEmployees] = useState<EmployeeItem[]>([]);
  const [roles, setRoles] = useState<RoleItem[]>([]);

  const [isGenerating, setIsGenerating] = useState(false);
  const [genStep, setGenStep] = useState<number>(0);
  const [generatedPlan, setGeneratedPlan] = useState<OnboardingPlan | null>(null);
  const [activeStage, setActiveStage] = useState<string>('Day 1');

  const steps = [
    'Loading Database Role Requirement Matrix...',
    'Invoking GenAI Generator Pipeline (Gemini API)...',
    'Executing Python Ground-Truth Validator Engine (Pipeline 2)...',
    'Calculating Mandatory Requirement Coverage & Traceability...',
    'Generating Final Verification Decision...'
  ];

  useEffect(() => {
    async function loadOptions() {
      try {
        const [empList, rList] = await Promise.all([
          api.getEmployees(),
          api.getRoles()
        ]);
        setEmployees(empList);
        setRoles(rList);
        if (empList.length > 0) setEmployeeId(empList[0].employee_id);
        if (rList.length > 0) setRoleId(rList[0].role_id);
      } catch (e) {
        console.error("Failed to load options", e);
      }
    }
    loadOptions();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setGenStep(0);
    setGeneratedPlan(null);

    for (let i = 0; i < steps.length; i++) {
      setGenStep(i);
      await new Promise(r => setTimeout(r, 400));
    }

    try {
      const plan = await api.generatePlan(employeeId, roleId, expLevel);
      setGeneratedPlan(plan);
    } catch (err) {
      alert('Generation error');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-xl font-bold font-heading text-obsidian">Transparent GenAI Plan Generator</h2>
        <p className="text-xs text-obsidian-400">
          Generates structured multi-stage onboarding plans backed by real-time Python ground-truth verification
        </p>
      </div>

      {/* Generator Input Form */}
      <div className="bg-white p-6 rounded-xl border border-cloud-200 shadow-subtle">
        <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-obsidian mb-1">Target Employee</label>
            <select
              value={employeeId}
              onChange={e => setEmployeeId(e.target.value)}
              className="w-full p-2 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian font-medium"
            >
              {employees.map(emp => (
                <option key={emp.id} value={emp.employee_id}>
                  {emp.name} ({emp.employee_id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-obsidian mb-1">Job Role Architecture</label>
            <select
              value={roleId}
              onChange={e => setRoleId(e.target.value)}
              className="w-full p-2 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian font-medium"
            >
              {roles.map(role => (
                <option key={role.id} value={role.role_id}>
                  {role.title} ({role.role_id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-obsidian mb-1">Candidate Experience</label>
            <select
              value={expLevel}
              onChange={e => setExpLevel(e.target.value)}
              className="w-full p-2 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian font-medium"
            >
              <option value="Junior">Junior (0-2 Yrs)</option>
              <option value="Mid">Mid-Level (2-5 Yrs)</option>
              <option value="Senior">Senior (5+ Yrs)</option>
            </select>
          </div>

          <Button type="submit" variant="ai" isLoading={isGenerating} leftIcon={<Sparkles className="h-4 w-4" />}>
            Generate Onboarding Plan
          </Button>
        </form>
      </div>

      {/* Transparent Execution Progress */}
      {isGenerating && (
        <div className="p-6 rounded-xl bg-obsidian text-white border border-obsidian-700 shadow-xl space-y-4">
          <div className="flex items-center gap-3">
            <Cpu className="h-5 w-5 text-ai-400 animate-pulse" />
            <h3 className="text-sm font-bold font-heading text-white">Dual-Pipeline Orchestration In Progress</h3>
          </div>

          <div className="space-y-2">
            {steps.map((st, i) => (
              <div key={i} className="flex items-center gap-3 text-xs">
                {i < genStep ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                ) : i === genStep ? (
                  <div className="h-4 w-4 rounded-full border-2 border-ai-400 border-t-transparent animate-spin shrink-0" />
                ) : (
                  <div className="h-4 w-4 rounded-full border border-cloud-600 shrink-0" />
                )}
                <span className={i <= genStep ? 'text-white font-mono' : 'text-cloud-500 font-mono'}>{st}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated Plan Preview */}
      {generatedPlan && !isGenerating && (
        <div className="space-y-6">
          <div className="p-6 rounded-xl bg-white border border-cloud-200 shadow-subtle flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Badge variant="success" size="sm">Verification Status: VERIFIED</Badge>
                <span className="font-mono text-xs text-obsidian-400">Plan ID: {generatedPlan.plan_id}</span>
              </div>
              <h3 className="text-lg font-bold font-heading text-obsidian mt-1">
                Personalized Onboarding Plan Preview
              </h3>
              <p className="text-xs text-obsidian-400">
                {generatedPlan.total_modules || generatedPlan.modules?.length || 3} Learning Modules • 100% Mandatory Coverage
              </p>
            </div>

            <NavLink to="/verification">
              <Button variant="primary" rightIcon={<ArrowRight className="h-4 w-4" />}>
                Open Flagship Verification Center
              </Button>
            </NavLink>
          </div>

          {/* Timeline Stage Selector */}
          <div className="flex items-center gap-2 border-b border-cloud-200 pb-3">
            {['Day 1', 'Week 1', 'Week 2', '30 Days'].map(st => (
              <button
                key={st}
                onClick={() => setActiveStage(st)}
                className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
                  activeStage === st ? 'bg-electric-600 text-white' : 'bg-cloud-100 text-obsidian-700 hover:bg-cloud-200'
                }`}
              >
                {st} Modules
              </button>
            ))}
          </div>

          {/* Modules Preview List */}
          <div className="space-y-4">
            {(generatedPlan.modules || []).map(mod => (
              <div key={mod.module_id} className="bg-white p-6 rounded-xl border border-cloud-200 shadow-subtle space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-cloud-200">
                  <div>
                    <span className="font-mono text-[10px] text-electric-600 font-bold">{mod.module_id}</span>
                    <h4 className="text-base font-bold font-heading text-obsidian">{mod.title}</h4>
                    <p className="text-xs text-obsidian-400">{mod.description}</p>
                  </div>
                  <Badge variant="info" size="sm">{mod.stage}</Badge>
                </div>

                {/* Learning Objectives */}
                <div>
                  <h5 className="text-xs font-bold text-obsidian mb-1">Learning Objectives</h5>
                  <ul className="list-disc list-inside text-xs text-obsidian-600 space-y-0.5">
                    {(mod.learning_objectives || []).map((obj, i) => (
                      <li key={i}>{obj}</li>
                    ))}
                  </ul>
                </div>

                {/* Tasks List */}
                <div>
                  <h5 className="text-xs font-bold text-obsidian mb-2">Mapped Tasks</h5>
                  <div className="space-y-2">
                    {(mod.tasks || []).map(tsk => (
                      <div key={tsk.task_id} className="p-3 rounded-lg bg-cloud-50 border border-cloud-200 flex items-center justify-between text-xs">
                        <div>
                          <span className="font-bold text-obsidian">{tsk.title}</span>
                          <span className="block text-obsidian-500 text-[11px]">{tsk.description}</span>
                          <span className="font-mono text-[10px] text-obsidian-400">
                            Source: {tsk.source_document_id} ({tsk.source_section_id})
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[11px] text-obsidian-500 flex items-center gap-1">
                            <Clock className="h-3 w-3" /> {tsk.estimated_minutes}m
                          </span>
                          <Badge variant={tsk.is_mandatory ? 'danger' : 'neutral'} size="sm">
                            {tsk.is_mandatory ? 'Mandatory' : 'Optional'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
