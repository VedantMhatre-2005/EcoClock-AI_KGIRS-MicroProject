import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.relational_db import init_db, SessionLocal
from app.database.neo4j_client import neo4j_client
from app.services.llm_service import llm_service
from app.graph.graph_builder import graph_builder
from app.database.schema import (
    DocumentModel, ExtractedEntityModel, ExtractedRelationshipModel,
    SustainabilityInitiativeModel, SustainabilityTargetModel, SDGModel
)

# Route Imports
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.climate import router as climate_router
from app.api.routes.emissions import router as emissions_router
from app.api.routes.energy import router as energy_router
from app.api.routes.water import router as water_router
from app.api.routes.waste import router as waste_router
from app.api.routes.transport import router as transport_router
from app.api.routes.documents import router as documents_router
from app.api.routes.graphrag import router as graphrag_router
from app.api.routes.knowledge_graph import router as kg_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.sdg import router as sdg_router
from app.api.routes.evaluation import router as evaluation_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ecoclock-ai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME}...")
    init_db()

    # Attempt Neo4j connection
    neo4j_connected = neo4j_client.connect()
    if neo4j_connected:
        logger.info("Connected to Neo4j. Initializing schema constraints.")
        neo4j_client.init_schema()
    else:
        logger.info("Neo4j offline. Operating in resilient standalone graph mirror mode.")

    # Rebuild in-memory graph index from SQLite persistence
    db = SessionLocal()
    try:
        # Load SDGs
        for s in db.query(SDGModel).all():
            graph_builder.add_node(s.id, "SDG", {"name": s.name, "sdg_number": s.sdg_number, "color": s.color})

        # Load Targets
        for t in db.query(SustainabilityTargetModel).all():
            graph_builder.add_node(t.id, "SustainabilityTarget", {"name": t.title, "target_year": t.target_year})

        # Load Initiatives
        for init in db.query(SustainabilityInitiativeModel).all():
            graph_builder.add_node(init.id, "SustainabilityInitiative", {"name": init.name, "status": init.status})

        # Load Documents
        for doc in db.query(DocumentModel).all():
            graph_builder.add_node(doc.id, "Document", {"name": doc.title, "title": doc.title, "type": doc.document_type})

        # Load Extracted Entities & Relationships
        for ent in db.query(ExtractedEntityModel).all():
            graph_builder.add_node(ent.canonical_name, ent.entity_type, {"name": ent.name})

        for rel in db.query(ExtractedRelationshipModel).all():
            graph_builder.add_relationship(
                relationship_id=rel.id,
                source_id=rel.source_entity,
                target_id=rel.target_entity,
                rel_type=rel.relationship_type,
                provenance={
                    "source_document_id": rel.document_id,
                    "chunk_id": rel.chunk_id,
                    "evidence_excerpt": rel.evidence_excerpt,
                    "extraction_method": rel.extraction_method,
                    "confidence": rel.confidence,
                    "verification_status": rel.verification_status
                }
            )
        logger.info(f"Graph initialized: {len(graph_builder.nodes)} nodes, {len(graph_builder.edges)} edges.")
    finally:
        db.close()

    yield

    # Shutdown
    logger.info("Shutting down EcoClock AI...")
    neo4j_client.close()

app = FastAPI(
    title=settings.APP_NAME,
    description="An Evidence-Grounded GraphRAG Platform for Intelligent Campus Sustainability and Climate Action",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System Status & Health Endpoints
@app.get(f"{settings.API_PREFIX}/health", tags=["System"])
def health_check():
    """Service health endpoint."""
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV
    }

@app.get(f"{settings.API_PREFIX}/system/status", tags=["System"])
def system_status():
    """Returns connectivity status of Ollama, Neo4j, SQLite, and knowledge graph."""
    ollama_conn = llm_service.check_connection()
    neo4j_alive = neo4j_client.is_connected

    return {
        "app_name": settings.APP_NAME,
        "institution": settings.INSTITUTION_NAME,
        "environment": settings.APP_ENV,
        "neo4j": {
            "connected": neo4j_alive,
            "uri": settings.NEO4J_URI
        },
        "ollama": {
            "connected": ollama_conn["connected"],
            "url": settings.OLLAMA_BASE_URL,
            "configured_model": settings.OLLAMA_MODEL,
            "version": ollama_conn.get("version")
        },
        "knowledge_graph": {
            "total_nodes": len(graph_builder.nodes),
            "total_edges": len(graph_builder.edges)
        },
        "embedding_model": settings.EMBEDDING_MODEL
    }

# Register Routers
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(climate_router, prefix=settings.API_PREFIX)
app.include_router(emissions_router, prefix=settings.API_PREFIX)
app.include_router(energy_router, prefix=settings.API_PREFIX)
app.include_router(water_router, prefix=settings.API_PREFIX)
app.include_router(waste_router, prefix=settings.API_PREFIX)
app.include_router(transport_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(graphrag_router, prefix=settings.API_PREFIX)
app.include_router(kg_router, prefix=settings.API_PREFIX)
app.include_router(simulation_router, prefix=settings.API_PREFIX)
app.include_router(sdg_router, prefix=settings.API_PREFIX)
app.include_router(evaluation_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

