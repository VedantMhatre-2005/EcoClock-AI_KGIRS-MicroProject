import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

class MetadataExtractor:
    @staticmethod
    def compute_sha256(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def extract_metadata(
        document_id: str,
        title: str,
        content: str,
        document_type: str = "GENERAL",
        source_type: str = "SYNTHETIC",
        institution_id: str = "VESIT",
        publication_date: Optional[str] = None
    ) -> Dict[str, Any]:
        file_hash = MetadataExtractor.compute_sha256(content)
        char_count = len(content)
        word_count = len(content.split())

        if not publication_date:
            publication_date = datetime.utcnow().strftime("%Y-%m-%d")

        return {
            "document_id": document_id,
            "title": title or "Untitled Document",
            "document_type": document_type,
            "publication_date": publication_date,
            "source_type": source_type,
            "institution_id": institution_id,
            "file_hash": file_hash,
            "file_size": char_count,
            "word_count": word_count
        }

