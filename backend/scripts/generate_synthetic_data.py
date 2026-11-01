"""
EcoClock AI - Synthetic Data Generator
Generates realistic, reproducible synthetic sustainability data for VESIT Green Campus.
Seed: 42
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Set fixed random seed
np.random.seed(42)

SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

# 1. INSTITUTION & CAMPUS INFRASTRUCTURE
INSTITUTION = {
    "id": "VESIT",
    "name": "VESIT Green Campus",
    "location": "Chembur, Mumbai, Maharashtra, India",
    "student_population": 3000,
    "faculty_staff_population": 200,
    "total_built_up_area_m2": 32500,
    "baseline_year": 2024,
    "target_carbon_neutral_year": 2040,
    "source_type": "SYNTHETIC"
}

BUILDINGS = [
    {"id": "BLD_ACA", "name": "Academic Block A", "area_m2": 7500, "primary_use": "Classrooms & Faculty Offices", "occupancy": 1100, "has_rooftop_solar": True, "solar_capacity_kw": 80},
    {"id": "BLD_ACB", "name": "Academic Block B", "area_m2": 6800, "primary_use": "Classrooms & Seminar Halls", "occupancy": 950, "has_rooftop_solar": True, "solar_capacity_kw": 70},
    {"id": "BLD_LAB", "name": "Computer Laboratories", "area_m2": 5200, "primary_use": "High-Density Computing Labs & Server Rooms", "occupancy": 650, "has_rooftop_solar": False, "solar_capacity_kw": 0},
    {"id": "BLD_LIB", "name": "Library", "area_m2": 3100, "primary_use": "Reading Rooms, Digital Archives & Stack Areas", "occupancy": 350, "has_rooftop_solar": True, "solar_capacity_kw": 30},
    {"id": "BLD_AUD", "name": "Auditorium", "area_m2": 2800, "primary_use": "Cultural Events, Keynotes & Large Conferences", "occupancy": 800, "has_rooftop_solar": False, "solar_capacity_kw": 0},
    {"id": "BLD_CAN", "name": "Canteen", "area_m2": 2100, "primary_use": "Food Preparation, Dining & Organic Waste Digestion", "occupancy": 400, "has_rooftop_solar": False, "solar_capacity_kw": 0},
    {"id": "BLD_ADM", "name": "Administration Block", "area_m2": 5000, "primary_use": "Administrative Offices, Council Chambers & Data Hub", "occupancy": 200, "has_rooftop_solar": True, "solar_capacity_kw": 40}
]

DEPARTMENTS = [
    {"id": "DEP_CMPN", "name": "Computer Engineering", "head": "Dr. N. Joshi", "building_id": "BLD_ACA"},
    {"id": "DEP_INFT", "name": "Information Technology", "head": "Dr. S. Nair", "building_id": "BLD_ACB"},
    {"id": "DEP_EXTC", "name": "Electronics & Telecommunication", "head": "Dr. R. Kulkarni", "building_id": "BLD_ACA"},
    {"id": "DEP_AIDS", "name": "Artificial Intelligence & Data Science", "head": "Dr. P. Sharma", "building_id": "BLD_LAB"},
    {"id": "DEP_ADMN", "name": "Administration & Campus Facilities", "head": "Mr. V. Deshmukh", "building_id": "BLD_ADM"}
]

# 2. EMISSION FACTORS (Documented standards & CEA India grid factors)
EMISSION_FACTORS = [
    {"id": "EF_ELEC_GRID", "category": "ELECTRICITY", "name": "Grid Electricity (CEA Baseline India v19)", "value": 0.82, "unit": "kg CO2e/kWh", "reference_year": 2024, "region": "Western Regional Grid, India", "source": "Central Electricity Authority (CEA) CO2 Baseline Database", "source_type": "DOCUMENTED", "version": "19.0"},
    {"id": "EF_DIESEL_GEN", "category": "DIESEL", "name": "Stationary Diesel Generator", "value": 2.68, "unit": "kg CO2e/litre", "reference_year": 2024, "region": "India National Average", "source": "IPCC Emission Factor Database", "source_type": "DOCUMENTED", "version": "2024.1"},
    {"id": "EF_TRANS_BUS", "category": "TRANSPORT", "name": "Municipal Transit / Public Bus", "value": 0.054, "unit": "kg CO2e/passenger-km", "reference_year": 2024, "region": "Urban India", "source": "India GHG Program Transport Guidance", "source_type": "DOCUMENTED", "version": "2.2"},
    {"id": "EF_TRANS_TRAIN", "category": "TRANSPORT", "name": "Suburban Electric Rail / Metro", "value": 0.028, "unit": "kg CO2e/passenger-km", "reference_year": 2024, "region": "Mumbai Suburban Rail", "source": "Indian Railways Carbon Accounting", "source_type": "DOCUMENTED", "version": "2023.4"},
    {"id": "EF_TRANS_CAR", "category": "TRANSPORT", "name": "Private Petrol / Diesel Passenger Car", "value": 0.175, "unit": "kg CO2e/passenger-km", "reference_year": 2024, "region": "India Metro", "source": "ARAI Carbon Footprint Guidelines", "source_type": "DOCUMENTED", "version": "3.1"},
    {"id": "EF_TRANS_BIKE", "category": "TRANSPORT", "name": "Two-Wheeler (Motorcycle / Scooter)", "value": 0.042, "unit": "kg CO2e/passenger-km", "reference_year": 2024, "region": "India Urban", "source": "ARAI Two-Wheeler Emission Benchmarks", "source_type": "DOCUMENTED", "version": "2.0"},
    {"id": "EF_WASTE_LANDFILL", "category": "WASTE", "name": "Unsegregated Municipal Solid Waste to Landfill", "value": 1.25, "unit": "kg CO2e/kg waste", "reference_year": 2024, "region": "Deonar / Kanjurmarg Mumbai", "source": "CPCB Municipal Solid Waste Technical Report", "source_type": "DOCUMENTED", "version": "1.8"},
    {"id": "EF_WASTE_COMPOST", "category": "WASTE", "name": "Decentralized Aerobic Composting", "value": 0.08, "unit": "kg CO2e/kg waste", "reference_year": 2024, "region": "Campus Compost Unit", "source": "IPCC Tier 1 Composting Factor", "source_type": "DOCUMENTED", "version": "2024.1"},
    {"id": "EF_WASTE_RECYCLE", "category": "WASTE", "name": "Dry Recyclables Recovery Avoided Factor", "value": -0.65, "unit": "kg CO2e/kg waste", "reference_year": 2024, "region": "Formal Recycling Stream", "source": "TERI Circular Waste Model", "source_type": "ESTIMATED", "version": "1.0"}
]

# 3. INSTITUTIONAL SUSTAINABILITY TARGETS
TARGETS = [
    {"id": "TRG_NET_ZERO", "title": "Campus Net-Zero Carbon Neutrality by 2040", "category": "CARBON", "baseline_year": 2024, "target_year": 2040, "baseline_value": 2450000.0, "target_value": 0.0, "unit": "kg CO2e/year", "status": "IN_PROGRESS", "source_type": "SYNTHETIC"},
    {"id": "TRG_RENEWABLE", "title": "50% Renewable Electricity Generation by 2030", "category": "ENERGY", "baseline_year": 2024, "target_year": 2030, "baseline_value": 14.8, "target_value": 50.0, "unit": "percentage", "status": "IN_PROGRESS", "source_type": "SYNTHETIC"},
    {"id": "TRG_ZERO_WASTE", "title": "Zero Waste to Landfill & 85% Recycling by 2028", "category": "WASTE", "baseline_year": 2024, "target_year": 2028, "baseline_value": 42.0, "target_value": 85.0, "unit": "percentage", "status": "IN_PROGRESS", "source_type": "SYNTHETIC"},
    {"id": "TRG_WATER_NEUTRAL", "title": "30% Reduction in Municipal Water Consumption by 2029", "category": "WATER", "baseline_year": 2024, "target_year": 2029, "baseline_value": 48000000.0, "target_value": 33600000.0, "unit": "litres/year", "status": "IN_PROGRESS", "source_type": "SYNTHETIC"},
    {"id": "TRG_GREEN_COMMUTE", "title": "70% Low-Carbon Campus Commute Share by 2027", "category": "TRANSPORT", "baseline_year": 2024, "target_year": 2027, "baseline_value": 52.0, "target_value": 70.0, "unit": "percentage", "status": "IN_PROGRESS", "source_type": "SYNTHETIC"}
]

# 4. SUSTAINABILITY INITIATIVES
INITIATIVES = [
    {
        "id": "INIT_SOLAR_PH1",
        "name": "Phase-1 Rooftop Solar Photovoltaic Grid-Tied Project (220 kWp)",
        "description": "Installation of 220 kWp monocrystalline rooftop PV modules across Academic Block A, Academic Block B, Library, and Administration Block.",
        "lead_department": "Campus Facilities & Electronics",
        "status": "COMPLETED",
        "start_date": "2023-01-15",
        "completion_date": "2023-11-30",
        "sdg_ids": ["SDG_7", "SDG_11", "SDG_13"],
        "target_ids": ["TRG_NET_ZERO", "TRG_RENEWABLE"],
        "carbon_reduction_estimate_kgco2e": 275000.0,
        "source_type": "SYNTHETIC"
    },
    {
        "id": "INIT_SOLAR_PH2",
        "name": "Phase-2 Solar Expansion & Battery Storage Proposal (150 kWp + 100 kWh BESS)",
        "description": "Feasibility project for adding 150 kWp canopy solar over campus parking and auditorium roof with battery energy storage.",
        "lead_department": "Green Campus Committee",
        "status": "PLANNED",
        "start_date": "2025-06-01",
        "completion_date": "2026-03-31",
        "sdg_ids": ["SDG_7", "SDG_9", "SDG_13"],
        "target_ids": ["TRG_NET_ZERO", "TRG_RENEWABLE"],
        "carbon_reduction_estimate_kgco2e": 185000.0,
        "source_type": "SYNTHETIC"
    },
    {
        "id": "INIT_RWH_SYSTEM",
        "name": "Integrated Rainwater Harvesting & Groundwater Recharge Cisterns",
        "description": "Collection system capturing runoff from 18,000 m2 roof surface with three 150,000-litre filtration cisterns for flushing and garden irrigation.",
        "lead_department": "Campus Infrastructure & Civil Works",
        "status": "ACTIVE",
        "start_date": "2023-07-01",
        "completion_date": "2024-05-15",
        "sdg_ids": ["SDG_6", "SDG_11", "SDG_12"],
        "target_ids": ["TRG_WATER_NEUTRAL"],
        "carbon_reduction_estimate_kgco2e": 12000.0,
        "source_type": "SYNTHETIC"
    },
    {
        "id": "INIT_BIOGAS_CANTEEN",
        "name": "Smart Food Waste Digester & Organic Aerobic Composting Pit",
        "description": "250 kg/day anaerobic biomethanation plant processing food waste from Canteen into cooking gas and organic nutrient-rich fertilizer.",
        "lead_department": "Canteen Committee & Green Club",
        "status": "ACTIVE",
        "start_date": "2023-09-01",
        "completion_date": "2024-02-10",
        "sdg_ids": ["SDG_12", "SDG_13", "SDG_15"],
        "target_ids": ["TRG_ZERO_WASTE", "TRG_NET_ZERO"],
        "carbon_reduction_estimate_kgco2e": 48000.0,
        "source_type": "SYNTHETIC"
    },
    {
        "id": "INIT_ELECTRIC_SHUTTLE",
        "name": "Zero-Emission Electric Campus Transit & Station Feeder Van",
        "description": "Operation of two 14-seater electric shuttle vans connecting Kurla / Chembur suburban train stations to VESIT campus for staff and students.",
        "lead_department": "Administration & Student Council",
        "status": "ACTIVE",
        "start_date": "2024-01-08",
        "completion_date": "2024-12-31",
        "sdg_ids": ["SDG_11", "SDG_13"],
        "target_ids": ["TRG_GREEN_COMMUTE", "TRG_NET_ZERO"],
        "carbon_reduction_estimate_kgco2e": 36000.0,
        "source_type": "SYNTHETIC"
    },
    {
        "id": "INIT_IOT_ENERGY_MGT",
        "name": "Campus-Wide IoT Smart Sub-Metering & Energy Audit Protocol",
        "description": "Deployment of 45 Modbus IoT smart electricity meters across all building distribution panels providing real-time telemetry.",
        "lead_department": "AI & Data Science & Computer Engineering",
        "status": "ACTIVE",
        "start_date": "2024-03-01",
        "completion_date": "2024-09-30",
        "sdg_ids": ["SDG_7", "SDG_9", "SDG_12"],
        "target_ids": ["TRG_NET_ZERO", "TRG_RENEWABLE"],
        "carbon_reduction_estimate_kgco2e": 55000.0,
        "source_type": "SYNTHETIC"
    },
    {
        "id": "INIT_BIODIVERSITY_ZONE",
        "name": "Miyawaki Urban Native Afforestation & Campus Biodiversity Arboretum",
        "description": "High-density plantation of 1,200 indigenous plant and tree species on campus periphery providing carbon sequestration and heat island mitigation.",
        "lead_department": "Nature Club & Environmental Cell",
        "status": "ACTIVE",
        "start_date": "2023-06-05",
        "completion_date": "2024-06-05",
        "sdg_ids": ["SDG_13", "SDG_15"],
        "target_ids": ["TRG_NET_ZERO"],
        "carbon_reduction_estimate_kgco2e": 14000.0,
        "source_type": "SYNTHETIC"
    }
]

# 5. UN SUSTAINABLE DEVELOPMENT GOALS (SDG 1 - 17)
SDGS = [
    {"id": "SDG_1", "sdg_number": 1, "name": "No Poverty", "description": "End poverty in all its forms everywhere.", "color": "#e5243b"},
    {"id": "SDG_2", "sdg_number": 2, "name": "Zero Hunger", "description": "End hunger, achieve food security and improved nutrition and promote sustainable agriculture.", "color": "#dda63a"},
    {"id": "SDG_3", "sdg_number": 3, "name": "Good Health and Well-being", "description": "Ensure healthy lives and promote well-being for all at all ages.", "color": "#4c9f38"},
    {"id": "SDG_4", "sdg_number": 4, "name": "Quality Education", "description": "Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all.", "color": "#c5192d"},
    {"id": "SDG_5", "sdg_number": 5, "name": "Gender Equality", "description": "Achieve gender equality and empower all women and girls.", "color": "#ff3a21"},
    {"id": "SDG_6", "sdg_number": 6, "name": "Clean Water and Sanitation", "description": "Ensure availability and sustainable management of water and sanitation for all.", "color": "#26bde2"},
    {"id": "SDG_7", "sdg_number": 7, "name": "Affordable and Clean Energy", "description": "Ensure access to affordable, reliable, sustainable and modern energy for all.", "color": "#fcc30b"},
    {"id": "SDG_8", "sdg_number": 8, "name": "Decent Work and Economic Growth", "description": "Promote sustained, inclusive and sustainable economic growth, full and productive employment.", "color": "#a21942"},
    {"id": "SDG_9", "sdg_number": 9, "name": "Industry, Innovation and Infrastructure", "description": "Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation.", "color": "#fd6925"},
    {"id": "SDG_10", "sdg_number": 10, "name": "Reduced Inequalities", "description": "Reduce inequality within and among countries.", "color": "#dd1367"},
    {"id": "SDG_11", "sdg_number": 11, "name": "Sustainable Cities and Communities", "description": "Make cities and human settlements inclusive, safe, resilient and sustainable.", "color": "#fd9d24"},
    {"id": "SDG_12", "sdg_number": 12, "name": "Responsible Consumption and Production", "description": "Ensure sustainable consumption and production patterns.", "color": "#bf8b2e"},
    {"id": "SDG_13", "sdg_number": 13, "name": "Climate Action", "description": "Take urgent action to combat climate change and its impacts.", "color": "#3f7e44"},
    {"id": "SDG_14", "sdg_number": 14, "name": "Life Below Water", "description": "Conserve and sustainably use the oceans, seas and marine resources for sustainable development.", "color": "#0a97d9"},
    {"id": "SDG_15", "sdg_number": 15, "name": "Life on Land", "description": "Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests.", "color": "#56c02b"},
    {"id": "SDG_16", "sdg_number": 16, "name": "Peace, Justice and Strong Institutions", "description": "Promote peaceful and inclusive societies for sustainable development.", "color": "#00689d"},
    {"id": "SDG_17", "sdg_number": 17, "name": "Partnerships for the Goals", "description": "Strengthen the means of implementation and revitalize the Global Partnership for Sustainable Development.", "color": "#19486a"}
]

# 6. TIME-SERIES GENERATION (24 Months: Nov 2024 to Oct 2026 or Jan 2024 to Dec 2025)
# Using 2024-01 through 2025-12 (24 complete calendar months)
MONTHS = pd.date_range(start="2024-01-01", periods=24, freq="MS")

def generate_monthly_timeseries():
    electricity_rows = []
    water_rows = []
    waste_rows = []
    transport_rows = []

    # Seasonal temperature and occupancy factors for Mumbai
    # High cooling demand: April, May, June, October
    # Monsoons: June, July, August, September (lower solar, high rainwater)
    # Holidays: May (summer break), December (winter break)
    month_weights = {
        1: {"temp": 1.0, "occ": 1.0, "solar": 1.1, "rain": 0.02},
        2: {"temp": 1.05, "occ": 1.0, "solar": 1.15, "rain": 0.02},
        3: {"temp": 1.25, "occ": 1.05, "solar": 1.25, "rain": 0.05},
        4: {"temp": 1.45, "occ": 0.95, "solar": 1.3, "rain": 0.1},
        5: {"temp": 1.55, "occ": 0.40, "solar": 1.2, "rain": 0.2}, # Summer break
        6: {"temp": 1.35, "occ": 0.85, "solar": 0.65, "rain": 1.8}, # Monsoons start
        7: {"temp": 1.20, "occ": 1.05, "solar": 0.50, "rain": 2.5}, # Peak rain
        8: {"temp": 1.18, "occ": 1.05, "solar": 0.55, "rain": 2.2},
        9: {"temp": 1.22, "occ": 1.0, "solar": 0.75, "rain": 1.4},
        10: {"temp": 1.35, "occ": 1.0, "solar": 1.05, "rain": 0.4},
        11: {"temp": 1.15, "occ": 0.95, "solar": 1.1, "rain": 0.1},
        12: {"temp": 1.0, "occ": 0.70, "solar": 1.05, "rain": 0.02} # Winter break
    }

    # Building base monthly electricity consumption (kWh)
    bld_base_elec = {
        "BLD_ACA": 32000,
        "BLD_ACB": 29000,
        "BLD_LAB": 48000, # High computing load, server rooms
        "BLD_LIB": 14000,
        "BLD_AUD": 11000,
        "BLD_CAN": 16000,
        "BLD_ADM": 19000
    }

    # Building base monthly water consumption (litres)
    bld_base_water = {
        "BLD_ACA": 750000,
        "BLD_ACB": 680000,
        "BLD_LAB": 420000,
        "BLD_LIB": 240000,
        "BLD_AUD": 190000,
        "BLD_CAN": 1150000, # Kitchen, washing, drinking
        "BLD_ADM": 370000
    }

    # Solar rooftop installations:
    # Phase 1 is 220 kWp installed across ACA (80kW), ACB (70kW), LIB (30kW), ADM (40kW)
    # Average solar generation in Mumbai: ~120 kWh per kWp per month adjusted by seasonal sun
    solar_capacities = {"BLD_ACA": 80, "BLD_ACB": 70, "BLD_LAB": 0, "BLD_LIB": 30, "BLD_AUD": 0, "BLD_CAN": 0, "BLD_ADM": 40}

    grid_ef = 0.82 # kg CO2e / kWh

    for dt in MONTHS:
        year = dt.year
        month = dt.month
        date_str = dt.strftime("%Y-%m")
        w = month_weights[month]

        # Year-over-year efficiency trend (slight 3% efficiency improvement in 2025 due to IoT management)
        y_factor = 0.97 if year == 2025 else 1.0

        for bld in BUILDINGS:
            bid = bld["id"]
            # Electricity
            base_kwh = bld_base_elec[bid] * w["temp"] * (0.3 + 0.7 * w["occ"]) * y_factor
            noise = np.random.normal(1.0, 0.03) # 3% realistic random variation
            actual_total_kwh = round(base_kwh * noise, 2)

            sol_kw = solar_capacities[bid]
            if sol_kw > 0:
                sol_kwh = round(sol_kw * 125 * w["solar"] * np.random.normal(1.0, 0.04), 2)
            else:
                sol_kwh = 0.0

            grid_kwh = max(0.0, round(actual_total_kwh - sol_kwh, 2))
            elec_emissions = round(grid_kwh * grid_ef, 2)

            rec_id = f"ELEC_{bid}_{date_str}"
            electricity_rows.append({
                "id": rec_id,
                "institution_id": "VESIT",
                "building_id": bid,
                "year": year,
                "month": month,
                "date_str": date_str,
                "grid_kwh": grid_kwh,
                "solar_kwh": sol_kwh,
                "total_kwh": actual_total_kwh,
                "emissions_kgco2e": elec_emissions,
                "source_type": "SYNTHETIC"
            })

            # Water
            base_w = bld_base_water[bid] * (0.2 + 0.8 * w["occ"])
            w_noise = np.random.normal(1.0, 0.04)
            consumption_l = round(base_w * w_noise, 2)

            # Rainwater harvesting captured on roofs during monsoon
            roof_area = bld["area_m2"] * 0.4
            rain_harvested = round(roof_area * (w["rain"] * 180) * 0.75, 2) # runoff collection formula

            water_rows.append({
                "id": f"WAT_{bid}_{date_str}",
                "institution_id": "VESIT",
                "building_id": bid,
                "year": year,
                "month": month,
                "date_str": date_str,
                "consumption_litres": consumption_l,
                "rainwater_harvested_litres": rain_harvested,
                "source_type": "SYNTHETIC"
            })

        # Campus Aggregate Waste
        base_waste_kg = 5800 * (0.3 + 0.7 * w["occ"]) * np.random.normal(1.0, 0.03)
        # Year 2025 saw increased recycling due to composting & segregation drive
        rec_ratio = 0.42 if year == 2024 else 0.54
        comp_ratio = 0.28 if year == 2024 else 0.32
        non_rec_ratio = max(0.05, 1.0 - rec_ratio - comp_ratio)

        tot_kg = round(base_waste_kg, 2)
        rec_kg = round(tot_kg * rec_ratio, 2)
        comp_kg = round(tot_kg * comp_ratio, 2)
        non_rec_kg = round(tot_kg * non_rec_ratio, 2)

        waste_emissions = round((non_rec_kg * 1.25) + (comp_kg * 0.08) + (rec_kg * -0.65), 2)
        waste_rows.append({
            "id": f"WST_{date_str}",
            "institution_id": "VESIT",
            "year": year,
            "month": month,
            "date_str": date_str,
            "recyclable_kg": rec_kg,
            "non_recyclable_kg": non_rec_kg,
            "composted_kg": comp_kg,
            "total_kg": tot_kg,
            "emissions_kgco2e": waste_emissions,
            "source_type": "SYNTHETIC"
        })

        # Transportation Data (Trips & Passenger-km by mode)
        # 3,200 total campus population, ~22 working days / month
        work_days = 22 if month not in [5, 12] else (8 if month == 5 else 16)
        active_commuters = int(3200 * w["occ"])

        # Commute modal shares: Train 48%, Bus 22%, Two-Wheeler 16%, Car 6%, Walking/Cycling 8%
        # Average return trip distances: Train 28km, Bus 14km, Two-Wheeler 12km, Car 18km, Walking 2km
        modes = [
            ("TRAIN", 0.48, 28, 0.028),
            ("BUS", 0.22, 14, 0.054),
            ("TWO_WHEELER", 0.16, 12, 0.042),
            ("CAR", 0.06, 18, 0.175),
            ("WALKING_CYCLING", 0.08, 2, 0.0)
        ]

        for mode_name, share, avg_km, ef in modes:
            trips = int(active_commuters * share * work_days * 2) # to and fro
            pkm = round(trips * avg_km / 2.0, 2)
            emiss = round(pkm * ef, 2)

            transport_rows.append({
                "id": f"TRN_{mode_name}_{date_str}",
                "institution_id": "VESIT",
                "year": year,
                "month": month,
                "date_str": date_str,
                "mode": mode_name,
                "user_type": "CAMPUS_COMMUNITY",
                "passenger_km": pkm,
                "trips_count": trips,
                "emissions_kgco2e": emiss,
                "source_type": "SYNTHETIC"
            })

    return (
        pd.DataFrame(electricity_rows),
        pd.DataFrame(water_rows),
        pd.DataFrame(waste_rows),
        pd.DataFrame(transport_rows)
    )

# 7. GENERATE SYNTHETIC DOCUMENTS (22 Comprehensive, Grounded Documents)
DOCUMENTS = [
    {
        "document_id": "DOC_POL_001",
        "title": "VESIT Green Campus Sustainability Policy 2024-2040",
        "document_type": "INSTITUTIONAL_POLICY",
        "publication_date": "2024-01-15",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """VESIT GREEN CAMPUS SUSTAINABILITY POLICY (2024-2040)
