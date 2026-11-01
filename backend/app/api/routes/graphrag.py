from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.api.dependencies import get_db
from app.rag.rag_pipeline import rag_pipeline

router = APIRouter(prefix="/graphrag", tags=["GraphRAG"])

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question about campus sustainability")
    mode: str = Field("HYBRID_GRAPHRAG", description="VECTOR_RAG, GRAPH_RAG, or HYBRID_GRAPHRAG")

class CypherRequest(BaseModel):
    question: str = Field(..., description="Natural language question to translate into Cypher and execute")

@router.post("/query")
def execute_graphrag_query(payload: QueryRequest, db: Session = Depends(get_db)):
    """
    Executes grounded Question-Answering across VECTOR_RAG, GRAPH_RAG, or HYBRID_GRAPHRAG.
    Returns direct answer, citations, graph paths, and execution latency.
    """
    return rag_pipeline.query(db=db, query_text=payload.query, mode=payload.mode)

@router.post("/cypher")
def execute_natural_language_to_cypher(payload: CypherRequest):
    """
    Translates question to safe read-only Cypher, executes it, and returns results with natural explanation.
    """
    return rag_pipeline.execute_nl_to_cypher(payload.question)

