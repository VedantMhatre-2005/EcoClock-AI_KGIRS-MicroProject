import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { ClimateClock } from './pages/ClimateClock';
import { Emissions } from './pages/Emissions';
import { Energy } from './pages/Energy';
import { Water } from './pages/Water';
import { Waste } from './pages/Waste';
import { Transport } from './pages/Transport';
import { GraphExplorer } from './pages/GraphExplorer';
import { AIExplorer } from './pages/AIExplorer';
import { Simulations } from './pages/Simulations';
import { SDGTracker } from './pages/SDGTracker';
import { Documents } from './pages/Documents';
import { Evaluation } from './pages/Evaluation';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="climate-clock" element={<ClimateClock />} />
          <Route path="emissions" element={<Emissions />} />
          <Route path="energy" element={<Energy />} />
          <Route path="water" element={<Water />} />
          <Route path="waste" element={<Waste />} />
          <Route path="transport" element={<Transport />} />
          <Route path="graph-explorer" element={<GraphExplorer />} />
          <Route path="ai-assistant" element={<AIExplorer />} />
          <Route path="simulations" element={<Simulations />} />
          <Route path="sdg-tracker" element={<SDGTracker />} />
          <Route path="documents" element={<Documents />} />
          <Route path="evaluation" element={<Evaluation />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;

