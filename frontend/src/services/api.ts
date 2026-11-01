import axios from 'axios';
import {
  DashboardSummary,
  ClimateClockData,
  EmissionsInventory,
  EnergyMetrics,
  WaterMetrics,
  WasteMetrics,
  TransportMetrics,
  SDGItem,
  DocumentItem,
  GraphRAGResponse,
  CypherResponse,
  SimulationResult,
  EvaluationMetric,
  SystemStatus
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes to allow local LLM inference on CPU without timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

export const apiService = {
  // System
  getHealth: async () => {
    const res = await apiClient.get('/health');
    return res.data;
  },
  getSystemStatus: async (): Promise<SystemStatus> => {
    const res = await apiClient.get('/system/status');
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await apiClient.get('/dashboard/summary');
    return res.data;
  },
  getDashboardTrends: async () => {
    const res = await apiClient.get('/dashboard/trends');
    return res.data;
  },

  // Climate Clock & Projection
  getClimateClock: async (targetDate?: string): Promise<ClimateClockData> => {
    const params = targetDate ? { target_date: targetDate } : {};
    const res = await apiClient.get('/climate/clock', { params });
    return res.data;
  },
  getClimateProjection: async (model: string = 'LINEAR', targetYear: number = 2040, annualRate?: number) => {
    const params: any = { model, target_year: targetYear };
    if (annualRate !== undefined) params.annual_rate = annualRate;
    const res = await apiClient.get('/climate/projection', { params });
    return res.data;
  },
  updateTarget: async (targetData: any) => {
    const res = await apiClient.post('/climate/targets', targetData);
    return res.data;
  },

  // Analytics Modules
  getEmissionsSummary: async (year: number = 2024): Promise<EmissionsInventory> => {
    const res = await apiClient.get('/emissions/summary', { params: { year } });
    return res.data;
  },
  getEmissionsTrends: async () => {
    const res = await apiClient.get('/emissions/trends');
    return res.data;
  },
  getEnergySummary: async (): Promise<EnergyMetrics> => {
    const res = await apiClient.get('/energy/summary');
    return res.data;
  },
  getWaterSummary: async (): Promise<WaterMetrics> => {
    const res = await apiClient.get('/water/summary');
    return res.data;
  },
  getWasteSummary: async (): Promise<WasteMetrics> => {
    const res = await apiClient.get('/waste/summary');
    return res.data;
  },
  getTransportSummary: async (): Promise<TransportMetrics> => {
    const res = await apiClient.get('/transport/summary');
    return res.data;
  },

  // SDGs
  getSDGs: async (): Promise<SDGItem[]> => {
    const res = await apiClient.get('/sdg');
    return res.data;
  },
  getSDGDetails: async (sdgId: string): Promise<SDGItem> => {
    const res = await apiClient.get(`/sdg/${sdgId}`);
    return res.data;
  },

  // Documents
  getDocuments: async (): Promise<DocumentItem[]> => {
    const res = await apiClient.get('/documents');
    return res.data;
  },
  getDocumentDetails: async (docId: string) => {
    const res = await apiClient.get(`/documents/${docId}`);
    return res.data;
  },
  uploadDocument: async (file: File, docType: string = 'GENERAL', sourceType: string = 'SYNTHETIC') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', docType);
    formData.append('source_type', sourceType);
    const res = await apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  reingestDocument: async (docId: string) => {
    const res = await apiClient.post(`/documents/${docId}/ingest`);
    return res.data;
  },
  deleteDocument: async (docId: string) => {
    const res = await apiClient.delete(`/documents/${docId}`);
    return res.data;
  },

  // GraphRAG
  queryGraphRAG: async (query: string, mode: string = 'HYBRID_GRAPHRAG'): Promise<GraphRAGResponse> => {
    const res = await apiClient.post('/graphrag/query', { query, mode });
    return res.data;
  },
  executeCypherQuery: async (question: string): Promise<CypherResponse> => {
    const res = await apiClient.post('/graphrag/cypher', { question });
    return res.data;
  },

  // Knowledge Graph
  getGraphSchema: async () => {
    const res = await apiClient.get('/graph/schema');
    return res.data;
  },
  exploreGraph: async (centerId?: string, depth: number = 2) => {
    const params: any = { depth };
    if (centerId) params.center_id = centerId;
    const res = await apiClient.get('/graph/explore', { params });
    return res.data;
  },
  getEntityDetails: async (entityId: string) => {
    const res = await apiClient.get(`/graph/entity/${entityId}`);
    return res.data;
  },

  // Simulations
  runSimulation: async (scenarioType: string, parameters: Record<string, any>): Promise<SimulationResult> => {
    const res = await apiClient.post('/simulations/run', { scenario_type: scenarioType, parameters });
    return res.data;
  },
  saveSimulation: async (name: string, scenarioType: string, parameters: Record<string, any>): Promise<SimulationResult> => {
    const res = await apiClient.post('/simulations/save', { name, scenario_type: scenarioType, parameters });
    return res.data;
  },
  listSimulations: async (): Promise<SimulationResult[]> => {
    const res = await apiClient.get('/simulations');
    return res.data;
  },
  deleteSimulation: async (id: string) => {
    const res = await apiClient.delete(`/simulations/${id}`);
    return res.data;
  },

  // Evaluation
  runEvaluation: async () => {
    const res = await apiClient.post('/evaluation/run');
    return res.data;
  },
  getEvaluationResults: async (): Promise<EvaluationMetric[]> => {
    const res = await apiClient.get('/evaluation/results');
    return res.data;
  }
};

