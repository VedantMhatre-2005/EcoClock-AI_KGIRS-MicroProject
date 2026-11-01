from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.evaluation.benchmark_runner import benchmark_runner

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.post("/run")
def run_evaluation_benchmark(db: Session = Depends(get_db)):
    """
    Executes live benchmark across 30 curated questions comparing VECTOR_RAG, GRAPH_RAG, and HYBRID_GRAPHRAG.
    Calculates Precision, Recall, F1, MRR, Recall@K, Support Rate, Correctness, and Latency.
    """
    return benchmark_runner.run_benchmark(db)

@router.get("/results")
def get_evaluation_results(db: Session = Depends(get_db)):
    """Retrieves persisted evaluation results for the comparative dashboard charts."""
    return benchmark_runner.get_latest_results(db)

