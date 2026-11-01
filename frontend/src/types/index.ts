export interface DashboardSummary {
  institution_name: string;
  source_type: string;
  kpis: {
    total_carbon_emissions_tonnes: number;
    baseline_emissions_tonnes: number;
    emissions_reduction_percentage: number;
    total_electricity_mwh: number;
    solar_generation_mwh: number;
    renewable_energy_percentage: number;
    total_water_consumption_million_litres: number;
    rainwater_harvested_million_litres: number;
    waste_diversion_rate: number;
    active_sustainability_initiatives: number;
    total_sustainability_initiatives: number;
  };
}

export interface ClimateClockData {
  institution_clock: {
    institution_name: string;
    target_date: string;
    target_year: number;
    baseline_year: number;
    baseline_emissions_kgco2e: number;
    baseline_emissions_tonnes_co2e: number;
    current_annual_emissions_kgco2e: number;
    current_annual_emissions_tonnes_co2e: number;
    annual_reduction_kgco2e: number;
    annual_reduction_tonnes_co2e: number;
    projected_net_zero_year: number | null;
    achieves_target_by_deadline: boolean;
    countdown: {
      years: number;
      months: number;
      days: number;
      hours: number;
      minutes: number;
      seconds: number;
      total_days: number;
      is_target_reached: boolean;
    };
    data_source_type: string;
    methodology_notes: string;
  };
  global_context_clock: {
    status: string;
    message: string;
    external_source_configured: boolean;
  };
}

export interface EmissionsInventory {
  year: number;
  unit: string;
  total_emissions_kgco2e: number;
  total_emissions_tonnes_co2e: number;
  scopes: {
    scope_1: {
      label: string;
      emissions_kgco2e: number;
      tonnes_co2e: number;
      percentage: number;
    };
    scope_2: {
      label: string;
      emissions_kgco2e: number;
      tonnes_co2e: number;
      percentage: number;
    };
    scope_3: {
      label: string;
      emissions_kgco2e: number;
      tonnes_co2e: number;
      percentage: number;
      breakdown?: {
        commuting_kgco2e: number;
        waste_kgco2e: number;
        water_embodied_kgco2e: number;
      };
    };
  };
}

export interface MonthlyEnergyTrend {
  date: string;
  grid_kwh: number;
  solar_kwh: number;
  total_kwh: number;
  emissions_kgco2e: number;
  solar_percentage: number;
}

export interface BuildingEnergyBreakdown {
  building_id: string;
  building_name: string;
  total_kwh: number;
  solar_kwh: number;
  emissions_kgco2e: number;
}

export interface EnergyMetrics {
  total_electricity_kwh: number;
  grid_electricity_kwh: number;
  solar_generation_kwh: number;
  renewable_percentage: number;
  monthly_trends: MonthlyEnergyTrend[];
  building_breakdown: BuildingEnergyBreakdown[];
}

export interface WaterMetrics {
  total_consumption_litres: number;
  total_rainwater_harvested_litres: number;
  rainwater_replacement_rate: number;
  monthly_trends: {
    date: string;
    consumption_litres: number;
    rainwater_harvested_litres: number;
  }[];
  building_breakdown: {
    building_id: string;
    building_name: string;
    consumption_litres: number;
    rainwater_harvested_litres: number;
  }[];
}

export interface WasteMetrics {
  total_waste_kg: number;
  recyclable_kg: number;
  non_recyclable_kg: number;
  composted_kg: number;
  recycling_rate: number;
  monthly_trends: {
    date: string;
    total_kg: number;
    recyclable_kg: number;
    non_recyclable_kg: number;
    composted_kg: number;
    emissions_kgco2e: number;
    recycling_rate: number;
  }[];
}

export interface TransportMetrics {
  total_passenger_km: number;
  total_trips: number;
  total_transport_emissions_kgco2e: number;
  modes: {
    mode: string;
    passenger_km: number;
    trips_count: number;
    emissions_kgco2e: number;
  }[];
}

export interface SDGItem {
  id: string;
  sdg_number: number;
  name: string;
  description: string;
  color: string;
  initiative_count: number;
  initiatives: {
    id: string;
    name: string;
    status: string;
    carbon_reduction_estimate_kgco2e: number;
  }[];
  has_initiatives: boolean;
}

export interface DocumentItem {
  id: string;
  title: string;
  document_type: string;
  publication_date: string;
  source_type: string;
  institution_id: string;
  file_size: number;
  status: string;
  chunk_count: number;
  entity_count: number;
  relationship_count: number;
  created_at: string;
}

export interface GraphRAGResponse {
  query: string;
  mode: string;
  answer: string;
  supporting_evidence: string;
  citations: {
    citation_id: string;
    document_id: string;
    document_title: string;
    chunk_id: string;
    section: string;
    excerpt: string;
  }[];
  graph_paths: {
    source: string;
    relationship: string;
    target: string;
    evidence: string;
  }[];
  retrieval_mode: string;
  latency_ms: number;
  confidence_score: number;
  is_grounded: boolean;
  ollama_used: boolean;
}

export interface CypherResponse {
  question: string;
  generated_cypher: string;
  is_valid: boolean;
  records: any[];
  execution_source: string;
  record_count: number;
  explanation: string;
  latency_ms: number;
  error?: string;
}

export interface SimulationResult {
  id?: string;
  name?: string;
  scenario_type: string;
  parameters: Record<string, any>;
  baseline_emissions_kgco2e: number;
  baseline_emissions_tonnes_co2e: number;
  projected_emissions_kgco2e: number;
  projected_emissions_tonnes_co2e: number;
  reduction_kgco2e: number;
  reduction_tonnes_co2e: number;
  percentage_reduction: number;
  resource_savings: Record<string, any>;
  details?: Record<string, any>;
  created_at?: string;
}

export interface EvaluationMetric {
  run_id: string;
  timestamp?: string;
  method: string;
  precision: number;
  recall: number;
  f1: number;
  mrr: number;
  recall_at_k: number;
  evidence_support_rate: number;
  answer_correctness: number;
  unsupported_claim_rate: number;
  avg_latency_ms: number;
  total_queries: number;
}

export interface SystemStatus {
  app_name: string;
  institution: string;
  environment: string;
  neo4j: {
    connected: boolean;
    uri: string;
  };
  ollama: {
    connected: boolean;
    url: string;
    configured_model: string;
    version?: string;
  };
  knowledge_graph: {
    total_nodes: number;
    total_edges: number;
  };
  embedding_model: string;
}

