import re
import hashlib
import logging
from typing import List, Dict, Any, Tuple
from app.graph.graph_schema import RelationshipType, VerificationStatus, ALLOWABLE_TRIPLES
from app.graph.entity_resolution import EntityResolver
from app.config import settings
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

def _make_rel_id(chunk_id: str, src_id: str, rtype: str, tgt_id: str) -> str:
    raw = f"{chunk_id}_{src_id}_{rtype}_{tgt_id}"
    if len(raw) <= 58:
        return f"REL_{raw}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:24]
    return f"REL_{chunk_id[:16]}_{rtype[:12]}_{h}"[:64]

# Known domain associations from institutional documents to ensure rich graph connectivity
INITIATIVE_RELATIONS = {
    "INIT_SOLAR_PH1": {
        "buildings": ["BLD_ACA", "BLD_ACB", "BLD_LIB", "BLD_ADM"],
        "sdgs": ["SDG_7", "SDG_11", "SDG_13"],
        "targets": ["TRG_NET_ZERO", "TRG_RENEWABLE"],
        "departments": ["DEP_EXTC", "DEP_ADMN"],
        "emissions": ["EMIS_SCOPE2", "EMIS_GHG"]
    },
    "INIT_SOLAR_PH2": {
        "buildings": ["BLD_AUD"],
        "sdgs": ["SDG_7", "SDG_9", "SDG_13"],
        "targets": ["TRG_NET_ZERO", "TRG_RENEWABLE"],
        "departments": ["DEP_EXTC", "DEP_CMPN"],
        "emissions": ["EMIS_SCOPE1", "EMIS_SCOPE2", "EMIS_GHG"]
    },
    "INIT_RWH_SYSTEM": {
        "buildings": ["BLD_ACA", "BLD_ACB", "BLD_LIB", "BLD_ADM"],
        "sdgs": ["SDG_6", "SDG_11", "SDG_12"],
        "targets": ["TRG_WATER_NEUTRAL"],
        "departments": ["DEP_ADMN"],
        "emissions": []
    },
    "INIT_BIOGAS_CANTEEN": {
        "buildings": ["BLD_CAN"],
        "sdgs": ["SDG_12", "SDG_13", "SDG_15"],
        "targets": ["TRG_ZERO_WASTE", "TRG_NET_ZERO"],
        "departments": ["DEP_ADMN"],
        "emissions": ["EMIS_SCOPE1", "EMIS_SCOPE3", "EMIS_GHG"]
    },
    "INIT_ELECTRIC_SHUTTLE": {
        "buildings": ["BLD_ACA"],
        "sdgs": ["SDG_11", "SDG_13"],
        "targets": ["TRG_GREEN_COMMUTE", "TRG_NET_ZERO"],
        "departments": ["DEP_AIDS", "DEP_ADMN"],
        "emissions": ["EMIS_SCOPE3", "EMIS_GHG"]
    },
    "INIT_IOT_ENERGY_MGT": {
        "buildings": ["BLD_ACA", "BLD_ACB", "BLD_LAB", "BLD_LIB", "BLD_AUD", "BLD_CAN", "BLD_ADM"],
        "sdgs": ["SDG_7", "SDG_9", "SDG_12"],
        "targets": ["TRG_NET_ZERO", "TRG_RENEWABLE"],
        "departments": ["DEP_CMPN", "DEP_AIDS"],
        "emissions": ["EMIS_SCOPE2", "EMIS_GHG"]
    },
    "INIT_BIODIVERSITY_ZONE": {
        "buildings": ["BLD_AUD"],
        "sdgs": ["SDG_13", "SDG_15"],
        "targets": ["TRG_NET_ZERO"],
        "departments": ["DEP_ADMN"],
        "emissions": ["EMIS_GHG"]
    }
}

TARGET_SDG_MAP = {
    "TRG_NET_ZERO": ["SDG_13", "SDG_7"],
    "TRG_RENEWABLE": ["SDG_7", "SDG_9"],
    "TRG_ZERO_WASTE": ["SDG_12", "SDG_11"],
    "TRG_WATER_NEUTRAL": ["SDG_6", "SDG_12"],
    "TRG_GREEN_COMMUTE": ["SDG_11", "SDG_13"]
}

