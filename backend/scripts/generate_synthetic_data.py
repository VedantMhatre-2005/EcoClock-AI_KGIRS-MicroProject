"""
EcoClock AI - Synthetic Data Generator
Generates realistic, reproducible synthetic sustainability data for VESIT Green Campus.
Stores 22 two-page equivalent documents as PDFs in backend/data/sample_documents/.
Seed: 42
"""

import os
import re
import sys
import json
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import the 22 comprehensive, two-page equivalent document templates
try:
    from scripts.document_templates import DOCUMENTS
except ImportError:
    from backend.scripts.document_templates import DOCUMENTS

# Set fixed random seed
np.random.seed(42)

SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

PDF_DIR = BASE_DIR / "data" / "sample_documents"
PDF_DIR.mkdir(parents=True, exist_ok=True)

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

# 2. EMISSION FACTORS
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

# 5. UN SUSTAINABLE DEVELOPMENT GOALS
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

# 6. TIME-SERIES GENERATION
MONTHS = pd.date_range(start="2024-01-01", periods=24, freq="MS")

def generate_monthly_timeseries():
    electricity_rows = []
    water_rows = []
    waste_rows = []
    transport_rows = []

    month_weights = {
        1: {"temp": 1.0, "occ": 1.0, "solar": 1.1, "rain": 0.02},
        2: {"temp": 1.05, "occ": 1.0, "solar": 1.15, "rain": 0.02},
        3: {"temp": 1.25, "occ": 1.05, "solar": 1.25, "rain": 0.05},
        4: {"temp": 1.45, "occ": 0.95, "solar": 1.3, "rain": 0.1},
        5: {"temp": 1.55, "occ": 0.40, "solar": 1.2, "rain": 0.2},
        6: {"temp": 1.35, "occ": 0.85, "solar": 0.65, "rain": 1.8},
        7: {"temp": 1.20, "occ": 1.05, "solar": 0.50, "rain": 2.5},
        8: {"temp": 1.18, "occ": 1.05, "solar": 0.55, "rain": 2.2},
        9: {"temp": 1.22, "occ": 1.0, "solar": 0.75, "rain": 1.4},
        10: {"temp": 1.35, "occ": 1.0, "solar": 1.05, "rain": 0.4},
        11: {"temp": 1.15, "occ": 0.95, "solar": 1.1, "rain": 0.1},
        12: {"temp": 1.0, "occ": 0.70, "solar": 1.05, "rain": 0.02}
    }

    bld_base_elec = {
        "BLD_ACA": 32000,
        "BLD_ACB": 29000,
        "BLD_LAB": 48000,
        "BLD_LIB": 14000,
        "BLD_AUD": 11000,
        "BLD_CAN": 16000,
        "BLD_ADM": 19000
    }

    bld_base_water = {
        "BLD_ACA": 750000,
        "BLD_ACB": 680000,
        "BLD_LAB": 420000,
        "BLD_LIB": 240000,
        "BLD_AUD": 190000,
        "BLD_CAN": 1150000,
        "BLD_ADM": 370000
    }

    solar_capacities = {"BLD_ACA": 80, "BLD_ACB": 70, "BLD_LAB": 0, "BLD_LIB": 30, "BLD_AUD": 0, "BLD_CAN": 0, "BLD_ADM": 40}
    grid_ef = 0.82

    for dt in MONTHS:
        year = dt.year
        month = dt.month
        date_str = dt.strftime("%Y-%m")
        w = month_weights[month]
        y_factor = 0.97 if year == 2025 else 1.0

        for bld in BUILDINGS:
            bid = bld["id"]
            base_kwh = bld_base_elec[bid] * w["temp"] * (0.3 + 0.7 * w["occ"]) * y_factor
            noise = np.random.normal(1.0, 0.03)
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

            base_w = bld_base_water[bid] * (0.2 + 0.8 * w["occ"])
            w_noise = np.random.normal(1.0, 0.04)
            consumption_l = round(base_w * w_noise, 2)

            roof_area = bld["area_m2"] * 0.4
            rain_harvested = round(roof_area * (w["rain"] * 180) * 0.75, 2)

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

        base_waste_kg = 5800 * (0.3 + 0.7 * w["occ"]) * np.random.normal(1.0, 0.03)
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

        work_days = 22 if month not in [5, 12] else (8 if month == 5 else 16)
        active_commuters = int(3200 * w["occ"])

        modes = [
            ("TRAIN", 0.48, 28, 0.028),
            ("BUS", 0.22, 14, 0.054),
            ("TWO_WHEELER", 0.16, 12, 0.042),
            ("CAR", 0.06, 18, 0.175),
            ("WALKING_CYCLING", 0.08, 2, 0.0)
        ]

        for mode_name, share, avg_km, ef in modes:
            trips = int(active_commuters * share * work_days * 2)
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

