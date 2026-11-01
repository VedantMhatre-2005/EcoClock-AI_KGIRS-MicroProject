import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database.relational_db import SessionLocal, init_db
from app.evaluation.benchmark_runner import benchmark_runner

def main():
    print("Executing EcoClock AI Evaluation Benchmark across 30 questions...")
    print("Methods: VECTOR_RAG vs GRAPH_RAG vs HYBRID_GRAPHRAG")
    init_db()
    db = SessionLocal()
    try:
        results = benchmark_runner.run_benchmark(db)
        print(f"\nCompleted Benchmark Run: {results['run_id']}")
        for method, res in results["results"].items():
            print(f"\n--- {method} ---")
            print(f"Recall@K: {res['recall_at_k']:.4f} | MRR: {res['mrr']:.4f}")
            print(f"Entity F1: {res['f1']:.4f} (P: {res['precision']:.4f}, R: {res['recall']:.4f})")
            print(f"Answer Correctness: {res['answer_correctness']:.4f} | Evidence Support: {res['evidence_support_rate']:.4f}")
            print(f"Average Latency: {res['avg_latency_ms']:.1f}ms")
    finally:
        db.close()

if __name__ == "__main__":
    main()

