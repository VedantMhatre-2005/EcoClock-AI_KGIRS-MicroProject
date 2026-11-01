from typing import Dict, Any

class WaterSimulator:
    @staticmethod
    def simulate(
        baseline_annual_litres: float = 48000000.0,
        fixture_efficiency_reduction_pct: float = 12.0,
        rainwater_cistern_expansion_m3: float = 250.0,
        greywater_reuse_litres_per_day: float = 15000.0,
        active_annual_days: int = 240,
        pumping_energy_intensity_kwh_per_m3: float = 0.627,
        grid_emission_factor_kgco2e_per_kwh: float = 0.82
    ) -> Dict[str, Any]:
        """
        Simulates campus water conservation interventions.
        Embodied carbon is derived explicitly from municipal water pumping and treatment energy displacement.
        """
        fixture_saved_litres = baseline_annual_litres * (fixture_efficiency_reduction_pct / 100.0)
        cistern_captured_litres = rainwater_cistern_expansion_m3 * 1000.0 * 8.5
        greywater_recycled_litres = greywater_reuse_litres_per_day * active_annual_days

        total_freshwater_saved_litres = fixture_saved_litres + cistern_captured_litres + greywater_recycled_litres
        projected_demand_litres = max(0.0, baseline_annual_litres - total_freshwater_saved_litres)

        embodied_carbon_factor_kg_per_litre = (pumping_energy_intensity_kwh_per_m3 * grid_emission_factor_kgco2e_per_kwh) / 1000.0
        avoided_emissions_kgco2e = total_freshwater_saved_litres * embodied_carbon_factor_kg_per_litre

        return {
            "intervention": "WATER_CONSERVATION",
            "baseline_annual_litres": baseline_annual_litres,
            "projected_annual_litres": round(projected_demand_litres, 2),
            "total_freshwater_saved_litres": round(total_freshwater_saved_litres, 2),
            "percentage_reduction": round((total_freshwater_saved_litres / baseline_annual_litres) * 100, 2),
            "breakdown": {
                "fixture_efficiency_litres": round(fixture_saved_litres, 2),
                "cistern_harvested_litres": round(cistern_captured_litres, 2),
                "greywater_recycled_litres": round(greywater_recycled_litres, 2)
            },
            "avoided_embodied_emissions_kgco2e": round(avoided_emissions_kgco2e, 2),
            "avoided_embodied_emissions_tonnes_co2e": round(avoided_emissions_kgco2e / 1000.0, 2),
            "methodology_disclaimer": "Avoided embodied emissions are calculated strictly from the displacement of municipal pumping and purification electricity (0.514 kg CO2e/m3), not assumed equal to direct water volume."
        }

water_simulator = WaterSimulator()
