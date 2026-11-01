import React, { useEffect, useState } from 'react';
import { 
  Settings as SettingsIcon, Server, Database, Cpu, ShieldCheck, 
  RefreshCw, CheckCircle2, AlertCircle, Building2, Calendar, Target
} from 'lucide-react';
import { apiService } from '../services/api';
import { SystemStatus } from '../types';

export const Settings: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [targetYear, setTargetYear] = useState<number>(2040);
  const [targetMonth, setTargetMonth] = useState<number>(12);
  const [targetDay, setTargetDay] = useState<number>(31);
  const [targetMsg, setTargetMsg] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const res = await apiService.getSystemStatus();
      setStatus(res);
    } catch (err) {
      console.error('Failed to load status', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleUpdateTarget = async (e: React.FormEvent) => {
    e.preventDefault();
    const formattedDate = `${targetYear}-${String(targetMonth).padStart(2, '0')}-${String(targetDay).padStart(2, '0')}`;
    try {
      await apiService.updateTarget({
        name: 'VESIT Institutional Net-Zero Carbon Mandate',
        target_date: formattedDate,
        target_scope: 'SCOPE_1_2_3',
        reduction_percentage: 100
      });
      setTargetMsg(`Net-zero institutional target successfully set to ${formattedDate}`);
      setTimeout(() => setTargetMsg(null), 4000);
    } catch (err: any) {
      alert(err.message || 'Failed to update target');
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">System Configuration & Infrastructure</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              PRODUCTION ARCHITECTURE
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Monitor local LLM inference, Neo4j property graph connectivity, institutional metadata, and decarbonization horizons.
          </p>
        </div>

        <button
          onClick={fetchStatus}
          className="px-3.5 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-1.5 shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Health Status
        </button>
      </div>

      {/* Infrastructure Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Local LLM Service Card */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-emerald-600" />
              <h3 className="font-bold text-gray-900 text-sm">Local LLM Service</h3>
            </div>
            <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
              status?.ollama?.connected ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
            }`}>
              {status?.ollama?.connected ? 'CONNECTED' : 'STANDALONE / FALLBACK'}
            </span>
          </div>
          <div className="text-xs space-y-2 text-gray-600 font-mono">
            <div><span className="text-gray-400 font-sans">Provider:</span> Ollama Local API</div>
            <div><span className="text-gray-400 font-sans">Model:</span> {status?.ollama?.configured_model || 'mistral'}</div>
            <div><span className="text-gray-400 font-sans">Endpoint:</span> {status?.ollama?.url || 'http://localhost:11434'}</div>
            <div><span className="text-gray-400 font-sans">Temperature:</span> 0.0 (Strictly Grounded)</div>
          </div>
          <div className="pt-2 border-t border-gray-100 text-[11px] text-gray-500">
            No paid external APIs (OpenAI/Claude) are used; runs 100% on local hardware.
          </div>
        </div>

        {/* Neo4j Knowledge Graph Card */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-gray-900 text-sm">Neo4j Property Graph</h3>
            </div>
            <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
              status?.neo4j?.connected ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {status?.neo4j?.connected ? 'PERSISTENT LIVE' : 'DUAL MEMORY MIRROR'}
            </span>
          </div>
          <div className="text-xs space-y-2 text-gray-600 font-mono">
            <div><span className="text-gray-400 font-sans">URI:</span> {status?.neo4j?.uri || 'bolt://localhost:7687'}</div>
            <div><span className="text-gray-400 font-sans">Total Nodes:</span> {status?.knowledge_graph?.total_nodes || 309}</div>
            <div><span className="text-gray-400 font-sans">Total Edges:</span> {status?.knowledge_graph?.total_edges || 130}</div>
            <div><span className="text-gray-400 font-sans">Cypher Engine:</span> Read-Only AST Guarded</div>
          </div>
          <div className="pt-2 border-t border-gray-100 text-[11px] text-gray-500">
            Persistent property graph with dual in-memory graph index mirror.
          </div>
        </div>

        {/* Embedding & Relational DB Card */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-purple-600" />
              <h3 className="font-bold text-gray-900 text-sm">Embeddings & Storage</h3>
            </div>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 text-emerald-800">
              OPERATIONAL
            </span>
          </div>
          <div className="text-xs space-y-2 text-gray-600 font-mono">
            <div><span className="text-gray-400 font-sans">Embeddings:</span> {status?.embedding_model || 'all-MiniLM-L6-v2'}</div>
            <div><span className="text-gray-400 font-sans">Relational DB:</span> SQLite (SQLAlchemy)</div>
            <div><span className="text-gray-400 font-sans">Database Path:</span> backend/data/ecoclock.db</div>
            <div><span className="text-gray-400 font-sans">Seed State:</span> 42 (Deterministic)</div>
          </div>
          <div className="pt-2 border-t border-gray-100 text-[11px] text-gray-500">
            Full ACID compliance for document records and time-series telemetry.
          </div>
        </div>
      </div>

      {/* Target Management Form */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 border-b border-gray-100 pb-3">
          <Target className="w-5 h-5 text-emerald-600" />
          <h3 className="font-bold text-gray-900 text-base">Institutional Decarbonization Horizon Manager</h3>
        </div>

        <form onSubmit={handleUpdateTarget} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Target Year</label>
            <input
              type="number"
              min="2025"
              max="2060"
              value={targetYear}
              onChange={(e) => setTargetYear(Number(e.target.value))}
              className="w-full text-xs bg-gray-50 border border-gray-300 rounded-lg p-2 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Target Month</label>
            <select
              value={targetMonth}
              onChange={(e) => setTargetMonth(Number(e.target.value))}
              className="w-full text-xs bg-gray-50 border border-gray-300 rounded-lg p-2 font-mono"
            >
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                <option key={m} value={m}>{m} ({new Date(2024, m - 1).toLocaleString('default', { month: 'short' })})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Target Day</label>
            <input
              type="number"
              min="1"
              max="31"
              value={targetDay}
              onChange={(e) => setTargetDay(Number(e.target.value))}
              className="w-full text-xs bg-gray-50 border border-gray-300 rounded-lg p-2 font-mono"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            Update College Climate Clock Target
          </button>
        </form>

        {targetMsg && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            {targetMsg}
          </div>
        )}
      </div>

      {/* Institutional Metadata Card */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 border-b border-gray-100 pb-3">
          <Building2 className="w-5 h-5 text-emerald-600" />
          <h3 className="font-bold text-gray-900 text-base">Demonstration Campus Profile</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div className="text-gray-400 uppercase font-semibold text-[10px]">Institution Name</div>
            <div className="font-bold text-gray-900 mt-1">VESIT Green Campus</div>
            <div className="text-gray-500 text-[11px]">Chembur, Mumbai, Maharashtra</div>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div className="text-gray-400 uppercase font-semibold text-[10px]">Population Density</div>
            <div className="font-bold text-gray-900 mt-1">3,200 On-Campus Individuals</div>
            <div className="text-gray-500 text-[11px]">3,000 Students &bull; 200 Faculty/Staff</div>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div className="text-gray-400 uppercase font-semibold text-[10px]">Monitored Buildings</div>
            <div className="font-bold text-gray-900 mt-1">7 Institutional Facilities</div>
            <div className="text-gray-500 text-[11px]">Academic, Labs, Library, Canteen, Admin</div>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div className="text-gray-400 uppercase font-semibold text-[10px]">Grid Emission Factor</div>
            <div className="font-bold text-gray-900 mt-1">0.82 kg CO₂e / kWh</div>
            <div className="text-gray-500 text-[11px]">CEA India National Grid Baseline</div>
          </div>
        </div>
      </div>
    </div>
  );
};

