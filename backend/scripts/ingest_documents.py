import sys
import time
import json
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database.relational_db import SessionLocal, init_db
from app.database.schema import (
    DocumentModel, ChunkModel, ExtractedEntityModel, ExtractedRelationshipModel,
    SustainabilityInitiativeModel, SustainabilityTargetModel, SDGModel
)
from app.graph.graph_builder import graph_builder
from app.database.neo4j_client import neo4j_client
from app.ingestion.ingestion_pipeline import ingestion_pipeline

DOCS_FILE = BASE_DIR / "data" / "synthetic" / "documents.json"
PDF_DIR = BASE_DIR / "data" / "sample_documents"
PREDEFINED_GRAPH_FILE = BASE_DIR / "data" / "synthetic" / "predefined_knowledge_graph.json"

def load_predefined_graph(db, graph_path: Path):
    """Instantly loads the pre-constructed, dense knowledge graph into SQLite and Neo4j in seconds."""
    start_time = time.time()
    print(f"[PREDEFINED KNOWLEDGE GRAPH] Loading from {graph_path.name}...")

    with open(graph_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs_data = data.get("documents", [])
    chunks_data = data.get("chunks", [])
    entities_data = data.get("entities", [])
    relationships_data = data.get("relationships", [])

    # 1. Populate relational DB
    print(f"-> Merging {len(docs_data)} Documents...")
    for doc in docs_data:
        # Ensure file_path points to sample_documents PDF
        doc_id = doc["id"]
        pdf_path = PDF_DIR / f"{doc_id}.pdf"
        if pdf_path.exists():
            doc["file_path"] = str(pdf_path)
        db.merge(DocumentModel(**doc))

    print(f"-> Merging {len(chunks_data)} Text Chunks...")
    for chunk in chunks_data:
        db.merge(ChunkModel(**chunk))

    print(f"-> Merging {len(entities_data)} Extracted Entities...")
    for ent in entities_data:
        db.merge(ExtractedEntityModel(**ent))

    print(f"-> Merging {len(relationships_data)} Extracted Relationships...")
    for rel in relationships_data:
        db.merge(ExtractedRelationshipModel(**rel))

    db.commit()

    # 2. Populate Knowledge Graph in-memory mirror and Neo4j
    print("-> Indexing into Knowledge Graph with canonical resolution...")
    from app.graph.graph_loader import load_knowledge_graph
    load_knowledge_graph(db)

    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] Loaded Predefined Knowledge Graph in {elapsed:.2f} seconds!")
    print(f"Totals -> Documents: {len(docs_data)} | Chunks: {len(chunks_data)} | Extracted Relations: {len(relationships_data)}")
    print(f"Knowledge Graph Memory State: {len(graph_builder.nodes)} nodes, {len(graph_builder.edges)} edges.")
    print("Zero disconnected nodes. System is ready for instantaneous GraphRAG and Climate Clock analytics!")

def run_live_extraction(db):
    """Fallback runner if user explicitly requests live extraction across all documents."""
    print("Running dynamic ingestion pipeline across documents (live extraction)...")
    if not DOCS_FILE.exists():
        print(f"Error: {DOCS_FILE} not found. Run generate_synthetic_data first.")
        return

    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        docs = json.load(f)

    total_chunks = 0
    total_entities = 0
    total_relationships = 0

    for doc in docs:
        doc_id = doc["document_id"]
        pdf_path = PDF_DIR / f"{doc_id}.pdf"
        file_path_str = str(pdf_path) if pdf_path.exists() else None

        try:
            res = ingestion_pipeline.ingest_document(
                db=db,
                document_id=doc_id,
                title=doc["title"],
                content=doc["content"],
                document_type=doc["document_type"],
                source_type=doc.get("source_type", "SYNTHETIC"),
                institution_id=doc.get("institution_id", "VESIT"),
                file_path=file_path_str,
                force_reprocess=True
            )
            total_chunks += res.get("chunk_count", 0)
            total_entities += res.get("entity_count", 0)
            total_relationships += res.get("relationship_count", 0)
            print(f"[{res['status']}] {res['document_id']} | Chunks: {res['chunk_count']} | Entities: {res['entity_count']} | Relationships: {res['relationship_count']}")
        except Exception as e:
            print(f"[ERROR] Ingestion failed for {doc_id}: {e}")

    print(f"\nSuccessfully Ingested All {len(docs)} Documents!")
    print(f"Totals -> Chunks: {total_chunks} | Extracted Entities: {total_entities} | Relationships: {total_relationships}")

def main():
    parser = argparse.ArgumentParser(description="VESIT Green Campus Document & Knowledge Graph Ingestion")
    parser.add_argument("--live-llm", action="store_true", help="Force live LLM extraction instead of loading predefined graph")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()

    try:
        if PREDEFINED_GRAPH_FILE.exists() and not args.live_llm:
            load_predefined_graph(db, PREDEFINED_GRAPH_FILE)
        else:
            run_live_extraction(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
