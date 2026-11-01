import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { EmissionsInventory } from '../types';
import {
  CloudLightning,
  Layers,
  Building2,
  Calendar,
  PieChart as PieIcon,
  HelpCircle,
  TrendingDown
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';

const SCOPE_COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

export const Emissions: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(2024);
  const [inventory, setInventory] = useState<EmissionsInventory | null>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [invData, trendsData] = await Promise.all([
          apiService.getEmissionsSummary(selectedYear),
          apiService.getEmissionsTrends()
        ]);
        setInventory(invData);
        setTrends(trendsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedYear]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-5 h-5 border-2 border-forest-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const scopes = inventory?.scopes;
  const pieData = [
    { name: 'Scope 1 (Diesel)', value: scopes?.scope_1.emissions_kgco2e || 0, color: '#f59e0b' },
    { name: 'Scope 2 (Grid Electricity)', value: scopes?.scope_2.emissions_kgco2e || 0, color: '#3b82f6' },
    { name: 'Scope 3 (Commuting/Waste/Water)', value: scopes?.scope_3.emissions_kgco2e || 0, color: '#10b981' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <CloudLightning className="w-5 h-5 text-forest-600" />
            <h3 className="font-extrabold text-xl text-stone-900 tracking-tight">Institutional Carbon Accounting</h3>
          </div>
          <p className="text-xs text-stone-500 mt-1">
            Standard GHG Protocol Scope 1, Scope 2, and Scope 3 footprint for VESIT Green Campus
          </p>
        </div>

        {/* Year Selector */}
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-stone-400" />
          <span className="text-xs text-stone-600">Reporting Year:</span>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="px-3 py-1.5 text-xs font-semibold bg-stone-50 border border-stone-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-forest-500"
          >
            <option value={2024}>2024 (Baseline Year)</option>
            <option value={2025}>2025 (Progress Year)</option>
          </select>
        </div>
      </div>

      {/* Overview Metric Totals */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="text-xs text-stone-500 font-medium">Total Institutional Footprint</div>
          <div className="text-3xl font-black font-mono text-stone-900 mt-1">
            {inventory?.total_emissions_tonnes_co2e.toLocaleString()}
            <span className="text-xs font-normal text-stone-500 ml-1">t CO2e</span>
          </div>
          <div className="text-[11px] text-stone-500 mt-1 font-mono">
            {inventory?.total_emissions_kgco2e.toLocaleString()} kg CO2e
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-amber-200/60 bg-amber-50/20 shadow-xs">
          <div className="text-xs text-amber-900 font-semibold">Scope 1 (Direct Combustion)</div>
          <div className="text-2xl font-bold font-mono text-amber-950 mt-1">
            {scopes?.scope_1.tonnes_co2e} <span className="text-xs font-normal text-amber-700">t CO2e</span>
          </div>
          <div className="text-[11px] text-amber-700 mt-1">
            {scopes?.scope_1.percentage}% of campus total (Diesel DG)
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-blue-200/60 bg-blue-50/20 shadow-xs">
          <div className="text-xs text-blue-900 font-semibold">Scope 2 (Purchased Electricity)</div>
          <div className="text-2xl font-bold font-mono text-blue-950 mt-1">
            {scopes?.scope_2.tonnes_co2e} <span className="text-xs font-normal text-blue-700">t CO2e</span>
          </div>
          <div className="text-[11px] text-blue-700 mt-1">
            {scopes?.scope_2.percentage}% of campus total (Grid CEA factor)
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-emerald-200/60 bg-emerald-50/20 shadow-xs">
          <div className="text-xs text-emerald-900 font-semibold">Scope 3 (Commute, Waste, Water)</div>
          <div className="text-2xl font-bold font-mono text-emerald-950 mt-1">
            {scopes?.scope_3.tonnes_co2e} <span className="text-xs font-normal text-emerald-700">t CO2e</span>
          </div>
          <div className="text-[11px] text-emerald-700 mt-1">
            {scopes?.scope_3.percentage}% of campus total
          </div>
        </div>
      </div>

      {/* Charts: Scope Distribution Pie & Scope 3 Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scope Distribution Pie */}
        <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
          <h4 className="font-bold text-base text-stone-900 mb-1">GHG Protocol Scope Distribution</h4>
          <p className="text-xs text-stone-500 mb-4">Proportion of Scope 1, Scope 2, and Scope 3 emissions</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                  formatter={(val: any) => [`${Number(val).toLocaleString()} kg CO2e`, 'Emissions']}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Scope 3 Detailed Components */}
        <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
          <h4 className="font-bold text-base text-stone-900 mb-1">Scope 3 Activity Distribution</h4>
          <p className="text-xs text-stone-500 mb-4">Commuter travel, municipal solid waste, and embodied water pumping</p>
          <div className="space-y-4 pt-2">
            {[
              {
                label: 'Student & Staff Commuting',
                kg: scopes?.scope_3.breakdown?.commuting_kgco2e || 580000,
                pct: 80.6,
                desc: 'Suburban rail, municipal buses, private cars, two-wheelers'
              },
              {
                label: 'Municipal Solid Waste Disposal',
                kg: scopes?.scope_3.breakdown?.waste_kgco2e || 115000,
                pct: 16.0,
                desc: 'Unsegregated waste sent to landfill less composting/recycling credits'
              },
              {
                label: 'Embodied Water Pumping Energy',
                kg: scopes?.scope_3.breakdown?.water_embodied_kgco2e || 24688,
                pct: 3.4,
                desc: 'Electricity consumed in municipal treatment and pipeline transmission'
              }
            ].map((item, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-stone-50 border border-stone-200/60">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-semibold text-xs text-stone-900">{item.label}</span>
                  <span className="font-mono font-bold text-xs text-stone-800">{item.kg.toLocaleString()} kg CO2e</span>
                </div>
                <div className="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
                  <div className="bg-forest-600 h-full rounded-full" style={{ width: `${item.pct}%` }}></div>
                </div>
                <div className="text-[11px] text-stone-500 mt-1">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

