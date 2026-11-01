import React, { useEffect, useState } from 'react';
import { Bus, Train, Bike, Car, AlertCircle, Zap, ShieldCheck } from 'lucide-react';
import { apiService } from '../services/api';
import { TransportMetrics } from '../types';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

const MODE_COLORS: Record<string, string> = {
  'Suburban Rail': '#059669', // Emerald
  'BEST Bus': '#0d9488', // Teal
  'Two-Wheeler': '#d97706', // Amber
  'Car': '#dc2626', // Red
  'Electric Shuttle': '#2563eb', // Blue
  'Bicycle / Walking': '#10b981' // Green
};

export const Transport: React.FC = () => {
  const [data, setData] = useState<TransportMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await apiService.getTransportSummary();
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load transport analytics');
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
          <h3 className="font-semibold text-lg">Error Loading Transport Analytics</h3>
          <p className="text-sm">{error || 'No transport data available.'}</p>
        </div>
      </div>
    );
  }

  const pieData = data.modes.map((m) => ({
    name: m.mode,
    value: m.emissions_kgco2e,
    color: MODE_COLORS[m.mode] || '#6b7280'
  }));

  const publicTransitKm = data.modes
    .filter((m) => ['Suburban Rail', 'BEST Bus', 'Electric Shuttle', 'Bicycle / Walking'].includes(m.mode))
    .reduce((sum, m) => sum + m.passenger_km, 0);

  const sustainableTransitShare = data.total_passenger_km > 0
    ? ((publicTransitKm / data.total_passenger_km) * 100).toFixed(1)
    : '0';

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">Campus Commute & Mobility (Scope 3)</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              SYNTHETIC DEMO
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Analyzing student, faculty, and staff commuting patterns across Mumbai suburban transit corridors, campus feeder shuttles, and private vehicular modes.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Chembur & Kurla Rail Feeder Active
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Total Commute Distance</span>
            <Train className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {(data.total_passenger_km / 1000).toFixed(1)}k <span className="text-sm font-normal text-gray-500">pkm</span>
          </div>
          <span className="text-xs text-gray-500 mt-1 block">Total annual passenger-km</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Total Commute Trips</span>
            <Bus className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {data.total_trips.toLocaleString()}
          </div>
          <span className="text-xs text-blue-600 mt-1 block">3,200 campus commuters</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Scope 3 Transport Footprint</span>
            <Car className="w-5 h-5 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-amber-700">
            {(data.total_transport_emissions_kgco2e / 1000).toFixed(2)} <span className="text-sm font-normal text-gray-500">tCO₂e</span>
          </div>
          <span className="text-xs text-amber-600 mt-1 block">{data.total_transport_emissions_kgco2e.toLocaleString()} kg CO₂e</span>
        </div>

        <div className="bg-emerald-50 p-5 rounded-xl border border-emerald-200 shadow-sm">
          <div className="flex items-center justify-between text-emerald-700 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Sustainable Transit Share</span>
            <Bike className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-700">
            {sustainableTransitShare}%
          </div>
          <span className="text-xs text-emerald-800 mt-1 block">Rail, Bus, Shuttle & Active</span>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Modal Passenger-km Comparison */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">Passenger Distance by Mode (pkm)</h3>
            <p className="text-sm text-gray-500">Total volume of distance traveled across commuting modes.</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.modes} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="mode" stroke="#6b7280" fontSize={11} angle={-15} textAnchor="end" />
                <YAxis stroke="#6b7280" fontSize={11} />
                <Tooltip
                  formatter={(val: number) => [`${val.toLocaleString()} pkm`, 'Distance']}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px' }}
                />
                <Bar dataKey="passenger_km" name="Passenger-km" fill="#059669" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Modal Emissions Breakdown Pie */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">Emissions Distribution by Mode</h3>
            <p className="text-sm text-gray-500">Carbon contribution in kg CO₂e by commute vehicle category.</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: number) => [`${val.toLocaleString()} kg CO₂e`, 'Emissions']}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px' }}
                />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Mode Inventory Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900">Commute Mode Carbon Accounting Table</h3>
          <p className="text-sm text-gray-500">Detailed breakdown of passenger distance, commute trips, and Scope 3 carbon intensity.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-gray-50 text-xs uppercase text-gray-700 font-semibold border-b border-gray-200">
              <tr>
                <th className="py-3 px-6">Commute Mode</th>
                <th className="py-3 px-6 text-right">Trips Logged</th>
                <th className="py-3 px-6 text-right">Passenger-km</th>
                <th className="py-3 px-6 text-right">Emissions (kg CO₂e)</th>
                <th className="py-3 px-6 text-right">Emissions (tCO₂e)</th>
                <th className="py-3 px-6 text-center">Transit Category</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.modes.map((m, idx) => {
                const isGreen = ['Suburban Rail', 'BEST Bus', 'Electric Shuttle', 'Bicycle / Walking'].includes(m.mode);
                return (
                  <tr key={idx} className="hover:bg-gray-50/75">
                    <td className="py-4 px-6 font-semibold text-gray-900 flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: MODE_COLORS[m.mode] || '#9ca3af' }}></span>
                      {m.mode}
                    </td>
                    <td className="py-4 px-6 text-right">{m.trips_count.toLocaleString()}</td>
                    <td className="py-4 px-6 text-right font-mono">{m.passenger_km.toLocaleString()}</td>
                    <td className="py-4 px-6 text-right font-mono font-bold text-gray-800">{m.emissions_kgco2e.toLocaleString()}</td>
                    <td className="py-4 px-6 text-right font-mono text-gray-600">{(m.emissions_kgco2e / 1000).toFixed(2)}</td>
                    <td className="py-4 px-6 text-center">
                      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                        isGreen ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'
                      }`}>
                        {isGreen ? 'Low Carbon' : 'High Carbon'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sustainable Transit Interventions */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-emerald-600 text-white rounded-lg">
            <Zap className="w-5 h-5" />
          </div>
          <h4 className="text-lg font-bold text-emerald-900">Campus Green Transit Strategies</h4>
        </div>
        <p className="text-sm text-emerald-800 mb-4 leading-relaxed">
          VESIT Green Campus actively encourages mass transit through subsidized suburban rail passes and dedicated electric mini-bus shuttles linking the campus to Kurla (Central Railway) and Chembur (Harbour Railway) commuter transit hubs.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-medium text-emerald-900">
          <div className="bg-white/80 p-3.5 rounded-lg border border-emerald-200">
            ⚡ <strong>4 EV Charging Points</strong> installed in the main faculty parking lot with solar canopy charging.
          </div>
          <div className="bg-white/80 p-3.5 rounded-lg border border-emerald-200">
            🚌 <strong>Zero-Fare Campus Electric Feeder</strong> running every 15 minutes during peak morning/evening hours.
          </div>
          <div className="bg-white/80 p-3.5 rounded-lg border border-emerald-200">
            🚲 <strong>Campus Bike Sharing Hub</strong> with 40 secured bicycles for local Chembur residential commutes.
          </div>
        </div>
      </div>
    </div>
  );
};

