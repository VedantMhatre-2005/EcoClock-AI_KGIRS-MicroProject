import re
from typing import Dict, Optional, Tuple, Any

# Pre-defined institutional alias lookup dictionary for high-precision entity resolution
KNOWN_ALIASES = {
    # Institution
    "vesit": ("VESIT", "VESIT Green Campus", "Institution"),
    "vesit green campus": ("VESIT", "VESIT Green Campus", "Institution"),
    "vivekananda education society's institute of technology": ("VESIT", "VESIT Green Campus", "Institution"),
    "campus": ("VESIT", "VESIT Green Campus", "Institution"),
    "institution": ("VESIT", "VESIT Green Campus", "Institution"),

    # Location
    "chembur": ("LOC_CHEMBUR", "Chembur, Mumbai", "Location"),
    "chembur mumbai": ("LOC_CHEMBUR", "Chembur, Mumbai", "Location"),
    "mumbai": ("LOC_MUMBAI", "Mumbai, Maharashtra", "Location"),

    # Buildings
    "academic block a": ("BLD_ACA", "Academic Block A", "Building"),
    "block a": ("BLD_ACA", "Academic Block A", "Building"),
    "bld_aca": ("BLD_ACA", "Academic Block A", "Building"),
    "academic block b": ("BLD_ACB", "Academic Block B", "Building"),
    "block b": ("BLD_ACB", "Academic Block B", "Building"),
    "bld_acb": ("BLD_ACB", "Academic Block B", "Building"),
    "computer laboratories": ("BLD_LAB", "Computer Laboratories", "Building"),
    "computer labs": ("BLD_LAB", "Computer Laboratories", "Building"),
    "lab block": ("BLD_LAB", "Computer Laboratories", "Building"),
    "bld_lab": ("BLD_LAB", "Computer Laboratories", "Building"),
    "library": ("BLD_LIB", "Library", "Building"),
    "bld_lib": ("BLD_LIB", "Library", "Building"),
    "auditorium": ("BLD_AUD", "Auditorium", "Building"),
    "bld_aud": ("BLD_AUD", "Auditorium", "Building"),
    "canteen": ("BLD_CAN", "Canteen", "Building"),
    "cafeteria": ("BLD_CAN", "Canteen", "Building"),
    "bld_can": ("BLD_CAN", "Canteen", "Building"),
    "administration block": ("BLD_ADM", "Administration Block", "Building"),
    "admin block": ("BLD_ADM", "Administration Block", "Building"),
    "bld_adm": ("BLD_ADM", "Administration Block", "Building"),

    # Departments
    "computer engineering": ("DEP_CMPN", "Computer Engineering", "Department"),
    "department of computer engineering": ("DEP_CMPN", "Computer Engineering", "Department"),
    "cmpn": ("DEP_CMPN", "Computer Engineering", "Department"),
    "dep_cmpn": ("DEP_CMPN", "Computer Engineering", "Department"),
    "information technology": ("DEP_INFT", "Information Technology", "Department"),
    "inft": ("DEP_INFT", "Information Technology", "Department"),
    "dep_inft": ("DEP_INFT", "Information Technology", "Department"),
    "electronics & telecommunication": ("DEP_EXTC", "Electronics & Telecommunication", "Department"),
    "extc": ("DEP_EXTC", "Electronics & Telecommunication", "Department"),
    "dep_extc": ("DEP_EXTC", "Electronics & Telecommunication", "Department"),
    "artificial intelligence & data science": ("DEP_AIDS", "Artificial Intelligence & Data Science", "Department"),
    "ai & data science": ("DEP_AIDS", "Artificial Intelligence & Data Science", "Department"),
    "aids": ("DEP_AIDS", "Artificial Intelligence & Data Science", "Department"),
    "dep_aids": ("DEP_AIDS", "Artificial Intelligence & Data Science", "Department"),
    "facilities": ("DEP_ADMN", "Administration & Campus Facilities", "Department"),
    "dep_admn": ("DEP_ADMN", "Administration & Campus Facilities", "Department"),

    # Targets
    "net zero 2040": ("TRG_NET_ZERO", "Campus Net-Zero Carbon Neutrality by 2040", "SustainabilityTarget"),
    "carbon neutrality": ("TRG_NET_ZERO", "Campus Net-Zero Carbon Neutrality by 2040", "SustainabilityTarget"),
    "trg_net_zero": ("TRG_NET_ZERO", "Campus Net-Zero Carbon Neutrality by 2040", "SustainabilityTarget"),
    "renewable electricity target": ("TRG_RENEWABLE", "50% Renewable Electricity Generation by 2030", "SustainabilityTarget"),
    "trg_renewable": ("TRG_RENEWABLE", "50% Renewable Electricity Generation by 2030", "SustainabilityTarget"),
    "zero waste target": ("TRG_ZERO_WASTE", "Zero Waste to Landfill & 85% Recycling by 2028", "SustainabilityTarget"),
    "trg_zero_waste": ("TRG_ZERO_WASTE", "Zero Waste to Landfill & 85% Recycling by 2028", "SustainabilityTarget"),
    "water conservation target": ("TRG_WATER_NEUTRAL", "30% Reduction in Municipal Water Consumption by 2029", "SustainabilityTarget"),
    "trg_water_neutral": ("TRG_WATER_NEUTRAL", "30% Reduction in Municipal Water Consumption by 2029", "SustainabilityTarget"),
    "green commute target": ("TRG_GREEN_COMMUTE", "70% Low-Carbon Campus Commute Share by 2027", "SustainabilityTarget"),
    "trg_green_commute": ("TRG_GREEN_COMMUTE", "70% Low-Carbon Campus Commute Share by 2027", "SustainabilityTarget"),

    # Initiatives
    "rooftop solar phase 1": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "phase 1 solar": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "phase-1 solar": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "init_solar_ph1": ("INIT_SOLAR_PH1", "Phase-1 Rooftop Solar Photovoltaic Project", "SustainabilityInitiative"),
    "phase 2 solar": ("INIT_SOLAR_PH2", "Phase-2 Solar Expansion & Battery Storage", "SustainabilityInitiative"),
    "phase-2 solar": ("INIT_SOLAR_PH2", "Phase-2 Solar Expansion & Battery Storage", "SustainabilityInitiative"),
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
    "sdg 1": ("SDG_1", "No Poverty", "SDG"),
    "sdg 6": ("SDG_6", "Clean Water and Sanitation", "SDG"),
    "clean water and sanitation": ("SDG_6", "Clean Water and Sanitation", "SDG"),
    "sdg_6": ("SDG_6", "Clean Water and Sanitation", "SDG"),
    "sdg 7": ("SDG_7", "Affordable and Clean Energy", "SDG"),
    "affordable and clean energy": ("SDG_7", "Affordable and Clean Energy", "SDG"),
    "sdg_7": ("SDG_7", "Affordable and Clean Energy", "SDG"),
    "sdg 9": ("SDG_9", "Industry, Innovation and Infrastructure", "SDG"),
    "industry innovation and infrastructure": ("SDG_9", "Industry, Innovation and Infrastructure", "SDG"),
    "sdg_9": ("SDG_9", "Industry, Innovation and Infrastructure", "SDG"),
    "sdg 11": ("SDG_11", "Sustainable Cities and Communities", "SDG"),
    "sustainable cities and communities": ("SDG_11", "Sustainable Cities and Communities", "SDG"),
    "sdg_11": ("SDG_11", "Sustainable Cities and Communities", "SDG"),
    "sdg 12": ("SDG_12", "Responsible Consumption and Production", "SDG"),
    "responsible consumption and production": ("SDG_12", "Responsible Consumption and Production", "SDG"),
    "sdg_12": ("SDG_12", "Responsible Consumption and Production", "SDG"),
    "sdg 13": ("SDG_13", "Climate Action", "SDG"),
    "climate action": ("SDG_13", "Climate Action", "SDG"),
    "sdg_13": ("SDG_13", "Climate Action", "SDG"),
    "sdg 15": ("SDG_15", "Life on Land", "SDG"),
    "life on land": ("SDG_15", "Life on Land", "SDG"),
    "sdg_15": ("SDG_15", "Life on Land", "SDG"),

    # Emission Factors
    "ef_elec_grid": ("EF_ELEC_GRID", "Grid Electricity Emission Factor (CEA)", "EmissionFactor"),
    "ef_diesel_gen": ("EF_DIESEL_GEN", "Stationary Diesel Generator Factor", "EmissionFactor"),
    "ef_trans_bus": ("EF_TRANS_BUS", "Municipal Transit Bus Emission Factor", "EmissionFactor"),
    "ef_trans_train": ("EF_TRANS_TRAIN", "Suburban Electric Rail Factor", "EmissionFactor"),
    "ef_trans_car": ("EF_TRANS_CAR", "Passenger Motorcar Emission Factor", "EmissionFactor"),
    "ef_trans_bike": ("EF_TRANS_BIKE", "Two-Wheeler Emission Factor", "EmissionFactor"),
    "ef_waste_landfill": ("EF_WASTE_LANDFILL", "Unsegregated Landfill Waste Factor", "EmissionFactor"),
    "ef_waste_compost": ("EF_WASTE_COMPOST", "Decentralized Aerobic Composting Factor", "EmissionFactor"),
    "ef_waste_recycle": ("EF_WASTE_RECYCLE", "Dry Recyclables Recovery Avoided Factor", "EmissionFactor"),

    # Energy Sources
    "grid electricity": ("ENG_GRID", "Regional Grid Electricity", "EnergySource"),
    "rooftop solar": ("ENG_SOLAR", "Rooftop Solar Photovoltaic Generation", "EnergySource"),
    "solar pv": ("ENG_SOLAR", "Rooftop Solar Photovoltaic Generation", "EnergySource"),
    "diesel": ("ENG_DIESEL", "Stationary Diesel Fuel", "EnergySource"),
    "diesel fuel": ("ENG_DIESEL", "Stationary Diesel Fuel", "EnergySource"),
    "biogas": ("ENG_BIOGAS", "Canteen Anaerobic Biogas", "EnergySource"),

    # Resources
    "water": ("RES_WATER", "Municipal Piped Freshwater", "Resource"),
    "freshwater": ("RES_WATER", "Municipal Piped Freshwater", "Resource"),
    "rainwater": ("RES_RAINWATER", "Harvested Rainwater", "Resource"),
    "greywater": ("RES_GREYWATER", "Recycled Canteen Greywater", "Resource"),
    "paper": ("RES_PAPER", "Academic & Administrative Paper", "Resource"),
    "food waste": ("RES_FOOD_WASTE", "Canteen Organic Food Scraps", "Resource"),
    "organic waste": ("RES_FOOD_WASTE", "Canteen Organic Food Scraps", "Resource"),
    "e-waste": ("RES_EWASTE", "Electronic Hardware Scrap", "Resource"),
    "plastics": ("RES_PLASTIC", "Post-Consumer Packaging Plastics", "Resource"),

    # Emissions
    "scope 1": ("EMIS_SCOPE1", "Scope 1 Direct Diesel Emissions", "Emission"),
    "scope 2": ("EMIS_SCOPE2", "Scope 2 Indirect Grid Electricity Emissions", "Emission"),
    "scope 3": ("EMIS_SCOPE3", "Scope 3 Commuter & Waste Emissions", "Emission"),
    "carbon emissions": ("EMIS_GHG", "Campus Greenhouse Gas Emissions", "Emission"),

    # Activities
    "commuting": ("ACT_COMMUTING", "Campus Community Commuting", "Activity"),
    "student commuting": ("ACT_COMMUTING", "Campus Community Commuting", "Activity"),
    "solar generation": ("ACT_SOLAR_GEN", "Rooftop Solar Electricity Generation", "Activity"),
    "rainwater harvesting": ("ACT_RWH", "Monsoon Terrace Rainwater Harvesting", "Activity"),
    "composting": ("ACT_COMPOSTING", "Decentralized Canteen Composting", "Activity"),
    "iot metering": ("ACT_IOT_METERING", "Smart IoT Telemetry & Demand Monitoring", "Activity"),
    "space cooling": ("ACT_COOLING", "Campus Space Air Conditioning & Chillers", "Activity"),

    # Climate Scenarios
    "linear decarbonization trajectory": ("SCEN_LINEAR", "Linear Decarbonization Trajectory (153k kg CO2e/yr)", "ClimateScenario"),
    "linear trajectory": ("SCEN_LINEAR", "Linear Decarbonization Trajectory (153k kg CO2e/yr)", "ClimateScenario"),
    "compound annual reduction trajectory": ("SCEN_COMPOUND", "Compound Annual Reduction Trajectory (12.5%/yr)", "ClimateScenario"),
    "compound trajectory": ("SCEN_COMPOUND", "Compound Annual Reduction Trajectory (12.5%/yr)", "ClimateScenario"),
}

