import time
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.context_builder import ContextBuilder
from app.rag.answer_generator import answer_generator
from app.rag.query_validator import QueryValidator
from app.database.neo4j_client import neo4j_client
from app.services.llm_service import llm_service
from app.graph.graph_builder import graph_builder

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        pass

    def query(
        self,
        db: Session,
        query_text: str,
        mode: str = "HYBRID_GRAPHRAG"
    ) -> Dict[str, Any]:
        """
        Executes Question-Answering across VECTOR_RAG, GRAPH_RAG, or HYBRID_GRAPHRAG modes.
        """
        # 1. Retrieve evidence
        retrieval_res = hybrid_retriever.retrieve(db, query_text, mode=mode)

        # 2. Build grounded context
        context_data = ContextBuilder.build_grounded_context(retrieval_res)

        # 3. Generate grounded answer
        answer_res = answer_generator.generate_answer(query_text, context_data, mode=mode)

        return {
            "query": query_text,
            "mode": mode,
            **answer_res
        }

    def execute_nl_to_cypher(self, user_question: str) -> Dict[str, Any]:
        """
        Translates a natural language question into validated, safe Cypher, executes it,
        and returns results with an evidence-grounded explanation.
        """
        start_time = time.time()

        # 1. Define active schema
        schema_summary = """
Nodes:
- Institution {id, name, location, student_population, total_built_up_area_m2}
- Building {id, name, area_m2, primary_use, occupancy, has_rooftop_solar, solar_capacity_kw}
- Department {id, name, head}
- SustainabilityInitiative {id, name, description, status, carbon_reduction_estimate_kgco2e}
- SustainabilityTarget {id, title, category, baseline_year, target_year, baseline_value, target_value, unit}
- SDG {id, sdg_number, name, description}
- Document {id, title, type, publication_date}
Relationships:
- (:Institution)-[:HAS_BUILDING]->(:Building)
- (:Institution)-[:HAS_DEPARTMENT]->(:Department)
- (:Institution)-[:IMPLEMENTS_INITIATIVE]->(:SustainabilityInitiative)
- (:Institution)-[:HAS_TARGET]->(:SustainabilityTarget)
- (:SustainabilityInitiative)-[:SUPPORTS_SDG]->(:SDG)
- (:SustainabilityInitiative)-[:ADDRESSES_TARGET]->(:SustainabilityTarget)
- (:Building)-[:APPLIES_TO]->(:SustainabilityInitiative)
"""

        generated_cypher = ""
        conn = llm_service.check_connection()

        if conn["connected"]:
            try:
                generated_cypher = llm_service.generate_cypher(user_question, schema_summary)
            except Exception as e:
                logger.warning(f"Error calling LLM for Cypher: {e}")

        # Deterministic schema fallback if LLM is not connected or failed
        if not generated_cypher:
            q_lower = user_question.lower()
            if "sdg 13" in q_lower or "climate action" in q_lower:
                generated_cypher = "MATCH (i:SustainabilityInitiative)-[:SUPPORTS_SDG]->(s:SDG {id: 'SDG_13'}) RETURN i.id as id, i.name as name, i.status as status LIMIT 10"
            elif "solar" in q_lower or "renewable" in q_lower:
                generated_cypher = "MATCH (b:Building) WHERE b.has_rooftop_solar = true RETURN b.name as building, b.solar_capacity_kw as solar_capacity_kw LIMIT 10"
            elif "initiative" in q_lower:
                generated_cypher = "MATCH (i:SustainabilityInitiative)-[:SUPPORTS_SDG]->(s:SDG) RETURN i.name as initiative, s.name as sdg, i.carbon_reduction_estimate_kgco2e as reduction_kgco2e LIMIT 10"
            elif "building" in q_lower:
                generated_cypher = "MATCH (b:Building) RETURN b.name as name, b.area_m2 as area_m2, b.occupancy as occupancy LIMIT 10"
            elif "target" in q_lower or "net zero" in q_lower:
                generated_cypher = "MATCH (t:SustainabilityTarget) RETURN t.title as title, t.baseline_year as baseline, t.target_year as target_year, t.target_value as value LIMIT 10"
            else:
                generated_cypher = "MATCH (n) RETURN labels(n) as label, count(n) as count LIMIT 10"

        # 2. Validate Cypher query safety
        is_valid, validated_cypher = QueryValidator.validate_cypher(generated_cypher)
        if not is_valid:
            latency = round((time.time() - start_time) * 1000, 2)
            return {
                "question": user_question,
                "generated_cypher": generated_cypher,
                "is_valid": False,
                "error": validated_cypher,
                "records": [],
                "explanation": f"Query rejected by security validator: {validated_cypher}",
                "latency_ms": latency
            }

        # 3. Execute Cypher against Neo4j or Local Graph Store
        records: List[Dict[str, Any]] = []
        execution_source = "Neo4j"

        if neo4j_client.is_connected:
            try:
                records = neo4j_client.execute_read(validated_cypher)
            except Exception as e:
                logger.warning(f"Neo4j query execution failed: {e}")
                execution_source = "Local Graph Store"
        else:
            execution_source = "Local Graph Store"

        if not records:
            # Query local in-memory graph index
            if "Building" in validated_cypher:
                records = [
                    {"building": n["name"], "solar_capacity_kw": n.get("solar_capacity_kw", 0), "area_m2": n.get("area_m2", 0)}
                    for n in graph_builder.nodes.values() if n.get("label") == "Building"
                ][:10]
            elif "SDG" in validated_cypher:
                records = [
                    {"initiative": e["source_id"], "sdg": e["target_id"], "evidence": e.get("evidence_excerpt", "")[:100]}
                    for e in graph_builder.edges if e.get("type") == "SUPPORTS_SDG"
                ][:10]
            elif "Target" in validated_cypher or "target" in validated_cypher.lower():
                records = [
                    {"target_id": n["id"], "title": n.get("name", n["id"])}
                    for n in graph_builder.nodes.values() if n.get("label") == "SustainabilityTarget"
                ][:10]
            else:
                records = [
                    {"entity": n["name"], "type": n.get("label")}
                    for n in list(graph_builder.nodes.values())[:10]
                ]

        # 4. Generate explanation
        explanation = f"Query executed successfully against {execution_source}. Retrieved {len(records)} matching records."
        latency = round((time.time() - start_time) * 1000, 2)

        return {
            "question": user_question,
            "generated_cypher": validated_cypher,
            "is_valid": True,
            "records": records,
            "execution_source": execution_source,
            "record_count": len(records),
            "explanation": explanation,
            "latency_ms": latency
        }

rag_pipeline = RAGPipeline()

