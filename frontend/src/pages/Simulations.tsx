import React, { useState, useEffect } from 'react';
import { 
  Sliders, Play, Save, Trash2, ArrowDownRight, Sun, Bus, Trash, 
  Droplet, Layers, AlertCircle, ShieldCheck
} from 'lucide-react';
import { apiService } from '../services/api';
import { SimulationResult } from '../types';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

export const Simulations: React.FC = () => {
  const [scenarioType, setScenarioType] = useState<string>('COMBINED');
  const [params, setParams] = useState<Record<string, any>>({
    solar_kw: 150,
    transport_shift_pct: 30,
    recycling_rate_pct: 60,
    rainwater_additional_litres: 200000
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [savedScenarios, setSavedScenarios] = useState<SimulationResult[]>([]);
  const [scenarioName, setScenarioName] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  // Load saved scenarios on mount
  const loadSaved = async () => {
    try {
      const list = await apiService.listSimulations();
      setSavedScenarios(list || []);
    } catch (err) {
      console.error('Failed to load saved scenarios', err);
    }
  };

  useEffect(() => {
    loadSaved();
    handleRunSimulation();
  }, [scenarioType]);

  const handleRunSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.runSimulation(scenarioType, params);
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Simulation execution failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveScenario = async () => {
    if (!scenarioName.trim()) return;
    try {
      await apiService.saveSimulation(scenarioName, scenarioType, params);
      setScenarioName('');
      setSaveSuccess('Scenario saved to institutional archive.');
      setTimeout(() => setSaveSuccess(null), 3500);
      loadSaved();
    } catch (err: any) {
      setError(err.message || 'Failed to save scenario');
    }
  };

  const handleDeleteSaved = async (id: string) => {
    try {
      await apiService.deleteSimulation(id);
      loadSaved();
    } catch (err: any) {
      setError(err.message || 'Failed to delete scenario');
    }
  };

  const chartData = result ? [
    {
      name: 'Campus Carbon Footprint',
      Baseline: Number(result.baseline_emissions_tonnes_co2e.toFixed(1)),
      Projected: Number(result.projected_emissions_tonnes_co2e.toFixed(1))
    }
  ] : [];

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">Intervention Simulation Engine</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              PHYSICS & FACTOR GROUNDED
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Simulate prospective decarbonization interventions: solar rooftop arrays, transport modal shift, composting diversion, and rainwater storage.
          </p>
        </div>

        {/* Scenario Selection Tabs */}
        <div className="flex flex-wrap bg-gray-100 p-1 rounded-xl border border-gray-200 gap-1">
          {[
            { id: 'COMBINED', label: 'Combined Plan', icon: Layers },
            { id: 'SOLAR_EXPANSION', label: 'Solar Expansion', icon: Sun },
            { id: 'TRANSPORT_MODAL_SHIFT', label: 'Transport Shift', icon: Bus },
            { id: 'WASTE_RECYCLING', label: 'Waste Circularity', icon: Trash },
            { id: 'WATER_CONSERVATION', label: 'Water Harvesting', icon: Droplet }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setScenarioType(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  scenarioType === item.id
                    ? 'bg-white text-emerald-800 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="w-3.5 h-3.5 text-emerald-600" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Simulation Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Interactive Controls */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <h3 className="font-bold text-gray-900 text-sm flex items-center gap-2">
              <Sliders className="w-4 h-4 text-emerald-600" />
              Scenario Parameters
            </h3>
            <span className="text-xs text-gray-400">Deterministic Model</span>
          </div>

          <div className="space-y-5">
            {/* Solar Capacity Slider */}
            {(scenarioType === 'COMBINED' || scenarioType === 'SOLAR_EXPANSION') && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-gray-700 flex items-center gap-1.5">
                    <Sun className="w-3.5 h-3.5 text-amber-500" /> Additional Solar Capacity:
                  </span>
                  <span className="font-mono font-bold text-emerald-700">{params.solar_kw || 150} kWp</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="500"
                  step="10"
                  value={params.solar_kw || 150}
                  onChange={(e) => setParams({ ...params, solar_kw: Number(e.target.value) })}
                  className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
                />
                <div className="flex justify-between text-[10px] text-gray-400">
                  <span>0 kW</span>
                  <span>250 kW</span>
                  <span>500 kW</span>
                </div>
              </div>
            )}

            {/* Transport Modal Shift Slider */}
            {(scenarioType === 'COMBINED' || scenarioType === 'TRANSPORT_MODAL_SHIFT') && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-gray-700 flex items-center gap-1.5">
                    <Bus className="w-3.5 h-3.5 text-blue-500" /> Private Shift to Rail/EV:
                  </span>
                  <span className="font-mono font-bold text-emerald-700">{params.transport_shift_pct || 30}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="80"
                  step="5"
                  value={params.transport_shift_pct || 30}
                  onChange={(e) => setParams({ ...params, transport_shift_pct: Number(e.target.value) })}
                  className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
                />
                <div className="flex justify-between text-[10px] text-gray-400">
                  <span>0%</span>
                  <span>40%</span>
                  <span>80%</span>
                </div>
              </div>
            )}

            {/* Waste Recycling & Composting Slider */}
            {(scenarioType === 'COMBINED' || scenarioType === 'WASTE_RECYCLING') && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-gray-700 flex items-center gap-1.5">
                    <Trash className="w-3.5 h-3.5 text-emerald-500" /> Target Waste Diversion:
                  </span>
                  <span className="font-mono font-bold text-emerald-700">{params.recycling_rate_pct || 60}%</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="90"
                  step="5"
                  value={params.recycling_rate_pct || 60}
                  onChange={(e) => setParams({ ...params, recycling_rate_pct: Number(e.target.value) })}
                  className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
                />
                <div className="flex justify-between text-[10px] text-gray-400">
                  <span>20%</span>
                  <span>55%</span>
                  <span>90%</span>
                </div>
              </div>
            )}

            {/* Rainwater Harvesting Capacity Slider */}
            {(scenarioType === 'COMBINED' || scenarioType === 'WATER_CONSERVATION') && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-gray-700 flex items-center gap-1.5">
                    <Droplet className="w-3.5 h-3.5 text-teal-500" /> Additional Rainwater Cistern:
                  </span>
                  <span className="font-mono font-bold text-emerald-700">
                    {((params.rainwater_additional_litres || 200000) / 1000).toFixed(0)}k Litres
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="500000"
                  step="25000"
                  value={params.rainwater_additional_litres || 200000}
                  onChange={(e) => setParams({ ...params, rainwater_additional_litres: Number(e.target.value) })}
                  className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
                />
                <div className="flex justify-between text-[10px] text-gray-400">
                  <span>0 L</span>
                  <span>250k L</span>
                  <span>500k L</span>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={loading}
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg text-xs flex items-center justify-center gap-2 shadow-sm transition-colors"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                <span>Re-calculate Impact</span>
              </>
            )}
          </button>
        </div>

        {/* Right: Simulation Results & Impact Cards */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-800 text-sm">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <div>{error}</div>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Headline Impact Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                  <div className="text-xs uppercase text-gray-500 font-semibold mb-1">Baseline Emissions</div>
                  <div className="text-2xl font-bold text-gray-800">
                    {result.baseline_emissions_tonnes_co2e.toFixed(1)} <span className="text-sm font-normal text-gray-500">tCO₂e</span>
                  </div>
                  <span className="text-xs text-gray-400 mt-1 block">Current campus footprint</span>
                </div>

                <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                  <div className="text-xs uppercase text-emerald-700 font-semibold mb-1">Projected Decarbonized</div>
                  <div className="text-2xl font-bold text-emerald-600">
                    {result.projected_emissions_tonnes_co2e.toFixed(1)} <span className="text-sm font-normal text-gray-500">tCO₂e</span>
                  </div>
                  <span className="text-xs text-emerald-700 mt-1 block">Post-intervention balance</span>
                </div>

                <div className="bg-emerald-50 p-5 rounded-xl border border-emerald-200 shadow-sm">
                  <div className="text-xs uppercase text-emerald-800 font-bold mb-1 flex items-center justify-between">
                    <span>Avoided Carbon</span>
                    <ArrowDownRight className="w-4 h-4 text-emerald-700" />
                  </div>
                  <div className="text-3xl font-extrabold text-emerald-700">
                    {result.percentage_reduction.toFixed(1)}%
                  </div>
                  <span className="text-xs text-emerald-800 mt-1 block">
                    -{(result.reduction_tonnes_co2e).toFixed(1)} tCO₂e/yr saved
                  </span>
                </div>
              </div>

              {/* Before / After Comparison Chart */}
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-3">
                <h4 className="font-bold text-gray-900 text-sm">Baseline vs Projected Campus Emissions (tCO₂e/yr)</h4>
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                      <YAxis stroke="#6b7280" fontSize={11} />
                      <Tooltip
                        formatter={(val: number) => [`${val} tCO₂e`, '']}
                        contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px' }}
                      />
                      <Legend />
                      <Bar dataKey="Baseline" fill="#9ca3af" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Projected" fill="#059669" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Resource Savings Summary */}
              {result.resource_savings && Object.keys(result.resource_savings).length > 0 && (
                <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
                  <h4 className="font-bold text-gray-900 text-xs uppercase tracking-wider">Estimated Resource Gains</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    {Object.entries(result.resource_savings).map(([k, v]) => (
                      <div key={k} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                        <div className="text-gray-500 capitalize">{k.replace(/_/g, ' ')}</div>
                        <div className="font-bold font-mono text-gray-900 text-sm mt-0.5">
                          {typeof v === 'number' ? v.toLocaleString() : String(v)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Save Scenario Bar */}
              <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 flex flex-col sm:flex-row gap-3 items-center justify-between">
                <div className="flex-1 w-full">
                  <input
                    type="text"
                    value={scenarioName}
                    onChange={(e) => setScenarioName(e.target.value)}
                    placeholder="Enter scenario name (e.g. Phase 2 2027 Master Plan)..."
                    className="w-full px-3 py-1.5 text-xs bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  />
                </div>
                <button
                  onClick={handleSaveScenario}
                  disabled={!scenarioName.trim()}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors whitespace-nowrap"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save Scenario
                </button>
              </div>

              {saveSuccess && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 font-medium flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  {saveSuccess}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Saved Scenarios Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-gray-900 text-base">Archived Institutional Scenarios</h3>
            <p className="text-xs text-gray-500 mt-0.5">Persistent scenarios saved for administrative planning reviews.</p>
          </div>
          <span className="text-xs bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full font-mono font-semibold">
            {savedScenarios.length} Saved
          </span>
        </div>

        {savedScenarios.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-600">
              <thead className="bg-gray-50 uppercase text-gray-700 font-semibold border-b border-gray-200">
                <tr>
                  <th className="py-3 px-6">Scenario Name</th>
                  <th className="py-3 px-6">Type</th>
                  <th className="py-3 px-6 text-right">Baseline (tCO₂e)</th>
                  <th className="py-3 px-6 text-right">Projected (tCO₂e)</th>
                  <th className="py-3 px-6 text-right">Avoided %</th>
                  <th className="py-3 px-6 text-right">Avoided tCO₂e</th>
                  <th className="py-3 px-6 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {savedScenarios.map((sc) => (
                  <tr key={sc.id} className="hover:bg-gray-50">
                    <td className="py-3.5 px-6 font-semibold text-gray-900">{sc.name || 'Untitled Scenario'}</td>
                    <td className="py-3.5 px-6 font-mono text-gray-500">{sc.scenario_type}</td>
                    <td className="py-3.5 px-6 text-right font-mono">{sc.baseline_emissions_tonnes_co2e.toFixed(1)}</td>
                    <td className="py-3.5 px-6 text-right font-mono font-bold text-emerald-700">{sc.projected_emissions_tonnes_co2e.toFixed(1)}</td>
                    <td className="py-3.5 px-6 text-right font-mono font-bold text-emerald-600">
                      -{sc.percentage_reduction.toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-6 text-right font-mono">{sc.reduction_tonnes_co2e.toFixed(1)}</td>
                    <td className="py-3.5 px-6 text-center">
                      <button
                        onClick={() => sc.id && handleDeleteSaved(sc.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 rounded hover:bg-red-50 transition-colors"
                        title="Delete Scenario"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-gray-400 italic">
            No saved scenarios yet. Adjust the parameter sliders above and click "Save Scenario" to persist an institutional plan.
          </div>
        )}
      </div>
    </div>
  );
};