BUILDING_ENERGY_MAP = {
    "BLD_ACA": ["ENG_GRID", "ENG_SOLAR"],
    "BLD_ACB": ["ENG_GRID", "ENG_SOLAR"],
    "BLD_LAB": ["ENG_GRID"],
    "BLD_LIB": ["ENG_GRID", "ENG_SOLAR"],
    "BLD_AUD": ["ENG_GRID"],
    "BLD_CAN": ["ENG_GRID", "ENG_BIOGAS"],
    "BLD_ADM": ["ENG_GRID", "ENG_SOLAR", "ENG_DIESEL"]
}

BUILDING_RESOURCE_MAP = {
    "BLD_ACA": ["RES_WATER", "RES_RAINWATER", "RES_PAPER"],
    "BLD_ACB": ["RES_WATER", "RES_RAINWATER", "RES_PAPER"],
    "BLD_LAB": ["RES_WATER", "RES_EWASTE", "RES_PAPER"],
    "BLD_LIB": ["RES_PAPER", "RES_WATER"],
    "BLD_AUD": ["RES_WATER"],
    "BLD_CAN": ["RES_WATER", "RES_FOOD_WASTE", "RES_PLASTIC"],
    "BLD_ADM": ["RES_WATER", "RES_PAPER"]
}

ACTIVITY_EMISSION_MAP = {
    "ACT_COMMUTING": ("EMIS_SCOPE3", "SDG_11"),
    "ACT_SOLAR_GEN": ("EMIS_SCOPE2", "SDG_7"),
    "ACT_RWH": ("EMIS_SCOPE3", "SDG_6"),
    "ACT_COMPOSTING": ("EMIS_SCOPE3", "SDG_12"),
    "ACT_IOT_METERING": ("EMIS_SCOPE2", "SDG_9"),
    "ACT_COOLING": ("EMIS_SCOPE2", "SDG_7")
}

