from typing import Dict, Any

STANDARD_CYPHER_QUERIES = {
    "BUILDINGS_HIGHEST_EMISSIONS": """
        MATCH (b:Building)-[r:GENERATES_EMISSION]->(e:Emission)
        RETURN b.id as building_id, b.name as building_name, e.annual_kgco2e as annual_emissions_kgco2e
        ORDER BY e.annual_kgco2e DESC
        LIMIT 10
    """,
    "INITIATIVES_SDG_13": """
        MATCH (i:SustainabilityInitiative)-[r:SUPPORTS_SDG]->(s:SDG)
        WHERE s.id = 'SDG_13' OR s.sdg_number = 13
        RETURN i.id as initiative_id, i.name as initiative_name, i.status as status, r.evidence_excerpt as evidence
    """,
    "INITIATIVES_MULTIPLE_SDGS": """
        MATCH (i:SustainabilityInitiative)-[:SUPPORTS_SDG]->(s:SDG)
        WITH i, collect(s.name) as sdgs, count(s) as sdg_count
        WHERE sdg_count > 1
        RETURN i.id as initiative_id, i.name as initiative_name, sdgs, sdg_count
        ORDER BY sdg_count DESC
    """,
    "TARGET_SUPPORTING_DOCS": """
        MATCH (t:SustainabilityTarget)<-[:ADDRESSES_TARGET]-(i:SustainabilityInitiative)-[:SUPPORTED_BY]->(d:Document)
        RETURN t.id as target_id, t.title as target_title, i.name as initiative, d.title as document_title
    """,
    "CAMPUS_ENERGY_EMISSIONS_CHAIN": """
        MATCH (inst:Institution)-[:HAS_BUILDING]->(b:Building)-[:USES_ENERGY_SOURCE]->(es:EnergySource)-[:GENERATES_EMISSION]->(e:Emission)
        RETURN inst.name as institution, b.name as building, es.name as energy_source, e.annual_kgco2e as emissions_kgco2e
    """,
    "FULL_SCHEMA_GRAPH": """
        CALL db.schema.visualization()
    """
}

