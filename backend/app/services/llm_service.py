import json
import logging
import time
import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.config import settings

logger = logging.getLogger(__name__)

class ExtractedEntity(BaseModel):
    name: str = Field(..., description="Mentioned name of the entity in the text")
    entity_type: str = Field(..., description="Node label")
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(1.0, ge=0.0, le=1.0)

class ExtractedRelationship(BaseModel):
    source_entity: str
    target_entity: str
    relationship_type: str
    evidence_excerpt: str
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    is_inferred: bool = Field(False)

class ExtractionResult(BaseModel):
    entities: List[ExtractedEntity] = Field(default_factory=list)
    relationships: List[ExtractedRelationship] = Field(default_factory=list)

class OllamaLLMService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self._cached_status: Optional[Dict[str, Any]] = None
        self._last_check_time: float = 0.0
        self._cache_ttl_sec: float = 15.0

    def check_connection(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Verifies Ollama HTTP server accessibility with 15s TTL caching."""
        if not settings.OLLAMA_ENABLED or settings.TESTING:
            return {"connected": False, "version": None, "url": self.base_url}

        now = time.time()
        if not force_refresh and self._cached_status and (now - self._last_check_time < self._cache_ttl_sec):
            return self._cached_status

        try:
            with httpx.Client(timeout=0.2) as client:
                res = client.get(f"{self.base_url}/api/version")
                if res.status_code == 200:
                    data = res.json()
                    self._cached_status = {"connected": True, "version": data.get("version", "unknown"), "url": self.base_url}
                    self._last_check_time = now
                    return self._cached_status
        except Exception:
            pass

        self._cached_status = {"connected": False, "version": None, "url": self.base_url, "error": f"Ollama not reachable at {self.base_url}"}
        self._last_check_time = now
        return self._cached_status

    def check_model_available(self) -> bool:
        """Checks if configured model (e.g. mistral) is pulled and available."""
        if not self.check_connection()["connected"]:
            return False
        try:
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name", "").split(":")[0] for m in res.json().get("models", [])]
                    return any(self.model in m or m in self.model for m in models)
        except Exception as e:
            logger.debug(f"Model availability check failed: {e}")
        return False

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.0, format_json: bool = False) -> str:
        """Synchronous query to Ollama's /api/generate endpoint."""
        conn = self.check_connection()
        if not conn["connected"]:
            raise ConnectionError(f"Ollama service unavailable at {self.base_url}. Ensure Ollama is running and accessible.")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
        if system:
            payload["system"] = system
        if format_json:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")
                return resp.json().get("response", "")
        except httpx.TimeoutException:
            raise TimeoutError(f"Ollama timed out after {self.timeout}s.")
        except Exception as e:
            raise RuntimeError(f"Error communicating with Ollama: {e}")

    def extract_graph_elements(self, chunk_text: str, document_title: str = "") -> ExtractionResult:
        system_prompt = """You are an expert GraphRAG Knowledge Graph Extractor specialized in campus sustainability.
Extract entities and relationships from the provided text according to this schema:
Node Types: Institution, Building, Department, Resource, EnergySource, Emission, Activity, SustainabilityInitiative, SustainabilityTarget, SDG, Location.
Relationship Types: HAS_BUILDING, HAS_DEPARTMENT, CONSUMES_RESOURCE, USES_ENERGY_SOURCE, GENERATES_EMISSION, PRODUCES_WASTE, IMPLEMENTS_INITIATIVE, SUPPORTS_SDG, HAS_TARGET, ADDRESSES_TARGET, REDUCES_EMISSION, ASSOCIATED_WITH.

Output ONLY valid JSON matching this schema:
{
  "entities": [
    {"name": "...", "entity_type": "...", "properties": {}, "confidence": 1.0}
  ],
  "relationships": [
    {"source_entity": "...", "target_entity": "...", "relationship_type": "...", "evidence_excerpt": "...", "confidence": 1.0, "is_inferred": false}
  ]
}
Temperature must be 0."""
        user_prompt = f"Document: {document_title}\nText:\n{chunk_text}\n\nExtract entities and relationships as JSON:"
        raw_response = self.generate(user_prompt, system=system_prompt, temperature=0.0, format_json=True)
        try:
            data = json.loads(raw_response)
            return ExtractionResult(**data)
        except Exception as e:
            logger.error(f"Failed to parse LLM extraction JSON: {e}")
            return ExtractionResult(entities=[], relationships=[])

    def generate_cypher(self, user_question: str, schema_description: str) -> str:
        system_prompt = f"""You are a Neo4j Cypher query expert for an institutional sustainability knowledge graph.
Given this Neo4j Schema:
{schema_description}

Rules:
1. Generate ONLY a single Cypher READ query (MATCH, WHERE, RETURN, ORDER BY, LIMIT).
2. NEVER use write statements (CREATE, MERGE, DELETE, SET, REMOVE, DROP).
3. Always include LIMIT 25 unless explicitly aggregating.
4. Output ONLY the raw Cypher query string without markdown fences."""
        user_prompt = f"Question: {user_question}\nGenerate Cypher:"
        cypher = self.generate(user_prompt, system=system_prompt, temperature=0.0).strip()
        if cypher.startswith("```"):
            cypher = cypher.split("\n", 1)[-1]
        if cypher.endswith("```"):
            cypher = cypher.rsplit("\n", 1)[0]
        return cypher.strip()

llm_service = OllamaLLMService()
