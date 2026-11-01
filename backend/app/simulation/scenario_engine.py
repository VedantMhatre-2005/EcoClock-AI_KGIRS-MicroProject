from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.climate.carbon_calculator import carbon_calculator
from app.simulation.solar_simulator import solar_simulator
from app.simulation.transport_simulator import transport_simulator
from app.simulation.waste_simulator import waste_simulator
from app.simulation.water_simulator import water_simulator

class ScenarioEngine:
    @staticmethod
    def run_scenario(
        db: Session,
        scenario_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes deterministic Python simulation according to scenario type.
        """
        inv_baseline = carbon_calculator.get_annual_inventory(db, year=2024)
        baseline_total_kg = inv_baseline["total_emissions_kgco2e"]

        reduction_kgco2e = 0.0
        resource_savings = {}
        details = {}

        if scenario_type == "SOLAR":
            cap_kw = float(parameters.get("additional_capacity_kw", 200.0))
            res = solar_simulator.simulate(additional_capacity_kw=cap_kw)
            reduction_kgco2e = res["avoided_emissions_kgco2e"]
            resource_savings = {
                "solar_kwh_generated": res["annual_generation_kwh"],
                "grid_kwh_displaced": res["displaced_grid_kwh"]
            }
            details = res

        elif scenario_type == "TRANSPORT":
            pct_pub = float(parameters.get("pct_shift_to_public_transit", 25.0))
            pct_act = float(parameters.get("pct_shift_to_cycling_walking", 15.0))
            res = transport_simulator.simulate(
                pct_shift_to_public_transit=pct_pub,
                pct_shift_to_cycling_walking=pct_act
            )
            reduction_kgco2e = res["avoided_emissions_kgco2e"]
            resource_savings = {
                "passenger_km_shifted": res["annual_passenger_km_shifted"],
                "commuters_shifted": res["commuters_shifted_to_public_transit"] + res["commuters_shifted_to_active_mobility"]
            }
            details = res

        elif scenario_type == "WASTE":
            w_red = float(parameters.get("waste_reduction_pct", 20.0))
            rec_pct = float(parameters.get("target_recycling_pct", 65.0))
            comp_pct = float(parameters.get("target_composting_pct", 25.0))
            res = waste_simulator.simulate(
                waste_reduction_pct=w_red,
                target_recycling_pct=rec_pct,
                target_composting_pct=comp_pct
            )
            reduction_kgco2e = res["avoided_emissions_kgco2e"]
            resource_savings = {
                "waste_avoided_kg": res["waste_avoided_kg"],
                "landfill_diversion_rate": res["landfill_diversion_rate"]
            }
            details = res

        elif scenario_type == "WATER":
            aerator_pct = float(parameters.get("fixture_efficiency_reduction_pct", 15.0))
            cistern_m3 = float(parameters.get("rainwater_cistern_expansion_m3", 300.0))
            greywater_lpd = float(parameters.get("greywater_reuse_litres_per_day", 18000.0))
            res = water_simulator.simulate(
                fixture_efficiency_reduction_pct=aerator_pct,
                rainwater_cistern_expansion_m3=cistern_m3,
                greywater_reuse_litres_per_day=greywater_lpd
            )
            reduction_kgco2e = res["avoided_embodied_emissions_kgco2e"]
            resource_savings = {
                "freshwater_saved_litres": res["total_freshwater_saved_litres"],
                "percentage_reduction": res["percentage_reduction"]
            }
            details = res

        elif scenario_type == "COMBINED":
            # Combine all four interventions
            solar_res = solar_simulator.simulate(
                additional_capacity_kw=float(parameters.get("solar_capacity_kw", 200.0))
            )
            trans_res = transport_simulator.simulate(
                pct_shift_to_public_transit=float(parameters.get("transport_public_shift_pct", 20.0)),
                pct_shift_to_cycling_walking=float(parameters.get("transport_active_shift_pct", 10.0))
            )
            waste_res = waste_simulator.simulate(
                waste_reduction_pct=float(parameters.get("waste_reduction_pct", 15.0)),
                target_recycling_pct=float(parameters.get("waste_recycling_pct", 60.0))
            )
            water_res = water_simulator.simulate(
                fixture_efficiency_reduction_pct=float(parameters.get("water_fixture_efficiency_pct", 15.0))
            )

            reduction_kgco2e = (
                solar_res["avoided_emissions_kgco2e"] +
                trans_res["avoided_emissions_kgco2e"] +
                waste_res["avoided_emissions_kgco2e"] +
                water_res["avoided_embodied_emissions_kgco2e"]
            )
            resource_savings = {
                "solar_kwh_generated": solar_res["annual_generation_kwh"],
                "passenger_km_shifted": trans_res["annual_passenger_km_shifted"],
                "waste_avoided_kg": waste_res["waste_avoided_kg"],
                "freshwater_saved_litres": water_res["total_freshwater_saved_litres"]
            }
            details = {
                "solar": solar_res,
                "transport": trans_res,
                "waste": waste_res,
                "water": water_res
            }

        projected_total_kg = max(0.0, baseline_total_kg - reduction_kgco2e)
        pct_red = round((reduction_kgco2e / baseline_total_kg) * 100, 2) if baseline_total_kg > 0 else 0.0

        return {
            "scenario_type": scenario_type,
            "parameters": parameters,
            "baseline_emissions_kgco2e": round(baseline_total_kg, 2),
            "baseline_emissions_tonnes_co2e": round(baseline_total_kg / 1000.0, 2),
            "projected_emissions_kgco2e": round(projected_total_kg, 2),
            "projected_emissions_tonnes_co2e": round(projected_total_kg / 1000.0, 2),
            "reduction_kgco2e": round(reduction_kgco2e, 2),
            "reduction_tonnes_co2e": round(reduction_kgco2e / 1000.0, 2),
            "percentage_reduction": pct_red,
            "resource_savings": resource_savings,
            "details": details
        }

scenario_engine = ScenarioEngine()