Institution: Vivekananda Education Society's Institute of Technology (VESIT Green Campus), Mumbai.
Approved by: Governing Board & Campus Sustainability Taskforce.

1. VISION AND MANDATE
VESIT Green Campus commits to becoming an environmentally exemplary educational institution by achieving net-zero operational greenhouse gas emissions by December 31, 2040. The institution recognises the imperative of evidence-based environmental stewardship aligned with the United Nations Sustainable Development Goals (SDGs), specifically SDG 6 (Clean Water and Sanitation), SDG 7 (Affordable and Clean Energy), SDG 11 (Sustainable Cities and Communities), SDG 12 (Responsible Consumption and Production), and SDG 13 (Climate Action).

2. SCOPE AND BOUNDARIES
This policy governs all operational activities across the 32,500 m2 built-up campus in Chembur, Mumbai, encompassing Academic Block A, Academic Block B, Computer Laboratories, Library, Auditorium, Canteen, and the Administration Block. It applies to over 3,000 undergraduate and postgraduate students and 200 faculty and administrative staff.

3. STRATEGIC DECARBONISATION TARGETS
3.1 Target Net-Zero: Reduce annual campus carbon emissions from baseline 2,450,000 kg CO2e in 2024 to net zero by 2040.
3.2 Renewable Electricity: Attain a minimum of 50% renewable energy penetration by 2030 through rooftop solar photovoltaic generation and renewable wheeling agreements.
3.3 Zero Waste to Landfill: Divert 85% of solid waste from municipal landfills by 2028 through source segregation, decentralized aerobic composting, and formal recycling channels.
3.4 Water Conservation: Reduce municipal water demand by 30% relative to baseline by 2029 via integrated rainwater harvesting and greywater recycling.
3.5 Sustainable Commuting: Increase the share of public transit, electric mobility, cycling, and walking to 70% of total passenger-kilometres by 2027.

