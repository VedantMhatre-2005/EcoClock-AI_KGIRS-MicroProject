from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.rag.vector_store import vector_store
from app.rag.graph_retriever import graph_retriever

class HybridRetriever:
    def __init__(
        self,
        vector_weight: float = 0.5,
        graph_weight: float = 0.5,
        top_k_chunks: int = 4,
        max_graph_depth: int = 2
    ):
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight
        self.top_k_chunks = top_k_chunks
        self.max_graph_depth = max_graph_depth

    def retrieve(self, db: Session, query: str, mode: str = "HYBRID_GRAPHRAG") -> Dict[str, Any]:
        """
        Executes evidence retrieval according to requested mode:
        VECTOR_RAG, GRAPH_RAG, or HYBRID_GRAPHRAG.
        """
        chunks: List[Dict[str, Any]] = []
        graph_data: Dict[str, Any] = {"nodes": [], "edges": [], "query_entities": []}

        if mode in ["VECTOR_RAG", "HYBRID_GRAPHRAG"]:
            chunks = vector_store.similarity_search(db, query, top_k=self.top_k_chunks)

        if mode in ["GRAPH_RAG", "HYBRID_GRAPHRAG"]:
            graph_data = graph_retriever.retrieve_subgraph(query, max_depth=self.max_graph_depth)

        # In HYBRID mode, score and prioritize chunks that are reinforced by graph edges
        if mode == "HYBRID_GRAPHRAG" and chunks and graph_data["edges"]:
            graph_chunk_ids = {e.get("chunk_id") for e in graph_data["edges"] if e.get("chunk_id")}
            for chunk in chunks:
                base_sim = chunk.get("similarity_score", 0.5)
                # Boost if chunk is direct graph provenance
                provenance_boost = 0.25 if chunk["chunk_id"] in graph_chunk_ids else 0.0
                # Weighted hybrid score
                hybrid_score = (self.vector_weight * base_sim) + (self.graph_weight * provenance_boost)
                chunk["hybrid_score"] = round(hybrid_score, 4)

            # Sort by hybrid score
            chunks.sort(key=lambda c: c.get("hybrid_score", 0.0), reverse=True)

        return {
            "mode": mode,
            "query": query,
            "chunks": chunks,
            "graph": graph_data,
            "retrieved_chunk_count": len(chunks),
            "retrieved_node_count": len(graph_data["nodes"]),
            "retrieved_edge_count": len(graph_data["edges"])
        }

hybrid_retriever = HybridRetriever()

