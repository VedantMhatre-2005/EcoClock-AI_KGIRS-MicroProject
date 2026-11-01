import React, { useEffect, useState } from 'react';
import { 
  FileText, Upload, RefreshCw, Trash2, Search, Eye, CheckCircle2, 
  AlertCircle, X, Layers, Tag, Database
} from 'lucide-react';
import { apiService } from '../services/api';
import { DocumentItem } from '../types';

export const Documents: React.FC = () => {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter & Search
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');

  // Upload Form State
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<string>('GENERAL');
  const [sourceType, setSourceType] = useState<string>('SYNTHETIC');
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadMsg, setUploadMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Document Details Modal
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null);
  const [detailsLoading, setDetailsLoading] = useState<boolean>(false);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiService.getDocuments();
      setDocs(res || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    setUploadMsg(null);
    try {
      await apiService.uploadDocument(uploadFile, docType, sourceType);
      setUploadMsg({ type: 'success', text: `Document "${uploadFile.name}" ingested into Knowledge Graph successfully!` });
      setUploadFile(null);
      fetchDocs();
      setTimeout(() => setIsUploadOpen(false), 2000);
    } catch (err: any) {
      setUploadMsg({ type: 'error', text: err.response?.data?.detail || err.message || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  const handleViewDetails = async (docId: string) => {
    try {
      setDetailsLoading(true);
      const details = await apiService.getDocumentDetails(docId);
      setSelectedDoc(details);
    } catch (err) {
      console.error('Failed to load document details', err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleReingest = async (docId: string) => {
    try {
      await apiService.reingestDocument(docId);
      fetchDocs();
    } catch (err: any) {
      alert(err.message || 'Re-ingest failed');
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to remove this document and its associated graph nodes?')) return;
    try {
      await apiService.deleteDocument(docId);
      fetchDocs();
    } catch (err: any) {
      alert(err.message || 'Delete failed');
    }
  };

  const filteredDocs = docs.filter((d) => {
    const matchesSearch = searchTerm === '' || d.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === 'ALL' || d.document_type === typeFilter;
    return matchesSearch && matchesType;
  });

  const totalChunks = docs.reduce((a, b) => a + (b.chunk_count || 0), 0);
  const totalEntities = docs.reduce((a, b) => a + (b.entity_count || 0), 0);

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">Document Repository & Ingestion Pipeline</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              {docs.length} Documents Indexed
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Browse, upload, and inspect evidence documents supplying chunks, entities, and relationships to the GraphRAG pipeline.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsUploadOpen(true)}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors"
          >
            <Upload className="w-3.5 h-3.5" />
            Upload Evidence Document
          </button>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Indexed Documents</div>
          <div className="text-2xl font-bold text-gray-900">{docs.length}</div>
          <span className="text-xs text-gray-400 mt-1 block">Full provenance tracked</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Vector Chunks</div>
          <div className="text-2xl font-bold text-blue-600">{totalChunks}</div>
          <span className="text-xs text-blue-600 mt-1 block">800 chars / 120 overlap</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Extracted Entities</div>
          <div className="text-2xl font-bold text-emerald-600">{totalEntities}</div>
          <span className="text-xs text-emerald-600 mt-1 block">Resolved canonical ontology</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Supported Formats</div>
          <div className="text-xs font-mono font-bold text-gray-700 mt-2">
            PDF, DOCX, TXT, CSV, JSON
          </div>
          <span className="text-xs text-gray-400 mt-1 block">Multi-format ingestion parser</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative flex-1 max-w-md w-full">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search documents by title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 font-medium">Type:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="text-xs bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5 text-gray-700 font-medium"
          >
            <option value="ALL">All Types ({docs.length})</option>
            <option value="POLICY">Policy Documents</option>
            <option value="AUDIT">Energy & Water Audits</option>
            <option value="UTILITY_BILL">Utility Billing Records</option>
            <option value="INITIATIVE_REPORT">Initiative Reports</option>
            <option value="RESEARCH_PAPER">Research Papers</option>
            <option value="GENERAL">General</option>
          </select>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-600">
            <thead className="bg-gray-50 uppercase text-gray-700 font-semibold border-b border-gray-200">
              <tr>
                <th className="py-3 px-6">Document Title</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4 text-center">Chunks</th>
                <th className="py-3 px-4 text-center">Entities</th>
                <th className="py-3 px-4 text-center">Triples</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-6 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="py-3.5 px-6 font-semibold text-gray-900 max-w-xs">
                    <div className="truncate">{doc.title}</div>
                    <div className="text-[10px] font-mono text-gray-400 mt-0.5">{doc.id}</div>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-gray-500">{doc.document_type}</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 text-[10px] font-semibold rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                      {doc.source_type}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center font-mono font-medium">{doc.chunk_count}</td>
                  <td className="py-3.5 px-4 text-center font-mono font-medium text-emerald-700">{doc.entity_count}</td>
                  <td className="py-3.5 px-4 text-center font-mono font-medium text-blue-700">{doc.relationship_count}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 text-emerald-800">
                      {doc.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-6 text-center">
                    <div className="flex items-center justify-center gap-1.5">
                      <button
                        onClick={() => handleViewDetails(doc.id)}
                        className="p-1.5 text-gray-500 hover:text-emerald-700 rounded hover:bg-emerald-50 transition-colors"
                        title="View Chunks and Entities"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleReingest(doc.id)}
                        className="p-1.5 text-gray-500 hover:text-blue-700 rounded hover:bg-blue-50 transition-colors"
                        title="Re-run Graph Extraction"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1.5 text-gray-500 hover:text-red-600 rounded hover:bg-red-50 transition-colors"
                        title="Delete Document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-gray-200 space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <Upload className="w-4 h-4 text-emerald-600" />
                Upload Evidence Document
              </h3>
              <button onClick={() => setIsUploadOpen(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">Select File (PDF, DOCX, TXT, CSV, JSON)</label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.csv,.json"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 border border-gray-200 rounded-lg p-2"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">Document Category</label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 font-medium"
                  >
                    <option value="POLICY">Policy</option>
                    <option value="AUDIT">Audit</option>
                    <option value="UTILITY_BILL">Utility Bill</option>
                    <option value="INITIATIVE_REPORT">Initiative Report</option>
                    <option value="RESEARCH_PAPER">Research Paper</option>
                    <option value="GENERAL">General</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">Source Truthfulness Tag</label>
                  <select
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 font-medium"
                  >
                    <option value="SYNTHETIC">Synthetic Demonstration</option>
                    <option value="ACTUAL_MEASURED">Actual Measured</option>
                    <option value="ESTIMATED">Estimated</option>
                  </select>
                </div>
              </div>

              {uploadMsg && (
                <div className={`p-3 rounded-lg text-xs font-medium flex items-center gap-2 ${
                  uploadMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-red-50 text-red-800'
                }`}>
                  {uploadMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-red-600" />}
                  {uploadMsg.text}
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(false)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white rounded-lg font-semibold flex items-center gap-1.5"
                >
                  {uploading ? 'Processing Graph...' : 'Ingest Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document Details Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-xl border border-gray-200 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-gray-100 pb-3">
              <div>
                <h3 className="font-bold text-gray-900 text-base">{selectedDoc.document?.title}</h3>
                <div className="text-xs text-gray-400 font-mono mt-0.5">{selectedDoc.document?.id}</div>
              </div>
              <button onClick={() => setSelectedDoc(null)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Extracted Chunks list */}
            <div>
              <h4 className="font-bold text-xs uppercase text-gray-700 tracking-wider mb-2 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                Indexed Chunks ({selectedDoc.chunks?.length || 0})
              </h4>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {selectedDoc.chunks?.map((c: any, i: number) => (
                  <div key={i} className="p-2.5 bg-gray-50 rounded-lg border border-gray-200 text-xs text-gray-700">
                    <div className="flex items-center justify-between text-[10px] text-gray-400 font-mono mb-1">
                      <span>Index: {c.chunk_index} &bull; Section: {c.section}</span>
                      <span>Chars: {c.content?.length}</span>
                    </div>
                    <p className="line-clamp-3 italic">"{c.content}"</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Extracted Entities list */}
            <div>
              <h4 className="font-bold text-xs uppercase text-gray-700 tracking-wider mb-2 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-emerald-600" />
                Extracted Entities ({selectedDoc.entities?.length || 0})
              </h4>
              <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
                {selectedDoc.entities?.map((ent: any, i: number) => (
                  <span key={i} className="px-2 py-1 bg-emerald-50 text-emerald-800 rounded-md text-[11px] font-semibold border border-emerald-200">
                    {ent.entity_name} ({ent.entity_label})
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