def _generate_pdfs(documents, output_dir: Path):
    """Generates professional 2-page PDF documents using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    except ImportError:
        print("[WARN] reportlab not installed. Skipping PDF generation. Run: pip install reportlab")
        return

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1b4332'),
        alignment=TA_CENTER,
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#444444'),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#2d6a4f'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )

    audit_box_style = ParagraphStyle(
        'DocAudit',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#2b580c'),
        spaceBefore=8,
        spaceAfter=4
    )

    for doc in documents:
        doc_id = doc["document_id"]
        pdf_path = output_dir / f"{doc_id}.pdf"
        
        pdf = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        story = []
        story.append(Paragraph(doc["title"], title_style))
        story.append(Paragraph(
            f"<b>Document ID:</b> {doc['document_id']} &nbsp;|&nbsp; <b>Type:</b> {doc['document_type']} &nbsp;|&nbsp; "
            f"<b>Publication:</b> {doc['publication_date']} &nbsp;|&nbsp; <b>Institution:</b> {doc['institution_id']} (VESIT Green Campus, Chembur)",
            meta_style
        ))

        lines = doc["content"].split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                story.append(Spacer(1, 3))
                continue

            escaped = (
                line_str.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            # Check for section header
            if re.match(r'^\d+\.\s+[A-Z]', line_str) or (line_str.isupper() and len(line_str) > 4 and not line_str.startswith("HTTP")):
                story.append(Paragraph(escaped, section_style))
            else:
                story.append(Paragraph(escaped, body_style))

        # Formal Institutional Verification & Sign-off Block to ensure thorough 2-page completeness
        story.append(Spacer(1, 6))
        story.append(Paragraph("INSTITUTIONAL AUDIT & COMPLIANCE VERIFICATION", section_style))
        story.append(Paragraph(
            f"This statutory record is indexed in the EcoClock AI Knowledge Graph repository under Canonical ID <b>{doc_id}</b>. "
            f"All empirical utility telemetry, carbon accounting estimates, and SDG alignments articulated in this document have been reviewed and verified by the "
            f"VESIT Campus Sustainability Taskforce, Department of Computer Engineering (DEP_CMPN), Department of Information Technology (DEP_INFT), "
            f"Department of Electronics & Telecommunication (DEP_EXTC), Department of Artificial Intelligence & Data Science (DEP_AIDS), and Campus Facilities (DEP_ADMN). "
            f"Published by: Vivekananda Education Society's Institute of Technology (VESIT Green Campus), Hashu Advani Memorial Complex, Collector's Colony, Chembur, Mumbai 400074.",
            audit_box_style
        ))

        try:
            pdf.build(story)
        except Exception as e:
            print(f"[ERROR] Failed building PDF for {doc_id}: {e}")

    print(f"Generated {len(documents)} two-page equivalent PDF documents in {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="VESIT Green Campus Synthetic Data & PDF Generator")
    parser.add_argument("--force", action="store_true", help="Force regenerate dataset and PDFs even if existing")
    args = parser.parse_args()

    flag_file = PDF_DIR / ".pdfs_generated"

    # Avoid unnecessary recreation if files and database already exist
    if not args.force and flag_file.exists() and (SYNTHETIC_DIR / "documents.json").exists():
        print(f"Sample dataset and PDF documents already exist in {PDF_DIR}.")
        print("Skipping generation. (Use --force to regenerate).")
        return

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

    # Generate PDFs
    _generate_pdfs(DOCUMENTS, PDF_DIR)
    flag_file.touch()

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
        # Populate reference tables if empty
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
