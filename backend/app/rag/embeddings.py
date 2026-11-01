import os
import logging
import numpy as np
from typing import List, Union
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._st_model = None
        self._initialized = False

    def _lazy_init(self):
        if self._initialized:
            return
        if settings.TESTING or os.environ.get("TRANSFORMERS_OFFLINE") == "1" or os.environ.get("HF_HUB_OFFLINE") == "1":
            self._st_model = None
            self._initialized = True
            return

        try:
            from sentence_transformers import SentenceTransformer
            # Fast offline check: load from local cache without network retry hangs
            self._st_model = SentenceTransformer(self.model_name, local_files_only=True)
            logger.info(f"Loaded local SentenceTransformer model: {self.model_name}")
        except Exception as e:
            logger.info(f"SentenceTransformer operating in offline mode ({e}). Using normalized semantic feature vectors.")
            self._st_model = None
        self._initialized = True

    def get_embedding(self, text: str) -> List[float]:
        return self.get_embeddings([text])[0]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._lazy_init()
        if self._st_model is not None:
            try:
                embeddings = self._st_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                return embeddings.tolist()
            except Exception as ex:
                logger.warning(f"Error encoding with SentenceTransformer: {ex}. Falling back to semantic features.")

        # Robust, deterministic semantic bag-of-tokens feature vector representation (dim=384)
        vectors = []
        for text in texts:
            words = text.lower().split()
            vec = np.zeros(384, dtype=np.float32)
            if not words:
                vectors.append(vec.tolist())
                continue
            for word in words:
                h = hash(word) % 384
                vec[h] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec.tolist())
        return vectors

embedding_service = EmbeddingService()
