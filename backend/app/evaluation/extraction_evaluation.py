from typing import List, Set, Dict, Any, Tuple

class ExtractionEvaluator:
    @staticmethod
    def evaluate_extraction(
        extracted_entities: List[str],
        ground_truth_entities: List[str]
    ) -> Dict[str, float]:
        """
        Computes Precision, Recall, and F1 score for extracted elements against ground truth.
        """
        pred_set = set(extracted_entities)
        gt_set = set(ground_truth_entities)

        if not gt_set and not pred_set:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
        if not gt_set or not pred_set:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        true_positives = len(pred_set.intersection(gt_set))
        precision = true_positives / float(len(pred_set)) if pred_set else 0.0
        recall = true_positives / float(len(gt_set)) if gt_set else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)
        }

extraction_evaluator = ExtractionEvaluator()