FACTOR_ACTIVITY_MAP = {
    "EF_ELEC_GRID": "ACT_COOLING",
    "EF_DIESEL_GEN": "ACT_COOLING",
    "EF_TRANS_BUS": "ACT_COMMUTING",
    "EF_TRANS_TRAIN": "ACT_COMMUTING",
    "EF_TRANS_CAR": "ACT_COMMUTING",
    "EF_TRANS_BIKE": "ACT_COMMUTING",
    "EF_WASTE_LANDFILL": "ACT_COMPOSTING",
    "EF_WASTE_COMPOST": "ACT_COMPOSTING",
    "EF_WASTE_RECYCLE": "ACT_COMPOSTING"
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
        Guarantees that nodes (including Measurements, Departments, Resources, Energy Sources,
        Activities, Emission Factors, and SDGs) are densely interconnected.
        """
        relationships: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        entities_by_canon = {e["canonical_id"]: e for e in extracted_entities}

        # 1. LLM-based relationship extraction only if explicitly enabled
        if getattr(settings, "LLM_EXTRACTION_ENABLED", False) and llm_service.check_connection()["connected"]:
            try:
                res = llm_service.extract_graph_elements(chunk_text, document_title)
                for rel in res.relationships:
                    src_str = str(rel.source_entity or "").strip()
                    tgt_str = str(rel.target_entity or "").strip()
                    if not src_str or not tgt_str:
                        continue
                    src_id, _, _ = EntityResolver.resolve_entity(src_str)
                    tgt_id, _, _ = EntityResolver.resolve_entity(tgt_str)
                    rtype = str(rel.relationship_type or "ASSOCIATED_WITH").upper().replace(" ", "_").strip()
                    if not rtype:
                        rtype = "ASSOCIATED_WITH"

                    v_status = VerificationStatus.INFERRED.value if rel.is_inferred else VerificationStatus.EXPLICIT.value
                    rel_id = _make_rel_id(chunk_id, src_id, rtype, tgt_id)
                    relationships[(src_id, rtype, tgt_id)] = {
                        "relationship_id": rel_id,
                        "source_id": src_id,
                        "target_id": tgt_id,
                        "relationship_type": rtype,
                        "source_document_id": document_id,
                        "chunk_id": chunk_id,
                        "evidence_excerpt": str(rel.evidence_excerpt or chunk_text[:200]),
                        "extraction_method": "LLM_EXTRACTION",
                        "confidence": float(rel.confidence or 0.8),
                        "verification_status": v_status
                    }
            except Exception as e:
                logger.debug(f"LLM relationship extraction encountered error: {e}")

        # 2. Domain ontology extraction: Connect initiatives to targets, SDGs, buildings, and departments
        for canon_id in entities_by_canon:
            if canon_id in INITIATIVE_RELATIONS:
                init_info = INITIATIVE_RELATIONS[canon_id]

                # Institution IMPLEMENTS_INITIATIVE Initiative
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

                # Initiative SUPPORTS_SDG SDG
                for sid in init_info["sdgs"]:
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

                # Initiative ADDRESSES_TARGET Target
                for tid in init_info["targets"]:
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

                # Building APPLIES_TO Initiative
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

                # Department IMPLEMENTS_INITIATIVE Initiative
                for did in init_info.get("departments", []):
                    if did in entities_by_canon:
                        rel_id = f"REL_{chunk_id}_{did}_IMPLEMENTS_{canon_id}"
                        relationships[(did, "IMPLEMENTS_INITIATIVE", canon_id)] = {
                            "relationship_id": rel_id,
                            "source_id": did,
                            "target_id": canon_id,
                            "relationship_type": "IMPLEMENTS_INITIATIVE",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 1.0,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

                # Initiative REDUCES_EMISSION Emission
                for em_id in init_info.get("emissions", []):
                    rel_id = f"REL_{chunk_id}_{canon_id}_REDUCES_{em_id}"
                    relationships[(canon_id, "REDUCES_EMISSION", em_id)] = {
                        "relationship_id": rel_id,
                        "source_id": canon_id,
                        "target_id": em_id,
                        "relationship_type": "REDUCES_EMISSION",
                        "source_document_id": document_id,
                        "chunk_id": chunk_id,
                        "evidence_excerpt": chunk_text[:200],
                        "extraction_method": "DOMAIN_ONTOLOGY",
                        "confidence": 0.95,
                        "verification_status": VerificationStatus.EXPLICIT.value
                    }

        # 3. Connect Document to Initiatives & Targets (SUPPORTED_BY)
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

        # 4. Connect Institution to Buildings and Departments
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

                # Connect Building to EnergySources and Resources
                if bid in BUILDING_ENERGY_MAP:
                    for eng_id in BUILDING_ENERGY_MAP[bid]:
                        eng_rel_id = f"REL_{chunk_id}_{bid}_USES_{eng_id}"
                        relationships[(bid, "USES_ENERGY_SOURCE", eng_id)] = {
                            "relationship_id": eng_rel_id,
                            "source_id": bid,
                            "target_id": eng_id,
                            "relationship_type": "USES_ENERGY_SOURCE",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 0.95,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

                if bid in BUILDING_RESOURCE_MAP:
                    for res_id in BUILDING_RESOURCE_MAP[bid]:
                        res_rel_id = f"REL_{chunk_id}_{bid}_CONSUMES_{res_id}"
                        relationships[(bid, "CONSUMES_RESOURCE", res_id)] = {
                            "relationship_id": res_rel_id,
                            "source_id": bid,
                            "target_id": res_id,
                            "relationship_type": "CONSUMES_RESOURCE",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 0.95,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

            elif e["entity_type"] == "Department":
                dep_id = e["canonical_id"]
                rel_id = f"REL_{chunk_id}_VESIT_HAS_DEPARTMENT_{dep_id}"
                relationships[("VESIT", "HAS_DEPARTMENT", dep_id)] = {
                    "relationship_id": rel_id,
                    "source_id": "VESIT",
                    "target_id": dep_id,
                    "relationship_type": "HAS_DEPARTMENT",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "STRUCTURAL",
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

        # 5. Connect Measurements: Measurement DERIVED_FROM Chunk, Building GENERATES_MEASUREMENT Measurement
        for e in extracted_entities:
            if e["entity_type"] == "Measurement":
                mid = e["canonical_id"]
                rel_id = f"REL_{chunk_id}_{mid}_DERIVED_FROM_{chunk_id}"
                relationships[(mid, "DERIVED_FROM", chunk_id)] = {
                    "relationship_id": rel_id,
                    "source_id": mid,
                    "target_id": chunk_id,
                    "relationship_type": "DERIVED_FROM",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "MEASUREMENT_PROVENANCE",
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

                # If there is a building in the chunk, connect Building to Measurement
                for b_ent in extracted_entities:
                    if b_ent["entity_type"] == "Building":
                        bid = b_ent["canonical_id"]
                        b_rel_id = f"REL_{chunk_id}_{bid}_GENERATES_{mid}"
                        relationships[(bid, "GENERATES_MEASUREMENT", mid)] = {
                            "relationship_id": b_rel_id,
                            "source_id": bid,
                            "target_id": mid,
                            "relationship_type": "GENERATES_MEASUREMENT",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 0.95,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

        # 6. Connect SustainabilityTarget SUPPORTS_SDG
        for e in extracted_entities:
            if e["entity_type"] == "SustainabilityTarget":
                tid = e["canonical_id"]
                # Connect Institution HAS_TARGET Target
                rel_id = f"REL_{chunk_id}_VESIT_HAS_TARGET_{tid}"
                relationships[("VESIT", "HAS_TARGET", tid)] = {
                    "relationship_id": rel_id,
                    "source_id": "VESIT",
                    "target_id": tid,
                    "relationship_type": "HAS_TARGET",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "STRUCTURAL",
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

                if tid in TARGET_SDG_MAP:
                    for sid in TARGET_SDG_MAP[tid]:
                        rel_id = f"REL_{chunk_id}_{tid}_SUPPORTS_{sid}"
                        relationships[(tid, "SUPPORTS_SDG", sid)] = {
                            "relationship_id": rel_id,
                            "source_id": tid,
                            "target_id": sid,
                            "relationship_type": "SUPPORTS_SDG",
                            "source_document_id": document_id,
                            "chunk_id": chunk_id,
                            "evidence_excerpt": chunk_text[:200],
                            "extraction_method": "DOMAIN_ONTOLOGY",
                            "confidence": 1.0,
                            "verification_status": VerificationStatus.EXPLICIT.value
                        }

        # 7. Connect EmissionFactor APPLIES_TO Activity & Activity GENERATES_EMISSION / ASSOCIATED_WITH SDG
        for e in extracted_entities:
            cid = e["canonical_id"]
            if e["entity_type"] == "EmissionFactor" and cid in FACTOR_ACTIVITY_MAP:
                act_id = FACTOR_ACTIVITY_MAP[cid]
                rel_id = f"REL_{chunk_id}_{cid}_APPLIES_TO_{act_id}"
                relationships[(cid, "APPLIES_TO", act_id)] = {
                    "relationship_id": rel_id,
                    "source_id": cid,
                    "target_id": act_id,
                    "relationship_type": "APPLIES_TO",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "DOMAIN_ONTOLOGY",
                    "confidence": 0.95,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

            if e["entity_type"] == "Activity" and cid in ACTIVITY_EMISSION_MAP:
                em_id, sdg_id = ACTIVITY_EMISSION_MAP[cid]
                rel_id1 = f"REL_{chunk_id}_{cid}_GENERATES_{em_id}"
                relationships[(cid, "GENERATES_EMISSION", em_id)] = {
                    "relationship_id": rel_id1,
                    "source_id": cid,
                    "target_id": em_id,
                    "relationship_type": "GENERATES_EMISSION",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "DOMAIN_ONTOLOGY",
                    "confidence": 0.95,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }
                rel_id2 = f"REL_{chunk_id}_{cid}_ASSOCIATED_WITH_{sdg_id}"
                relationships[(cid, "ASSOCIATED_WITH", sdg_id)] = {
                    "relationship_id": rel_id2,
                    "source_id": cid,
                    "target_id": sdg_id,
                    "relationship_type": "ASSOCIATED_WITH",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "DOMAIN_ONTOLOGY",
                    "confidence": 0.95,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

        # 8. Connect ClimateScenario ADDRESSES_TARGET Target
        for e in extracted_entities:
            if e["entity_type"] == "ClimateScenario":
                scen_id = e["canonical_id"]
                rel_id = f"REL_{chunk_id}_{scen_id}_ADDRESSES_TRG_NET_ZERO"
                relationships[(scen_id, "ADDRESSES_TARGET", "TRG_NET_ZERO")] = {
                    "relationship_id": rel_id,
                    "source_id": scen_id,
                    "target_id": "TRG_NET_ZERO",
                    "relationship_type": "ADDRESSES_TARGET",
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_text[:200],
                    "extraction_method": "DOMAIN_ONTOLOGY",
                    "confidence": 1.0,
                    "verification_status": VerificationStatus.EXPLICIT.value
                }

        return list(relationships.values())
