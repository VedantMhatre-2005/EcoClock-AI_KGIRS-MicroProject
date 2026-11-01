import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import { SystemStatus } from '../../types';
import { Database, Cpu, ShieldCheck, Activity, Info } from 'lucide-react';

interface NavbarProps {
  title: string;
}

export const Navbar: React.FC<NavbarProps> = ({ title }) => {
  const [status, setStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await apiService.getSystemStatus();
        setStatus(data);
      } catch (e) {
        // Fallback status if offline
        setStatus(null);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-white/90 backdrop-blur-md border-b border-stone-200 px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      {/* Page Title & Breadcrumb */}
      <div className="flex items-center space-x-3">
        <h2 className="text-lg font-bold text-stone-900 tracking-tight">{title}</h2>
        <span className="text-xs text-stone-400 font-normal">/</span>
        <span className="text-xs font-medium text-stone-500">Institution: VESIT Green Campus</span>
      </div>

      {/* System Status Badges */}
      <div className="flex items-center space-x-2.5">
        {/* Data Provenance Badge */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold" title="All values backed by persisted synthetic campus dataset">
          <Info className="w-3.5 h-3.5 text-amber-600" />
          <span>SYNTHETIC DEMO</span>
        </div>

        {/* Ollama Status Badge */}
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            status?.ollama?.connected
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : 'bg-stone-50 text-stone-600 border-stone-200'
          }`}
          title={`Ollama Local LLM (${status?.ollama?.configured_model || 'mistral'})`}
        >
          <Cpu className="w-3.5 h-3.5 text-stone-500" />
          <span className="font-mono text-[11px]">
            Ollama: {status?.ollama?.connected ? 'Online (Mistral)' : 'Offline / Standby'}
          </span>
        </div>

        {/* Neo4j Status Badge */}
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            status?.neo4j?.connected
              ? 'bg-teal-50 text-teal-800 border-teal-200'
              : 'bg-stone-50 text-stone-600 border-stone-200'
          }`}
          title="Neo4j Knowledge Graph Status"
        >
          <Database className="w-3.5 h-3.5 text-stone-500" />
          <span className="font-mono text-[11px]">
            Neo4j: {status?.neo4j?.connected ? 'Connected' : 'Local Mirror (Active)'}
          </span>
        </div>

        {/* Graph Size */}
        {status?.knowledge_graph && (
          <div className="hidden lg:flex items-center space-x-1 px-2.5 py-1 rounded-full bg-stone-100 text-stone-600 text-xs font-mono">
            <Activity className="w-3.5 h-3.5 text-stone-400" />
            <span>{status.knowledge_graph.total_nodes} nodes</span>
          </div>
        )}
      </div>
    </header>
  );
};

