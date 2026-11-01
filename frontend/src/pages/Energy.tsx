import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { EnergyMetrics } from '../types';
import { Zap, Sun, ShieldAlert, Sparkles, Building2 } from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';

export const Energy: React.FC = () => {
  const [energyData, setEnergyData] = useState<EnergyMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchEnergy = async () => {
      try {
        setLoading(true);
        const data = await apiService.getEnergySummary();
        setEnergyData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchEnergy();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-5 h-5 border-2 border-forest-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="text-xs text-stone-500 font-medium">Total Electricity (24m)</div>
          <div className="text-3xl font-black font-mono text-stone-900 mt-1">
            {energyData?.total_electricity_kwh.toLocaleString()}
            <span className="text-xs font-normal text-stone-500 ml-1">kWh</span>
          </div>
          <div className="text-[11px] text-stone-500 mt-1">Campus aggregate demand</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-emerald-200/70 bg-emerald-50/20 shadow-xs">
          <div className="text-xs text-emerald-900 font-semibold flex items-center gap-1">
            <Sun className="w-4 h-4 text-emerald-600" />
            Solar Clean Generation
          </div>
          <div className="text-3xl font-black font-mono text-emerald-950 mt-1">
            {energyData?.solar_generation_kwh.toLocaleString()}
            <span className="text-xs font-normal text-emerald-700 ml-1">kWh</span>
          </div>
          <div className="text-[11px] text-emerald-700 mt-1 font-semibold">
            {energyData?.renewable_percentage}% of total electricity
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="text-xs text-stone-500 font-medium">Grid Electricity Purchase</div>
          <div className="text-3xl font-black font-mono text-stone-900 mt-1">
            {energyData?.grid_electricity_kwh.toLocaleString()}
            <span className="text-xs font-normal text-stone-500 ml-1">kWh</span>
          </div>
          <div className="text-[11px] text-stone-500 mt-1">Displaced by on-site PV</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="text-xs text-stone-500 font-medium">Renewable Target (2030)</div>
          <div className="text-3xl font-black font-mono text-forest-700 mt-1">
            50%
          </div>
          <div className="text-[11px] text-forest-600 font-semibold mt-1">
            Target TRG_RENEWABLE in progress
          </div>
        </div>
      </div>

      {/* Monthly Generation Chart */}
      <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="font-bold text-base text-stone-900">24-Month Energy Dynamics: Grid vs Rooftop Solar</h4>
            <p className="text-xs text-stone-500">Monthly time-series displaying seasonal solar generation peak vs summer cooling demand</p>
          </div>
          <span className="text-xs px-2 py-0.5 rounded-md bg-stone-100 text-stone-600 font-mono">kWh/month</span>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={energyData?.monthly_trends || []}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              <Area type="monotone" dataKey="grid_kwh" name="Grid Electricity" stroke="#3b82f6" fill="#bfdbfe" fillOpacity={0.6} />
              <Area type="monotone" dataKey="solar_kwh" name="Solar Electricity" stroke="#10b981" fill="#a7f3d0" fillOpacity={0.8} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Building-Wise Energy Table & Chart */}
      <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
        <h4 className="font-bold text-base text-stone-900 mb-1">Building-Level Annual Energy Breakdown (2024 Baseline)</h4>
        <p className="text-xs text-stone-500 mb-4">Consumption, rooftop solar contribution, and Scope 2 emissions across campus blocks</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-stone-50 text-stone-600 uppercase text-[10px] font-bold border-b border-stone-200">
              <tr>
                <th className="py-3 px-4">Building Name</th>
                <th className="py-3 px-4">ID</th>
                <th className="py-3 px-4">Total Demand (kWh)</th>
                <th className="py-3 px-4">Solar Generated (kWh)</th>
                <th className="py-3 px-4">Solar Share (%)</th>
                <th className="py-3 px-4">Grid Emissions (t CO2e)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 font-mono">
              {energyData?.building_breakdown.map((b) => {
                const pct = b.total_kwh > 0 ? ((b.solar_kwh / b.total_kwh) * 100).toFixed(1) : '0.0';
                return (
                  <tr key={b.building_id} className="hover:bg-stone-50/50">
                    <td className="py-3 px-4 font-sans font-semibold text-stone-900 flex items-center gap-2">
                      <Building2 className="w-3.5 h-3.5 text-stone-400" />
                      {b.building_name}
                    </td>
                    <td className="py-3 px-4 text-stone-500">{b.building_id}</td>
                    <td className="py-3 px-4 text-stone-800">{b.total_kwh.toLocaleString()}</td>
                    <td className="py-3 px-4 text-emerald-700 font-bold">{b.solar_kwh.toLocaleString()}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        Number(pct) > 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-stone-100 text-stone-500'
                      }`}>
                        {pct}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-stone-800">{(b.emissions_kgco2e / 1000).toFixed(1)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

