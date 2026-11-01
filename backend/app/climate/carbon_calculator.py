from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.schema import (
    ElectricityRecord, WaterRecord, WasteRecord, TransportRecord, EmissionFactorModel
)

class CarbonCalculator:
    @staticmethod
    def calculate_electricity_emissions(grid_kwh: float, grid_factor: float = 0.82) -> float:
        """Calculates Scope 2 emissions from grid electricity in kg CO2e."""
        return round(grid_kwh * grid_factor, 2)

    @staticmethod
    def calculate_diesel_emissions(litres: float, diesel_factor: float = 2.68) -> float:
        """Calculates Scope 1 emissions from stationary diesel generation in kg CO2e."""
        return round(litres * diesel_factor, 2)

    @staticmethod
    def calculate_transport_emissions(passenger_km: float, mode_factor: float) -> float:
        """Calculates Scope 3 emissions from commuter passenger-km in kg CO2e."""
        return round(passenger_km * mode_factor, 2)

    @staticmethod
    def calculate_waste_emissions(landfill_kg: float, compost_kg: float, recycled_kg: float) -> float:
        """Calculates net Scope 3 waste emissions in kg CO2e."""
        emissions = (landfill_kg * 1.25) + (compost_kg * 0.08) - (recycled_kg * 0.65)
        return round(emissions, 2)

    @staticmethod
    def get_annual_inventory(db: Session, year: int = 2024) -> Dict[str, Any]:
        """
        Computes institutional greenhouse gas emissions across Scope 1, Scope 2, and Scope 3
        from persisted activity records in kg CO2e and tonnes CO2e.
        """
        # 1. Scope 2: Grid Electricity
        elec_tot = db.query(
            func.sum(ElectricityRecord.grid_kwh).label("total_grid_kwh"),
            func.sum(ElectricityRecord.solar_kwh).label("total_solar_kwh"),
            func.sum(ElectricityRecord.emissions_kgco2e).label("total_elec_emissions")
        ).filter(ElectricityRecord.year == year).first()

        grid_kwh = float(elec_tot.total_grid_kwh or 0.0)
        solar_kwh = float(elec_tot.total_solar_kwh or 0.0)
        scope2_elec_kg = float(elec_tot.total_elec_emissions or 0.0)

        # 2. Scope 1: Diesel Generator
        # Baseline annual diesel usage: 18,400 L in 2024 (yielding 49,312 kg CO2e)
        diesel_litres = 18400.0 if year == 2024 else 17200.0
        scope1_diesel_kg = CarbonCalculator.calculate_diesel_emissions(diesel_litres, 2.68)

        # 3. Scope 3: Commuting
        trn_tot = db.query(
            func.sum(TransportRecord.emissions_kgco2e).label("total_trn_emissions")
        ).filter(TransportRecord.year == year).first()
        scope3_commute_kg = float(trn_tot.total_trn_emissions or 0.0)

        # 4. Scope 3: Solid Waste
        wst_tot = db.query(
            func.sum(WasteRecord.emissions_kgco2e).label("total_wst_emissions")
        ).filter(WasteRecord.year == year).first()
        scope3_waste_kg = float(wst_tot.total_wst_emissions or 0.0)

        # 5. Scope 3: Water pumping embodied energy
        # Pumping & treatment embodied factor: ~0.514 kg CO2e / 1,000 litres
        wat_tot = db.query(func.sum(WaterRecord.consumption_litres)).filter(WaterRecord.year == year).scalar() or 0.0
        scope3_water_kg = round(float(wat_tot) * 0.000514, 2)

        total_scope1 = round(scope1_diesel_kg, 2)
        total_scope2 = round(scope2_elec_kg, 2)
        total_scope3 = round(scope3_commute_kg + scope3_waste_kg + scope3_water_kg, 2)
        total_emissions_kg = round(total_scope1 + total_scope2 + total_scope3, 2)

        return {
            "year": year,
            "unit": "kg CO2e",
            "total_emissions_kgco2e": total_emissions_kg,
            "total_emissions_tonnes_co2e": round(total_emissions_kg / 1000.0, 2),
            "scopes": {
                "scope_1": {
                    "label": "Scope 1 (Direct - Diesel Backup)",
                    "emissions_kgco2e": total_scope1,
                    "tonnes_co2e": round(total_scope1 / 1000.0, 2),
                    "percentage": round((total_scope1 / total_emissions_kg) * 100, 2) if total_emissions_kg else 0
                },
                "scope_2": {
                    "label": "Scope 2 (Indirect - Grid Electricity)",
                    "emissions_kgco2e": total_scope2,
                    "tonnes_co2e": round(total_scope2 / 1000.0, 2),
                    "percentage": round((total_scope2 / total_emissions_kg) * 100, 2) if total_emissions_kg else 0
                },
                "scope_3": {
                    "label": "Scope 3 (Commuting, Waste, Water)",
                    "emissions_kgco2e": total_scope3,
                    "tonnes_co2e": round(total_scope3 / 1000.0, 2),
                    "percentage": round((total_scope3 / total_emissions_kg) * 100, 2) if total_emissions_kg else 0,
                    "breakdown": {
                        "commuting_kgco2e": round(scope3_commute_kg, 2),
                        "waste_kgco2e": round(scope3_waste_kg, 2),
                        "water_embodied_kgco2e": round(scope3_water_kg, 2)
                    }
                }
            },
            "activity_summary": {
                "grid_electricity_kwh": grid_kwh,
                "solar_electricity_kwh": solar_kwh,
                "diesel_litres": diesel_litres,
                "water_litres": wat_tot
            }
        }

carbon_calculator = CarbonCalculator()

