import logging
from typing import Dict, Any, List, Set, Optional
from app.database.neo4j_client import neo4j_client
from app.graph.graph_schema import VALID_NODE_LABELS, VALID_RELATIONSHIP_TYPES

logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    def __init__(self):
        # In-memory graph mirror for instant multi-hop traversal and offline fallback
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.adjacency: Dict[str, List[Dict[str, Any]]] = {}

    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]):
        if label not in VALID_NODE_LABELS:
            label = "Entity"
        clean_props = {k: v for k, v in properties.items() if v is not None}
        clean_props["id"] = node_id
        clean_props["label"] = label

        # Update local mirror
        self.nodes[node_id] = clean_props
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []

        # If Neo4j is connected, upsert via MERGE
        if neo4j_client.is_connected:
            try:
                cypher = f"""
                MERGE (n:{label} {{id: $id}})
                SET n += $props
                """
                neo4j_client.execute_write(cypher, {"id": node_id, "props": clean_props})
            except Exception as e:
                logger.warning(f"Neo4j add_node error for {node_id}: {e}")

    def add_relationship(
        self,
        relationship_id: str,
        source_id: str,
        target_id: str,
        rel_type: str,
        provenance: Dict[str, Any]
    ):
        if rel_type not in VALID_RELATIONSHIP_TYPES:
            rel_type = "ASSOCIATED_WITH"

        edge_data = {
            "relationship_id": relationship_id,
            "source_id": source_id,
            "target_id": target_id,
            "type": rel_type,
            **provenance
        }

        # Check local mirror duplicate
        if not any(e["relationship_id"] == relationship_id for e in self.edges):
            self.edges.append(edge_data)
            if source_id not in self.adjacency:
                self.adjacency[source_id] = []
            self.adjacency[source_id].append(edge_data)

        # Upsert in Neo4j if connected
        if neo4j_client.is_connected:
            try:
                cypher = f"""
                MATCH (a {{id: $source_id}})
                MATCH (b {{id: $target_id}})
                MERGE (a)-[r:{rel_type} {{relationship_id: $rel_id}}]->(b)
                SET r += $props
                """
                neo4j_client.execute_write(cypher, {
                    "source_id": source_id,
                    "target_id": target_id,
                    "rel_id": relationship_id,
                    "props": provenance
                })
            except Exception as e:
                logger.warning(f"Neo4j add_relationship error: {e}")

    def get_subgraph(self, entity_ids: List[str], max_depth: int = 2) -> Dict[str, Any]:
        """
        Traverses graph from starting entity IDs up to max_depth hops.
        Returns nodes, edges, and provenance paths.
        """
        visited_nodes: Set[str] = set()
        subgraph_nodes: List[Dict[str, Any]] = []
        subgraph_edges: List[Dict[str, Any]] = []

        queue = [(eid, 0) for eid in entity_ids if eid in self.nodes]
        for eid, _ in queue:
            visited_nodes.add(eid)
            subgraph_nodes.append(self.nodes[eid])

        edge_ids_seen = set()

        while queue:
            curr_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            for edge in self.adjacency.get(curr_id, []):
                tgt_id = edge["target_id"]
                if edge["relationship_id"] not in edge_ids_seen:
                    edge_ids_seen.add(edge["relationship_id"])
                    subgraph_edges.append(edge)

                if tgt_id in self.nodes and tgt_id not in visited_nodes:
                    visited_nodes.add(tgt_id)
                    subgraph_nodes.append(self.nodes[tgt_id])
                    queue.append((tgt_id, depth + 1))

        return {
            "nodes": subgraph_nodes,
            "edges": subgraph_edges,
            "total_nodes": len(subgraph_nodes),
            "total_edges": len(subgraph_edges)
        }

    def get_all_graph(self) -> Dict[str, Any]:
        """Returns the full knowledge graph for the Graph Explorer visualizer."""
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges)
        }

graph_builder = KnowledgeGraphBuilder()

