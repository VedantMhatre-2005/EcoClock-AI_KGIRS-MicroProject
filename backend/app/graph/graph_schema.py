from enum import Enum
from typing import Dict, List, Set

class NodeLabel(str, Enum):
    INSTITUTION = "Institution"
    BUILDING = "Building"
    DEPARTMENT = "Department"
    RESOURCE = "Resource"
    ENERGY_SOURCE = "EnergySource"
    EMISSION = "Emission"
    ACTIVITY = "Activity"
    SUSTAINABILITY_INITIATIVE = "SustainabilityInitiative"
    SUSTAINABILITY_TARGET = "SustainabilityTarget"
    SDG = "SDG"
    DOCUMENT = "Document"
    CHUNK = "Chunk"
    MEASUREMENT = "Measurement"
    EMISSION_FACTOR = "EmissionFactor"
    CLIMATE_SCENARIO = "ClimateScenario"
    LOCATION = "Location"

class RelationshipType(str, Enum):
    HAS_BUILDING = "HAS_BUILDING"
    HAS_DEPARTMENT = "HAS_DEPARTMENT"
    CONSUMES_RESOURCE = "CONSUMES_RESOURCE"
    USES_ENERGY_SOURCE = "USES_ENERGY_SOURCE"
    GENERATES_EMISSION = "GENERATES_EMISSION"
    PRODUCES_WASTE = "PRODUCES_WASTE"
    GENERATES_MEASUREMENT = "GENERATES_MEASUREMENT"
    IMPLEMENTS_INITIATIVE = "IMPLEMENTS_INITIATIVE"
    SUPPORTS_SDG = "SUPPORTS_SDG"
    HAS_TARGET = "HAS_TARGET"
    ADDRESSES_TARGET = "ADDRESSES_TARGET"
    SUPPORTED_BY = "SUPPORTED_BY"
    HAS_CHUNK = "HAS_CHUNK"
    DERIVED_FROM = "DERIVED_FROM"
    APPLIES_TO = "APPLIES_TO"
    REDUCES_EMISSION = "REDUCES_EMISSION"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"

class VerificationStatus(str, Enum):
    EXPLICIT = "EXPLICIT"    # Directly stated in text
    INFERRED = "INFERRED"    # LLM-derived hypothesis
    VERIFIED = "VERIFIED"    # Programmatically or manually validated

VALID_NODE_LABELS: Set[str] = {label.value for label in NodeLabel}
VALID_RELATIONSHIP_TYPES: Set[str] = {rel.value for rel in RelationshipType}

# Schema graph constraints and allowable relationship pairs
ALLOWABLE_TRIPLES = {
    ("Institution", "HAS_BUILDING", "Building"),
    ("Institution", "HAS_DEPARTMENT", "Department"),
    ("Institution", "IMPLEMENTS_INITIATIVE", "SustainabilityInitiative"),
    ("Institution", "HAS_TARGET", "SustainabilityTarget"),
    ("Building", "CONSUMES_RESOURCE", "Resource"),
    ("Building", "USES_ENERGY_SOURCE", "EnergySource"),
    ("Building", "GENERATES_EMISSION", "Emission"),
    ("Building", "PRODUCES_WASTE", "Emission"),
    ("Department", "IMPLEMENTS_INITIATIVE", "SustainabilityInitiative"),
    ("Activity", "GENERATES_EMISSION", "Emission"),
    ("SustainabilityInitiative", "SUPPORTS_SDG", "SDG"),
    ("SustainabilityInitiative", "ADDRESSES_TARGET", "SustainabilityTarget"),
    ("SustainabilityInitiative", "REDUCES_EMISSION", "Emission"),
    ("SustainabilityTarget", "SUPPORTS_SDG", "SDG"),
    ("Document", "HAS_CHUNK", "Chunk"),
    ("SustainabilityInitiative", "SUPPORTED_BY", "Document"),
    ("SustainabilityTarget", "SUPPORTED_BY", "Document"),
    ("Measurement", "DERIVED_FROM", "Chunk"),
    ("EmissionFactor", "APPLIES_TO", "Activity"),
    ("ClimateScenario", "ADDRESSES_TARGET", "SustainabilityTarget"),
    ("Activity", "ASSOCIATED_WITH", "SDG"),
}

