import React, { useEffect, useState, useMemo } from 'react';
import { 
  Network, Search, ZoomIn, ZoomOut, RefreshCw, Layers, ShieldCheck, 
  ExternalLink, Info, X
} from 'lucide-react';
import { apiService } from '../services/api';

const LABEL_COLORS: Record<string, { bg: string; border: string; text: string; fill: string }> = {
  Institution: { bg: '#e0e7ff', border: '#4f46e5', text: '#3730a3', fill: '#4f46e5' },
  Building: { bg: '#dbeafe', border: '#2563eb', text: '#1e40af', fill: '#3b82f6' },
  Initiative: { bg: '#d1fae5', border: '#059669', text: '#065f46', fill: '#10b981' },
  SustainabilityInitiative: { bg: '#d1fae5', border: '#059669', text: '#065f46', fill: '#10b981' },
  Target: { bg: '#fee2e2', border: '#dc2626', text: '#991b1b', fill: '#ef4444' },
  SustainabilityTarget: { bg: '#fee2e2', border: '#dc2626', text: '#991b1b', fill: '#ef4444' },
  SDG: { bg: '#f3e8ff', border: '#7c3aed', text: '#5b21b6', fill: '#8b5cf6' },
  Department: { bg: '#ccfbf1', border: '#0d9488', text: '#115e59', fill: '#0d9488' },
  Document: { bg: '#ede9fe', border: '#6366f1', text: '#4338ca', fill: '#6366f1' },
  Measurement: { bg: '#fef3c7', border: '#d97706', text: '#92400e', fill: '#f59e0b' },
  Metric: { bg: '#fef3c7', border: '#d97706', text: '#92400e', fill: '#f59e0b' },
  EnergySource: { bg: '#fef9c3', border: '#ca8a04', text: '#854d0e', fill: '#eab308' },
  Resource: { bg: '#cffafe', border: '#0891b2', text: '#155e75', fill: '#06b6d4' },
  Emission: { bg: '#ffedd5', border: '#ea580c', text: '#9a3412', fill: '#f97316' },
  EmissionSource: { bg: '#ffedd5', border: '#ea580c', text: '#9a3412', fill: '#f97316' },
  EmissionFactor: { bg: '#ffe4e6', border: '#e11d48', text: '#9f1239', fill: '#f43f5e' },
  Policy: { bg: '#ccfbf1', border: '#0d9488', text: '#115e59', fill: '#14b8a6' },
  Default: { bg: '#f3f4f6', border: '#6b7280', text: '#374151', fill: '#9ca3af' }
};

