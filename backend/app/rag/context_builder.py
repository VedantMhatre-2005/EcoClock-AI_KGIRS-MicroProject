from typing import Dict, Any, List

class ContextBuilder:
    @staticmethod
    def build_grounded_context(retrieval_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structures retrieved textual chunks and graph triples into prompt context and traceable citations.
        """
        chunks: List[Dict[str, Any]] = retrieval_result.get("chunks", [])
        graph_data: Dict[str, Any] = retrieval_result.get("graph", {})
        edges: List[Dict[str, Any]] = graph_data.get("edges", [])
        nodes: List[Dict[str, Any]] = graph_data.get("nodes", [])

        context_lines: List[str] = []
        citations: List[Dict[str, Any]] = []

        # 1. Format Document Chunks with Source Attribution
        if chunks:
            context_lines.append("=== RETRIEVED DOCUMENT EVIDENCE ===")
            for i, chunk in enumerate(chunks, 1):
                doc_title = chunk.get("document_title", "Document")
                doc_id = chunk.get("document_id", "Unknown")
                chunk_id = chunk.get("chunk_id", f"chk_{i}")
                section = chunk.get("section", "General")
                content = chunk.get("content", "").strip()

                context_lines.append(f"[{i}] Document: {doc_title} (ID: {doc_id}, Chunk: {chunk_id}, Section: {section})")
                context_lines.append(f"Content: {content}\n")

                citations.append({
                    "citation_id": f"[{i}]",
                    "document_id": doc_id,
                    "document_title": doc_title,
                    "chunk_id": chunk_id,
                    "section": section,
                    "excerpt": content[:180] + "..." if len(content) > 180 else content
                })

        # 2. Format Graph Relational Triples
        if edges:
            context_lines.append("=== KNOWLEDGE GRAPH RELATIONSHIPS ===")
            node_name_map = {n["id"]: n.get("name", n["id"]) for n in nodes}
            for j, edge in enumerate(edges[:15], 1):
                src_name = node_name_map.get(edge["source_id"], edge["source_id"])
                tgt_name = node_name_map.get(edge["target_id"], edge["target_id"])
                rel_type = edge.get("type", "ASSOCIATED_WITH")
                method = edge.get("extraction_method", "VERIFIED")
                confidence = edge.get("confidence", 1.0)
                excerpt = edge.get("evidence_excerpt", "")

                context_lines.append(
                    f"- ({src_name}) -[:{rel_type}]-> ({tgt_name}) [Method: {method}, Conf: {confidence}]"
                )
                if excerpt:
                    context_lines.append(f"  Provenance: \"{excerpt[:120]}\"")

        formatted_context = "\n".join(context_lines)
        return {
            "formatted_context": formatted_context,
            "citations": citations,
            "graph_paths": [
                {
                    "source": edge["source_id"],
                    "relationship": edge.get("type", "ASSOCIATED_WITH"),
                    "target": edge["target_id"],
                    "evidence": edge.get("evidence_excerpt", "")
                } for edge in edges[:10]
            ],
            "has_evidence": bool(chunks or edges)
        }

