from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.graph.graph_schema import VerificationStatus

class RelationshipProvenance(BaseModel):
    relationship_id: str
    source_document_id: str
    chunk_id: Optional[str] = None
    evidence_excerpt: str = Field(..., description="Verbatim textual evidence grounding this relationship")
    extraction_method: str = Field("LLM_EXTRACTION", description="Extraction technique: LLM_EXTRACTION, RULE_BASED, MANUAL")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    verification_status: VerificationStatus = Field(VerificationStatus.EXPLICIT)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class EntityProvenance(BaseModel):
    document_id: str
    chunk_id: Optional[str] = None
    mention_text: str
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    verification_status: VerificationStatus = Field(VerificationStatus.EXPLICIT)