4. GOVERNANCE AND OVERSIGHT
The Campus Sustainability Taskforce, chaired by the Principal and comprising Department Heads from Computer Engineering, Information Technology, Electronics, and AI & Data Science, alongside student sustainability ambassadors, shall meet quarterly to audit metrics, review progress against target trajectories, and mandate corrective actions."""
    },
    {
        "document_id": "DOC_AUD_002",
        "title": "Comprehensive Campus Environmental and Carbon Audit Report 2024",
        "document_type": "AUDIT_REPORT",
        "publication_date": "2024-03-31",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """COMPREHENSIVE CAMPUS ENVIRONMENTAL AND CARBON AUDIT REPORT 2024
Lead Auditor: Energy and Carbon Advisory Bureau in coordination with VESIT Green Campus Committee.

1. EXECUTIVE SUMMARY
An exhaustive baseline audit for calendar year 2024 evaluated Scope 1, Scope 2, and core Scope 3 greenhouse gas emissions for VESIT Green Campus. The baseline institutional carbon footprint is measured at 2,450,000 kg CO2e (2,450 metric tonnes CO2e).

2. EMISSION SOURCE BREAKDOWN
- Scope 1 (Direct Emissions): Stationary diesel generator sets (DG) consumed 18,400 litres of diesel fuel for emergency power backup during grid interruptions, generating 49,312 kg CO2e (emission factor 2.68 kg CO2e/L).
- Scope 2 (Indirect Emissions from Purchased Electricity): Total annual grid electricity purchase reached 2,050,000 kWh from the Maharashtra regional grid. Applying the Central Electricity Authority (CEA) emission factor of 0.82 kg CO2e/kWh, grid electricity emissions equal 1,681,000 kg CO2e, representing 68.6% of the campus total.
- Scope 3 (Commuting, Waste, Water): Student and staff commuting generated 580,000 kg CO2e across suburban rail, municipal buses, two-wheelers, and private vehicles. Municipal waste sent to landfill contributed 115,000 kg CO2e. Embodied water pumping and treatment accounted for 24,688 kg CO2e.

