import time
import logging
from typing import Dict, Any, List
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

GROUNDING_SYSTEM_PROMPT = """You are EcoClock AI, a factual campus sustainability assistant.
Strict Grounding Rules:
1. Answer the question using ONLY the provided Document Evidence and Knowledge Graph Relationships.
2. Every factual statement must cite its source (e.g., [1], [2], or graph relation).
3. Never invent, extrapolate, or hallucinate missing measurements or dates.
4. If the provided evidence does not contain sufficient facts to answer the question, you MUST reply:
"Information not available in the indexed sustainability documents."
5. Do not use outside knowledge about other universities or hypothetical data."""

INSTITUTIONAL_STOPWORDS = {
    "vesit", "green", "campus", "college", "institution", "what", "which", "how",
    "many", "much", "does", "that", "this", "were", "with", "from", "2024", "2025",
    "total", "annual", "about", "have", "there", "their", "where", "when", "show"
}

class AnswerGenerator:
    def __init__(self, min_similarity_threshold: float = 0.12):
        self.min_similarity_threshold = min_similarity_threshold

    def generate_answer(
        self,
        query: str,
        context_data: Dict[str, Any],
        mode: str = "HYBRID_GRAPHRAG"
    ) -> Dict[str, Any]:
        """
        Generates a grounded natural language answer supported by traceable citations and graph paths.
        """
        start_time = time.time()
        citations = context_data.get("citations", [])
        graph_paths = context_data.get("graph_paths", [])
        formatted_context = context_data.get("formatted_context", "")

        # Extract substantive content keywords from the user query
        query_words = [
            w.lower() for w in query.split()
            if len(w) > 3 and w.lower() not in INSTITUTIONAL_STOPWORDS
        ]
        citation_text = (
            " ".join(c.get("excerpt", "").lower() for c in citations) + " " +
            " ".join(gp.get("relationship", "").lower() + " " + gp.get("target", "").lower() for gp in graph_paths)
        )
        
        # Check if substantive keywords appear in retrieved evidence
        matching_words = [qw for qw in query_words if qw in citation_text]
        min_required = 2 if len(query_words) >= 3 else (1 if query_words else 0)
        overlap = len(matching_words) >= min_required if query_words else False

        # Strict check: If no evidence or terms do not align with corpus
        if not context_data.get("has_evidence") or not formatted_context.strip() or not overlap:
            latency = round((time.time() - start_time) * 1000, 2)
            return {
                "answer": "Information not available in the indexed sustainability documents.",
                "supporting_evidence": "No relevant document chunks or graph nodes were found matching this query.",
                "citations": [],
                "graph_paths": [],
                "retrieval_mode": mode,
                "latency_ms": latency,
                "confidence_score": 0.0,
                "is_grounded": True,
                "ollama_used": False
            }

        # Check if Ollama is connected
        conn = llm_service.check_connection()
        ollama_available = conn["connected"]
        answer_text = ""
        ollama_used = False

        if ollama_available:
            try:
                user_prompt = f"Question: {query}\n\n{formatted_context}\n\nAnswer:"
                answer_text = llm_service.generate(
                    prompt=user_prompt,
                    system=GROUNDING_SYSTEM_PROMPT,
                    temperature=0.0
                ).strip()
                ollama_used = True
            except Exception as e:
                logger.warning(f"Ollama inference error: {e}. Falling back to structured evidence synthesis.")
                ollama_used = False

        if not answer_text:
            synthesis_parts = []
            if citations:
                synthesis_parts.append(f"Based on indexed sustainability documentation:")
                for c in citations[:3]:
                    synthesis_parts.append(f"• According to {c['document_title']} ({c['chunk_id']}): {c['excerpt']}")
            if graph_paths:
                synthesis_parts.append(f"\nKnowledge Graph Path Evidence:")
                for gp in graph_paths[:3]:
                    synthesis_parts.append(f"• {gp['source']} -[{gp['relationship']}]-> {gp['target']}")

            answer_text = "\n".join(synthesis_parts)

        latency = round((time.time() - start_time) * 1000, 2)
        confidence = min(1.0, 0.5 + (0.1 * len(citations)) + (0.05 * len(graph_paths)))

        return {
            "answer": answer_text,
            "supporting_evidence": formatted_context[:600],
            "citations": citations,
            "graph_paths": graph_paths,
            "retrieval_mode": mode,
            "latency_ms": latency,
            "confidence_score": round(confidence, 2),
            "is_grounded": True,
            "ollama_used": ollama_used
        }

answer_generator = AnswerGenerator()
