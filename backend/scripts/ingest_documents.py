import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database.relational_db import SessionLocal, init_db
from app.ingestion.ingestion_pipeline import ingestion_pipeline

DOCS_FILE = BASE_DIR / "data" / "synthetic" / "documents.json"

def main():
    print("Ingesting synthetic documents into EcoClock AI GraphRAG pipeline (force_reprocess=True)...")
    init_db()
    db = SessionLocal()

    if not DOCS_FILE.exists():
        print(f"Error: {DOCS_FILE} not found. Run generate_synthetic_data first.")
        return

    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        docs = json.load(f)

    total_chunks = 0
    total_entities = 0
    total_relationships = 0

    try:
        for doc in docs:
            res = ingestion_pipeline.ingest_document(
                db=db,
                document_id=doc["document_id"],
                title=doc["title"],
                content=doc["content"],
                document_type=doc["document_type"],
                source_type=doc.get("source_type", "SYNTHETIC"),
                institution_id=doc.get("institution_id", "VESIT"),
                force_reprocess=True
            )
            total_chunks += res.get("chunk_count", 0)
            total_entities += res.get("entity_count", 0)
            total_relationships += res.get("relationship_count", 0)
            print(f"[{res['status']}] {res['document_id']} | Chunks: {res['chunk_count']} | Entities: {res['entity_count']} | Relationships: {res['relationship_count']}")

        print(f"\nSuccessfully Ingested All {len(docs)} Documents!")
        print(f"Totals -> Chunks: {total_chunks} | Extracted Entities: {total_entities} | Relationships: {total_relationships}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