3. BUILDING-LEVEL INTENSITY
The Computer Laboratories block exhibited the highest specific electricity intensity at 112 kWh/m2/year, driven by high-density compute labs, machine learning workstation racks, and 24/7 server room cooling. Academic Block A and Academic Block B registered 51 kWh/m2/year and 49 kWh/m2/year respectively. The Library demonstrated 54 kWh/m2/year.

4. AUDITOR RECOMMENDATIONS
Priority must be placed on expanding on-site solar generation beyond the existing 220 kWp arrays, installing variable refrigerant flow (VRF) cooling controls in the Computer Laboratories, and scaling food waste composting."""
    },
    {
        "document_id": "DOC_ENG_003",
        "title": "Rooftop Solar Photovoltaic Performance Assessment: Phase 1",
        "document_type": "TECHNICAL_REPORT",
        "publication_date": "2024-06-20",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """ROOFTOP SOLAR PHOTOVOLTAIC PERFORMANCE ASSESSMENT: PHASE 1
Authors: Department of Electronics & Telecommunication and Campus Facilities.

1. SYSTEM OVERVIEW
The Phase-1 Rooftop Solar PV installation comprises 220 kWp grid-interactive monocrystalline silicon arrays distributed as follows:
- Academic Block A: 80 kWp (200 modules of 400Wp each)
- Academic Block B: 70 kWp (175 modules)
- Administration Block: 40 kWp (100 modules)
- Library: 30 kWp (75 modules)
The system was commissioned under net-metering regulations with the local electricity distribution company (Adani Electricity / BEST).

2. GENERATION PERFORMANCE (JULY 2023 - JUNE 2024)
Over the 12-month evaluation cycle, the 220 kWp array yielded 312,400 kWh of clean solar electricity. Generation was highest during March, April, and May (averaging 31,500 kWh/month) and lowest during the monsoon months of July and August (averaging 14,200 kWh/month due to cloud cover and atmospheric attenuation).

3. ENVIRONMENTAL AND FINANCIAL IMPACT
The 312,400 kWh displaced equivalent grid purchases, yielding an annual reduction of 256,168 kg CO2e based on the regional emission factor of 0.82 kg CO2e/kWh. Campus electricity bills were reduced by approximately INR 34.3 lakhs, demonstrating an estimated simple payback period of 4.2 years against capital investment.

