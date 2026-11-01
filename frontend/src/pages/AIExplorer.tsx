import React, { useState } from 'react';
import { 
  Sparkles, Send, FileText, Network, Code, Clock, CheckCircle2, 
  AlertTriangle, ShieldCheck, HelpCircle, Layers, ArrowRight
} from 'lucide-react';
import { apiService } from '../services/api';
import { GraphRAGResponse, CypherResponse } from '../types';

const SAMPLE_QUESTIONS = [
  "What are VESIT's primary Scope 1 and Scope 2 emission sources?",
  "How much rooftop solar capacity is installed on Academic Block A?",
  "What rainwater harvesting initiatives contribute to SDG 6?",
  "How does the institution handle organic canteen waste?",
  "What is the capital cost of a 100 kW solar array?" // Fallback test
];

export const AIExplorer: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'GRAPHRAG' | 'CYPHER'>('GRAPHRAG');
  const [query, setQuery] = useState<string>('');
  const [retrievalMode, setRetrievalMode] = useState<string>('HYBRID_GRAPHRAG');
  const [loading, setLoading] = useState<boolean>(false);
  const [ragResult, setRagResult] = useState<GraphRAGResponse | null>(null);
  const [cypherResult, setCypherResult] = useState<CypherResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const queryToRun = customQuery || query;
    if (!queryToRun.trim()) return;

    setLoading(true);
    setError(null);

    try {
      if (activeTab === 'GRAPHRAG') {
        const res = await apiService.queryGraphRAG(queryToRun, retrievalMode);
        setRagResult(res);
      } else {
        const res = await apiService.executeCypherQuery(queryToRun);
        setCypherResult(res);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error executing query');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleClick = (sample: string) => {
    setQuery(sample);
    handleSubmit(undefined, sample);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">AI Sustainability Assistant & GraphRAG</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              EVIDENCE GROUNDED
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Query campus sustainability documents and property graph via local Mistral LLM and hybrid retrieval with strict provenance citations.
          </p>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex bg-gray-100 p-1 rounded-xl border border-gray-200">
          <button
            onClick={() => {
              setActiveTab('GRAPHRAG');
              setError(null);
            }}
            className={`flex items-center gap-2 px-4 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              activeTab === 'GRAPHRAG'
                ? 'bg-white text-emerald-800 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            Hybrid GraphRAG
          </button>
          <button
            onClick={() => {
              setActiveTab('CYPHER');
              setError(null);
            }}
            className={`flex items-center gap-2 px-4 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              activeTab === 'CYPHER'
                ? 'bg-white text-emerald-800 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Code className="w-3.5 h-3.5 text-blue-600" />
            NL to Cypher Query
          </button>
        </div>
      </div>

      {/* Query Bar Card */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                activeTab === 'GRAPHRAG'
                  ? 'Ask a sustainability question (e.g. What are our Scope 1 emissions?)...'
                  : 'Enter question for Cypher generation (e.g. List all buildings with solar arrays)...'
              }
              className="flex-1 px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white text-gray-900"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white font-semibold rounded-xl text-sm flex items-center gap-2 shadow-sm transition-colors"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <span>Query</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </div>

          {/* Sub-controls */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
            {activeTab === 'GRAPHRAG' ? (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Layers className="w-3.5 h-3.5 text-gray-400" />
                <span className="font-medium">Retrieval Mode:</span>
                <select
                  value={retrievalMode}
                  onChange={(e) => setRetrievalMode(e.target.value)}
                  className="bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1 text-xs text-gray-800 font-medium focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="HYBRID_GRAPHRAG">Hybrid GraphRAG (Vector + Multi-Hop Graph)</option>
                  <option value="VECTOR_RAG">Vector RAG Baseline (Cosine Similarity)</option>
                  <option value="GRAPH_RAG">Basic Graph RAG (Entity Subgraphs)</option>
                </select>
              </div>
            ) : (
              <div className="text-xs text-blue-700 flex items-center gap-1.5 font-medium">
                <Code className="w-3.5 h-3.5" />
                Read-only Cypher generation constrained to validated AST tokens
              </div>
            )}

            <span className="text-xs text-gray-400 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Strict Grounding Fallback Enabled
            </span>
          </div>
        </form>

        {/* Sample Question Pills */}
        <div className="pt-2 border-t border-gray-100">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5" /> Curated Test Questions:
          </div>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_QUESTIONS.map((sq, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSampleClick(sq)}
                className="text-xs bg-gray-50 hover:bg-emerald-50 hover:text-emerald-700 border border-gray-200 hover:border-emerald-300 rounded-full px-3 py-1 text-gray-600 transition-colors text-left"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-800 text-sm">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <div>{error}</div>
        </div>
      )}

      {/* GraphRAG Result View */}
      {activeTab === 'GRAPHRAG' && ragResult && (
        <div className="space-y-6">
          {/* Main Answer Box */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-100 pb-3">
              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-1 text-xs font-semibold rounded-full flex items-center gap-1.5 ${
                  ragResult.is_grounded 
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : 'bg-amber-100 text-amber-800 border border-amber-300'
                }`}>
                  {ragResult.is_grounded ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> : <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />}
                  {ragResult.is_grounded ? 'Grounding Verified' : 'Missing Evidence Fallback'}
                </span>
                <span className="text-xs font-mono text-gray-500">
                  Mode: {ragResult.retrieval_mode}
                </span>
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-500 font-mono">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {ragResult.latency_ms.toFixed(0)} ms
                </span>
                <span>Confidence: {(ragResult.confidence_score * 100).toFixed(0)}%</span>
              </div>
            </div>

            <div className="prose text-gray-800 text-sm leading-relaxed max-w-none">
              <p className="text-base font-medium text-gray-900">{ragResult.answer}</p>
            </div>
          </div>

          {/* Citations & Evidence Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Document Citations */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-600" />
                  Document Citations ({ragResult.citations.length})
                </h3>
                <span className="text-xs text-gray-400">Verbatim Excerpts</span>
              </div>

              {ragResult.citations.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
                  {ragResult.citations.map((c, i) => (
                    <div key={i} className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-xs space-y-1.5">
                      <div className="flex items-center justify-between text-gray-700 font-semibold">
                        <span className="truncate">{c.document_title}</span>
                        <span className="text-[10px] text-gray-400 font-mono">ID: {c.citation_id}</span>
                      </div>
                      <div className="text-[11px] text-gray-500 font-medium">Section: {c.section}</div>
                      <p className="text-gray-700 italic bg-white p-2 rounded border border-gray-100 leading-relaxed">
                        "{c.excerpt}"
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500 italic p-4 text-center">No matching document chunks retrieved.</p>
              )}
            </div>

            {/* Knowledge Graph Traversal Paths */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                  <Network className="w-4 h-4 text-emerald-600" />
                  Knowledge Graph Triples ({ragResult.graph_paths.length})
                </h3>
                <span className="text-xs text-gray-400">Multi-Hop Traversal</span>
              </div>

              {ragResult.graph_paths.length > 0 ? (
                <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
                  {ragResult.graph_paths.map((p, i) => (
                    <div key={i} className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-xs space-y-1">
                      <div className="flex items-center gap-2 font-mono text-gray-800">
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-semibold text-[11px] truncate max-w-[120px]">
                          {p.source}
                        </span>
                        <span className="text-emerald-700 font-bold flex items-center gap-1 text-[11px]">
                          <ArrowRight className="w-3 h-3" /> {p.relationship} <ArrowRight className="w-3 h-3" />
                        </span>
                        <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded font-semibold text-[11px] truncate max-w-[120px]">
                          {p.target}
                        </span>
                      </div>
                      {p.evidence && (
                        <div className="text-[11px] text-gray-500 italic pt-1">
                          Evidence: {p.evidence}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500 italic p-4 text-center">No explicit graph triples traversed.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Cypher Result View */}
      {activeTab === 'CYPHER' && cypherResult && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-300">
                  AST Validated Cypher
                </span>
                <span className="text-xs text-gray-500 font-mono">
                  Source: {cypherResult.execution_source}
                </span>
              </div>
              <span className="text-xs text-gray-500 font-mono">
                {cypherResult.latency_ms.toFixed(0)} ms &bull; {cypherResult.record_count} Records
              </span>
            </div>

            {/* Generated Code Block */}
            <div>
              <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Generated Cypher Query</div>
              <pre className="p-3 bg-gray-900 text-emerald-400 font-mono text-xs rounded-lg overflow-x-auto">
                {cypherResult.generated_cypher}
              </pre>
            </div>

            <p className="text-xs text-gray-600">{cypherResult.explanation}</p>
          </div>

          {/* Results Table */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-bold text-gray-900 text-sm">Query Execution Results</h3>
            </div>
            {cypherResult.records && cypherResult.records.length > 0 ? (
              <div className="overflow-x-auto max-h-80">
                <table className="w-full text-left text-xs text-gray-600">
                  <thead className="bg-gray-50 uppercase text-gray-700 font-semibold border-b border-gray-200">
                    <tr>
                      {Object.keys(cypherResult.records[0]).map((key) => (
                        <th key={key} className="py-2.5 px-4 font-mono">{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 font-mono">
                    {cypherResult.records.map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {Object.values(row).map((val: any, cidx) => (
                          <td key={cidx} className="py-2.5 px-4 truncate max-w-xs">
                            {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-gray-500 italic">
                Query executed successfully, returning 0 records matching the filters.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

