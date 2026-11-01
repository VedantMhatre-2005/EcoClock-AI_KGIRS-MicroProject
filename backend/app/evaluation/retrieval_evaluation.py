from typing import List, Set, Dict, Any

class RetrievalEvaluator:
    @staticmethod
    def evaluate_retrieval(
        retrieved_items: List[str],
        ground_truth_items: List[str],
        k: int = 5
    ) -> Dict[str, float]:
        """
        Computes Recall@K, Precision@K, and MRR (Mean Reciprocal Rank).
        """
        if not ground_truth_items:
            # If ground truth is empty (e.g. negative question), perfect retrieval means retrieving 0 irrelevant items
            return {
                "recall_at_k": 1.0 if not retrieved_items else 0.0,
                "precision_at_k": 1.0 if not retrieved_items else 0.0,
                "reciprocal_rank": 1.0 if not retrieved_items else 0.0
            }

        gt_set = set(ground_truth_items)
        top_k = retrieved_items[:k]
        hits = [item for item in top_k if item in gt_set]

        recall = len(hits) / float(len(gt_set)) if gt_set else 0.0
        precision = len(hits) / float(len(top_k)) if top_k else 0.0

        rr = 0.0
        for rank, item in enumerate(retrieved_items, 1):
            if item in gt_set:
                rr = 1.0 / rank
                break

        return {
            "recall_at_k": round(recall, 4),
            "precision_at_k": round(precision, 4),
            "reciprocal_rank": round(rr, 4)
        }

retrieval_evaluator = RetrievalEvaluator()

