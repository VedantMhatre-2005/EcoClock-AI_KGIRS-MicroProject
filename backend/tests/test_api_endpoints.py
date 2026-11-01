import pytest
from app.database.relational_db import SessionLocal, init_db
from app.main import health_check, system_status
from app.api.routes.dashboard import get_dashboard_summary
from app.api.routes.climate import get_climate_clock
from app.api.routes.energy import get_energy_summary
from app.api.routes.water import get_water_summary
from app.api.routes.waste import get_waste_summary
from app.api.routes.transport import get_transport_summary
from app.api.routes.sdg import list_sdgs
from app.api.routes.knowledge_graph import get_graph_schema
from app.api.routes.graphrag import execute_graphrag_query, QueryRequest

@pytest.fixture(scope="module")
def db():
    init_db()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_health_endpoint():
    res = health_check()
    assert res["status"] == "HEALTHY"
    assert "EcoClock AI" in res["app"]

def test_system_status_endpoint():
    res = system_status()
    assert "neo4j" in res
    assert "ollama" in res
    assert "knowledge_graph" in res

def test_dashboard_summary_endpoint(db):
    res = get_dashboard_summary(db=db)
    assert "kpis" in res
    assert "total_carbon_emissions_tonnes" in res["kpis"]

def test_climate_clock_endpoint(db):
    res = get_climate_clock(db=db)
    assert "institution_clock" in res
    assert "countdown" in res["institution_clock"]
    assert res["global_context_clock"]["status"] == "UNAVAILABLE"

def test_energy_summary_endpoint(db):
    res = get_energy_summary(db=db)
    assert "total_electricity_kwh" in res
    assert "monthly_trends" in res

def test_water_summary_endpoint(db):
    res = get_water_summary(db=db)
    assert "total_consumption_litres" in res

def test_waste_summary_endpoint(db):
    res = get_waste_summary(db=db)
    assert "recycling_rate" in res

def test_transport_summary_endpoint(db):
    res = get_transport_summary(db=db)
    assert "total_passenger_km" in res

def test_sdg_list_endpoint(db):
    res = list_sdgs(db=db)
    assert len(res) == 17

def test_graph_schema_endpoint():
    res = get_graph_schema()
    assert "node_labels" in res
    assert "relationship_types" in res

def test_graphrag_grounded_answer(db):
    payload = QueryRequest(
        query="What is the net zero target year for VESIT Green Campus?",
        mode="HYBRID_GRAPHRAG"
    )
    res = execute_graphrag_query(payload=payload, db=db)
    assert "answer" in res
    assert "citations" in res
    assert res["is_grounded"] is True

def test_graphrag_unsupported_query(db):
    payload = QueryRequest(
        query="What are the commercial airline passenger miles chartered by VESIT in 2024?",
        mode="HYBRID_GRAPHRAG"
    )
    res = execute_graphrag_query(payload=payload, db=db)
    assert "not available" in res["answer"].lower() or "no relevant" in res["supporting_evidence"].lower()
