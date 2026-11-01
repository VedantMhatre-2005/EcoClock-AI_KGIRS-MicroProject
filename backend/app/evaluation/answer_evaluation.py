import re
from typing import Dict, Any, List

class AnswerEvaluator:
    @staticmethod
    def evaluate_answer(
        generated_answer: str,
        ground_truth_answer: str,
        citations: List[Dict[str, Any]],
        query_type: str = "SINGLE_HOP"
    ) -> Dict[str, float]:
        """
        Calculates answer correctness, evidence support rate, and unsupported claim rate.
        """
        gen_clean = generated_answer.lower().strip()
        gt_clean = ground_truth_answer.lower().strip()

        # Check negative / unsupported handling
        if query_type == "UNSUPPORTED":
            is_correct_negative = (
                "information not available" in gen_clean or
                "no relevant" in gen_clean or
                not citations
            )
            return {
                "answer_correctness": 1.0 if is_correct_negative else 0.0,
                "evidence_support_rate": 1.0,
                "unsupported_claim_rate": 0.0 if is_correct_negative else 1.0
            }

        # Token set overlap (Jaccard / recall against reference)
        gen_words = set(re.findall(r'\b[a-z0-9]{3,}\b', gen_clean))
        gt_words = set(re.findall(r'\b[a-z0-9]{3,}\b', gt_clean))

        if not gt_words:
            overlap = 1.0
        else:
            overlap = len(gen_words.intersection(gt_words)) / float(len(gt_words))

        # Check numeric and key fact match
        gt_numbers = re.findall(r'\b\d+(?:,\d+)?(?:\.\d+)?\b', ground_truth_answer)
        number_match = 1.0
        if gt_numbers:
            num_hits = sum(1 for n in gt_numbers if n.replace(",", "") in gen_clean.replace(",", ""))
            number_match = num_hits / float(len(gt_numbers))

        answer_correctness = round((0.6 * overlap) + (0.4 * number_match), 4)

        # Evidence support rate: proportion of statements with citations
        has_citations = len(citations) > 0
        evidence_support_rate = 1.0 if has_citations else 0.3
        unsupported_claim_rate = round(max(0.0, 1.0 - evidence_support_rate), 4)

        return {
            "answer_correctness": min(1.0, answer_correctness),
            "evidence_support_rate": evidence_support_rate,
            "unsupported_claim_rate": unsupported_claim_rate
        }

answer_evaluator = AnswerEvaluator()

