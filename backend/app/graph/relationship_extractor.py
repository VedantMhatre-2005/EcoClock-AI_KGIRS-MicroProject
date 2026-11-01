import re
from typing import List, Dict, Any, Tuple
from app.graph.graph_schema import RelationshipType, VerificationStatus, ALLOWABLE_TRIPLES
from app.graph.entity_resolution import EntityResolver
from app.services.llm_service import llm_service

# Known domain associations from institutional documents to ensure rich graph connectivity
INITIATIVE_RELATIONS = {
    "INIT_SOLAR_PH1": {
        "buildings": ["BLD_ACA", "BLD_ACB", "BLD_LIB", "BLD_ADM"],
        "sdgs": ["SDG_7", "SDG_11", "SDG_13"],
        "targets": ["TRG_NET_ZERO", "TRG_RENEWABLE"]
    },
    "INIT_SOLAR_PH2": {
        "buildings": ["BLD_AUD"],
        "sdgs": ["SDG_7", "SDG_9", "SDG_13"],
        "targets": ["TRG_NET_ZERO", "TRG_RENEWABLE"]
    },
    "INIT_RWH_SYSTEM": {
        "buildings": ["BLD_ACA", "BLD_ACB", "BLD_LIB"],
        "sdgs": ["SDG_6", "SDG_11", "SDG_12"],
        "targets": ["TRG_WATER_NEUTRAL"]
    },
    "INIT_BIOGAS_CANTEEN": {
        "buildings": ["BLD_CAN"],
        "sdgs": ["SDG_12", "SDG_13", "SDG_15"],
        "targets": ["TRG_ZERO_WASTE", "TRG_NET_ZERO"]
    },
    "INIT_ELECTRIC_SHUTTLE": {
        "buildings": [],
        "sdgs": ["SDG_11", "SDG_13"],
        "targets": ["TRG_GREEN_COMMUTE", "TRG_NET_ZERO"]
    },
    "INIT_IOT_ENERGY_MGT": {
        "buildings": ["BLD_ACA", "BLD_ACB", "BLD_LAB", "BLD_LIB", "BLD_AUD", "BLD_CAN", "BLD_ADM"],
        "sdgs": ["SDG_7", "SDG_9", "SDG_12"],
        "targets": ["TRG_NET_ZERO", "TRG_RENEWABLE"]
    },
    "INIT_BIODIVERSITY_ZONE": {
        "buildings": ["BLD_AUD"],
        "sdgs": ["SDG_13", "SDG_15"],
        "targets": ["TRG_NET_ZERO"]
    }
}

class RelationshipExtractor:
    def __init__(self):
        pass

    def extract_from_chunk(
        self,
        chunk_text: str,
        document_id: str,
        chunk_id: str,
        extracted_entities: List[Dict[str, Any]],
        document_title: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Extracts schema-constrained relationships connecting recognized entities with explicit provenance.
        """
        relationships: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        entities_by_canon = {e["canonical_id"]: e for e in extracted_entities}

        # 1. LLM-based relationship extraction if Ollama is connected
        if llm_service.check_connection()["connected"]:
            try:
                res = llm_service.extract_graph_elements(chunk_text, document_title)
                for rel in res.relationships:
                    src_id, _, src_type = EntityResolver.resolve_entity(rel.source_entity)
                    tgt_id, _, tgt_type = EntityResolver.resolve_entity(rel.target_entity)
                    rtype = rel.relationship_type.upper()

                    v_status = VerificationStatus.INFERRED.value if rel.is_inferred else VerificationStatus.EXPLICIT.value
                    rel_id = f"REL_{chunk_id}_{src_id}_{rtype}_{tgt_id}"
                    relationships[(src_id, rtype, tgt_id)] = {
                        "relationship_id": rel_id,
                        "source_id": src_id,
                        "target_id": tgt_id,
                        "relationship_type": rtype,
                        "source_document_id": document_id,
                        "chunk_id": chunk_id,
                        "evidence_excerpt": rel.evidence_excerpt or chunk_text[:200],
                        "extraction_method": "LLM_EXTRACTION",
                        "confidence": rel.confidence,
                        "verification_status": v_status
                    }
            except Exception:
                pass

        # 2. Domain ontology extraction: connect initiatives present in chunk to their targets, SDGs, and buildings
        for canon_id in entities_by_canon:
            if canon_id in INITIATIVE_RELATIONS:
                init_info = INITIATIVE_RELATIONS[canon_id]

                # Connect to institution
                rel_id = f"REL_{chunk_id}_VESIT_IMPLEMENTS_{canon_id}"
                relationships[("VESIT", "IMPLEMENTS_INITIATIVE", canon_id)] = {
                    "relationship_id": rel_id,
                    "source_id": "VESIT",
                    "target_id": canon_id,
                    "relationship_type": "IMPLEMENTS_INITIATIVE",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "DOMAIN_ONTOLOGY",
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

                # Connect to SDGs mentioned or linked
                for sid in init_info["sdgs"]:
                    if sid in entities_by_canon or sid.lower() in chunk_text.lower():
                        rel_id = f"REL_{chunk_id}_{canon_id}_SUPPORTS_{sid}"
                        relationships[(canon_id, "SUPPORTS_SDG", sid)] = {
                            "relationship_id": rel_id,
                            "source_id": canon_id,
                            "target_id": sid,
                            "relationship_type": "SUPPORTS_SDG",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 1.0,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

                # Connect to Targets
                for tid in init_info["targets"]:
                    if tid in entities_by_canon or tid.lower() in chunk_text.lower():
                        rel_id = f"REL_{chunk_id}_{canon_id}_ADDRESSES_{tid}"
                        relationships[(canon_id, "ADDRESSES_TARGET", tid)] = {
                            "relationship_id": rel_id,
                            "source_id": canon_id,
                            "target_id": tid,
                            "relationship_type": "ADDRESSES_TARGET",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 1.0,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

                # Connect to Buildings
                for bid in init_info["buildings"]:
                    if bid in entities_by_canon:
                        rel_id = f"REL_{chunk_id}_{bid}_APPLIES_TO_{canon_id}"
                        relationships[(bid, "APPLIES_TO", canon_id)] = {
                            "relationship_id": rel_id,
                            "source_id": bid,
                            "target_id": canon_id,
                            "relationship_type": "APPLIES_TO",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 1.0,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

        # 3. Connect Document to Initiatives & Targets mentioned in chunk
        for e in extracted_entities:
            cid = e["canonical_id"]
            if e["entity_type"] in ["SustainabilityInitiative", "SustainabilityTarget"]:
                rel_id = f"REL_{chunk_id}_{cid}_SUPPORTED_BY_{document_id}"
                relationships[(cid, "SUPPORTED_BY", document_id)] = {
                    "relationship_id": rel_id,
                    "source_id": cid,
                    "target_id": document_id,
                    "relationship_type": "SUPPORTED_BY",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "DOCUMENT_PROVENANCE",
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

        # 4. Connect Institution to Buildings present
        for e in extracted_entities:
            if e["entity_type"] == "Building":
                bid = e["canonical_id"]
                rel_id = f"REL_{chunk_id}_VESIT_HAS_BUILDING_{bid}"
                relationships[("VESIT", "HAS_BUILDING", bid)] = {
                    "relationship_id": rel_id,
                    "source_id": "VESIT",
                    "target_id": bid,
                    "relationship_type": "HAS_BUILDING",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "STRUCTURAL",
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

        return list(relationships.values())
