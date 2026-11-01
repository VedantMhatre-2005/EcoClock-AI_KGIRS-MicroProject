import React, { useEffect, useState } from 'react';
import { Target, CheckCircle2, AlertCircle, ArrowUpRight, Globe, Layers, X, ShieldCheck } from 'lucide-react';
import { apiService } from '../services/api';
import { SDGItem } from '../types';

// Official UN SDG Hex Colors
const SDG_COLORS: Record<number, string> = {
  1: '#E5243B', 2: '#DDA63A', 3: '#4C9F38', 4: '#C5192D',
  5: '#FF3A21', 6: '#26BDE2', 7: '#FCC30B', 8: '#A21942',
  9: '#FD6925', 10: '#DD1367', 11: '#FD9D24', 12: '#BF8B2E',
  13: '#3F7E44', 14: '#0A97D9', 15: '#56C02B', 16: '#00689D',
  17: '#19486A'
};

const PRIORITY_SDGS = [6, 7, 11, 12, 13, 15];

export const SDGTracker: React.FC = () => {
  const [sdgs, setSdgs] = useState<SDGItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSDG, setSelectedSDG] = useState<SDGItem | null>(null);

  useEffect(() => {
    const fetchSDGs = async () => {
      try {
        setLoading(true);
        const res = await apiService.getSDGs();
        setSdgs(res || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load SDG mapping data');
      } finally {
        setLoading(false);
      }
    };
    fetchSDGs();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-xl flex items-center gap-4 text-red-800">
        <AlertCircle className="w-8 h-8 text-red-600" />
        <div>
          <h3 className="font-semibold text-lg">Error Loading SDG Tracker</h3>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  const activeCount = sdgs.filter((s) => s.has_initiatives).length;
  const totalInitiatives = sdgs.reduce((acc, s) => acc + (s.initiative_count || 0), 0);
  const unmappedCount = 17 - activeCount;

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">UN Sustainable Development Goals (SDG) Alignment</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              AGENDA 2030 MAPPED
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Systematic tracking and evidence mapping of institutional climate, energy, circularity, and resource projects to the 17 UN SDGs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-semibold">
            <Globe className="w-4 h-4 text-emerald-600" />
            {activeCount} / 17 SDGs Actively Addressed
          </span>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Mapped SDGs</div>
          <div className="text-3xl font-bold text-gray-900">{activeCount} <span className="text-sm font-normal text-gray-400">/ 17</span></div>
          <span className="text-xs text-emerald-600 font-medium mt-1 block">Institutional coverage</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Active Campus Initiatives</div>
          <div className="text-3xl font-bold text-emerald-600">{totalInitiatives}</div>
          <span className="text-xs text-gray-500 mt-1 block">Cross-cutting climate actions</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Institutional Priority Focus</div>
          <div className="text-3xl font-bold text-blue-600">6 <span className="text-sm font-normal text-gray-400">Core Goals</span></div>
          <span className="text-xs text-blue-600 mt-1 block">SDGs 6, 7, 11, 12, 13, 15</span>
        </div>
      </div>

      {/* 17 SDG Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {sdgs.map((sdg) => {
          const isPriority = PRIORITY_SDGS.includes(sdg.sdg_number);
          const color = SDG_COLORS[sdg.sdg_number] || '#333';

          return (
            <div
              key={sdg.id || sdg.sdg_number}
              onClick={() => setSelectedSDG(sdg)}
              className={`p-4 rounded-xl border cursor-pointer transition-all hover:shadow-md relative overflow-hidden flex flex-col justify-between h-44 ${
                sdg.has_initiatives ? 'bg-white border-gray-200 hover:border-emerald-400' : 'bg-gray-50/60 border-gray-200 opacity-70'
              }`}
            >
              {/* Top Bar Color Stripe */}
              <div className="absolute top-0 left-0 right-0 h-1.5" style={{ backgroundColor: color }}></div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xl font-black font-mono" style={{ color }}>
                    {sdg.sdg_number}
                  </span>
                  {isPriority && (
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                      PRIORITY
                    </span>
                  )}
                </div>
                <h4 className="text-xs font-bold text-gray-900 line-clamp-2 leading-tight">
                  {sdg.name}
                </h4>
              </div>

              <div className="pt-2 border-t border-gray-100 flex items-center justify-between text-[11px]">
                <span className={`font-semibold ${sdg.has_initiatives ? 'text-emerald-700' : 'text-gray-400'}`}>
                  {sdg.initiative_count || 0} Initiatives
                </span>
                <ArrowUpRight className="w-3.5 h-3.5 text-gray-400" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected SDG Detail Modal / Drawer */}
      {selectedSDG && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-xl border border-gray-200 space-y-5 relative max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-gray-100 pb-4">
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-extrabold text-xl shadow-sm"
                  style={{ backgroundColor: SDG_COLORS[selectedSDG.sdg_number] || '#059669' }}
                >
                  {selectedSDG.sdg_number}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 leading-snug">{selectedSDG.name}</h3>
                  <span className="text-xs text-gray-500 font-mono">UN Sustainable Development Goal {selectedSDG.sdg_number}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedSDG(null)}
                className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">
              {selectedSDG.description}
            </p>

            <div>
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-3">
                Mapped Institutional Actions ({selectedSDG.initiatives?.length || 0})
              </h4>

              {selectedSDG.initiatives && selectedSDG.initiatives.length > 0 ? (
                <div className="space-y-2.5">
                  {selectedSDG.initiatives.map((ini) => (
                    <div key={ini.id} className="p-3 bg-white rounded-xl border border-gray-200 text-xs space-y-1.5">
                      <div className="flex items-center justify-between font-semibold text-gray-900">
                        <span>{ini.name}</span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                          {ini.status}
                        </span>
                      </div>
                      {ini.carbon_reduction_estimate_kgco2e > 0 && (
                        <div className="text-[11px] text-emerald-700 font-mono font-medium flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          Est. Avoided: {ini.carbon_reduction_estimate_kgco2e.toLocaleString()} kg CO₂e/yr
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center text-xs text-gray-400 italic bg-gray-50 rounded-xl border border-gray-100">
                  No active campus initiatives currently mapped to SDG {selectedSDG.sdg_number}.
                </div>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedSDG(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Institutional Gap Analysis */}
      <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-6 space-y-3">
        <div className="flex items-center gap-2 text-amber-900 font-bold text-base">
          <Layers className="w-5 h-5 text-amber-600" />
          Institutional SDG Gap Analysis
        </div>
        <p className="text-xs text-amber-800 leading-relaxed">
          While VESIT demonstrates leadership in environmental and resource goals (Clean Energy, Water, Climate Action, Sustainable Cities), {unmappedCount} goals currently lack explicit campus policy initiatives. Recommended institutional expansions include creating formal ocean/marine conservation awareness partnerships (SDG 14) and expanding gender equity in STEM programs (SDG 5).
        </p>
      </div>
    </div>
  );
};

