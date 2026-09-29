import React, { useState } from 'react';
import { api } from '../services/api';
import { ReportSummary } from '../types';
import { Button } from '../components/common/Button';
import { FileSpreadsheet, Download, Printer, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [selectedReportType, setSelectedReportType] = useState<string>('validation');
  const [report, setReport] = useState<ReportSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const data = await api.getReport(selectedReportType);
      setReport(data);
    } catch (e) {
      alert('Error fetching report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SkillSprint_AI_${selectedReportType.toUpperCase()}_Report.json`;
    a.click();
  };

  const handleExportCSV = () => {
    if (!report) return;
    const csvHeader = 'Requirement ID,Title,Category,Is Mandatory,Priority,Source Doc\n';
    const csvRows = report.data
      .map(
        (r: any) =>
          `"${r.requirement_id}","${r.title}","${r.category}",${r.is_mandatory},"${r.priority}","${r.source_document_id}"`
      )
      .join('\n');
    const blob = new Blob([csvHeader + csvRows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SkillSprint_AI_${selectedReportType.toUpperCase()}_Report.csv`;
    a.click();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold font-heading text-obsidian">Compliance & Audit Reports Export Center</h2>
        <p className="text-xs text-obsidian-400">Export official verification, ground-truth requirement matrix, and security audit reports</p>
      </div>

      {/* Report Config Box */}
      <div className="bg-white p-6 rounded-xl border border-cloud-200 shadow-subtle flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold text-obsidian">Report Type:</label>
          <select
            value={selectedReportType}
            onChange={e => setSelectedReportType(e.target.value)}
            className="p-2 text-xs bg-cloud-100 border border-cloud-300 rounded-lg text-obsidian font-semibold"
          >
            <option value="validation">Validation & Coverage Report</option>
            <option value="comparison">Requirement Comparison Matrix</option>
            <option value="security">Security & Adversarial Audit Report</option>
            <option value="onboarding">Executive Onboarding Summary</option>
          </select>

          <Button onClick={handleGenerateReport} variant="primary" size="sm" isLoading={loading}>
            Generate Report
          </Button>
        </div>

        {report && (
          <div className="flex items-center gap-2">
            <Button onClick={handleExportJSON} variant="outline" size="sm" leftIcon={<Download className="h-3.5 w-3.5" />}>
              Export JSON
            </Button>
            <Button onClick={handleExportCSV} variant="outline" size="sm" leftIcon={<FileSpreadsheet className="h-3.5 w-3.5" />}>
              Export CSV
            </Button>
            <Button onClick={() => window.print()} variant="ghost" size="sm" leftIcon={<Printer className="h-3.5 w-3.5" />}>
              Print / Save PDF
            </Button>
          </div>
        )}
      </div>

      {/* Generated Report Display */}
      {report && (
        <div className="bg-white p-6 rounded-xl border border-cloud-200 shadow-subtle space-y-6">
          <div className="border-b border-cloud-200 pb-4">
            <h3 className="text-base font-bold font-heading text-obsidian">{report.title}</h3>
            <p className="text-xs text-obsidian-400 font-mono">Generated At: {report.generated_at}</p>
          </div>

          {/* Metrics Summary Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(report.summary_metrics).map(([k, v]) => (
              <div key={k} className="p-3 rounded-lg bg-cloud-100 border border-cloud-200">
                <span className="text-[10px] font-mono text-obsidian-400 uppercase block">{k.replace(/_/g, ' ')}</span>
                <span className="text-base font-bold font-heading text-obsidian">{String(v)}</span>
              </div>
            ))}
          </div>

          {/* Data Table */}
          <div className="overflow-x-auto border border-cloud-200 rounded-lg">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-cloud-100 border-b border-cloud-200 font-mono text-[10px] text-obsidian-500 uppercase">
                  <th className="p-3">Req ID</th>
                  <th className="p-3">Title</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Priority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cloud-200">
                {report.data.map((row: any) => (
                  <tr key={row.id}>
                    <td className="p-3 font-mono font-bold text-electric-600">{row.requirement_id}</td>
                    <td className="p-3 font-semibold text-obsidian">{row.title}</td>
                    <td className="p-3 text-obsidian-600">{row.category}</td>
                    <td className="p-3 font-mono">{row.is_mandatory ? 'Mandatory' : 'Optional'}</td>
                    <td className="p-3 font-mono">{row.priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