4. MAINTENANCE OBSERVATIONS
Bi-weekly panel cleaning is critical in Mumbai's dusty urban environment; unwashed arrays suffered a 12.4% soiling degradation penalty during dry winter months."""
    },
    {
        "document_id": "DOC_ENG_004",
        "title": "Phase-2 Solar Canopy and Energy Storage Feasibility Study",
        "document_type": "FEASIBILITY_STUDY",
        "publication_date": "2024-11-10",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """FEASIBILITY STUDY: PHASE-2 SOLAR CANOPY AND ENERGY STORAGE SYSTEM
Prepared for: VESIT Governing Board and Green Campus Committee.

1. PROJECT RATIONALE
To accelerate progress toward the 50% renewable electricity target by 2030 (TRG_RENEWABLE) and institutional carbon neutrality by 2040 (TRG_NET_ZERO), the campus must expand solar capacity beyond available building roofs.

2. PROPOSED ARCHITECTURE
The feasibility assessment recommends installing:
- 150 kWp elevated solar photovoltaic canopy over the central two-wheeler and four-wheeler parking zones.
- 50 kWp bifacial PV modules over the Auditorium perimeter roof.
- 100 kWh lithium iron phosphate (LiFePO4) Battery Energy Storage System (BESS) integrated with an energy management inverter.

3. PROJECTED OUTPUT AND AVOIDED EMISSIONS
The combined 200 kWp addition will generate an estimated 284,000 kWh annually. At 0.82 kg CO2e/kWh grid intensity, the avoided emissions will equal 232,880 kg CO2e annually. When added to Phase 1, total campus solar generation will reach nearly 600,000 kWh/year, meeting approximately 28% of total campus electricity demand.

4. PEAK SHAVING AND DIESEL GENERATOR ABATEMENT
The 100 kWh battery storage allows peak load shaving between 18:00 and 21:00 during evening academic sessions, and provides instantaneous uninterruptible backup, reducing annual diesel generator run-hours by 45 hours and preventing 2,400 litres of diesel combustion (6,432 kg CO2e avoided)."""
    },
    {
        "document_id": "DOC_WAT_005",
        "title": "Campus Water Audit and Conservation Strategy Report 2024",
        "document_type": "AUDIT_REPORT",
        "publication_date": "2024-05-18",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """CAMPUS WATER AUDIT AND CONSERVATION STRATEGY REPORT 2024
Audited by: Environmental Cell and Civil Infrastructure Division, VESIT Green Campus.

1. BASELINE WATER FOOTPRINT
In 2024, total municipal piped water consumption stood at 48,000,000 litres (48,000 m3). Daily consumption averages approximately 131,500 litres during active semester days.

2. CONSUMPTION DISTRIBUTION
- Canteen and Catering: 28% (36,800 L/day) - food preparation, utensil washing, and drinking water purification reject.
- Restrooms and Sanitation: 46% (60,500 L/day) - dual-flush toilets, urinals, and handwashing basins across Academic Block A, Academic Block B, and Computer Laboratories.
- Landscape and Garden Irrigation: 18% (23,600 L/day) - maintenance of campus lawns and tree groves.
- Laboratory and Cleaning: 8% (10,600 L/day).

3. RAINWATER HARVESTING SYSTEM PERFORMANCE
The campus integrated rainwater harvesting system captures surface runoff from 18,000 m2 of terrace roofs across Academic Block A, B, and the Library. Three underground recharge filtration cisterns with a combined capacity of 450,000 litres harvested 12,400,000 litres during the 2024 monsoon season (June to September). Harvested water is routed through sand-gravel bed filters and used for toilet flushing and cooling tower replenishment.

4. RECOMMENDATIONS AND TARGETS
Achieving Target TRG_WATER_NEUTRAL (30% reduction by 2029) requires:
- Retrofitting 140 washroom faucets with aerators, reducing tap flow from 9 L/min to 3.5 L/min (saving 3,500,000 L/yr).
- Upgrading the existing canteen greywater reed-bed biofilter to recycle 15,000 litres daily for landscape irrigation."""
    },
    {
        "document_id": "DOC_WST_006",
        "title": "Solid Waste Management and Decentralized Composting Audit 2024",
        "document_type": "AUDIT_REPORT",
        "publication_date": "2024-08-12",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """SOLID WASTE MANAGEMENT AND DECENTRALIZED COMPOSTING AUDIT 2024
VESIT Green Campus Sustainable Operations Review.

1. WASTE GENERATION PROFILE
Total municipal solid waste generated across the institution in 2024 was 68,400 kg (68.4 metric tonnes).
Composition analysis reveals:
- Organic and Kitchen Waste (Canteen and dining): 42% (28,728 kg)
- Recyclable Paper, Cardboard, and Packaging: 33% (22,572 kg)
- Plastic bottles, wrappers, and containers: 14% (9,576 kg)
- Electronic Waste and Laboratory Hardware: 3% (2,052 kg)
- Non-recyclable Inert Waste: 8% (5,472 kg)

2. DECENTRALIZED TREATMENT INITIATIVE
Under initiative INIT_BIOGAS_CANTEEN, a 250 kg/day anaerobic biomethanation plant coupled with twin 500-litre aerobic composting tumblers was commissioned adjacent to the Canteen.
In 2024, the facility successfully processed 19,200 kg of food scraps, preventing uncontrolled anaerobic decomposition at Deonar landfill.
Avoided landfill emissions are calculated at 1.25 kg CO2e/kg waste, preventing 24,000 kg CO2e, while producing 1,400 kg of enriched bio-manure utilized across campus botanical beds.

3. DRY RECYCLING AND E-WASTE PARTNERSHIPS
VESIT partners with authorized e-waste recycler Greenscape Solutions for responsible dismantling of obsolete computer motherboards, CRTs, and lithium batteries in compliance with E-Waste Management Rules 2022. In 2024, 1,850 kg of electronic scrap was recovered, avoiding toxic heavy metal contamination and supporting SDG 12."""
    },
    {
        "document_id": "DOC_TRN_007",
        "title": "Comprehensive Campus Commuter Mobility and Transportation Survey 2024",
        "document_type": "SURVEY_REPORT",
        "publication_date": "2024-04-15",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """CAMPUS COMMUTER MOBILITY AND TRANSPORTATION SURVEY 2024
Conducted by: Department of Artificial Intelligence & Data Science and Student Council.
Sample Size: 2,140 student respondents and 172 faculty and staff members.

1. MODAL SPLIT
Survey analysis establishes the following commuting split:
- Suburban Rail (Harbour & Central Line): 48% of commuter trips (avg one-way commute: 14 km).
- BEST Municipal Transit Buses: 22% (avg one-way: 7 km).
- Two-Wheelers (Petrol motorcycles and scooters): 16% (avg one-way: 6 km).
- Private Passenger Cars (Single-occupant and carpool): 6% (avg one-way: 9 km).
- Walking and Cycling (Locals within 2 km radius): 8%.

2. EMISSIONS ATTRIBUTION
Transportation accounts for approximately 580,000 kg CO2e annually (23.7% of total campus footprint). Although private passenger cars account for only 6% of trips, they generate 28.5% of total commuting emissions due to high specific carbon intensity (0.175 kg CO2e/pkm). Two-wheelers contribute 19.3% of transport emissions. Suburban rail and municipal buses account for the majority of passenger-kilometres while maintaining low specific carbon intensity (0.028 and 0.054 kg CO2e/pkm respectively).

3. INITIATIVE: CAMPUS ELECTRIC FEEDER SHUTTLE
Initiative INIT_ELECTRIC_SHUTTLE operates two 14-seater electric shuttle vans between Chembur and Kurla railway stations and the campus gate. Since launch in January 2024, the shuttle has completed over 1,800 trips, carrying 21,500 passenger-trips and displacing 36,000 kg CO2e of auto-rickshaw and private vehicle journeys."""
    },
    {
        "document_id": "DOC_IOT_008",
        "title": "IoT Smart Energy Metering and Real-Time Building Telemetry Report",
        "document_type": "TECHNICAL_REPORT",
        "publication_date": "2024-10-05",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """IOT SMART ENERGY METERING AND REAL-TIME TELEMETRY REPORT
Department: AI & Data Science and Computer Engineering.
Project Code: INIT_IOT_ENERGY_MGT.

1. ARCHITECTURE AND DEPLOYMENT
In March 2024, 45 Modbus-RS485 smart multi-function digital energy meters were deployed across all main electrical distribution boards (MDBs) and sub-distribution boards (SDBs) in seven campus buildings.
Telemetry is aggregated by five edge gateways using MQTT and transmitted over campus Wi-Fi to a local time-series monitoring server.

2. INSIGHTS AND ANOMALY DETECTION
Real-time monitoring revealed critical operational inefficiencies:
- Computer Laboratories Base Load: Standby power consumption during non-operational nighttime hours (22:00 to 06:00) averaged 24 kW due to idling desktop power supplies and server room air conditioners operating at non-optimal setpoints (19°C instead of 24°C).
- Phantom Loads in Auditorium: Sound consoles and stage lighting transformers consumed 3.8 kW in quiescent mode.
- Academic Block Peak Concurrency: Peak power demand of 410 kW occurs between 11:30 and 14:00 on weekdays when laboratory sessions, lecture air conditioning, and canteen catering run simultaneously.

3. OPTIMIZATION ACTIONS TAKEN
Automated relay shutdowns for computer lab clusters and adjusting server room HVAC setpoints to 24°C resulted in a measured 4.8% reduction in monthly electricity consumption, saving approximately 98,000 kWh annually (80,360 kg CO2e avoided)."""
    },
    {
        "document_id": "DOC_SDG_009",
        "title": "VESIT Strategic SDG Alignment and Action Framework 2024-2030",
        "document_type": "STRATEGIC_PLAN",
        "publication_date": "2024-02-01",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """VESIT STRATEGIC SDG ALIGNMENT AND ACTION FRAMEWORK (2024-2030)
Document Ref: VESIT/SDG/2024/V1.

1. INSTITUTIONAL COMMITMENT
VESIT Green Campus formally anchors its sustainability strategy to the United Nations 2030 Agenda for Sustainable Development. While all 17 SDGs are recognized, the college prioritizes six core goals where campus operations and academic research exert direct, measurable impact.

2. CORE SDG MAPPINGS AND INITIATIVES
- SDG 6: Clean Water and Sanitation
  - Initiative: Integrated Rainwater Harvesting & Filtration Cisterns (INIT_RWH_SYSTEM).
  - Target: 30% reduction in municipal water demand by 2029 (TRG_WATER_NEUTRAL).
  - Outcome: 12.4 million litres harvested annually; zero untreated effluent discharge.

- SDG 7: Affordable and Clean Energy
  - Initiative: Phase-1 (220 kWp) and Phase-2 (200 kWp) Rooftop Solar Projects (INIT_SOLAR_PH1, INIT_SOLAR_PH2).
  - Target: 50% renewable electricity share by 2030 (TRG_RENEWABLE).
  - Outcome: Over 312,000 kWh solar generated annually in Phase 1, expanding to 600,000 kWh in Phase 2.

- SDG 11: Sustainable Cities and Communities
  - Initiatives: Electric Campus Feeder Transit (INIT_ELECTRIC_SHUTTLE) and Miyawaki Urban Forest (INIT_BIODIVERSITY_ZONE).
  - Target: 70% low-carbon commuting share by 2027 (TRG_GREEN_COMMUTE).

- SDG 12: Responsible Consumption and Production
  - Initiative: Canteen Food Waste Digester and Composting (INIT_BIOGAS_CANTEEN) and E-Waste Disposal protocol.
  - Target: 85% diversion from municipal landfills by 2028 (TRG_ZERO_WASTE).

- SDG 13: Climate Action
  - Target: Institutional Carbon Neutrality by 2040 (TRG_NET_ZERO).
  - Outcome: Tracking through the interactive College Climate Clock and evidence-grounded GraphRAG platform.

- SDG 15: Life on Land
  - Initiative: Miyawaki Urban Native Afforestation (INIT_BIODIVERSITY_ZONE) preserving 1,200 native flora specimens."""
    },
    {
        "document_id": "DOC_BIO_010",
        "title": "Miyawaki Native Afforestation and Campus Carbon Sequestration Report",
        "document_type": "PROJECT_REPORT",
        "publication_date": "2024-07-10",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """MIYAWAKI NATIVE AFFORESTATION AND CAMPUS CARBON SEQUESTRATION REPORT
Project: INIT_BIODIVERSITY_ZONE
Supervised by: Environmental Cell and Nature Club.

1. PROJECT BACKGROUND
In June 2023, VESIT Green Campus dedicated a 600 m2 peripheral plot behind the Auditorium to high-density afforestation utilizing the Japanese Miyawaki technique. 1,200 saplings across 32 indigenous tree and shrub species (including Neem, Peepal, Jamun, Karanj, and Bamboo) were planted with organic soil conditioning.

2. SURVIVAL RATE AND CANOPY DEVELOPMENT
At the 12-month audit in June 2024, the plantation recorded a 94.2% survival rate. The dense canopy has reached an average height of 3.8 metres, creating a multi-layered urban micro-habitat attracting 24 bird species and diverse pollinators.

3. ESTIMATED CARBON SEQUESTRATION
Based on standard allometric biomass equations for tropical urban afforestation:
- Current annual sequestration: approximately 14,000 kg CO2e/year.
- Projected maturity sequestration (at 10 years): 38,000 kg CO2e/year.
In addition, thermal infrared sensor measurements demonstrated a localized microclimate cooling effect of 2.3°C compared to adjacent paved asphalt parking areas, mitigating the campus urban heat island phenomenon."""
    },
    {
        "document_id": "DOC_BLD_011",
        "title": "Building Energy Benchmark: Computer Laboratories High-Density Compute Audit",
        "document_type": "BENCHMARK_REPORT",
        "publication_date": "2024-09-15",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """BUILDING ENERGY BENCHMARK: COMPUTER LABORATORIES HIGH-DENSITY COMPUTE AUDIT
Facility: Computer Laboratories Building (BLD_LAB)
Area: 5,200 m2 | Dedicated Labs: 16 Computer Labs, 2 Server Rooms, 1 AI Research Center.

1. ENERGY CONSUMPTION ANALYSIS
The Computer Laboratories building consumed 582,400 kWh in 2024, accounting for 28.4% of total campus electricity usage despite occupying only 16% of total campus floor area.
Specific energy consumption reached 112 kWh/m2/year.

2. SUB-SYSTEM POWER BREAKDOWN
- Computing Workstations & Lab Equipment: 44% (256,256 kWh)
- Air Conditioning and Climate Control: 41% (238,784 kWh)
- Lighting (LED luminaires): 9% (52,416 kWh)
- Auxiliary Equipment and UPS losses: 6% (34,944 kWh)

3. OPPORTUNITIES FOR EFFICIENCY
- Power Usage Effectiveness (PUE) in the primary AI cluster server room is currently 1.74, indicating significant cooling inefficiency. Implementing aisle containment and variable-speed inverter chillers can reduce PUE to 1.32.
- Installing smart master switch relays for lab workstation benches to prevent overnight phantom draws of idle PCs will conserve an estimated 32,000 kWh/year (26,240 kg CO2e)."""
    },
    {
        "document_id": "DOC_BLD_012",
        "title": "Facility Sustainability Review: Canteen and Dining Hall Operations",
        "document_type": "FACILITY_REPORT",
        "publication_date": "2024-08-28",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """FACILITY SUSTAINABILITY REVIEW: CANTEEN AND DINING HALL OPERATIONS
Facility: Canteen Building (BLD_CAN) | Daily Footfall: ~2,200 meals and snacks.

1. OPERATIONAL OVERVIEW
The Canteen is the campus's primary point of solid food waste generation and high daily water demand. Daily operations consume an average of 38,000 litres of water and produce 120 kg of wet kitchen waste.

2. BIOGAS CONVERSION PROGRESS
The anaerobic biomethanation plant installed under INIT_BIOGAS_CANTEEN utilizes wet kitchen peelings, leftover rice, and vegetable trimmings. The system generates 12 m3 of methane-rich biogas daily, piped directly to the canteen commercial kitchen to fuel two low-pressure commercial burners. This displaces 14 commercial LPG cylinders (19 kg each) per month, reducing operating costs by INR 25,000 monthly and abating 7,200 kg CO2e annually.

3. SINGLE-USE PLASTIC ELIMINATION
In compliance with Maharashtra Plastic Waste Management regulations, the Canteen successfully transitioned 100% of beverage and food containers to stainless steel reusable cutlery and biodegradable bagasse containers. Sale of packaged single-use PET water bottles under 500ml was replaced with three commercial chilled RO refill kiosks."""
    },
    {
        "document_id": "DOC_BLD_013",
        "title": "Facility Sustainability Review: Library Energy and Daylighting Optimization",
        "document_type": "FACILITY_REPORT",
        "publication_date": "2024-04-02",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """FACILITY SUSTAINABILITY REVIEW: LIBRARY ENERGY AND DAYLIGHTING OPTIMIZATION
Facility: Library Building (BLD_LIB) | Built-Up Area: 3,100 m2.

1. LIGHTING AND DAYLIGHTING ASSESSMENT
The Library building features an east-facing glazed facade providing high natural daylighting throughout morning hours. In October 2023, conventional fluorescent tube fittings were completely replaced with 18W daylight-harvesting dimmable LED fixtures. The smart lighting system dims interior rows automatically when ambient sunlight surpasses 400 lux.

2. SOLAR GENERATION INTEGRATION
A 30 kWp rooftop solar PV array mounted on the Library roof generated 42,600 kWh in 2024. The Library's total electricity consumption for the year was 168,200 kWh, meaning on-site solar directly supplied 25.3% of the building's electrical demand.

3. DIGITALIZATION AND PAPER CONSERVATION
Through the Library's e-repository portal and digital subscription drive, institutional paper consumption for journal printing decreased by 65% since 2022, saving approximately 4.2 tonnes of paper and avoiding 5,880 kg CO2e embodied emissions."""
    },
    {
        "document_id": "DOC_BLD_014",
        "title": "Facility Sustainability Review: Auditorium HVAC and Event Load Management",
        "document_type": "FACILITY_REPORT",
        "publication_date": "2024-10-18",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """FACILITY SUSTAINABILITY REVIEW: AUDITORIUM HVAC AND EVENT LOAD MANAGEMENT
Facility: Auditorium (BLD_AUD) | Seating Capacity: 800 seats | Area: 2,800 m2.

1. OCCUPANCY PROFILE AND LOAD DYNAMICS
The Auditorium represents an intermittent high-demand electrical load. During annual technical festivals, cultural symposiums, and convocation ceremonies, instantaneous cooling load reaches 140 TR (tons of refrigeration). However, the building remains largely unoccupied for approximately 65% of calendar weekdays.

2. ENERGY INTENSITY AND MANAGEMENT
Annual electricity consumption was 134,200 kWh in 2024. Prior to the installation of IoT sub-metering, chilled water pumps and ventilation blowers were frequently left operational during rehearsals and setup days.
Implementing an automated occupancy-based scheduling protocol has curbed wasted idle consumption by 22,000 kWh annually (18,040 kg CO2e).

3. PROPOSED ROOF SOLAR RETROFIT
The Auditorium possesses an unobstructed curved roof area of 1,200 m2. Phase 2 solar planning incorporates a 50 kWp lightweight bifacial PV installation expected to generate 71,000 kWh annually."""
    },
    {
        "document_id": "DOC_TRN_015",
        "title": "Campus Commuting Decarbonisation: Electric Shuttle Route Optimization Study",
        "document_type": "MOBILITY_REPORT",
        "publication_date": "2024-11-25",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """CAMPUS COMMUTING DECARBONISATION: ELECTRIC SHUTTLE ROUTE OPTIMIZATION STUDY
Project: INIT_ELECTRIC_SHUTTLE | Operators: Administration and Student Mobility Volunteers.

1. VEHICLE PERFORMANCE SPECIFICATIONS
Two 14-passenger Mahindra Supro EV vans equipped with 48V / 20 kWh lithium-ion battery packs operate continuously between 07:45 and 10:30, and 16:00 and 18:30 on academic working days. Charging takes place on-campus during off-peak hours (11:00 to 15:00) utilizing solar electricity from the Academic Block A rooftop array.

2. SERVICE METRICS (JANUARY - OCTOBER 2024)
- Total Kilometres Traveled: 24,800 km.
- Passenger-Trips Delivered: 38,400 student and staff journeys.
- Average Fleet Energy Consumption: 0.18 kWh/km.
- Grid Electricity Consumed: 4,464 kWh (supplied predominantly by on-site solar).

3. EMISSION SAVINGS CALCULATION
Displaced trips primarily substitute shared three-wheeler auto-rickshaws (CNG/Petrol factor: 0.082 kg CO2e/pkm) and private two-wheelers (0.042 kg CO2e/pkm). Net avoided emissions for the 10-month evaluation period total 31,200 kg CO2e. Expanding the fleet with two additional 24-seater electric mini-buses will triple commuter ridership and eliminate 95,000 kg CO2e annually."""
    },
    {
        "document_id": "DOC_WAT_016",
        "title": "Rainwater Harvesting Hydrological Yield and Recharge Assessment 2024",
        "document_type": "TECHNICAL_REPORT",
        "publication_date": "2024-10-12",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """RAINWATER HARVESTING HYDROLOGICAL YIELD AND RECHARGE ASSESSMENT 2024
Hydrological Consultant: AquaTerra Environmental for VESIT Green Campus.

1. CATCHMENT CHARACTERISTICS
- Rooftop Catchment (Academic Blocks A, B, and Library): 18,000 m2 reinforced concrete terrace with food-grade epoxy waterproof lining.
- Paved Walkway Catchment: 4,200 m2 interlocking permeable concrete pavers.
- Mean Annual Monsoon Rainfall (Mumbai suburbs): 2,420 mm.

2. SYSTEM YIELD
Applying a conservative runoff coefficient of 0.85 for concrete terraces and 0.70 for permeable paved walkways, total harvestable runoff potential is estimated at 39,200,000 litres.
Due to storage cistern constraints (total active volume: 450,000 litres), 12,400,000 litres were directly captured, filtered through rapid sand-gravel beds, and stored for plumbing usage. The remaining excess runoff was diverted to four deep injection borewells providing groundwater recharge to the local aquifer table.

3. QUALITY TESTING
Laboratory testing of harvested water in August 2024 confirmed pH 7.2, total dissolved solids (TDS) of 84 ppm, and zero coliform contamination, meeting non-potable institutional recycling criteria (BIS 10500 standards)."""
    },
    {
        "document_id": "DOC_CLM_017",
        "title": "VESIT Climate Action Roadmap 2024-2040: Net-Zero Trajectory Modeling",
        "document_type": "STRATEGIC_PLAN",
        "publication_date": "2024-03-01",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """VESIT CLIMATE ACTION ROADMAP (2024-2040): NET-ZERO TRAJECTORY MODELING
Author: Campus Decarbonization Working Group.

1. BASELINE REFERENCE (YEAR 2024)
Total Institutional Carbon Emissions: E0 = 2,450,000 kg CO2e/year.
Scope 1: 49,312 kg CO2e (2.0%)
Scope 2: 1,681,000 kg CO2e (68.6%)
Scope 3: 719,688 kg CO2e (29.4%)

2. MATHEMATICAL DECARBONIZATION PATHWAYS
To attain net-zero by the target date of December 31, 2040 (t_target = 2040, horizon = 16 years):

Model A: Linear Reduction Trajectory
E(t) = E0 - r * (t - t0)
Required annual reduction: r = 2,450,000 / 16 = 153,125 kg CO2e/year.

Model B: Compound Annual Reduction Trajectory
E(t) = E0 * (1 - p)^(t - t0)
Target residual emissions by 2040: < 2% of baseline (< 49,000 kg CO2e).
Required compound reduction factor: p = 22.8% per annum if relying solely on operational interventions, or p = 12.5% per annum when coupled with high-integrity local tree carbon sequestration.

3. PHASED INTERVENTIONS SCHEDULE
- Phase I (2024-2027): Commissioning Phase-2 Solar (200 kWp), fleet electrification of staff buses, full canteen organic composting, campus LED conversion. Target reduction: 480,000 kg CO2e/yr.
- Phase II (2028-2032): Off-site open access green energy wheeling (1.2 MW solar wind hybrid), heat pump water heaters, rainwater cistern expansion. Target reduction: 1,150,000 kg CO2e/yr.
- Phase III (2033-2040): High-efficiency chiller plant upgrades, AI predictive energy optimization, zero-emission supply chain procurement, residual sequestration via urban forest mature growth. Remaining emissions: 0 kg CO2e."""
    },
    {
        "document_id": "DOC_WST_018",
        "title": "Campus Circular Economy and Zero-Waste Policy Guidelines",
        "document_type": "INSTITUTIONAL_POLICY",
        "publication_date": "2024-09-01",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """CAMPUS CIRCULAR ECONOMY AND ZERO-WASTE POLICY GUIDELINES
Authority: VESIT Campus Facilities and Environmental Cell.
Policy Target: TRG_ZERO_WASTE (85% landfill diversion by 2028).

1. MANDATORY SOURCE SEGREGATION
All academic blocks, administrative offices, and common corridors must maintain four-stream color-coded recycling receptacles:
- Green Bin: Organic, biodegradable food and horticulture waste.
- Blue Bin: Clean dry paper, notebooks, textbooks, cardboard cartons.
- Red Bin: Rigid plastics, beverage cans, aluminum foil packaging.
- Black Bin: Domestic sanitary and non-recyclable inert waste.

2. CENTRAL COMPOSTING AND BIOGAS FACILITY
Organic waste collected from the Canteen and green horticulture clippings from campus gardens are banned from municipal garbage disposal trucks. All wet organics must be delivered to the Biogas plant and twin aerobic compost tumblers behind the Canteen.

3. RECYCLING AND CIRCULAR PROCUREMENT
Paper procurement must mandate a minimum of 70% post-consumer recycled content for all academic examination books and administrative stationery. Single-use plastic cutlery, disposable plastic water bottles, and styrofoam food containers are strictly prohibited from campus premises."""
    },
    {
        "document_id": "DOC_ENG_019",
        "title": "HVAC and Chiller Plant Energy Efficiency Audit across Academic Blocks",
        "document_type": "AUDIT_REPORT",
        "publication_date": "2024-07-22",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """HVAC AND CHILLER PLANT ENERGY EFFICIENCY AUDIT ACROSS ACADEMIC BLOCKS
Audited by: Thermal Engineering Research Lab & External BEE Accredited Energy Auditors.

1. SCOPE OF COOLING AUDIT
Air conditioning and ventilation account for approximately 38% of total annual campus electricity consumption. The audit evaluated split AC units, VRF systems, and packaged ductable units across Academic Block A, Block B, and Computer Laboratories.

2. KEY FINDINGS
- Operating Setpoints: Over 62% of faculty cabins and classroom ACs were set to 19°C - 20°C, significantly below the Bureau of Energy Efficiency (BEE) recommended default comfort setpoint of 24°C. Each 1°C increase in AC setpoint yields a documented 6% electricity saving.
- Refrigerant Leakage and Condenser Fouling: 14 split units in Academic Block A exhibited condenser dust fouling resulting in a 18% coefficient of performance (COP) penalty.

3. MANDATED ACTION PLAN
- Enforce mandatory thermostat lock at 24°C across all administrative and academic air conditioning units starting August 1, 2024.
- Implement quarterly coil cleaning schedules.
- Transition aging R-22 refrigerant systems to low-GWP refrigerants (R-32 or R-290).
Total projected annual energy saving from cooling setpoint optimization is 142,000 kWh, preventing 116,440 kg CO2e."""
    },
    {
        "document_id": "DOC_ADM_020",
        "title": "Green Campus Annual Progress Report 2024: Key Performance Indicators",
        "document_type": "ANNUAL_REPORT",
        "publication_date": "2024-12-15",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """GREEN CAMPUS ANNUAL PROGRESS REPORT 2024: KEY PERFORMANCE INDICATORS
Vivekananda Education Society's Institute of Technology (VESIT Green Campus), Mumbai.

1. 2024 AT A GLANCE
- Overall Carbon Footprint: 2,450,000 kg CO2e (Baseline Year).
- Total Electricity Consumed: 2,362,400 kWh (Grid: 2,050,000 kWh | Solar PV: 312,400 kWh).
- Renewable Energy Penetration: 13.2% of total electricity demand.
- Total Water Consumption: 48,000,000 litres.
- Rainwater Harvested: 12,400,000 litres (replacing 25.8% of freshwater needs).
- Total Solid Waste Generated: 68,400 kg.
- Landfill Diversion Rate (Recycling + Composting): 48.2% achieved.
- Clean Commuting Mode Share: 52% across suburban rail, electric shuttle, and non-motorized transport.

2. PROGRESS AGAINST SUSTAINABILITY TARGETS
- TRG_NET_ZERO (Net Zero by 2040): In progress. Baseline established; linear trajectory requires 153,125 kg CO2e annual abatement.
- TRG_RENEWABLE (50% Solar by 2030): In progress. Phase 1 active; Phase 2 proposal awaiting board clearance.
- TRG_ZERO_WASTE (85% Diversion by 2028): In progress. Composting plant active; single-use plastics banned.
- TRG_WATER_NEUTRAL (30% Reduction by 2029): In progress. Aerator retrofit initiated.
- TRG_GREEN_COMMUTE (70% Low Carbon by 2027): In progress. EV shuttle operational with 38,400 passenger-trips.

3. RESEARCH AND COMMUNITY ENGAGEMENT
The institution's AI & Data Science and Computer Engineering departments launched the EcoClock AI initiative: a GraphRAG-powered evidence-grounded monitoring and climate countdown engine to provide public transparency and decision-support for campus climate action."""
    },
    {
        "document_id": "DOC_RES_021",
        "title": "GraphRAG for Educational Campus Decarbonization: Methodology and Architecture",
        "document_type": "RESEARCH_PAPER",
        "publication_date": "2024-11-01",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """GRAPHRAG FOR EDUCATIONAL CAMPUS DECARBONIZATION: METHODOLOGY AND ARCHITECTURE
Authors: AI & Data Science Department, VESIT Green Campus.

1. ABSTRACT
Conventional vector-based Retrieval-Augmented Generation (RAG) retrieves unstructured text fragments based on cosine similarity, often failing to capture multi-hop relational dependencies between institutional sustainability policies, quantitative utility telemetry, and global sustainability frameworks such as the UN SDGs. This paper presents EcoClock AI, a hybrid GraphRAG architecture combining persistent Neo4j property graphs, local SentenceTransformers embeddings, and a locally hosted Mistral LLM via Ollama.

2. GRAPH SCHEMA AND ONTOLOGY
The knowledge graph models institutional decarbonization across 16 node classes (Institution, Building, Department, Resource, EnergySource, Emission, Activity, SustainabilityInitiative, SustainabilityTarget, SDG, Document, Chunk, Measurement, EmissionFactor, ClimateScenario, Location) and 17 directed relationship classes preserving evidence provenance (chunk ID, document ID, extraction method, confidence, and verification status).

3. HYBRID RETRIEVAL MECHANISM
Queries are resolved through a dual-channel retrieval mechanism:
- Vector similarity retrieves relevant narrative chunks with high semantic coverage.
- Graph traversal identifies entity neighborhoods, multi-hop paths connecting campus activities to target indicators, and UN SDG mappings.
A fusion ranking engine scores retrieved evidence to ground Mistral answer generation, preventing ungrounded hallucination."""
    },
    {
        "document_id": "DOC_SMR_022",
        "title": "Comprehensive Summary: Campus Infrastructure, Buildings, and Resource Baseline",
        "document_type": "REFERENCE_GUIDE",
        "publication_date": "2024-12-20",
        "institution_id": "VESIT",
        "source_type": "SYNTHETIC",
        "content": """CAMPUS INFRASTRUCTURE, BUILDINGS, AND RESOURCE BASELINE REFERENCE
Institution: VESIT Green Campus, Chembur, Mumbai.

1. CAMPUS INFRASTRUCTURE SUMMARY
- Total Buildings: 7 key blocks (Academic Block A, Academic Block B, Computer Laboratories, Library, Auditorium, Canteen, Administration Block).
- Departments: Computer Engineering (ACA), Information Technology (ACB), Electronics & Telecommunication (ACA), AI & Data Science (LAB), Administration (ADM).
- Student Population: 3,000 | Faculty & Staff: 200 | Total Campus Community: 3,200.
- Total Built-Up Area: 32,500 m2.

2. KEY OPERATIONAL METRICS
- Grid Electricity: Maharashtra State Grid (CEA factor: 0.82 kg CO2e/kWh).
- Installed Rooftop Solar: 220 kWp (Phase 1 across ACA, ACB, LIB, ADM) generating ~312,000 kWh/year.
- Diesel Generator Backup: 18,400 litres consumed in 2024 (IPCC factor: 2.68 kg CO2e/L).
- Annual Municipal Water Consumption: 48,000,000 litres.
- Annual Rainwater Harvested: 12,400,000 litres.
- Annual Solid Waste: 68,400 kg (Recycling rate: 48.2% in 2024).
- Total Baseline Emissions: 2,450,000 kg CO2e/year (2,450 tonnes CO2e).
- Declared Net-Zero Target Date: December 31, 2040."""
    }
]

