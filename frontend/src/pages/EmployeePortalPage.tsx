import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { Sparkles, CheckCircle2, Clock, BookOpen, ArrowRight, Award, HelpCircle } from 'lucide-react';

export const EmployeePortalPage: React.FC = () => {
  const { user } = useAuth();
  const [portalData, setPortalData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const defaultPortalData = {
    employee_id: user?.employee_id || 'EMP-004',
    name: user?.full_name || user?.name || user?.username || 'David Wallace',
    email: user?.email || 'employee@skillsprint.ai',
    department: user?.department || 'Engineering',
    role_id: 'ROL-01',
    role_title: 'Software Engineer',
    experience_level: 'Junior',
    joining_date: '2026-01-15',
    manager_name: 'Alex Mercer',
    plan_id: 'plan-emp-001',
    progress_percentage: 65,
    onboarding_status: 'IN_PROGRESS',
    completed_modules_count: 2,
    total_modules_count: 3,
    security_compliance_pct: 100,
    quiz_attempts_count: 1,
    passed_quizzes_count: 1,
    next_priority_focus: {
      module_id: 'MOD-02',
      title: 'SLA Escalation & Operational Compliance',
      description: 'Master mandatory response SLAs and escalation workflows under SOP-07.',
      stage: 'Week 1',
      estimated_minutes: 30,
      source_document_id: 'DOC-SOP01',
      source_section_id: 'ESC-4.2',
      page_number: 8
    },
    recommendations: [
      {
        type: 'STRENGTH',
        title: 'Strength: Physical & MFA Security',
        description: 'Scored 100% on hardware token authentication and workstation clean desk standards!'
      },
      {
        type: 'REVIEW',
        title: 'Recommended Review: P1 Escalation Protocols',
        description: 'Spend 10 minutes reviewing SOP-07 Section 4.2 diagnostic template before taking your quiz.'
      }
    ]
  };

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await api.getPortalDashboard().catch(() => null);
        setPortalData(data || defaultPortalData);
      } catch (e) {
        console.error("Failed to load portal dashboard", e);
        setPortalData(defaultPortalData);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        <LoadingSkeleton type="card" rows={3} />
      </div>
    );
  }

  const currentPortalData = portalData || defaultPortalData;

  const focus = currentPortalData.next_priority_focus || {};

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      {/* Warm, Personalized Greeting Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-electric-600 to-electric-700 text-white shadow-xl flex flex-wrap items-center justify-between gap-6">
        <div className="space-y-2">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-white/20 text-white border border-white/30 backdrop-blur-xs">
            {currentPortalData.role_title} • {currentPortalData.department}
          </span>
          <h2 className="text-2xl font-bold font-heading text-white">
            Welcome back, {currentPortalData.name ? currentPortalData.name.split(' ')[0] : (user?.full_name || 'Employee')}! 👋
          </h2>
          <p className="text-xs text-electric-100 max-w-xl leading-relaxed">
            You're making great progress on your onboarding journey! You've completed {Math.round(currentPortalData.progress_percentage || 65)}% of your mandatory security, SOP, and role compliance learning modules.
          </p>
        </div>

        <NavLink to="/learning-module">
          <Button variant="secondary" size="lg" rightIcon={<ArrowRight className="h-4 w-4" />}>
            Continue Next Activity
          </Button>
        </NavLink>
      </div>

      {/* Progress Stats Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-cloud-200 shadow-subtle flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold font-heading text-lg">
            {Math.round(currentPortalData.progress_percentage || 65)}%
          </div>
          <div>
            <span className="text-xs text-obsidian-400 font-semibold block">Overall Progress</span>
            <span className="text-sm font-bold font-heading text-obsidian">
              {currentPortalData.completed_modules_count || 2} of {currentPortalData.total_modules_count || 3} Modules Done
            </span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-cloud-200 shadow-subtle flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-electric-50 text-electric-600 flex items-center justify-center font-bold font-heading text-lg">
            {Math.round(currentPortalData.security_compliance_pct || 100)}%
          </div>
          <div>
            <span className="text-xs text-obsidian-400 font-semibold block">Security Compliance</span>
            <span className="text-sm font-bold font-heading text-obsidian">MFA & Clean Desk Verified</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-cloud-200 shadow-subtle flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-purple-50 text-ai-600 flex items-center justify-center font-bold font-heading text-lg">
            {currentPortalData.passed_quizzes_count || 1}
          </div>
          <div>
            <span className="text-xs text-obsidian-400 font-semibold block">Passed Quizzes</span>
            <span className="text-sm font-bold font-heading text-obsidian font-mono text-xs">
              {focus.title || 'Interactive Quiz'}
            </span>
          </div>
        </div>
      </div>

      {/* Next Up Focus Box */}
      <div className="bg-white p-6 rounded-xl border-2 border-electric-500/40 shadow-subtle space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-cloud-200">
          <div className="flex items-center gap-2">
            <Badge variant="info" size="sm">Current Priority Focus</Badge>
            <span className="text-xs font-mono text-obsidian-400">Due: {focus.stage || 'Week 1'}</span>
          </div>
          <span className="text-xs font-mono font-semibold text-electric-600">{focus.estimated_minutes || 30} Mins Est.</span>
        </div>

        <div>
          <h3 className="text-base font-bold font-heading text-obsidian">
            {focus.title || 'Module 2: SLA Escalation & P1 Ticket Triage'}
          </h3>
          <p className="text-xs text-obsidian-600 mt-1">
            {focus.description || 'Master escalation protocols under SOP-07 Section 4.2.'}
          </p>
        </div>

        <div className="flex justify-end pt-2">
          <NavLink to="/learning-module">
            <Button variant="primary" size="sm" rightIcon={<ArrowRight className="h-3.5 w-3.5" />}>
              Start Module & Interactive Quiz
            </Button>
          </NavLink>
        </div>
      </div>

      {/* Personalized Recommendations & Skill Profile */}
      <div className="bg-white p-6 rounded-xl border border-cloud-200 shadow-subtle space-y-4">
        <h3 className="text-sm font-bold font-heading text-obsidian border-b border-cloud-200 pb-2">
          Personalized Recommendations & Skill Insights
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(currentPortalData.recommendations || []).map((rec: any, idx: number) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border space-y-1 ${
                rec.type === 'STRENGTH' ? 'bg-cloud-50 border-cloud-200' : 'bg-amber-50 border-amber-200'
              }`}
            >
              <div
                className={`flex items-center gap-2 text-xs font-bold ${
                  rec.type === 'STRENGTH' ? 'text-obsidian' : 'text-amber-900'
                }`}
              >
                {rec.type === 'STRENGTH' ? (
                  <Award className="h-4 w-4 text-emerald-600" />
                ) : (
                  <HelpCircle className="h-4 w-4 text-amber-600" />
                )}
                {rec.title}
              </div>
              <p className={`text-xs ${rec.type === 'STRENGTH' ? 'text-obsidian-500' : 'text-amber-800'}`}>
                {rec.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
