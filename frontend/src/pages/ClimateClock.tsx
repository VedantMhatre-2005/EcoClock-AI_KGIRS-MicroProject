import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { ClimateClockData } from '../types';
import { ClimateClockHero } from '../components/climate-clock/ClimateClockHero';
import {
  Clock,
  TrendingDown,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  Calendar,
  Layers,
  ArrowRight
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

export const ClimateClock: React.FC = () => {
  const [clockData, setClockData] = useState<ClimateClockData | null>(null);
  const [modelType, setModelType] = useState<string>('LINEAR');
  const [annualReductionRate, setAnnualReductionRate] = useState<number>(153125);
  const [compoundRatePct, setCompoundRatePct] = useState<number>(14.5);
  const [projectionData, setProjectionData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchClock = async (targetDate?: string) => {
    try {
      setLoading(true);
      const data = await apiService.getClimateClock(targetDate);
      setClockData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjection = async () => {
    try {
      const rate = modelType === 'LINEAR' ? annualReductionRate : compoundRatePct;
      const data = await apiService.getClimateProjection(modelType, 2040, rate);
      setProjectionData(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchClock();
  }, []);

  useEffect(() => {
    fetchProjection();
  }, [modelType, annualReductionRate, compoundRatePct]);

  return (
    <div className="space-y-6">
      {/* Dynamic Climate Clock Hero Component */}
      <ClimateClockHero clockData={clockData} onTargetDateChange={fetchClock} />

      {/* Projection Mathematical Model Controls */}
      <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-stone-100 gap-4">
          <div>
            <h3 className="text-base font-bold text-stone-900 tracking-tight flex items-center gap-2">
              <Layers className="w-4 h-4 text-forest-600" />
              Decarbonization Trajectory Modeling
            </h3>
            <p className="text-xs text-stone-500">
              Select mathematical model to project emissions trajectory against declared net-zero deadline
            </p>
          </div>

          {/* Model Type Selector */}
          <div className="flex bg-stone-100 p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setModelType('LINEAR')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                modelType === 'LINEAR'
                  ? 'bg-white text-forest-700 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              Linear Model: E(t) = E0 - r(t - t0)
            </button>
            <button
              onClick={() => setModelType('COMPOUND')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                modelType === 'COMPOUND'
                  ? 'bg-white text-forest-700 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              Compound Model: E(t) = E0(1 - p)^(t - t0)
            </button>
          </div>
        </div>

        {/* Sliders & Trajectory Parameters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-6">
          {modelType === 'LINEAR' ? (
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-stone-600">Annual Reduction Rate (r):</span>
                <span className="font-mono font-bold text-forest-700">{annualReductionRate.toLocaleString()} kg CO2e/yr</span>
              </div>
              <input
                type="range"
                min="50000"
                max="300000"
                step="5000"
                value={annualReductionRate}
                onChange={(e) => setAnnualReductionRate(Number(e.target.value))}
                className="w-full accent-forest-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-stone-400 font-mono">
                <span>50,000 kg</span>
                <span>Required: 153,125 kg</span>
                <span>300,000 kg</span>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-stone-600">Compound Percentage Rate (p):</span>
                <span className="font-mono font-bold text-forest-700">{compoundRatePct}% per year</span>
              </div>
              <input
                type="range"
                min="5.0"
                max="35.0"
                step="0.5"
                value={compoundRatePct}
                onChange={(e) => setCompoundRatePct(Number(e.target.value))}
                className="w-full accent-forest-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-stone-400 font-mono">
                <span>5%</span>
                <span>Target: 14.5%</span>
                <span>35%</span>
              </div>
            </div>
          )}

          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/60">
            <div className="text-xs text-stone-500 font-medium">Mathematically Projected Net-Zero Year</div>
            <div className="text-2xl font-black font-mono text-stone-900 mt-1">
              {projectionData?.projected_net_zero_year ? projectionData.projected_net_zero_year : 'Never (> 2050)'}
            </div>
            <div className="text-[11px] mt-1 font-semibold">
              {projectionData?.achieves_target_by_deadline ? (
                <span className="text-forest-600">✓ Meets or beats 2040 institutional target</span>
              ) : (
                <span className="text-amber-600">⚠ Insufficient rate: Misses 2040 target</span>
              )}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/60">
            <div className="text-xs text-stone-500 font-medium">Model Formula & Baseline</div>
            <div className="font-mono text-xs font-bold text-stone-800 mt-1">
              {projectionData?.formula || 'E(t) = E0 - r(t - t0)'}
            </div>
            <div className="text-[11px] text-stone-500 mt-1">
              E0 = 2,450,000 kg CO2e (Year 2024 Baseline)
            </div>
          </div>
        </div>

        {/* Projection Trajectory Chart */}
        <div className="h-80 w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={projectionData?.trajectory || []}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
              <YAxis
                tick={{ fontSize: 11, fill: '#64748b' }}
                tickLine={false}
                tickFormatter={(val) => `${val / 1000}k`}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                formatter={(val: any) => [`${Number(val).toLocaleString()} kg CO2e`, 'Projected Emissions']}
              />
              <ReferenceLine x={2040} stroke="#dc2626" strokeDasharray="4 4" label={{ value: 'Target 2040', fill: '#dc2626', fontSize: 11 }} />
              <ReferenceLine y={0} stroke="#10b981" strokeWidth={1.5} />
              <Line
                type="monotone"
                dataKey="emissions_kgco2e"
                stroke="#059669"
                strokeWidth={3}
                dot={{ r: 3, fill: '#059669' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Global Climate Context Clock State (Truthful Representation per Section 11) */}
      <div className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-xs">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 rounded-lg bg-stone-100 flex items-center justify-center text-stone-600">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-stone-900 text-sm">Global Climate Context Clock</h4>
            <p className="text-xs text-stone-500">Global remaining carbon budget countdown indicator</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200/80 flex items-start space-x-3 text-xs text-amber-900">
          <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <div className="font-bold text-amber-950">Explicit Unavailable State (Requirement Section 11)</div>
            <p className="mt-1 leading-relaxed text-amber-800">
              {clockData?.global_context_clock?.message ||
                "Global climate-budget information requires a verified, legitimate external data source (such as the Mercator Research Institute on Global Commons and Climate Change / IPCC API). Because no live external global budget service is configured, EcoClock AI truthfully displays an unavailable state rather than fabricating ungrounded global countdown numbers."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

