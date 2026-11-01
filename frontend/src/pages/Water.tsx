import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { WaterMetrics } from '../types';
import { Droplets, CloudRain, ShieldCheck, Building2, TrendingDown } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

export const Water: React.FC = () => {
  const [waterData, setWaterData] = useState<WaterMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchWater = async () => {
      try {
        setLoading(true);
        const data = await apiService.getWaterSummary();
        setWaterData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchWater();
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
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="text-xs text-stone-500 font-medium">Total Municipal Demand (24m)</div>
          <div className="text-3xl font-black font-mono text-stone-900 mt-1">
            {((waterData?.total_consumption_litres || 0) / 1000000).toFixed(1)}
            <span className="text-xs font-normal text-stone-500 ml-1">Million Litres</span>
          </div>
          <div className="text-[11px] text-stone-500 mt-1">Piped municipal supply</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-teal-200/70 bg-teal-50/20 shadow-xs">
          <div className="text-xs text-teal-900 font-semibold flex items-center gap-1">
            <CloudRain className="w-4 h-4 text-teal-600" />
            Rainwater Harvested
          </div>
          <div className="text-3xl font-black font-mono text-teal-950 mt-1">
            {((waterData?.total_rainwater_harvested_litres || 0) / 1000000).toFixed(1)}
            <span className="text-xs font-normal text-teal-700 ml-1">Million Litres</span>
          </div>
          <div className="text-[11px] text-teal-700 mt-1 font-semibold">
            {waterData?.rainwater_replacement_rate}% freshwater replacement
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="text-xs text-stone-500 font-medium">Daily Intensity / Student</div>
          <div className="text-3xl font-black font-mono text-stone-900 mt-1">
            41.2
            <span className="text-xs font-normal text-stone-500 ml-1">L / day</span>
          </div>
          <div className="text-[11px] text-stone-500 mt-1">Based on 3,200 campus population</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-stone-200/80 shadow-xs">
          <div className="text-xs text-stone-500 font-medium">Target TRG_WATER_NEUTRAL</div>
          <div className="text-3xl font-black font-mono text-cyan-700 mt-1">
            -30%
          </div>
          <div className="text-[11px] text-cyan-600 font-semibold mt-1">
            Reduction target by 2029
          </div>
        </div>
      </div>

      {/* Monthly Trends */}
      <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="font-bold text-base text-stone-900">Monthly Water Consumption & Monsoon Harvesting</h4>
            <p className="text-xs text-stone-500">Peak rainwater harvesting yield during monsoon season (June to September)</p>
          </div>
          <span className="text-xs px-2 py-0.5 rounded-md bg-stone-100 text-stone-600 font-mono">Litres/month</span>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={waterData?.monthly_trends || []}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              <Bar dataKey="consumption_litres" name="Freshwater Consumed" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="rainwater_harvested_litres" name="Rainwater Harvested" fill="#0d9488" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Building-Wise Breakdown */}
      <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
        <h4 className="font-bold text-base text-stone-900 mb-1">Building-Wise Water Demand (2024 Baseline)</h4>
        <p className="text-xs text-stone-500 mb-4">Breakdown across canteen kitchen, academic classrooms, labs, and admin block</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {waterData?.building_breakdown.map((b) => (
            <div key={b.building_id} className="p-4 rounded-2xl bg-stone-50 border border-stone-200/60">
              <div className="text-xs font-bold text-stone-900 flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-cyan-600" />
                {b.building_name}
              </div>
              <div className="text-xl font-mono font-black text-stone-900 mt-2">
                {(b.consumption_litres / 1000000).toFixed(2)} <span className="text-xs font-normal text-stone-500">M L</span>
              </div>
              <div className="text-[11px] text-teal-700 font-semibold mt-1">
                Harvested: {(b.rainwater_harvested_litres / 1000000).toFixed(2)} M L
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