class EntityResolver:
    @staticmethod
    def normalize_text(text: Any) -> str:
        if isinstance(text, dict):
            text = text.get("name") or text.get("id") or text.get("entity") or str(text)
        elif not isinstance(text, str):
            text = str(text or "")
        text = text.lower().strip()
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'[^\w\s\-_]', '', text)
        return text

    @staticmethod
    def resolve_entity(name: Any, entity_type: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Resolves entity name to canonical ID, canonical label, and standardized entity type.
        Returns: (canonical_id, canonical_name, entity_type)
        """
        if isinstance(name, dict):
            name_str = str(name.get("name") or name.get("id") or name.get("entity") or "").strip()
            entity_type = entity_type or name.get("type") or name.get("entity_type")
        else:
            name_str = str(name or "").strip()

        normalized = EntityResolver.normalize_text(name_str)
        if normalized in KNOWN_ALIASES:
            return KNOWN_ALIASES[normalized]

        # Check regex matches for SDG (e.g. "SDG 13", "SDG_13", "Goal 13")
        sdg_match = re.match(r'^(?:sdg|goal)[\s_]*([0-9]{1,2})$', normalized)
        if sdg_match:
            sdg_num = int(sdg_match.group(1))
            if 1 <= sdg_num <= 17:
                return (f"SDG_{sdg_num}", f"SDG {sdg_num}", "SDG")

        # Stable hash-based ID for custom entities
        safe_id = "ENT_" + re.sub(r'[^A-Z0-9]', '_', name_str.upper().strip())[:32]
        return (safe_id, name_str.strip() or "Unnamed Entity", entity_type or "Entity")
