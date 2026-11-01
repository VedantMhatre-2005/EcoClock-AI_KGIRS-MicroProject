from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    document_type = Column(String(64), nullable=False)
    publication_date = Column(String(32), nullable=False)
    source_type = Column(String(32), default="SYNTHETIC")
    institution_id = Column(String(64), default="VESIT")
    file_path = Column(String(512), nullable=True)
    file_hash = Column(String(64), nullable=False, index=True)
    file_size = Column(Integer, default=0)
    status = Column(String(32), default="UPLOADED") # UPLOADED, PROCESSING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    entity_count = Column(Integer, default=0)
    relationship_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan")


class ChunkModel(Base):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    char_length = Column(Integer, nullable=False)
    page_number = Column(Integer, default=1)
    section = Column(String(128), default="General")
    embedding_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("DocumentModel", back_populates="chunks")


class ExtractedEntityModel(Base):
    __tablename__ = "extracted_entities"

    id = Column(String(64), primary_key=True)
    document_id = Column(String(64), nullable=False, index=True)
    chunk_id = Column(String(64), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    canonical_name = Column(String(255), nullable=False, index=True)
    properties_json = Column(Text, default="{}")
    confidence = Column(Float, default=1.0)
    verification_status = Column(String(32), default="EXPLICIT") # EXPLICIT, INFERRED, VERIFIED
    created_at = Column(DateTime, default=datetime.utcnow)


class ExtractedRelationshipModel(Base):
    __tablename__ = "extracted_relationships"

    id = Column(String(64), primary_key=True)
    document_id = Column(String(64), nullable=False, index=True)
    chunk_id = Column(String(64), nullable=True, index=True)
    source_entity = Column(String(255), nullable=False, index=True)
    target_entity = Column(String(255), nullable=False, index=True)
    relationship_type = Column(String(64), nullable=False, index=True)
    evidence_excerpt = Column(Text, nullable=True)
    extraction_method = Column(String(64), default="LLM_EXTRACTION")
    confidence = Column(Float, default=1.0)
    verification_status = Column(String(32), default="EXPLICIT")
    created_at = Column(DateTime, default=datetime.utcnow)


class ElectricityRecord(Base):
    __tablename__ = "electricity_records"

    id = Column(String(64), primary_key=True)
    institution_id = Column(String(64), default="VESIT")
    building_id = Column(String(64), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    date_str = Column(String(16), nullable=False, index=True)
    grid_kwh = Column(Float, default=0.0)
    solar_kwh = Column(Float, default=0.0)
    total_kwh = Column(Float, default=0.0)
    emissions_kgco2e = Column(Float, default=0.0)
    source_type = Column(String(32), default="SYNTHETIC")


class WaterRecord(Base):
    __tablename__ = "water_records"

    id = Column(String(64), primary_key=True)
    institution_id = Column(String(64), default="VESIT")
    building_id = Column(String(64), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    date_str = Column(String(16), nullable=False, index=True)
    consumption_litres = Column(Float, default=0.0)
    rainwater_harvested_litres = Column(Float, default=0.0)
    source_type = Column(String(32), default="SYNTHETIC")


class WasteRecord(Base):
    __tablename__ = "waste_records"

    id = Column(String(64), primary_key=True)
    institution_id = Column(String(64), default="VESIT")
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    date_str = Column(String(16), nullable=False, index=True)
    recyclable_kg = Column(Float, default=0.0)
    non_recyclable_kg = Column(Float, default=0.0)
    composted_kg = Column(Float, default=0.0)
    total_kg = Column(Float, default=0.0)
    emissions_kgco2e = Column(Float, default=0.0)
    source_type = Column(String(32), default="SYNTHETIC")


class TransportRecord(Base):
    __tablename__ = "transport_records"

    id = Column(String(64), primary_key=True)
    institution_id = Column(String(64), default="VESIT")
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    date_str = Column(String(16), nullable=False, index=True)
    mode = Column(String(64), nullable=False) # BUS, TRAIN, CAR, TWO_WHEELER, WALKING, CYCLING
    user_type = Column(String(32), default="STUDENT") # STUDENT, FACULTY, STAFF
    passenger_km = Column(Float, default=0.0)
    trips_count = Column(Integer, default=0)
    emissions_kgco2e = Column(Float, default=0.0)
    source_type = Column(String(32), default="SYNTHETIC")


class SustainabilityInitiativeModel(Base):
    __tablename__ = "sustainability_initiatives"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    lead_department = Column(String(128), default="Green Campus Committee")
    status = Column(String(32), default="ACTIVE") # PLANNED, ACTIVE, COMPLETED
    start_date = Column(String(32), nullable=True)
    completion_date = Column(String(32), nullable=True)
    sdg_ids_json = Column(Text, default="[]")
    target_ids_json = Column(Text, default="[]")
    carbon_reduction_estimate_kgco2e = Column(Float, default=0.0)
    source_type = Column(String(32), default="SYNTHETIC")


class SustainabilityTargetModel(Base):
    __tablename__ = "sustainability_targets"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(64), default="CARBON") # CARBON, ENERGY, WATER, WASTE, TRANSPORT
    baseline_year = Column(Integer, default=2024)
    target_year = Column(Integer, default=2040)
    baseline_value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)
    status = Column(String(32), default="IN_PROGRESS")
    source_type = Column(String(32), default="SYNTHETIC")


class EmissionFactorModel(Base):
    __tablename__ = "emission_factors"

    id = Column(String(64), primary_key=True)
    category = Column(String(64), nullable=False) # ELECTRICITY, DIESEL, TRANSPORT, WASTE
    name = Column(String(128), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(64), nullable=False)
    reference_year = Column(Integer, default=2024)
    region = Column(String(64), default="India / Maharashtra")
    source = Column(String(255), nullable=False)
    source_type = Column(String(32), default="SYNTHETIC") # DOCUMENTED, SYNTHETIC, ESTIMATED
    version = Column(String(16), default="1.0")


class SDGModel(Base):
    __tablename__ = "sdgs"

    id = Column(String(32), primary_key=True)
    sdg_number = Column(Integer, nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    color = Column(String(16), default="#10b981")
    official_targets_json = Column(Text, default="[]")


class SimulationRecord(Base):
    __tablename__ = "simulations"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    scenario_type = Column(String(64), nullable=False) # SOLAR, TRANSPORT, WASTE, WATER, COMBINED
    parameters_json = Column(Text, nullable=False)
    baseline_emissions_kgco2e = Column(Float, default=0.0)
    projected_emissions_kgco2e = Column(Float, default=0.0)
    reduction_kgco2e = Column(Float, default=0.0)
    percentage_reduction = Column(Float, default=0.0)
    resource_savings_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class EvaluationBenchmark(Base):
    __tablename__ = "evaluation_benchmarks"

    id = Column(String(64), primary_key=True)
    query_id = Column(String(64), unique=True, nullable=False)
    question = Column(Text, nullable=False)
    query_type = Column(String(64), nullable=False) # SINGLE_HOP, MULTI_HOP, AGGREGATION, COMPARATIVE, EVIDENCE_BASED, UNSUPPORTED
    ground_truth_answer = Column(Text, nullable=False)
    ground_truth_entities_json = Column(Text, default="[]")
    ground_truth_relationships_json = Column(Text, default="[]")
    ground_truth_chunks_json = Column(Text, default="[]")
    complexity = Column(String(32), default="MEDIUM")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(String(64), primary_key=True)
    run_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    method = Column(String(64), nullable=False) # VECTOR_RAG, GRAPH_RAG, HYBRID_GRAPHRAG
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    f1 = Column(Float, default=0.0)
    mrr = Column(Float, default=0.0)
    recall_at_k = Column(Float, default=0.0)
    evidence_support_rate = Column(Float, default=0.0)
    answer_correctness = Column(Float, default=0.0)
    unsupported_claim_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    total_queries = Column(Integer, default=0)
    details_json = Column(Text, default="{}")

