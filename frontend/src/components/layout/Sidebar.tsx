import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Clock,
  LayoutDashboard,
  CloudLightning,
  Zap,
  Droplets,
  Trash2,
  Bus,
  Share2,
  Bot,
  Sliders,
  Globe,
  FileText,
  BarChart3,
  Settings,
  Leaf
} from 'lucide-react';

const navigationItems = [
  { name: 'Overview', to: '/', icon: LayoutDashboard },
  { name: 'Climate Clock', to: '/climate-clock', icon: Clock, badge: 'Hero' },
  { name: 'Carbon Emissions', to: '/emissions', icon: CloudLightning },
  { name: 'Energy & Solar', to: '/energy', icon: Zap },
  { name: 'Water & Rainwater', to: '/water', icon: Droplets },
  { name: 'Waste & Circularity', to: '/waste', icon: Trash2 },
  { name: 'Transportation', to: '/transport', icon: Bus },
  { name: 'Graph Explorer', to: '/graph-explorer', icon: Share2 },
  { name: 'AI Assistant', to: '/ai-assistant', icon: Bot, badge: 'Mistral' },
  { name: 'Simulations', to: '/simulations', icon: Sliders },
  { name: 'SDG Tracker', to: '/sdg-tracker', icon: Globe },
  { name: 'Documents', to: '/documents', icon: FileText },
  { name: 'Evaluation', to: '/evaluation', icon: BarChart3, badge: 'Benchmark' },
  { name: 'Settings', to: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white border-r border-stone-200 flex flex-col h-screen sticky top-0 select-none shadow-sm z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-stone-100 flex items-center space-x-3 bg-gradient-to-r from-emerald-50/50 to-transparent">
        <div className="w-10 h-10 rounded-xl bg-forest-600 text-white flex items-center justify-center shadow-md shadow-forest-600/20">
          <Leaf className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-stone-900 tracking-tight flex items-center gap-1.5">
            EcoClock <span className="text-forest-600 text-xs px-1.5 py-0.5 rounded font-mono bg-forest-50 border border-forest-200">AI</span>
          </h1>
          <p className="text-[11px] text-stone-500 font-medium">Campus GraphRAG System</p>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-stone-400">
          Navigation
        </div>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-forest-50 text-forest-700 font-semibold shadow-xs border border-forest-200/60'
                    : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="w-4 h-4 text-stone-500" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-forest-100 text-forest-700">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-stone-100 bg-stone-50/50 text-[11px] text-stone-500">
        <div className="flex items-center justify-between mb-1">
          <span className="font-semibold text-stone-700">VESIT Green Campus</span>
          <span className="w-2 h-2 rounded-full bg-forest-500"></span>
        </div>
        <p className="text-stone-400 text-[10px]">Academic Microproject 2026</p>
      </div>
    </aside>
  );
};