export const GraphExplorer: React.FC = () => {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & State
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedLabel, setSelectedLabel] = useState<string>('ALL');
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [nodeDetails, setNodeDetails] = useState<any | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const fetchGraph = async (centerId?: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiService.exploreGraph(centerId, 2);
      setNodes(res.nodes || []);
      setEdges(res.edges || []);
      if (centerId && res.nodes) {
        const found = res.nodes.find((n: any) => n.id === centerId);
        if (found) setSelectedNode(found);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch graph data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  // When selectedNode changes, load details
  useEffect(() => {
    if (!selectedNode) {
      setNodeDetails(null);
      return;
    }
    const loadDetails = async () => {
      try {
        const details = await apiService.getEntityDetails(selectedNode.id);
        setNodeDetails(details);
      } catch (err) {
        console.error('Failed to load entity details', err);
      }
    };
    loadDetails();
  }, [selectedNode]);

  // Safe node label and name extractor
  const getNodeName = (n: any): string => {
    return n?.name || n?.title || n?.id || 'Unnamed Entity';
  };

  // Unique labels for filter
  const availableLabels = useMemo(() => {
    const set = new Set<string>();
    nodes.forEach((n) => {
      if (n?.label) set.add(n.label);
    });
    return Array.from(set).sort();
  }, [nodes]);

  // Filter nodes & connected edges
  const filteredNodes = useMemo(() => {
    return nodes.filter((n) => {
      const name = getNodeName(n).toLowerCase();
      const id = (n?.id || '').toLowerCase();
      const search = searchTerm.toLowerCase();
      const matchesSearch = searchTerm === '' || name.includes(search) || id.includes(search);
      const matchesLabel = selectedLabel === 'ALL' || n?.label === selectedLabel;
      return matchesSearch && matchesLabel;
    });
  }, [nodes, searchTerm, selectedLabel]);

  // Compute Layout Positions (Deterministic Circle Layout / Grid)
  const nodePositionMap = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    const count = filteredNodes.length;
    if (count === 0) return map;

    const centerX = 450;
    const centerY = 350;

    // Arrange in concentric rings
    const ringCapacity = 16;
    filteredNodes.forEach((node, index) => {
      const ringIndex = Math.floor(index / ringCapacity);
      const indexInRing = index % ringCapacity;
      const ringItems = Math.min(count - ringIndex * ringCapacity, ringCapacity);
      const radius = 130 + ringIndex * 90;
      const angle = (indexInRing / ringItems) * 2 * Math.PI;

      map.set(node.id, {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    });

    return map;
  }, [filteredNodes]);

  // Visible edges connecting filtered nodes
  const visibleEdges = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    return edges.filter((e) => nodeIds.has(e.source_id) && nodeIds.has(e.target_id));
  }, [edges, filteredNodes]);

  // Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPanOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">Knowledge Graph Explorer</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              {nodes.length} Nodes &bull; {edges.length} Edges
            </span>
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Interactive visualization of VESIT Green Campus ontology: entities, relationships, document citations, and provenance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setZoomLevel(1);
              setPanOffset({ x: 0, y: 0 });
              fetchGraph();
            }}
            className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset View
          </button>
        </div>
      </div>

      {/* Control Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="flex flex-1 items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search entities (e.g. Solar, Canteen, SDG 7)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="flex items-center gap-1.5 text-xs text-gray-600">
            <Layers className="w-4 h-4 text-gray-400" />
            <select
              value={selectedLabel}
              onChange={(e) => setSelectedLabel(e.target.value)}
              className="text-xs bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="ALL">All Entity Types ({nodes.length})</option>
              {availableLabels.map((lbl) => (
                <option key={lbl} value={lbl}>
                  {lbl} ({nodes.filter((n) => n.label === lbl).length})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Zoom controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoomLevel((z) => Math.max(0.4, z - 0.2))}
            className="p-1.5 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 text-gray-600"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono text-gray-500 min-w-12 text-center">
            {Math.round(zoomLevel * 100)}%
          </span>
          <button
            onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.2))}
            className="p-1.5 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 text-gray-600"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Graph Canvas & Side Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SVG Interactive Canvas */}
        <div className="lg:col-span-3 bg-white rounded-xl border border-gray-200 shadow-sm relative overflow-hidden h-[600px] select-none">
          {loading && (
            <div className="absolute inset-0 bg-white/70 z-20 flex items-center justify-center">
              <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 z-20 flex items-center justify-center p-6 text-red-600">
              {error}
            </div>
          )}

          <div
            className="w-full h-full cursor-grab active:cursor-grabbing bg-radial-dots"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
          >
            <svg className="w-full h-full">
              <g
                transform={`translate(${panOffset.x}, ${panOffset.y}) scale(${zoomLevel})`}
                style={{ transition: 'transform 0.1s ease-out' }}
              >
                {/* Edges */}
                {visibleEdges.map((edge) => {
                  const srcPos = nodePositionMap.get(edge.source_id);
                  const tgtPos = nodePositionMap.get(edge.target_id);
                  if (!srcPos || !tgtPos) return null;

                  const isHighlighted = selectedNode && (
                    selectedNode.id === edge.source_id || selectedNode.id === edge.target_id
                  );

                  return (
                    <g key={edge.id || `${edge.source_id}-${edge.target_id}`}>
                      <line
                        x1={srcPos.x}
                        y1={srcPos.y}
                        x2={tgtPos.x}
                        y2={tgtPos.y}
                        stroke={isHighlighted ? '#059669' : '#d1d5db'}
                        strokeWidth={isHighlighted ? 2.5 : 1.2}
                        strokeOpacity={isHighlighted ? 0.9 : 0.5}
                      />
                      <text
                        x={(srcPos.x + tgtPos.x) / 2}
                        y={(srcPos.y + tgtPos.y) / 2 - 4}
                        fontSize={8}
                        fill="#9ca3af"
                        textAnchor="middle"
                        className="pointer-events-none select-none"
                      >
                        {edge.type}
                      </text>
                    </g>
                  );
                })}

                {/* Nodes */}
                {filteredNodes.map((node) => {
                  const pos = nodePositionMap.get(node.id);
                  if (!pos) return null;
                  const isSelected = selectedNode?.id === node.id;
                  const colorScheme = LABEL_COLORS[node.label] || LABEL_COLORS.Default;

                  return (
                    <g
                      key={node.id}
                      transform={`translate(${pos.x}, ${pos.y})`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedNode(node);
                      }}
                      className="cursor-pointer group"
                    >
                      <circle
                        r={isSelected ? 18 : 12}
                        fill={colorScheme.fill}
                        stroke={isSelected ? '#111827' : colorScheme.border}
                        strokeWidth={isSelected ? 3 : 1.5}
                        fillOpacity={0.9}
                        className="transition-all duration-150 group-hover:stroke-emerald-600 group-hover:stroke-[3px] group-hover:fill-opacity-100"
                      />
                      <text
                        y={isSelected ? 28 : 22}
                        fontSize={10}
                        fontWeight={isSelected ? 'bold' : 'normal'}
                        fill={isSelected ? '#111827' : '#4b5563'}
                        textAnchor="middle"
                        className="pointer-events-none select-none"
                      >
                        {getNodeName(node).length > 18 ? getNodeName(node).slice(0, 16) + '...' : getNodeName(node)}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>
          </div>

          {/* Canvas Floating Overlay Controls */}
          <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-lg border border-gray-200 text-xs text-gray-600 flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Initiative
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Building
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span> SDG
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Metric
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> Target
            </span>
          </div>
        </div>

        {/* Selected Entity Details Panel */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex flex-col h-[600px] overflow-y-auto">
          {selectedNode ? (
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 uppercase">
                    {selectedNode.label}
                  </span>
                  <h3 className="text-lg font-bold text-gray-900 mt-1">{getNodeName(selectedNode)}</h3>
                  <div className="text-xs font-mono text-gray-400 mt-0.5">{selectedNode.id}</div>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Provenance Badge */}
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-xs space-y-1">
                <div className="flex items-center justify-between font-semibold text-emerald-900">
                  <span className="flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    Provenance Verified
                  </span>
                  <span className="font-mono">{selectedNode.provenance?.status || 'EXPLICIT'}</span>
                </div>
                {selectedNode.provenance?.source_document_id && (
                  <div className="text-emerald-700 text-[11px] truncate">
                    Source: {selectedNode.provenance.source_document_id}
                  </div>
                )}
              </div>

              {/* Connected Relationships */}
              <div>
                <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                  Connected Relationships ({nodeDetails?.degree || 0})
                </h4>
                {nodeDetails?.connected_edges && nodeDetails.connected_edges.length > 0 ? (
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {nodeDetails.connected_edges.map((e: any, idx: number) => {
                      const isOutgoing = e.source_id === selectedNode.id;
                      const neighborId = isOutgoing ? e.target_id : e.source_id;
                      const neighbor = nodes.find((n) => n.id === neighborId);

                      return (
                        <div
                          key={idx}
                          onClick={() => {
                            if (neighbor) setSelectedNode(neighbor);
                          }}
                          className="p-2.5 rounded-lg border border-gray-100 hover:border-emerald-300 hover:bg-emerald-50/50 cursor-pointer text-xs transition-colors"
                        >
                          <div className="flex items-center justify-between text-gray-500 text-[10px]">
                            <span>{isOutgoing ? 'OUTGOING ➔' : 'INCOMING ⬅'}</span>
                            <span className="font-semibold text-emerald-700">{e.type}</span>
                          </div>
                          <div className="font-medium text-gray-800 mt-1 truncate">
                            {neighbor ? getNodeName(neighbor) : neighborId}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500 italic">No direct relationships connected.</p>
                )}
              </div>

              {/* Raw Properties Accordion */}
              {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                <div className="border-t border-gray-100 pt-3">
                  <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">Entity Properties</h4>
                  <div className="bg-gray-50 rounded-lg p-2.5 text-xs font-mono space-y-1 text-gray-600 max-h-36 overflow-y-auto">
                    {Object.entries(selectedNode.properties).map(([key, val]) => (
                      <div key={key} className="truncate">
                        <span className="font-semibold text-gray-800">{key}:</span> {String(val)}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Subgraph re-center action */}
              <button
                onClick={() => fetchGraph(selectedNode.id)}
                className="w-full mt-2 py-2 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <Network className="w-3.5 h-3.5" />
                Focus Subgraph on this Entity
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 p-6 space-y-3">
              <Network className="w-12 h-12 text-gray-300" />
              <div>
                <h4 className="font-semibold text-gray-700">No Entity Selected</h4>
                <p className="text-xs text-gray-500 mt-1">
                  Click any node on the graph canvas to inspect properties, provenance, and relationships.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
