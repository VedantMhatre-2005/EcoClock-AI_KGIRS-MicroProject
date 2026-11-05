import re
import hashlib
import logging
from typing import List, Dict, Any
from app.graph.graph_schema import NodeLabel, VerificationStatus
from app.graph.entity_resolution import EntityResolver, KNOWN_ALIASES
from app.services.llm_service import llm_service

from app.config import settings

logger = logging.getLogger(__name__)

def _make_ent_id(chunk_id: str, canon_id: str) -> str:
    raw = f"{chunk_id}_{canon_id}" if chunk_id else canon_id
    if len(raw) <= 58:
        return f"ENT_{raw}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:24]
    prefix = chunk_id[:16] if chunk_id else "ENT"
    return f"ENT_{prefix}_{h}"[:64]

class EntityExtractor:
    def __init__(self):
        pass

    def extract_from_text(self, text: str, document_id: str, chunk_id: str = None, document_title: str = "") -> List[Dict[str, Any]]:
        """
        Extracts entities from chunk text. Uses LLM if explicitly enabled; augments with deterministic
        ontology pattern matching to guarantee complete evidence coverage.
        """
        extracted_entities: Dict[str, Dict[str, Any]] = {}

        # 1. Try Ollama LLM extraction only if explicitly enabled
        if getattr(settings, "LLM_EXTRACTION_ENABLED", False) and llm_service.check_connection()["connected"]:
            try:
                res = llm_service.extract_graph_elements(text, document_title)
                for ent in res.entities:
                    name_str = str(ent.name or "").strip()
                    if not name_str:
                        continue
                    canon_id, canon_name, resolved_type = EntityResolver.resolve_entity(name_str, ent.entity_type)
                    ent_id = _make_ent_id(chunk_id, canon_id)
                    extracted_entities[canon_id] = {
                        "id": ent_id,
                        "canonical_id": canon_id,
                        "name": canon_name,
                        "entity_type": resolved_type,
                        "properties": ent.properties if isinstance(ent.properties, dict) else {},
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "confidence": float(ent.confidence or 0.9),
                        "verification_status": VerificationStatus.EXPLICIT.value
                    }
            except Exception as e:
                logger.debug(f"LLM entity extraction error: {e}")

        # 2. Ontology & Pattern matching extraction (guarantees schema completeness)
        text_lower = text.lower()
        for alias, (canon_id, canon_name, entity_type) in KNOWN_ALIASES.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                if canon_id not in extracted_entities:
                    ent_id = _make_ent_id(chunk_id, canon_id)
                    extracted_entities[canon_id] = {
                        "id": ent_id,
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
                meas_canon = f"MEAS_{val_str}_{unit_str.replace(' ', '_')}"
                meas_id = _make_ent_id(chunk_id, meas_canon)
                extracted_entities[meas_canon] = {
                    "id": meas_id,
                    "canonical_id": meas_canon,
                    "name": f"{val_str} {unit_str}",
                    "entity_type": NodeLabel.MEASUREMENT.value,
                    "properties": {"value": float(val_str), "unit": unit_str},
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

        return list(extracted_entities.values())
