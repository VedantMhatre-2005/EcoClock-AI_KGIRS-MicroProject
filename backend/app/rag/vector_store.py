import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.database.schema import ChunkModel, DocumentModel
from app.rag.embeddings import embedding_service

class VectorStore:
    def __init__(self):
        self._cached_chunks: List[Dict[str, Any]] = []
        self._cached_embeddings: Optional[np.ndarray] = None
        self._is_indexed = False

    def build_index(self, db: Session):
        """Indexes all persisted chunks with embeddings."""
        chunks = db.query(ChunkModel, DocumentModel.title).join(
            DocumentModel, ChunkModel.document_id == DocumentModel.id
        ).all()

        if not chunks:
            self._cached_chunks = []
            self._cached_embeddings = np.empty((0, 384))
            self._is_indexed = True
            return

        chunk_list = []
        texts = []
        for chunk, doc_title in chunks:
            chunk_list.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_title": doc_title,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "section": chunk.section,
                "page_number": chunk.page_number
            })
            texts.append(f"{doc_title} - {chunk.section}: {chunk.content}")

        vectors = embedding_service.get_embeddings(texts)
        self._cached_chunks = chunk_list
        self._cached_embeddings = np.array(vectors, dtype=np.float32)
        self._is_indexed = True

    def similarity_search(self, db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Computes cosine similarity between query and all indexed chunks."""
        if not self._is_indexed or len(self._cached_chunks) == 0:
            self.build_index(db)

        if len(self._cached_chunks) == 0 or self._cached_embeddings is None or len(self._cached_embeddings) == 0:
            return []

        q_vec = np.array(embedding_service.get_embedding(query), dtype=np.float32)
        norms = np.linalg.norm(self._cached_embeddings, axis=1) * np.linalg.norm(q_vec)
        norms[norms == 0] = 1e-10
        scores = np.dot(self._cached_embeddings, q_vec) / norms

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            chunk_data = dict(self._cached_chunks[idx])
            chunk_data["similarity_score"] = round(score, 4)
            results.append(chunk_data)

        return results

vector_store = VectorStore()

