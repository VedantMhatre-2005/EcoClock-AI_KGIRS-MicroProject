import React, { useEffect, useState } from 'react';
import { Trash2, Recycle, Leaf, AlertCircle, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import { WasteMetrics } from '../types';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

export const Waste: React.FC = () => {
  const [data, setData] = useState<WasteMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await apiService.getWasteSummary();
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load waste data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-xl flex items-center gap-4 text-red-800">
        <AlertCircle className="w-8 h-8 text-red-600" />
        <div>
          <h3 className="font-semibold text-lg">Error Loading Waste Analytics</h3>
          <p className="text-sm">{error || 'No data returned from server.'}</p>
        </div>
      </div>
    );
  }

  const divertedTotal = data.recyclable_kg + data.composted_kg;
  const diversionRate = data.total_waste_kg > 0 ? ((divertedTotal / data.total_waste_kg) * 100).toFixed(1) : '0';

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">Waste Management & Circularity</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              SYNTHETIC DEMO
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Tracking solid waste segregation, wet-waste on-site aerobic composting, dry recycling, and landfill diversion at VESIT Green Campus.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5">
            <Leaf className="w-4 h-4 text-amber-600" />
            Zero Single-Use Plastic Mandate Active
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Total Generated</span>
            <Trash2 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {(data.total_waste_kg / 1000).toFixed(2)} <span className="text-sm font-normal text-gray-500">Tonnes</span>
          </div>
          <span className="text-xs text-gray-500 mt-1 block">{data.total_waste_kg.toLocaleString()} kg total</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Dry Recyclable</span>
            <Recycle className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {(data.recyclable_kg / 1000).toFixed(2)} <span className="text-sm font-normal text-gray-500">Tonnes</span>
          </div>
          <span className="text-xs text-blue-600 mt-1 block">Paper, cardboard & e-waste</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Composted (Wet)</span>
            <Leaf className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-emerald-600">
            {(data.composted_kg / 1000).toFixed(2)} <span className="text-sm font-normal text-gray-500">Tonnes</span>
          </div>
          <span className="text-xs text-emerald-600 mt-1 block">On-site organic pit</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Non-Recyclable</span>
            <AlertCircle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-amber-700">
            {(data.non_recyclable_kg / 1000).toFixed(2)} <span className="text-sm font-normal text-gray-500">Tonnes</span>
          </div>
          <span className="text-xs text-amber-600 mt-1 block">Sent to municipal landfill</span>
        </div>

        <div className="bg-emerald-50 p-5 rounded-xl border border-emerald-200 shadow-sm">
          <div className="flex items-center justify-between text-emerald-700 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Circularity / Diversion</span>
            <ArrowUpRight className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-700">
            {diversionRate}%
          </div>
          <span className="text-xs text-emerald-800 mt-1 block">Diverted from Deonar landfill</span>
        </div>
      </div>

      {/* 24-Month Waste Generation & Diversion Trend Chart */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-gray-900">24-Month Waste Stream Trajectory</h3>
            <p className="text-sm text-gray-500">
              Monthly breakdown showing composting growth, recycling initiatives, and residual landfill volume.
            </p>
          </div>
          <div className="text-xs text-gray-400">Unit: Kilograms (kg)</div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.monthly_trends} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" stroke="#6b7280" fontSize={11} tickFormatter={(val) => val.slice(0, 7)} />
              <YAxis stroke="#6b7280" fontSize={11} />
              <Tooltip
                formatter={(val: number) => [`${val.toLocaleString()} kg`, '']}
                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px' }}
              />
              <Legend verticalAlign="top" height={36} />
              <Area type="monotone" dataKey="composted_kg" name="Composted Organic Waste" stackId="1" stroke="#059669" fill="#10b981" fillOpacity={0.6} />
              <Area type="monotone" dataKey="recyclable_kg" name="Dry Recyclable Material" stackId="1" stroke="#2563eb" fill="#60a5fa" fillOpacity={0.6} />
              <Area type="monotone" dataKey="non_recyclable_kg" name="Landfill Residuals" stackId="1" stroke="#d97706" fill="#fcd34d" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Campus Waste Initiatives & Protocols */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-700">
            <Leaf className="w-5 h-5" />
          </div>
          <h4 className="font-bold text-gray-900">Aerobic Pit Composting</h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            The VESIT Canteen and botanical garden kitchen waste is routed directly to three aerated compost bins, producing nutrient-rich organic fertilizer used across all campus grounds.
          </p>
          <div className="pt-2 border-t border-gray-100 flex items-center gap-2 text-xs text-emerald-700 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Eliminates ~0.21 kg CO₂e per kg composted
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700">
            <Recycle className="w-5 h-5" />
          </div>
          <h4 className="font-bold text-gray-900">Authorized E-Waste Recycling</h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            Obsolete laboratory electronics, PCB boards, and UPS batteries are collected biannually and handed over to Maharashtra Pollution Control Board (MPCB) certified e-waste aggregators.
          </p>
          <div className="pt-2 border-t border-gray-100 flex items-center gap-2 text-xs text-blue-700 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-blue-600" />
            MPCB Certified Chain-of-Custody
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center text-amber-700">
            <Trash2 className="w-5 h-5" />
          </div>
          <h4 className="font-bold text-gray-900">Single-Use Plastic Ban</h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            Strict campus policy prohibiting single-use plastic cups, water bottles, and disposable cutlery. Water refill fountains are positioned across all 7 institutional buildings.
          </p>
          <div className="pt-2 border-t border-gray-100 flex items-center gap-2 text-xs text-amber-700 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-amber-600" />
            92% Compliance in Canteen Audits
          </div>
        </div>
      </div>
    </div>
  );
};

