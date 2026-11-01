from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.graph.graph_schema import VALID_NODE_LABELS, VALID_RELATIONSHIP_TYPES
from app.graph.graph_builder import graph_builder

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])

@router.get("/schema")
def get_graph_schema():
    """Returns official ontology labels and relationship types."""
    return {
        "node_labels": sorted(list(VALID_NODE_LABELS)),
        "relationship_types": sorted(list(VALID_RELATIONSHIP_TYPES)),
        "description": "EcoClock AI Academic Decarbonization Property Graph Schema"
    }

@router.get("/explore")
def explore_graph(
    center_id: Optional[str] = Query(None, description="Starting entity ID"),
    depth: int = Query(2, ge=1, le=4)
):
    """
    Returns nodes and edges for the React Flow interactive graph explorer.
    If center_id is provided, returns localized neighborhood; otherwise returns full graph.
    """
    if center_id:
        return graph_builder.get_subgraph([center_id], max_depth=depth)
    return graph_builder.get_all_graph()

@router.get("/entity/{entity_id}")
def get_entity_details(entity_id: str):
    """Returns detailed properties and immediate relational edges for an entity."""
    if entity_id not in graph_builder.nodes:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found in knowledge graph.")

    node = graph_builder.nodes[entity_id]
    edges = [
        e for e in graph_builder.edges
        if e["source_id"] == entity_id or e["target_id"] == entity_id
    ]

    return {
        "entity": node,
        "connected_edges": edges,
        "degree": len(edges)
    }

