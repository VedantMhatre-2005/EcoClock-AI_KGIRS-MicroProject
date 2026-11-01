import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';

const routeTitleMap: Record<string, string> = {
  '/': 'Campus Sustainability Overview',
  '/climate-clock': 'Interactive College Climate Clock',
  '/emissions': 'Carbon Accounting & Scope Inventory',
  '/energy': 'Electricity & Renewable Solar Energy',
  '/water': 'Water Consumption & Rainwater Harvesting',
  '/waste': 'Solid Waste Management & Recycling',
  '/transport': 'Commuter Mobility & Transportation',
  '/graph-explorer': 'Campus Knowledge Graph Explorer',
  '/ai-assistant': 'AI Sustainability Assistant (GraphRAG)',
  '/simulations': 'Climate Action Scenario Simulator',
  '/sdg-tracker': 'UN Sustainable Development Goals (SDG) Tracker',
  '/documents': 'Institutional Sustainability Documents',
  '/evaluation': 'GraphRAG Benchmark & Evaluation Framework',
  '/settings': 'System Settings & Architecture'
};

export const Layout: React.FC = () => {
  const location = useLocation();
  const currentTitle = routeTitleMap[location.pathname] || 'EcoClock AI';

  return (
    <div className="flex min-h-screen bg-[#F8FAF9]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar title={currentTitle} />
        <main className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

