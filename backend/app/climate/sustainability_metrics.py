from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.schema import (
    ElectricityRecord, WaterRecord, WasteRecord, TransportRecord, SustainabilityInitiativeModel, SustainabilityTargetModel
)
from app.climate.carbon_calculator import carbon_calculator

class SustainabilityMetricsService:
    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        """High-level institutional KPI summary cards for the main overview dashboard."""
        inv_2024 = carbon_calculator.get_annual_inventory(db, year=2024)
        inv_2025 = carbon_calculator.get_annual_inventory(db, year=2025)

        # 24-month electricity totals
        elec_tot = db.query(
            func.sum(ElectricityRecord.total_kwh).label("total_kwh"),
            func.sum(ElectricityRecord.grid_kwh).label("grid_kwh"),
            func.sum(ElectricityRecord.solar_kwh).label("solar_kwh")
        ).first()

        tot_kwh = float(elec_tot.total_kwh or 0.0)
        sol_kwh = float(elec_tot.solar_kwh or 0.0)
        solar_pct = round((sol_kwh / tot_kwh) * 100, 2) if tot_kwh > 0 else 0.0

        # Water totals
        wat_tot = db.query(
            func.sum(WaterRecord.consumption_litres).label("consumed"),
            func.sum(WaterRecord.rainwater_harvested_litres).label("harvested")
        ).first()

        # Waste totals
        wst_tot = db.query(
            func.sum(WasteRecord.total_kg).label("total_kg"),
            func.sum(WasteRecord.recyclable_kg).label("recycled_kg"),
            func.sum(WasteRecord.composted_kg).label("compost_kg")
        ).first()

        tot_waste = float(wst_tot.total_kg or 0.0)
        diverted_waste = float(wst_tot.recycled_kg or 0.0) + float(wst_tot.compost_kg or 0.0)
        recycling_rate = round((diverted_waste / tot_waste) * 100, 2) if tot_waste > 0 else 0.0

        # Initiatives
        active_inits = db.query(SustainabilityInitiativeModel).filter(
            SustainabilityInitiativeModel.status == "ACTIVE"
        ).count()
        total_inits = db.query(SustainabilityInitiativeModel).count()

        return {
            "institution_name": "VESIT Green Campus",
            "source_type": "SYNTHETIC_DEMO",
            "kpis": {
                "total_carbon_emissions_tonnes": inv_2025["total_emissions_tonnes_co2e"],
                "baseline_emissions_tonnes": inv_2024["total_emissions_tonnes_co2e"],
                "emissions_reduction_percentage": round(
                    ((inv_2024["total_emissions_kgco2e"] - inv_2025["total_emissions_kgco2e"]) / inv_2024["total_emissions_kgco2e"]) * 100, 2
                ),
                "total_electricity_mwh": round(tot_kwh / 1000.0, 2),
                "solar_generation_mwh": round(sol_kwh / 1000.0, 2),
                "renewable_energy_percentage": solar_pct,
                "total_water_consumption_million_litres": round(float(wat_tot.consumed or 0.0) / 1000000.0, 2),
                "rainwater_harvested_million_litres": round(float(wat_tot.harvested or 0.0) / 1000000.0, 2),
                "waste_diversion_rate": recycling_rate,
                "active_sustainability_initiatives": active_inits,
                "total_sustainability_initiatives": total_inits
            }
        }

    @staticmethod
    def get_energy_metrics(db: Session) -> Dict[str, Any]:
        """Detailed energy metrics: solar vs grid, monthly time-series, building breakdown."""
        # Monthly aggregates
        monthly = db.query(
            ElectricityRecord.date_str,
            func.sum(ElectricityRecord.grid_kwh).label("grid_kwh"),
            func.sum(ElectricityRecord.solar_kwh).label("solar_kwh"),
            func.sum(ElectricityRecord.total_kwh).label("total_kwh"),
            func.sum(ElectricityRecord.emissions_kgco2e).label("emissions_kgco2e")
        ).group_by(ElectricityRecord.date_str).order_by(ElectricityRecord.date_str).all()

        monthly_series = [
            {
                "date": r.date_str,
                "grid_kwh": round(float(r.grid_kwh), 2),
                "solar_kwh": round(float(r.solar_kwh), 2),
                "total_kwh": round(float(r.total_kwh), 2),
                "emissions_kgco2e": round(float(r.emissions_kgco2e), 2),
                "solar_percentage": round((float(r.solar_kwh) / float(r.total_kwh)) * 100, 2) if float(r.total_kwh) > 0 else 0.0
            }
            for r in monthly
        ]

        # Building breakdown (2024 annual)
        bld_stats = db.query(
            ElectricityRecord.building_id,
            func.sum(ElectricityRecord.total_kwh).label("total_kwh"),
            func.sum(ElectricityRecord.solar_kwh).label("solar_kwh"),
            func.sum(ElectricityRecord.emissions_kgco2e).label("emissions_kgco2e")
        ).filter(ElectricityRecord.year == 2024).group_by(ElectricityRecord.building_id).all()

        bld_names = {
            "BLD_ACA": "Academic Block A",
            "BLD_ACB": "Academic Block B",
            "BLD_LAB": "Computer Laboratories",
            "BLD_LIB": "Library",
            "BLD_AUD": "Auditorium",
            "BLD_CAN": "Canteen",
            "BLD_ADM": "Administration Block"
        }

        building_breakdown = [
            {
                "building_id": r.building_id,
                "building_name": bld_names.get(r.building_id, r.building_id),
                "total_kwh": round(float(r.total_kwh), 2),
                "solar_kwh": round(float(r.solar_kwh), 2),
                "emissions_kgco2e": round(float(r.emissions_kgco2e), 2)
            }
            for r in bld_stats
        ]

        tot_grid = sum(m["grid_kwh"] for m in monthly_series)
        tot_solar = sum(m["solar_kwh"] for m in monthly_series)
        tot_elec = sum(m["total_kwh"] for m in monthly_series)

        return {
            "total_electricity_kwh": round(tot_elec, 2),
            "grid_electricity_kwh": round(tot_grid, 2),
            "solar_generation_kwh": round(tot_solar, 2),
            "renewable_percentage": round((tot_solar / tot_elec) * 100, 2) if tot_elec > 0 else 0.0,
            "monthly_trends": monthly_series,
            "building_breakdown": building_breakdown
        }

    @staticmethod
    def get_water_metrics(db: Session) -> Dict[str, Any]:
        """Monthly water trends, building breakdown, intensity."""
        monthly = db.query(
            WaterRecord.date_str,
            func.sum(WaterRecord.consumption_litres).label("consumption"),
            func.sum(WaterRecord.rainwater_harvested_litres).label("harvested")
        ).group_by(WaterRecord.date_str).order_by(WaterRecord.date_str).all()

        monthly_series = [
            {
                "date": r.date_str,
                "consumption_litres": round(float(r.consumption), 2),
                "rainwater_harvested_litres": round(float(r.harvested), 2)
            }
            for r in monthly
        ]

        # Building breakdown (2024)
        bld_stats = db.query(
            WaterRecord.building_id,
            func.sum(WaterRecord.consumption_litres).label("consumption"),
            func.sum(WaterRecord.rainwater_harvested_litres).label("harvested")
        ).filter(WaterRecord.year == 2024).group_by(WaterRecord.building_id).all()

        bld_names = {
            "BLD_ACA": "Academic Block A",
            "BLD_ACB": "Academic Block B",
            "BLD_LAB": "Computer Laboratories",
            "BLD_LIB": "Library",
            "BLD_AUD": "Auditorium",
            "BLD_CAN": "Canteen",
            "BLD_ADM": "Administration Block"
        }

        building_breakdown = [
            {
                "building_id": r.building_id,
                "building_name": bld_names.get(r.building_id, r.building_id),
                "consumption_litres": round(float(r.consumption), 2),
                "rainwater_harvested_litres": round(float(r.harvested), 2)
            }
            for r in bld_stats
        ]

        total_consumed = sum(m["consumption_litres"] for m in monthly_series)
        total_harvested = sum(m["rainwater_harvested_litres"] for m in monthly_series)

        return {
            "total_consumption_litres": round(total_consumed, 2),
            "total_rainwater_harvested_litres": round(total_harvested, 2),
            "rainwater_replacement_rate": round((total_harvested / total_consumed) * 100, 2) if total_consumed > 0 else 0.0,
            "monthly_trends": monthly_series,
            "building_breakdown": building_breakdown
        }

    @staticmethod
    def get_waste_metrics(db: Session) -> Dict[str, Any]:
        """Waste generation, recycling, composting, emissions."""
        records = db.query(WasteRecord).order_by(WasteRecord.date_str).all()
        monthly_series = [
            {
                "date": r.date_str,
                "total_kg": r.total_kg,
                "recyclable_kg": r.recyclable_kg,
                "non_recyclable_kg": r.non_recyclable_kg,
                "composted_kg": r.composted_kg,
                "emissions_kgco2e": r.emissions_kgco2e,
                "recycling_rate": round(((r.recyclable_kg + r.composted_kg) / r.total_kg) * 100, 2) if r.total_kg > 0 else 0.0
            }
            for r in records
        ]

        tot_w = sum(r.total_kg for r in records)
        tot_r = sum(r.recyclable_kg for r in records)
        tot_nr = sum(r.non_recyclable_kg for r in records)
        tot_c = sum(r.composted_kg for r in records)

        return {
            "total_waste_kg": round(tot_w, 2),
            "recyclable_kg": round(tot_r, 2),
            "non_recyclable_kg": round(tot_nr, 2),
            "composted_kg": round(tot_c, 2),
            "recycling_rate": round(((tot_r + tot_c) / tot_w) * 100, 2) if tot_w > 0 else 0.0,
            "monthly_trends": monthly_series
        }

    @staticmethod
    def get_transport_metrics(db: Session) -> Dict[str, Any]:
        """Transportation modal split, trips, passenger-km, emissions."""
        mode_stats = db.query(
            TransportRecord.mode,
            func.sum(TransportRecord.passenger_km).label("total_pkm"),
            func.sum(TransportRecord.trips_count).label("total_trips"),
            func.sum(TransportRecord.emissions_kgco2e).label("total_emissions")
        ).group_by(TransportRecord.mode).all()

        modes = [
            {
                "mode": r.mode,
                "passenger_km": round(float(r.total_pkm), 2),
                "trips_count": int(r.total_trips),
                "emissions_kgco2e": round(float(r.total_emissions), 2)
            }
            for r in mode_stats
        ]

        total_pkm = sum(m["passenger_km"] for m in modes)
        total_trips = sum(m["trips_count"] for m in modes)
        total_emissions = sum(m["emissions_kgco2e"] for m in modes)

        return {
            "total_passenger_km": round(total_pkm, 2),
            "total_trips": total_trips,
            "total_transport_emissions_kgco2e": round(total_emissions, 2),
            "modes": modes
        }

sustainability_metrics = SustainabilityMetricsService()

