import re
from typing import Dict, Optional, Tuple

# Pre-defined institutional alias lookup dictionary for high-precision entity resolution
KNOWN_ALIASES = {
    # Institution
    "vesit": ("VESIT", "VESIT Green Campus", "Institution"),
    "vesit green campus": ("VESIT", "VESIT Green Campus", "Institution"),
    "vivekananda education society's institute of technology": ("VESIT", "VESIT Green Campus", "Institution"),
    "campus": ("VESIT", "VESIT Green Campus", "Institution"),
    "institution": ("VESIT", "VESIT Green Campus", "Institution"),

    # Buildings
    "academic block a": ("BLD_ACA", "Academic Block A", "Building"),
    "block a": ("BLD_ACA", "Academic Block A", "Building"),
    "academic block b": ("BLD_ACB", "Academic Block B", "Building"),
    "block b": ("BLD_ACB", "Academic Block B", "Building"),
    "computer laboratories": ("BLD_LAB", "Computer Laboratories", "Building"),
    "computer labs": ("BLD_LAB", "Computer Laboratories", "Building"),
    "lab block": ("BLD_LAB", "Computer Laboratories", "Building"),
    "library": ("BLD_LIB", "Library", "Building"),
    "auditorium": ("BLD_AUD", "Auditorium", "Building"),
    "canteen": ("BLD_CAN", "Canteen", "Building"),
    "cafeteria": ("BLD_CAN", "Canteen", "Building"),
    "administration block": ("BLD_ADM", "Administration Block", "Building"),
    "admin block": ("BLD_ADM", "Administration Block", "Building"),

    # Departments
    "computer engineering": ("DEP_CMPN", "Computer Engineering", "Department"),
    "department of computer engineering": ("DEP_CMPN", "Computer Engineering", "Department"),
    "cmpn": ("DEP_CMPN", "Computer Engineering", "Department"),
    "information technology": ("DEP_INFT", "Information Technology", "Department"),
    "inft": ("DEP_INFT", "Information Technology", "Department"),
    "electronics & telecommunication": ("DEP_EXTC", "Electronics & Telecommunication", "Department"),
    "extc": ("DEP_EXTC", "Electronics & Telecommunication", "Department"),
    "artificial intelligence & data science": ("DEP_AIDS", "Artificial Intelligence & Data Science", "Department"),
    "ai & data science": ("DEP_AIDS", "Artificial Intelligence & Data Science", "Department"),
    "aids": ("DEP_AIDS", "Artificial Intelligence & Data Science", "Department"),

    # Targets
    "net zero 2040": ("TRG_NET_ZERO", "Campus Net-Zero Carbon Neutrality by 2040", "SustainabilityTarget"),
    "carbon neutrality": ("TRG_NET_ZERO", "Campus Net-Zero Carbon Neutrality by 2040", "SustainabilityTarget"),
    "trg_net_zero": ("TRG_NET_ZERO", "Campus Net-Zero Carbon Neutrality by 2040", "SustainabilityTarget"),
    "renewable electricity target": ("TRG_RENEWABLE", "50% Renewable Electricity Generation by 2030", "SustainabilityTarget"),
    "zero waste target": ("TRG_ZERO_WASTE", "Zero Waste to Landfill & 85% Recycling by 2028", "SustainabilityTarget"),
    "water conservation target": ("TRG_WATER_NEUTRAL", "30% Reduction in Municipal Water Consumption by 2029", "SustainabilityTarget"),
    "green commute target": ("TRG_GREEN_COMMUTE", "70% Low-Carbon Campus Commute Share by 2027", "SustainabilityTarget"),

    # Initiatives
    "rooftop solar phase 1": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "phase 1 solar": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "phase-1 solar": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "init_solar_ph1": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "phase 2 solar": ("INIT_SOLAR_PH2", "Phase-2 Solar Expansion & Battery Storage", "SustainabilityInitiative"),
    "init_solar_ph2": ("INIT_SOLAR_PH2", "Phase-2 Solar Expansion & Battery Storage", "SustainabilityInitiative"),
    "rainwater harvesting": ("INIT_RWH_SYSTEM", "Integrated Rainwater Harvesting System", "SustainabilityInitiative"),
    "init_rwh_system": ("INIT_RWH_SYSTEM", "Integrated Rainwater Harvesting System", "SustainabilityInitiative"),
    "canteen biogas": ("INIT_BIOGAS_CANTEEN", "Smart Food Waste Digester & Composting", "SustainabilityInitiative"),
    "biogas plant": ("INIT_BIOGAS_CANTEEN", "Smart Food Waste Digester & Composting", "SustainabilityInitiative"),
    "init_biogas_canteen": ("INIT_BIOGAS_CANTEEN", "Smart Food Waste Digester & Composting", "SustainabilityInitiative"),
    "electric shuttle": ("INIT_ELECTRIC_SHUTTLE", "Zero-Emission Electric Campus Transit", "SustainabilityInitiative"),
    "init_electric_shuttle": ("INIT_ELECTRIC_SHUTTLE", "Zero-Emission Electric Campus Transit", "SustainabilityInitiative"),
    "iot energy management": ("INIT_IOT_ENERGY_MGT", "Campus-Wide IoT Smart Sub-Metering", "SustainabilityInitiative"),
    "init_iot_energy_mgt": ("INIT_IOT_ENERGY_MGT", "Campus-Wide IoT Smart Sub-Metering", "SustainabilityInitiative"),
    "miyawaki forest": ("INIT_BIODIVERSITY_ZONE", "Miyawaki Urban Native Afforestation", "SustainabilityInitiative"),
    "init_biodiversity_zone": ("INIT_BIODIVERSITY_ZONE", "Miyawaki Urban Native Afforestation", "SustainabilityInitiative"),

    # SDGs
    "sdg 6": ("SDG_6", "Clean Water and Sanitation", "SDG"),
    "clean water and sanitation": ("SDG_6", "Clean Water and Sanitation", "SDG"),
    "sdg 7": ("SDG_7", "Affordable and Clean Energy", "SDG"),
    "affordable and clean energy": ("SDG_7", "Affordable and Clean Energy", "SDG"),
    "sdg 11": ("SDG_11", "Sustainable Cities and Communities", "SDG"),
    "sustainable cities and communities": ("SDG_11", "Sustainable Cities and Communities", "SDG"),
    "sdg 12": ("SDG_12", "Responsible Consumption and Production", "SDG"),
    "responsible consumption and production": ("SDG_12", "Responsible Consumption and Production", "SDG"),
    "sdg 13": ("SDG_13", "Climate Action", "SDG"),
    "climate action": ("SDG_13", "Climate Action", "SDG"),
    "sdg 15": ("SDG_15", "Life on Land", "SDG"),
    "life on land": ("SDG_15", "Life on Land", "SDG"),
}

class EntityResolver:
    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'[^\w\s\-_]', '', text)
        return text

    @staticmethod
    def resolve_entity(name: str, entity_type: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Resolves entity name to canonical ID, canonical label, and standardized entity type.
        Returns: (canonical_id, canonical_name, entity_type)
        """
        normalized = EntityResolver.normalize_text(name)
        if normalized in KNOWN_ALIASES:
            return KNOWN_ALIASES[normalized]

        # Check regex matches for SDG (e.g. "SDG 13", "SDG_13", "Goal 13")
        sdg_match = re.match(r'^(?:sdg|goal)[\s_]*([0-9]{1,2})$', normalized)
        if sdg_match:
            sdg_num = int(sdg_match.group(1))
            if 1 <= sdg_num <= 17:
                return (f"SDG_{sdg_num}", f"SDG {sdg_num}", "SDG")

        # Stable hash-based ID for custom entities
        safe_id = "ENT_" + re.sub(r'[^A-Z0-9]', '_', name.upper().strip())[:32]
        return (safe_id, name.strip(), entity_type or "Entity")

