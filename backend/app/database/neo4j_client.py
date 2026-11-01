import logging
import socket
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver
from app.config import settings

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self._admin_driver: Optional[Driver] = None
        self._readonly_driver: Optional[Driver] = None
        self._is_connected: bool = False

    def connect(self) -> bool:
        if not settings.NEO4J_ENABLED or settings.TESTING:
            self._is_connected = False
            self._admin_driver = None
            self._readonly_driver = None
            return False

        # Fast socket pre-check to prevent long retry blocks if Neo4j port is not listening
        try:
            parsed = urlparse(settings.NEO4J_URI)
            host = parsed.hostname or "localhost"
            port = parsed.port or 7687
            with socket.create_connection((host, port), timeout=0.2):
                pass
        except Exception as ex:
            self._is_connected = False
            self._admin_driver = None
            self._readonly_driver = None
            logger.info(f"Neo4j service not reachable at {settings.NEO4J_URI} ({ex}). Running in local graph mirror mode.")
            return False

        try:
            driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
                connection_timeout=2
            )
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    self._admin_driver = driver
                    self._is_connected = True
                    logger.info("Successfully connected to Neo4j database (Admin).")

            try:
                self._readonly_driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_READONLY_USERNAME, settings.NEO4J_READONLY_PASSWORD),
                    connection_timeout=2
                )
            except Exception:
                self._readonly_driver = self._admin_driver

            return self._is_connected
        except Exception as e:
            self._is_connected = False
            self._admin_driver = None
            self._readonly_driver = None
            logger.info(f"Neo4j driver connection failed: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        return self._is_connected and self._admin_driver is not None

    def close(self):
        if self._admin_driver:
            try:
                self._admin_driver.close()
            except Exception:
                pass
        if self._readonly_driver and self._readonly_driver != self._admin_driver:
            try:
                self._readonly_driver.close()
            except Exception:
                pass
        self._admin_driver = None
        self._readonly_driver = None
        self._is_connected = False

    def init_schema(self):
        """Creates unique constraints and indexes for node types."""
        if not self.is_connected:
            return

        constraints = [
            "CREATE CONSTRAINT institution_id_unique IF NOT EXISTS FOR (n:Institution) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT building_id_unique IF NOT EXISTS FOR (n:Building) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT department_id_unique IF NOT EXISTS FOR (n:Department) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT resource_id_unique IF NOT EXISTS FOR (n:Resource) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT energysource_id_unique IF NOT EXISTS FOR (n:EnergySource) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT emission_id_unique IF NOT EXISTS FOR (n:Emission) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT activity_id_unique IF NOT EXISTS FOR (n:Activity) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT initiative_id_unique IF NOT EXISTS FOR (n:SustainabilityInitiative) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT target_id_unique IF NOT EXISTS FOR (n:SustainabilityTarget) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT sdg_id_unique IF NOT EXISTS FOR (n:SDG) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (n:Document) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (n:Chunk) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT measurement_id_unique IF NOT EXISTS FOR (n:Measurement) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT emissionfactor_id_unique IF NOT EXISTS FOR (n:EmissionFactor) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT climatescenario_id_unique IF NOT EXISTS FOR (n:ClimateScenario) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT location_id_unique IF NOT EXISTS FOR (n:Location) REQUIRE n.id IS UNIQUE",
        ]

        with self._admin_driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as ex:
                    logger.debug(f"Constraint setup notice: {ex}")

    def execute_write(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.is_connected:
            raise ConnectionError("Neo4j is not connected.")
        with self._admin_driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def execute_read(self, cypher: str, parameters: Optional[Dict[str, Any]] = None, timeout: int = 15) -> List[Dict[str, Any]]:
        if not self.is_connected:
            raise ConnectionError("Neo4j is not connected.")
        driver = self._readonly_driver or self._admin_driver
        with driver.session() as session:
            result = session.run(cypher, parameters or {}, timeout=timeout)
            return [record.data() for record in result]

neo4j_client = Neo4jClient()
