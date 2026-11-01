import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { DashboardSummary, ClimateClockData } from '../types';
import { ClimateClockHero } from '../components/climate-clock/ClimateClockHero';
import {
  CloudLightning,
  Zap,
  Droplets,
  Trash2,
  Globe,
  TrendingDown,
  ArrowUpRight,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, PieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#10b981', '#0d9488', '#3b82f6', '#f59e0b', '#8b5cf6'];

export const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [clockData, setClockData] = useState<ClimateClockData | null>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [sumRes, clockRes, trendsRes] = await Promise.all([
          apiService.getDashboardSummary(),
          apiService.getClimateClock(),
          apiService.getDashboardTrends()
        ]);
        setSummary(sumRes);
        setClockData(clockRes);
        setTrends(trendsRes);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleTargetChange = async (newDate: string) => {
    try {
      const updatedClock = await apiService.getClimateClock(newDate);
      setClockData(updatedClock);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-3 text-stone-500 font-medium">
          <div className="w-5 h-5 border-2 border-forest-600 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading campus sustainability data...</span>
        </div>
      </div>
    );
  }

  const kpis = summary?.kpis;

  return (
    <div className="space-y-6">
      {/* Central Interactive College Climate Clock Hero */}
      <ClimateClockHero clockData={clockData} onTargetDateChange={handleTargetChange} />

      {/* KPI Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Total Carbon */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-xs font-medium">Carbon Emissions</span>
            <CloudLightning className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-stone-900 tracking-tight">
            {kpis?.total_carbon_emissions_tonnes || 0}
            <span className="text-xs font-normal text-stone-500 ml-1">t CO2e</span>
          </div>
          <div className="text-[11px] font-semibold text-emerald-600 mt-1 flex items-center">
            <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
            {kpis?.emissions_reduction_percentage || 0}% from baseline
          </div>
        </div>

        {/* Electricity */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-xs font-medium">Electricity Consumed</span>
            <Zap className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-stone-900 tracking-tight">
            {kpis?.total_electricity_mwh || 0}
            <span className="text-xs font-normal text-stone-500 ml-1">MWh</span>
          </div>
          <div className="text-[11px] text-stone-500 mt-1 font-medium">
            24-month total
          </div>
        </div>

        {/* Solar Generation */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-xs font-medium">Solar Clean Energy</span>
            <Sparkles className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-stone-900 tracking-tight">
            {kpis?.renewable_energy_percentage || 0}%
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {kpis?.solar_generation_mwh || 0} MWh generated
          </div>
        </div>

        {/* Water */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-xs font-medium">Water Consumption</span>
            <Droplets className="w-4 h-4 text-cyan-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-stone-900 tracking-tight">
            {kpis?.total_water_consumption_million_litres || 0}
            <span className="text-xs font-normal text-stone-500 ml-1">M L</span>
          </div>
          <div className="text-[11px] text-cyan-700 font-medium mt-1">
            {kpis?.rainwater_harvested_million_litres || 0} M L harvested
          </div>
        </div>

        {/* Waste Recycling Rate */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-xs font-medium">Waste Diversion</span>
            <Trash2 className="w-4 h-4 text-teal-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-stone-900 tracking-tight">
            {kpis?.waste_diversion_rate || 0}%
          </div>
          <div className="text-[11px] text-teal-700 font-medium mt-1">
            Target: 85% by 2028
          </div>
        </div>

        {/* Initiatives */}
        <div className="bg-white p-4 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between text-stone-500 mb-2">
            <span className="text-xs font-medium">Sustainability Action</span>
            <Globe className="w-4 h-4 text-forest-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-stone-900 tracking-tight">
            {kpis?.active_sustainability_initiatives || 0} / {kpis?.total_sustainability_initiatives || 0}
          </div>
          <div className="text-[11px] text-forest-700 font-medium mt-1">
            Active Projects Aligned
          </div>
        </div>
      </div>

      {/* Main Charts: Emissions & Energy Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Energy & Solar Generation Chart */}
        <div className="bg-white p-6 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="font-bold text-base text-stone-900">Monthly Electricity & Solar Trajectory</h4>
              <p className="text-xs text-stone-500">24-month timeline showing grid electricity vs on-site rooftop solar</p>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-md bg-stone-100 text-stone-600 font-mono">kWh/month</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends?.energy_monthly || []}>
                <defs>
                  <linearGradient id="colorGrid" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.6}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                <Area type="monotone" dataKey="grid_kwh" name="Grid Electricity" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorGrid)" />
                <Area type="monotone" dataKey="solar_kwh" name="Solar Generated" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorSolar)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Water Consumption & Rainwater Harvested */}
        <div className="bg-white p-6 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="font-bold text-base text-stone-900">Water Consumption & Monsoon Harvesting</h4>
              <p className="text-xs text-stone-500">Seasonal rainwater cistern capture displacing municipal supply</p>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-md bg-stone-100 text-stone-600 font-mono">Litres</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends?.water_monthly || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                <Bar dataKey="consumption_litres" name="Freshwater Demand" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="rainwater_harvested_litres" name="Harvested Rainwater" fill="#0d9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* AI Grounded Insights Card */}
      <div className="bg-gradient-to-r from-forest-50 via-teal-50/40 to-white p-6 rounded-2xl border border-forest-200/80 shadow-xs">
        <div className="flex items-center space-x-2 text-forest-800 font-bold text-sm mb-2">
          <Sparkles className="w-4 h-4 text-forest-600" />
          <span>GraphRAG Evidence Summary</span>
        </div>
        <p className="text-stone-700 text-sm leading-relaxed">
          VESIT Green Campus achieved a measured <span className="font-semibold text-forest-900">5.8% reduction</span> in operational carbon emissions from the 2024 baseline (2,450 t CO2e to 2,308 t CO2e in 2025). The 220 kWp Phase-1 Rooftop Solar installation displaced 312,400 kWh of grid electricity. Expanding Phase-2 solar over the Auditorium and Parking Canopy (200 kWp) will meet 28% of campus load, advancing SDG 7 and SDG 13.
        </p>
      </div>
    </div>
  );
};

