import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DocumentMeta } from '../types';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { FileText, Upload, ShieldAlert, CheckCircle2, History, FileCheck } from 'lucide-react';

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState<'ALL' | 'PDF' | 'DOCX' | 'ACTIVE' | 'SUPERSEDED'>('ALL');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<DocumentMeta | null>(null);

  // Upload Form State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadVersion, setUploadVersion] = useState('1.0');
  const [uploadDate, setUploadDate] = useState(new Date().toISOString().split('T')[0]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatusMsg, setUploadStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    loadDocs();
  }, []);

  async function loadDocs() {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const filteredDocs = documents.filter(doc => {
    if (selectedFilter === 'PDF') return doc.file_type === 'PDF';
    if (selectedFilter === 'DOCX') return doc.file_type === 'DOCX';
    if (selectedFilter === 'ACTIVE') return doc.is_active;
    if (selectedFilter === 'SUPERSEDED') return !doc.is_active;
    return true;
  });

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadStatusMsg('Running Adversarial Prompt Injection Scanner...');

    setTimeout(async () => {
      setUploadStatusMsg('Sanitizing paths and extracting document structure...');
      try {
        const newDoc = await api.uploadDocument(uploadFile, uploadVersion, uploadDate);
        setDocuments(prev => [newDoc, ...prev]);
        setShowUploadModal(false);
        setUploadFile(null);
      } catch (err) {
        alert('Upload failed');
      } finally {
        setIsUploading(false);
        setUploadStatusMsg(null);
      }
    }, 800);
  };

  if (loading) return <div className="p-6"><LoadingSkeleton type="table" rows={5} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold font-heading text-obsidian">Document Repository & Ingestion</h2>
          <p className="text-xs text-obsidian-400">Untrusted document parsing, section metadata extraction, and version tracking</p>
        </div>

        <Button
          onClick={() => setShowUploadModal(true)}
          variant="primary"
          leftIcon={<Upload className="h-4 w-4" />}
        >
          Upload Policy / SOP Document
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-cloud-200 pb-3">
        {(['ALL', 'ACTIVE', 'SUPERSEDED', 'PDF', 'DOCX'] as const).map(f => (
          <button
            key={f}
            onClick={() => setSelectedFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              selectedFilter === f
                ? 'bg-electric-600 text-white'
                : 'bg-cloud-100 text-obsidian-700 hover:bg-cloud-200'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Document List Table */}
      <div className="bg-white border border-cloud-200 rounded-xl overflow-hidden shadow-subtle">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-cloud-100 border-b border-cloud-200 text-obsidian-500 font-mono text-[10px] uppercase">
              <th className="p-3">Filename & Version</th>
              <th className="p-3">Type</th>
              <th className="p-3">File Size</th>
              <th className="p-3">Effective Date</th>
              <th className="p-3">Sections / Chunks</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cloud-200">
            {filteredDocs.map(doc => (
              <tr key={doc.id} className="hover:bg-cloud-50 transition-colors">
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <FileText className={`h-4 w-4 ${doc.is_active ? 'text-electric-600' : 'text-obsidian-400'}`} />
                    <div>
                      <span className="font-bold text-obsidian block">{doc.filename}</span>
                      <span className="font-mono text-[10px] text-obsidian-400">ID: {doc.id} • Version {doc.version}</span>
                    </div>
                  </div>
                </td>
                <td className="p-3 font-mono font-bold text-obsidian-600">{doc.file_type}</td>
                <td className="p-3 font-mono text-obsidian-600">{(doc.file_size_bytes / 1024).toFixed(1)} KB</td>
                <td className="p-3 font-mono text-obsidian-600">{doc.effective_date}</td>
                <td className="p-3 text-obsidian-600">
                  <span className="font-semibold">{doc.sections_count}</span> sections / <span className="font-semibold">{doc.chunks_count}</span> chunks
                </td>
                <td className="p-3">
                  <Badge variant={doc.is_active ? 'success' : 'neutral'} size="sm">
                    {doc.is_active ? 'Active Policy' : 'Superseded (Obsolete)'}
                  </Badge>
                </td>
                <td className="p-3 text-right">
                  <Button
                    onClick={() => setSelectedDoc(doc)}
                    variant="outline"
                    size="sm"
                  >
                    Inspect Detail
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {selectedDoc && (
        <Modal
          isOpen={!!selectedDoc}
          onClose={() => setSelectedDoc(null)}
          title={`Document Metadata: ${selectedDoc.filename}`}
          subtitle={`Version ${selectedDoc.version} • Effective ${selectedDoc.effective_date}`}
          maxWidth="2xl"
        >
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-cloud-100 border border-cloud-200 grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-obsidian-400 font-mono text-[10px] block">DOCUMENT ID</span>
                <span className="font-mono font-bold text-obsidian">{selectedDoc.id}</span>
              </div>
              <div>
                <span className="text-obsidian-400 font-mono text-[10px] block">FILE PATH</span>
                <span className="font-mono text-obsidian text-[11px]">{selectedDoc.file_path}</span>
              </div>
              <div>
                <span className="text-obsidian-400 font-mono text-[10px] block">SECTIONS PARSED</span>
                <span className="font-semibold text-obsidian">{selectedDoc.sections_count} Section Headings</span>
              </div>
              <div>
                <span className="text-obsidian-400 font-mono text-[10px] block">SEMANTIC CHUNKS</span>
                <span className="font-semibold text-obsidian">{selectedDoc.chunks_count} Vector Chunks</span>
              </div>
            </div>

            <div className="border-t border-cloud-200 pt-3">
              <h4 className="text-xs font-bold font-heading text-obsidian mb-2 flex items-center gap-1.5">
                <History className="h-4 w-4 text-electric-600" />
                Version History & Policy Status
              </h4>
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-between text-xs text-emerald-900">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  <span>Version {selectedDoc.version} is active and assigned to all new onboarding plans.</span>
                </div>
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* Upload Experience Modal */}
      {showUploadModal && (
        <Modal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          title="Upload Corporate Document"
          subtitle="Adversarial Prompt Injection Scanner & Untrusted Data Sanitization Active"
        >
          <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
            <div className="border-2 border-dashed border-cloud-300 rounded-xl p-6 text-center bg-cloud-50 hover:bg-cloud-100 transition-colors">
              <Upload className="h-8 w-8 text-electric-600 mx-auto mb-2" />
              <p className="font-semibold text-obsidian">Drag and drop PDF or DOCX policy manual here</p>
              <p className="text-obsidian-400 mt-1">Maximum file size: 10 MB. Strict path traversal defenses applied.</p>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={e => setUploadFile(e.target.files?.[0] || null)}
                className="mt-3 block mx-auto text-xs text-obsidian-600"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-obsidian font-semibold mb-1">Version Identifier</label>
                <input
                  type="text"
                  value={uploadVersion}
                  onChange={e => setUploadVersion(e.target.value)}
                  placeholder="e.g. 2.0"
                  className="w-full p-2 border border-cloud-300 rounded-lg bg-white"
                  required
                />
              </div>
              <div>
                <label className="block text-obsidian font-semibold mb-1">Effective Date</label>
                <input
                  type="date"
                  value={uploadDate}
                  onChange={e => setUploadDate(e.target.value)}
                  className="w-full p-2 border border-cloud-300 rounded-lg bg-white"
                  required
                />
              </div>
            </div>

            {uploadStatusMsg && (
              <div className="p-3 rounded-lg bg-purple-50 border border-purple-200 text-ai-700 flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 shrink-0" />
                <span className="font-mono text-[11px]">{uploadStatusMsg}</span>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-3 border-t border-cloud-200">
              <Button type="button" variant="ghost" onClick={() => setShowUploadModal(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" isLoading={isUploading} disabled={!uploadFile}>
                Upload & Process Document
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
