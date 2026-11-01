import time
import json
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.schema import EvaluationResult, EvaluationBenchmark
from app.evaluation.benchmark_dataset import BENCHMARK_QUESTIONS
from app.rag.rag_pipeline import rag_pipeline
from app.evaluation.retrieval_evaluation import retrieval_evaluator
from app.evaluation.answer_evaluation import answer_evaluator
from app.evaluation.extraction_evaluation import extraction_evaluator

class BenchmarkRunner:
    @staticmethod
    def seed_benchmarks(db: Session):
        """Seeds benchmark questions into database if not already present."""
        if db.query(EvaluationBenchmark).count() == 0:
            for b in BENCHMARK_QUESTIONS:
                db.add(EvaluationBenchmark(
                    id=b["query_id"],
                    query_id=b["query_id"],
                    question=b["question"],
                    query_type=b["query_type"],
                    ground_truth_answer=b["ground_truth_answer"],
                    ground_truth_entities_json=json.dumps(b["ground_truth_entities"]),
                    ground_truth_chunks_json=json.dumps(b["ground_truth_chunks"]),
                    complexity=b["complexity"]
                ))
            db.commit()

    @staticmethod
    def run_benchmark(db: Session) -> Dict[str, Any]:
        """
        Executes genuine comparative evaluation across VECTOR_RAG, GRAPH_RAG, and HYBRID_GRAPHRAG.
        Persists metrics to SQLite.
        """
        BenchmarkRunner.seed_benchmarks(db)
        run_id = f"RUN_{uuid.uuid4().hex[:8]}"
        modes = ["VECTOR_RAG", "GRAPH_RAG", "HYBRID_GRAPHRAG"]
        results_by_mode: Dict[str, Dict[str, Any]] = {}

        for mode in modes:
            total_recalls = []
            total_precisions = []
            total_f1s = []
            total_mrrs = []
            total_recalls_at_k = []
            total_support_rates = []
            total_correctness = []
            total_unsupported_rates = []
            latencies = []

            for q in BENCHMARK_QUESTIONS:
                t0 = time.time()
                res = rag_pipeline.query(db, q["question"], mode=mode)
                latency_ms = (time.time() - t0) * 1000.0
                latencies.append(latency_ms)

                # Evaluate retrieval
                retrieved_chunks = [c["chunk_id"] for c in res.get("citations", [])]
                ret_metrics = retrieval_evaluator.evaluate_retrieval(
                    retrieved_chunks, q["ground_truth_chunks"], k=5
                )
                total_recalls_at_k.append(ret_metrics["recall_at_k"])
                total_mrrs.append(ret_metrics["reciprocal_rank"])

                # Evaluate entities
                retrieved_entities = [gp["source"] for gp in res.get("graph_paths", [])] + [gp["target"] for gp in res.get("graph_paths", [])]
                ext_metrics = extraction_evaluator.evaluate_extraction(
                    retrieved_entities, q["ground_truth_entities"]
                )
                total_precisions.append(ext_metrics["precision"])
                total_recalls.append(ext_metrics["recall"])
                total_f1s.append(ext_metrics["f1"])

                # Evaluate answer
                ans_metrics = answer_evaluator.evaluate_answer(
                    res["answer"], q["ground_truth_answer"], res.get("citations", []), q["query_type"]
                )
                total_correctness.append(ans_metrics["answer_correctness"])
                total_support_rates.append(ans_metrics["evidence_support_rate"])
                total_unsupported_rates.append(ans_metrics["unsupported_claim_rate"])

            # Compute macro averages
            avg_prec = round(sum(total_precisions) / len(total_precisions), 4)
            avg_rec = round(sum(total_recalls) / len(total_recalls), 4)
            avg_f1 = round(sum(total_f1s) / len(total_f1s), 4)
            avg_mrr = round(sum(total_mrrs) / len(total_mrrs), 4)
            avg_rec_k = round(sum(total_recalls_at_k) / len(total_recalls_at_k), 4)
            avg_supp = round(sum(total_support_rates) / len(total_support_rates), 4)
            avg_corr = round(sum(total_correctness) / len(total_correctness), 4)
            avg_unsup = round(sum(total_unsupported_rates) / len(total_unsupported_rates), 4)
            avg_lat = round(sum(latencies) / len(latencies), 2)

            mode_summary = {
                "run_id": run_id,
                "method": mode,
                "precision": avg_prec,
                "recall": avg_rec,
                "f1": avg_f1,
                "mrr": avg_mrr,
                "recall_at_k": avg_rec_k,
                "evidence_support_rate": avg_supp,
                "answer_correctness": avg_corr,
                "unsupported_claim_rate": avg_unsup,
                "avg_latency_ms": avg_lat,
                "total_queries": len(BENCHMARK_QUESTIONS)
            }
            results_by_mode[mode] = mode_summary

            # Persist record
            eval_record = EvaluationResult(
                id=f"{run_id}_{mode}",
                run_id=run_id,
                method=mode,
                precision=avg_prec,
                recall=avg_rec,
                f1=avg_f1,
                mrr=avg_mrr,
                recall_at_k=avg_rec_k,
                evidence_support_rate=avg_supp,
                answer_correctness=avg_corr,
                unsupported_claim_rate=avg_unsup,
                avg_latency_ms=avg_lat,
                total_queries=len(BENCHMARK_QUESTIONS)
            )
            db.add(eval_record)

        db.commit()

        return {
            "run_id": run_id,
            "results": results_by_mode
        }

    @staticmethod
    def get_latest_results(db: Session) -> List[Dict[str, Any]]:
        """Retrieves most recent evaluation run results."""
        latest_record = db.query(EvaluationResult).order_by(EvaluationResult.timestamp.desc()).first()
        if not latest_record:
            # If no runs yet, run benchmark to produce real results
            return list(BenchmarkRunner.run_benchmark(db)["results"].values())

        run_id = latest_record.run_id
        records = db.query(EvaluationResult).filter(EvaluationResult.run_id == run_id).all()
        return [
            {
                "run_id": r.run_id,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "method": r.method,
                "precision": r.precision,
                "recall": r.recall,
                "f1": r.f1,
                "mrr": r.mrr,
                "recall_at_k": r.recall_at_k,
                "evidence_support_rate": r.evidence_support_rate,
                "answer_correctness": r.answer_correctness,
                "unsupported_claim_rate": r.unsupported_claim_rate,
                "avg_latency_ms": r.avg_latency_ms,
                "total_queries": r.total_queries
            }
            for r in records
        ]

benchmark_runner = BenchmarkRunner()

