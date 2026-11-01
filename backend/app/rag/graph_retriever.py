import re
from typing import List, Dict, Any, Set
from app.graph.entity_resolution import EntityResolver, KNOWN_ALIASES
from app.graph.graph_builder import graph_builder

class GraphRetriever:
    def __init__(self):
        pass

    def extract_query_entities(self, query: str) -> List[str]:
        """Identifies entities mentioned in the natural language query."""
        matched_canonical_ids: Set[str] = set()
        q_lower = query.lower()

        # Check alias lookup
        for alias, (canon_id, _, _) in KNOWN_ALIASES.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, q_lower):
                matched_canonical_ids.add(canon_id)

        # Keyword mapping for broad topics
        topic_map = {
            "solar": "INIT_SOLAR_PH1",
            "photovoltaic": "INIT_SOLAR_PH1",
            "electricity": "TRG_RENEWABLE",
            "energy": "TRG_RENEWABLE",
            "water": "INIT_RWH_SYSTEM",
            "rainwater": "INIT_RWH_SYSTEM",
            "waste": "INIT_BIOGAS_CANTEEN",
            "compost": "INIT_BIOGAS_CANTEEN",
            "biogas": "INIT_BIOGAS_CANTEEN",
            "transport": "INIT_ELECTRIC_SHUTTLE",
            "commute": "INIT_ELECTRIC_SHUTTLE",
            "shuttle": "INIT_ELECTRIC_SHUTTLE",
            "bus": "INIT_ELECTRIC_SHUTTLE",
            "net zero": "TRG_NET_ZERO",
            "neutrality": "TRG_NET_ZERO",
            "carbon": "TRG_NET_ZERO",
            "emissions": "TRG_NET_ZERO",
            "iot": "INIT_IOT_ENERGY_MGT",
            "metering": "INIT_IOT_ENERGY_MGT",
            "forest": "INIT_BIODIVERSITY_ZONE",
            "miyawaki": "INIT_BIODIVERSITY_ZONE",
            "tree": "INIT_BIODIVERSITY_ZONE"
        }

        for kw, target_id in topic_map.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                matched_canonical_ids.add(target_id)

        # Check SDGs
        sdg_matches = re.findall(r'\bsdg\s*([0-9]{1,2})\b', q_lower)
        for num in sdg_matches:
            matched_canonical_ids.add(f"SDG_{num}")

        return list(matched_canonical_ids)

    def retrieve_subgraph(self, query: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Retrieves graph neighborhood and multi-hop paths relevant to the user query.
        """
        entity_ids = self.extract_query_entities(query)
        if not entity_ids:
            # If no specific entity identified, anchor on institution
            entity_ids = ["VESIT"]

        subgraph = graph_builder.get_subgraph(entity_ids, max_depth=max_depth)
        return {
            "query_entities": entity_ids,
            "nodes": subgraph["nodes"],
            "edges": subgraph["edges"],
            "total_nodes": subgraph["total_nodes"],
            "total_edges": subgraph["total_edges"]
        }

graph_retriever = GraphRetriever()

