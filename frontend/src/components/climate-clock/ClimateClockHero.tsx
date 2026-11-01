import React, { useState, useEffect } from 'react';
import { ClimateClockData } from '../../types';
import { Clock, AlertTriangle, ShieldCheck, TrendingDown, Calendar, Info } from 'lucide-react';

interface ClimateClockHeroProps {
  clockData: ClimateClockData | null;
  onTargetDateChange?: (date: string) => void;
}

export const ClimateClockHero: React.FC<ClimateClockHeroProps> = ({ clockData, onTargetDateChange }) => {
  const [secondsRemaining, setSecondsRemaining] = useState<number>(0);
  const [editingTarget, setEditingTarget] = useState<boolean>(false);
  const [targetInput, setTargetInput] = useState<string>('2040-12-31');

  const iclock = clockData?.institution_clock;

  useEffect(() => {
    if (iclock?.countdown) {
      setTargetInput(iclock.target_date);
      // Calculate total seconds until target date
      const targetTime = new Date(`${iclock.target_date}T00:00:00Z`).getTime();
      const updateSeconds = () => {
        const now = new Date().getTime();
        const diff = Math.max(0, Math.floor((targetTime - now) / 1000));
        setSecondsRemaining(diff);
      };
      updateSeconds();
      const interval = setInterval(updateSeconds, 1000);
      return () => clearInterval(interval);
    }
  }, [iclock?.target_date]);

  // Breakdown secondsRemaining
  const years = Math.floor(secondsRemaining / (365.25 * 86400));
  const remAfterYears = secondsRemaining % Math.floor(365.25 * 86400);
  const months = Math.floor(remAfterYears / (30.44 * 86400));
  const remAfterMonths = remAfterYears % Math.floor(30.44 * 86400);
  const days = Math.floor(remAfterMonths / 86400);
  const remAfterDays = remAfterMonths % 86400;
  const hours = Math.floor(remAfterDays / 3600);
  const minutes = Math.floor((remAfterDays % 3600) / 60);
  const seconds = remAfterDays % 60;

  const handleApplyTarget = (e: React.FormEvent) => {
    e.preventDefault();
    if (onTargetDateChange && targetInput) {
      onTargetDateChange(targetInput);
      setEditingTarget(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-emerald-100 p-6 lg:p-8 shadow-sm relative overflow-hidden">
      {/* Background soft gradient flourish */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-emerald-50 via-teal-50/40 to-transparent rounded-full -mr-20 -mt-20 pointer-events-none"></div>

      {/* Clock Top Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-stone-100 gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-2xl bg-forest-600 text-white flex items-center justify-center shadow-lg shadow-forest-600/25">
            <Clock className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-extrabold text-xl text-stone-900 tracking-tight">College Climate Clock</h3>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-forest-100 text-forest-700">
                Institutional Target
              </span>
            </div>
            <p className="text-xs text-stone-500 font-medium">
              Countdown to Institutional Carbon Neutrality for {iclock?.institution_name || 'VESIT Green Campus'}
            </p>
          </div>
        </div>

        {/* Target Date Controller */}
        <div className="flex items-center space-x-2">
          {editingTarget ? (
            <form onSubmit={handleApplyTarget} className="flex items-center space-x-2">
              <input
                type="date"
                value={targetInput}
                onChange={(e) => setTargetInput(e.target.value)}
                className="px-3 py-1.5 text-xs font-mono border border-forest-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-forest-500"
              />
              <button
                type="submit"
                className="px-3 py-1.5 text-xs font-semibold bg-forest-600 text-white rounded-lg hover:bg-forest-700 transition-colors"
              >
                Set Target
              </button>
              <button
                type="button"
                onClick={() => setEditingTarget(false)}
                className="px-2 py-1.5 text-xs text-stone-500 hover:text-stone-800"
              >
                Cancel
              </button>
            </form>
          ) : (
            <div className="flex items-center space-x-2 bg-stone-50 px-3 py-1.5 rounded-xl border border-stone-200/80">
              <Calendar className="w-4 h-4 text-forest-600" />
              <span className="text-xs text-stone-600">Target Date:</span>
              <span className="font-bold font-mono text-xs text-stone-900">{iclock?.target_date || '2040-12-31'}</span>
              <button
                onClick={() => setEditingTarget(true)}
                className="text-[11px] text-forest-700 font-semibold hover:underline ml-1"
              >
                Edit
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Countdown Display */}
      <div className="my-8">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 lg:gap-4">
          {[
            { label: 'YEARS', value: years },
            { label: 'MONTHS', value: months },
            { label: 'DAYS', value: days },
            { label: 'HOURS', value: hours },
            { label: 'MINUTES', value: minutes },
            { label: 'SECONDS', value: seconds },
          ].map((item, idx) => (
            <div
              key={idx}
              className="bg-gradient-to-b from-stone-50/80 to-stone-100/60 rounded-2xl p-4 text-center border border-stone-200/60 shadow-xs hover:border-forest-200 transition-all"
            >
              <div className="text-3xl sm:text-4xl lg:text-5xl font-black text-forest-800 font-mono tracking-tight">
                {String(item.value).padStart(2, '0')}
              </div>
              <div className="text-[10px] font-bold tracking-wider text-stone-500 uppercase mt-1">
                {item.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trajectory & Net Zero Context */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-stone-100 text-xs">
        <div className="flex items-start space-x-3 p-3 rounded-xl bg-forest-50/40 border border-forest-100">
          <TrendingDown className="w-5 h-5 text-forest-600 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-stone-800">Decarbonization Rate</div>
            <div className="text-stone-600 mt-0.5">
              Required linear abatement: <span className="font-mono font-bold text-forest-700">153.1 tonnes CO2e/yr</span>
            </div>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 rounded-xl bg-teal-50/40 border border-teal-100">
          <ShieldCheck className="w-5 h-5 text-teal-600 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-stone-800">Mathematical Projection</div>
            <div className="text-stone-600 mt-0.5">
              Projected Net-Zero Year: <span className="font-mono font-bold text-teal-700">{iclock?.projected_net_zero_year || 2040}</span>
              {iclock?.achieves_target_by_deadline ? (
                <span className="ml-1.5 text-[10px] font-bold text-forest-600">✓ On Track</span>
              ) : (
                <span className="ml-1.5 text-[10px] font-bold text-amber-600">⚠ Off Track</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 rounded-xl bg-amber-50/40 border border-amber-100">
          <Info className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-stone-800">Data Distinction</div>
            <div className="text-stone-600 mt-0.5">
              Distinguishing configured institutional target date from mathematical projection trajectory.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

