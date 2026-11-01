import re
from typing import List, Dict, Any
from app.graph.graph_schema import NodeLabel, VerificationStatus
from app.graph.entity_resolution import EntityResolver, KNOWN_ALIASES
from app.services.llm_service import llm_service

class EntityExtractor:
    def __init__(self):
        pass

    def extract_from_text(self, text: str, document_id: str, chunk_id: str = None, document_title: str = "") -> List[Dict[str, Any]]:
        """
        Extracts entities from chunk text. Uses LLM if available; augments with deterministic
        ontology pattern matching to guarantee complete evidence coverage.
        """
        extracted_entities: Dict[str, Dict[str, Any]] = {}

        # 1. Try Ollama LLM extraction if connected
        if llm_service.check_connection()["connected"]:
            try:
                res = llm_service.extract_graph_elements(text, document_title)
                for ent in res.entities:
                    canon_id, canon_name, resolved_type = EntityResolver.resolve_entity(ent.name, ent.entity_type)
                    extracted_entities[canon_id] = {
                        "id": f"{chunk_id}_{canon_id}" if chunk_id else canon_id,
                        "canonical_id": canon_id,
                        "name": canon_name,
                        "entity_type": resolved_type,
                        "properties": ent.properties,
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "confidence": ent.confidence,
                        "verification_status": VerificationStatus.EXPLICIT.value
                    }
            except Exception:
                pass

        # 2. Ontology & Pattern matching extraction (guarantees schema completeness)
        text_lower = text.lower()
        for alias, (canon_id, canon_name, entity_type) in KNOWN_ALIASES.items():
            # Check whole word match
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                if canon_id not in extracted_entities:
                    extracted_entities[canon_id] = {
                        "id": f"{chunk_id}_{canon_id}" if chunk_id else canon_id,
                        "canonical_id": canon_id,
                        "name": canon_name,
                        "entity_type": entity_type,
                        "properties": {},
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "confidence": 1.0,
                        "verification_status": VerificationStatus.EXPLICIT.value
                    }

        # 3. Detect quantitative Measurements (e.g., "220 kWp", "2,450,000 kg CO2e", "312,400 kWh")
        measurement_patterns = [
            (r'([\d,]+(?:\.\d+)?)\s*(kWp|kW|kWh|kg\s*CO2e|metric\s*tonnes|litres|m2|m3)', "Measurement")
        ]
        for pat, etype in measurement_patterns:
            matches = re.finditer(pat, text, re.IGNORECASE)
            for m in matches:
                val_str = m.group(1).replace(",", "")
                unit_str = m.group(2)
                meas_id = f"MEAS_{chunk_id}_{val_str}_{unit_str}"
                extracted_entities[meas_id] = {
                    "id": meas_id,
                    "canonical_id": meas_id,
                    "name": f"{val_str} {unit_str}",
                    "entity_type": NodeLabel.MEASUREMENT.value,
                    "properties": {"value": float(val_str), "unit": unit_str},
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

        return list(extracted_entities.values())

