from typing import Dict, Any, List
from app.ingestion.document_loader import DocumentLoader
from app.ingestion.metadata_extractor import MetadataExtractor
from app.ingestion.chunker import TextChunker

class DocumentProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.metadata_extractor = MetadataExtractor()

    def process_raw_text(
        self,
        document_id: str,
        title: str,
        content: str,
        document_type: str = "GENERAL",
        source_type: str = "SYNTHETIC",
        institution_id: str = "VESIT",
        publication_date: str = None
    ) -> Dict[str, Any]:
        """Processes raw string document into validated metadata and chunks."""
        metadata = self.metadata_extractor.extract_metadata(
            document_id=document_id,
            title=title,
            content=content,
            document_type=document_type,
            source_type=source_type,
            institution_id=institution_id,
            publication_date=publication_date
        )

        chunks = self.chunker.chunk_document(
            document_id=document_id,
            text=content,
            title=metadata["title"],
            source_type=source_type
        )

        return {
            "metadata": metadata,
            "chunks": chunks,
            "chunk_count": len(chunks)
        }

    def process_file(
        self,
        file_path: str,
        document_id: str,
        document_type: str = "GENERAL",
        source_type: str = "SYNTHETIC",
        institution_id: str = "VESIT"
    ) -> Dict[str, Any]:
        """Loads and processes document from filesystem."""
        loaded = DocumentLoader.load_file(file_path)
        return self.process_raw_text(
            document_id=document_id,
            title=loaded["title"],
            content=loaded["content"],
            document_type=document_type,
            source_type=source_type,
            institution_id=institution_id
        )

