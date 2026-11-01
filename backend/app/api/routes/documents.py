import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.database.schema import DocumentModel, ChunkModel, ExtractedEntityModel, ExtractedRelationshipModel
from app.ingestion.ingestion_pipeline import ingestion_pipeline
from app.ingestion.document_loader import DocumentLoader
from app.config import BASE_DIR

router = APIRouter(prefix="/documents", tags=["Documents"])
UPLOAD_DIR = BASE_DIR / "data" / "raw"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("")
def list_documents(db: Session = Depends(get_db)):
    """Lists all uploaded and indexed documents with status and entity/relationship counts."""
    docs = db.query(DocumentModel).order_by(DocumentModel.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "document_type": d.document_type,
            "publication_date": d.publication_date,
            "source_type": d.source_type,
            "institution_id": d.institution_id,
            "file_size": d.file_size,
            "status": d.status,
            "chunk_count": d.chunk_count,
            "entity_count": d.entity_count,
            "relationship_count": d.relationship_count,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in docs
    ]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("GENERAL"),
    source_type: str = Form("SYNTHETIC"),
    db: Session = Depends(get_db)
):
    """Uploads document file, validates extension, saves to raw storage, and ingests into GraphRAG."""
    allowed_exts = {".pdf", ".docx", ".txt", ".csv", ".json"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: PDF, DOCX, TXT, CSV, JSON."
        )

    saved_path = UPLOAD_DIR / file.filename
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        loaded = DocumentLoader.load_file(str(saved_path))
        doc_id = f"DOC_UPL_{Path(file.filename).stem.upper()[:16]}"

        ingest_res = ingestion_pipeline.ingest_document(
            db=db,
            document_id=doc_id,
            title=loaded["title"],
            content=loaded["content"],
            document_type=document_type,
            source_type=source_type,
            institution_id="VESIT",
            file_path=str(saved_path)
        )
        return ingest_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {e}")

@router.get("/{document_id}")
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    """Returns document metadata, extracted chunks, entities, and relationships."""
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    chunks = db.query(ChunkModel).filter(ChunkModel.document_id == document_id).all()
    entities = db.query(ExtractedEntityModel).filter(ExtractedEntityModel.document_id == document_id).all()
    relationships = db.query(ExtractedRelationshipModel).filter(ExtractedRelationshipModel.document_id == document_id).all()

    return {
        "metadata": {
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "publication_date": doc.publication_date,
            "source_type": doc.source_type,
            "status": doc.status,
            "chunk_count": doc.chunk_count,
            "entity_count": doc.entity_count,
            "relationship_count": doc.relationship_count,
            "file_size": doc.file_size
        },
        "content_excerpt": doc.content[:1000] + ("..." if len(doc.content) > 1000 else ""),
        "chunks": [
            {"id": c.id, "index": c.chunk_index, "section": c.section, "content": c.content, "char_length": c.char_length}
            for c in chunks
        ],
        "entities": [
            {"id": e.id, "name": e.name, "type": e.entity_type, "confidence": e.confidence, "status": e.verification_status}
            for e in entities[:50]
        ],
        "relationships": [
            {
                "id": r.id,
                "source": r.source_entity,
                "relationship": r.relationship_type,
                "target": r.target_entity,
                "evidence": r.evidence_excerpt,
                "confidence": r.confidence,
                "status": r.verification_status
            }
            for r in relationships[:50]
        ]
    }

@router.post("/{document_id}/ingest")
def reingest_document(document_id: str, db: Session = Depends(get_db)):
    """Forces re-ingestion of a document."""
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    return ingestion_pipeline.ingest_document(
        db=db,
        document_id=doc.id,
        title=doc.title,
        content=doc.content,
        document_type=doc.document_type,
        source_type=doc.source_type,
        institution_id=doc.institution_id,
        force_reprocess=True
    )

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Deletes document and cascades removal of associated chunks and extracted elements."""
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    db.query(ExtractedEntityModel).filter(ExtractedEntityModel.document_id == document_id).delete()
    db.query(ExtractedRelationshipModel).filter(ExtractedRelationshipModel.document_id == document_id).delete()
    db.delete(doc)
    db.commit()

    return {"deleted": True, "document_id": document_id}