def main():
    print("Generating VESIT Green Campus Synthetic Dataset...")

    # Save institutions
    with open(SYNTHETIC_DIR / "institution.json", "w", encoding="utf-8") as f:
        json.dump(INSTITUTION, f, indent=2)

    # Save buildings
    df_bld = pd.DataFrame(BUILDINGS)
    df_bld.to_csv(SYNTHETIC_DIR / "buildings.csv", index=False)

    # Save departments
    df_dep = pd.DataFrame(DEPARTMENTS)
    df_dep.to_csv(SYNTHETIC_DIR / "departments.csv", index=False)

    # Save emission factors
    df_ef = pd.DataFrame(EMISSION_FACTORS)
    df_ef.to_csv(SYNTHETIC_DIR / "emission_factors.csv", index=False)

    # Save targets
    df_trg = pd.DataFrame(TARGETS)
    df_trg.to_csv(SYNTHETIC_DIR / "sustainability_targets.csv", index=False)

    # Save initiatives
    with open(SYNTHETIC_DIR / "sustainability_initiatives.json", "w", encoding="utf-8") as f:
        json.dump(INITIATIVES, f, indent=2)

    # Save SDGs
    with open(SYNTHETIC_DIR / "sdgs.json", "w", encoding="utf-8") as f:
        json.dump(SDGS, f, indent=2)

    # Generate and save timeseries
    df_elec, df_wat, df_wst, df_trn = generate_monthly_timeseries()
    df_elec.to_csv(SYNTHETIC_DIR / "electricity_records.csv", index=False)
    df_wat.to_csv(SYNTHETIC_DIR / "water_records.csv", index=False)
    df_wst.to_csv(SYNTHETIC_DIR / "waste_records.csv", index=False)
    df_trn.to_csv(SYNTHETIC_DIR / "transport_records.csv", index=False)

    # Save documents as JSON and JSONL
    with open(SYNTHETIC_DIR / "documents.json", "w", encoding="utf-8") as f:
        json.dump(DOCUMENTS, f, indent=2)

    with open(SYNTHETIC_DIR / "documents.jsonl", "w", encoding="utf-8") as f:
        for doc in DOCUMENTS:
            f.write(json.dumps(doc) + "\n")

    print(f"Generated {len(BUILDINGS)} buildings, {len(DEPARTMENTS)} departments, {len(EMISSION_FACTORS)} emission factors.")
    print(f"Generated {len(df_elec)} electricity records, {len(df_wat)} water records, {len(df_wst)} waste records, {len(df_trn)} transport records.")
    print(f"Generated {len(DOCUMENTS)} comprehensive synthetic sustainability documents.")

    # Populate SQLite database directly
    from app.database.relational_db import SessionLocal, init_db
    from app.database.schema import (
        DocumentModel, ChunkModel, ElectricityRecord, WaterRecord,
        WasteRecord, TransportRecord, SustainabilityInitiativeModel,
        SustainabilityTargetModel, EmissionFactorModel, SDGModel
    )

    init_db()
    db = SessionLocal()
    try:
        # Check if already populated
        if db.query(SDGModel).count() == 0:
            for s in SDGS:
                db.add(SDGModel(
                    id=s["id"],
                    sdg_number=s["sdg_number"],
                    name=s["name"],
                    description=s["description"],
                    color=s["color"]
                ))

            for ef in EMISSION_FACTORS:
                db.add(EmissionFactorModel(**ef))

            for trg in TARGETS:
                db.add(SustainabilityTargetModel(**trg))

            for init in INITIATIVES:
                db.add(SustainabilityInitiativeModel(
                    id=init["id"],
                    name=init["name"],
                    description=init["description"],
                    lead_department=init["lead_department"],
                    status=init["status"],
                    start_date=init["start_date"],
                    completion_date=init["completion_date"],
                    sdg_ids_json=json.dumps(init["sdg_ids"]),
                    target_ids_json=json.dumps(init["target_ids"]),
                    carbon_reduction_estimate_kgco2e=init["carbon_reduction_estimate_kgco2e"],
                    source_type=init["source_type"]
                ))

            for _, row in df_elec.iterrows():
                db.add(ElectricityRecord(**row.to_dict()))

            for _, row in df_wat.iterrows():
                db.add(WaterRecord(**row.to_dict()))

            for _, row in df_wst.iterrows():
                db.add(WasteRecord(**row.to_dict()))

            for _, row in df_trn.iterrows():
                db.add(TransportRecord(**row.to_dict()))

            db.commit()
            print("Successfully populated SQLite database with synthetic records.")
    finally:
        db.close()

if __name__ == "__main__":
    main()

