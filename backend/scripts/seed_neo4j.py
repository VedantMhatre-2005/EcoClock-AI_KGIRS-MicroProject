import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database.neo4j_client import neo4j_client
from scripts.generate_synthetic_data import INSTITUTION, BUILDINGS, DEPARTMENTS, TARGETS, INITIATIVES, SDGS, EMISSION_FACTORS

def seed():
    print("Attempting to connect to Neo4j...")
    if not neo4j_client.connect():
        print("Neo4j is currently unreachable. When running with Docker Compose, seed_neo4j will populate Neo4j automatically.")
        return

    print("Connected to Neo4j. Initializing schema constraints...")
    neo4j_client.init_schema()

    # 1. Seed Institution
    cypher_inst = """
    MERGE (i:Institution {id: $id})
    SET i.name = $name, i.location = $location, i.student_population = $student_population,
        i.faculty_staff_population = $faculty_staff_population, i.total_built_up_area_m2 = $total_built_up_area_m2
    """
    neo4j_client.execute_write(cypher_inst, INSTITUTION)

    # 2. Seed Buildings & HAS_BUILDING
    for b in BUILDINGS:
        cypher_bld = """
        MATCH (i:Institution {id: 'VESIT'})
        MERGE (b:Building {id: $id})
        SET b.name = $name, b.area_m2 = $area_m2, b.primary_use = $primary_use,
            b.occupancy = $occupancy, b.has_rooftop_solar = $has_rooftop_solar, b.solar_capacity_kw = $solar_capacity_kw
        MERGE (i)-[:HAS_BUILDING]->(b)
        """
        neo4j_client.execute_write(cypher_bld, b)

    # 3. Seed Departments & HAS_DEPARTMENT
    for d in DEPARTMENTS:
        cypher_dep = """
        MATCH (i:Institution {id: 'VESIT'})
        MERGE (dep:Department {id: $id})
        SET dep.name = $name, dep.head = $head
        MERGE (i)-[:HAS_DEPARTMENT]->(dep)
        """
        neo4j_client.execute_write(cypher_dep, d)

    # 4. Seed Targets & HAS_TARGET
    for t in TARGETS:
        cypher_trg = """
        MATCH (i:Institution {id: 'VESIT'})
        MERGE (trg:SustainabilityTarget {id: $id})
        SET trg.title = $title, trg.category = $category, trg.baseline_year = $baseline_year,
            trg.target_year = $target_year, trg.baseline_value = $baseline_value, trg.target_value = $target_value,
            trg.unit = $unit, trg.status = $status
        MERGE (i)-[:HAS_TARGET]->(trg)
        """
        neo4j_client.execute_write(cypher_trg, t)

    # 5. Seed SDGs
    for s in SDGS:
        cypher_sdg = """
        MERGE (sdg:SDG {id: $id})
        SET sdg.sdg_number = $sdg_number, sdg.name = $name, sdg.description = $description, sdg.color = $color
        """
        neo4j_client.execute_write(cypher_sdg, s)

    # 6. Seed Initiatives & SUPPORTS_SDG / ADDRESSES_TARGET
    for init in INITIATIVES:
        cypher_init = """
        MATCH (i:Institution {id: 'VESIT'})
        MERGE (init:SustainabilityInitiative {id: $id})
        SET init.name = $name, init.description = $description, init.lead_department = $lead_department,
            init.status = $status, init.carbon_reduction_estimate_kgco2e = $carbon_reduction_estimate_kgco2e
        MERGE (i)-[:IMPLEMENTS_INITIATIVE]->(init)
        """
        neo4j_client.execute_write(cypher_init, init)

        for sid in init["sdg_ids"]:
            neo4j_client.execute_write("""
            MATCH (init:SustainabilityInitiative {id: $init_id})
            MATCH (sdg:SDG {id: $sdg_id})
            MERGE (init)-[:SUPPORTS_SDG]->(sdg)
            """, {"init_id": init["id"], "sdg_id": sid})

        for tid in init["target_ids"]:
            neo4j_client.execute_write("""
            MATCH (init:SustainabilityInitiative {id: $init_id})
            MATCH (trg:SustainabilityTarget {id: $trg_id})
            MERGE (init)-[:ADDRESSES_TARGET]->(trg)
            """, {"init_id": init["id"], "trg_id": tid})

    print("Successfully seeded Neo4j knowledge graph.")

if __name__ == "__main__":
    seed()

