from typing import Dict, Any

class SolarSimulator:
    @staticmethod
    def simulate(
        additional_capacity_kw: float,
        generation_yield_kwh_per_kwp: float = 1420.0, # Typical annual yield in Mumbai
        grid_emission_factor_kg_per_kwh: float = 0.82,
        displacement_ratio: float = 0.95
    ) -> Dict[str, Any]:
        """
        Simulates solar PV adoption impact on grid displacement and avoided emissions.
        """
        annual_generation_kwh = additional_capacity_kw * generation_yield_kwh_per_kwp
        effective_displaced_kwh = annual_generation_kwh * displacement_ratio
        avoided_emissions_kgco2e = effective_displaced_kwh * grid_emission_factor_kg_per_kwh

        return {
            "intervention": "SOLAR_ADOPTION",
            "installed_capacity_kw": additional_capacity_kw,
            "annual_generation_kwh": round(annual_generation_kwh, 2),
            "displaced_grid_kwh": round(effective_displaced_kwh, 2),
            "avoided_emissions_kgco2e": round(avoided_emissions_kgco2e, 2),
            "avoided_emissions_tonnes_co2e": round(avoided_emissions_kgco2e / 1000.0, 2),
            "assumptions": {
                "annual_yield_kwh_per_kwp": generation_yield_kwh_per_kwp,
                "grid_emission_factor": grid_emission_factor_kg_per_kwh,
                "grid_displacement_efficiency": displacement_ratio
            }
        }

solar_simulator = SolarSimulator()

