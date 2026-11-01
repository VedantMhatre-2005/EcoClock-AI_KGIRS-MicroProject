import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.schema import DocumentModel, ChunkModel, ExtractedEntityModel, ExtractedRelationshipModel
from app.ingestion.document_processor import DocumentProcessor
from app.graph.entity_extractor import EntityExtractor
from app.graph.relationship_extractor import RelationshipExtractor
from app.graph.graph_builder import graph_builder

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()

    def ingest_document(
        self,
        db: Session,
        document_id: str,
        title: str,
        content: str,
        document_type: str = "GENERAL",
        source_type: str = "SYNTHETIC",
        institution_id: str = "VESIT",
        file_path: Optional[str] = None,
        force_reprocess: bool = False
    ) -> Dict[str, Any]:
        """
        Executes complete ingestion pipeline for a document:
        Validation -> Chunking -> Metadata -> Entity & Rel Extraction -> Graph Builder -> Persistence.
        """
        # 1. Process text and metadata
        processed = self.processor.process_raw_text(
            document_id=document_id,
            title=title,
            content=content,
            document_type=document_type,
            source_type=source_type,
            institution_id=institution_id
        )

        metadata = processed["metadata"]
        chunks = processed["chunks"]

        # 2. Check for duplicate document by file_hash
        existing_doc = db.query(DocumentModel).filter(
            (DocumentModel.id == document_id) | (DocumentModel.file_hash == metadata["file_hash"])
        ).first()

        if existing_doc and existing_doc.status == "COMPLETED" and not force_reprocess:
            logger.info(f"Document {document_id} already ingested. Skipping duplicate.")
            return {
                "document_id": existing_doc.id,
                "title": existing_doc.title,
                "status": "COMPLETED",
                "is_duplicate": True,
                "entity_count": existing_doc.entity_count,
                "relationship_count": existing_doc.relationship_count,
                "chunk_count": existing_doc.chunk_count
            }

        # 3. Create or update Document record in DB
        doc_record = existing_doc or DocumentModel(
            id=document_id,
            title=metadata["title"],
            document_type=document_type,
            publication_date=metadata["publication_date"],
            source_type=source_type,
            institution_id=institution_id,
            file_path=file_path,
            file_hash=metadata["file_hash"],
            file_size=metadata["file_size"],
            status="PROCESSING",
            content=content
        )
        if not existing_doc:
            db.add(doc_record)
        else:
            doc_record.status = "PROCESSING"
        db.commit()

        # Add Document node to knowledge graph
        graph_builder.add_node(
            node_id=document_id,
            label="Document",
            properties={
                "title": metadata["title"],
                "type": document_type,
                "source_type": source_type,
                "publication_date": metadata["publication_date"]
            }
        )

        total_entities_count = 0
        total_relationships_count = 0

        # 4. Process each chunk
        for chunk_data in chunks:
            chunk_id = chunk_data["chunk_id"]

            # Save Chunk to relational DB
            chunk_record = ChunkModel(
                id=chunk_id,
                document_id=document_id,
                chunk_index=chunk_data["chunk_index"],
                content=chunk_data["content"],
                char_length=chunk_data["char_length"],
                page_number=chunk_data["page_number"],
                section=chunk_data["section"]
            )
            db.merge(chunk_record)

            # Add Chunk node to knowledge graph & connect to Document
            graph_builder.add_node(
                node_id=chunk_id,
                label="Chunk",
                properties={
                    "index": chunk_data["chunk_index"],
                    "section": chunk_data["section"],
                    "document_id": document_id
                }
            )
            graph_builder.add_relationship(
                relationship_id=f"REL_{document_id}_HAS_CHUNK_{chunk_id}",
                source_id=document_id,
                target_id=chunk_id,
                rel_type="HAS_CHUNK",
                provenance={
                    "source_document_id": document_id,
                    "chunk_id": chunk_id,
                    "evidence_excerpt": chunk_data["content"][:150],
                    "extraction_method": "STRUCTURAL",
                    "confidence": 1.0,
                    "verification_status": "EXPLICIT"
                }
            )

            # 5. Extract Entities
            chunk_entities = self.entity_extractor.extract_from_text(
                text=chunk_data["content"],
                document_id=document_id,
                chunk_id=chunk_id,
                document_title=metadata["title"]
            )

            for ent in chunk_entities:
                ent_db = ExtractedEntityModel(
                    id=ent["id"],
                    document_id=document_id,
                    chunk_id=chunk_id,
                    name=ent["name"],
                    entity_type=ent["entity_type"],
                    canonical_name=ent["name"],
                    properties_json=json.dumps(ent.get("properties", {})),
                    confidence=ent["confidence"],
                    verification_status=ent["verification_status"]
                )
                db.merge(ent_db)

                graph_builder.add_node(
                    node_id=ent["canonical_id"],
                    label=ent["entity_type"],
                    properties={
                        "name": ent["name"],
                        "canonical_id": ent["canonical_id"],
                        **ent.get("properties", {})
                    }
                )
                total_entities_count += 1

            # 6. Extract Relationships
            chunk_relationships = self.relationship_extractor.extract_from_chunk(
                chunk_text=chunk_data["content"],
                document_id=document_id,
                chunk_id=chunk_id,
                extracted_entities=chunk_entities,
                document_title=metadata["title"]
            )

            for rel in chunk_relationships:
                rel_db = ExtractedRelationshipModel(
                    id=rel["relationship_id"],
                    document_id=document_id,
                    chunk_id=chunk_id,
                    source_entity=rel["source_id"],
                    target_entity=rel["target_id"],
                    relationship_type=rel["relationship_type"],
                    evidence_excerpt=rel["evidence_excerpt"],
                    extraction_method=rel["extraction_method"],
                    confidence=rel["confidence"],
                    verification_status=rel["verification_status"]
                )
                db.merge(rel_db)

                graph_builder.add_relationship(
                    relationship_id=rel["relationship_id"],
                    source_id=rel["source_id"],
                    target_id=rel["target_id"],
                    rel_type=rel["relationship_type"],
                    provenance={
                        "source_document_id": document_id,
                        "chunk_id": chunk_id,
                        "evidence_excerpt": rel["evidence_excerpt"],
                        "extraction_method": rel["extraction_method"],
                        "confidence": rel["confidence"],
                        "verification_status": rel["verification_status"]
                    }
                )
                total_relationships_count += 1

        # 7. Finalize Document record
        doc_record.status = "COMPLETED"
        doc_record.entity_count = total_entities_count
        doc_record.relationship_count = total_relationships_count
        doc_record.chunk_count = len(chunks)
        db.commit()

        logger.info(f"Ingested {document_id}: {len(chunks)} chunks, {total_entities_count} entities, {total_relationships_count} relationships.")

        return {
            "document_id": document_id,
            "title": metadata["title"],
            "status": "COMPLETED",
            "chunk_count": len(chunks),
            "entity_count": total_entities_count,
            "relationship_count": total_relationships_count
        }

ingestion_pipeline = IngestionPipeline()
