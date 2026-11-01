from typing import Dict, Any

class WasteSimulator:
    @staticmethod
    def simulate(
        baseline_annual_waste_kg: float = 68400.0,
        waste_reduction_pct: float = 15.0,
        target_recycling_pct: float = 60.0,
        target_composting_pct: float = 30.0,
        landfill_ef: float = 1.25,
        compost_ef: float = 0.08,
        recycle_avoided_ef: float = -0.65
    ) -> Dict[str, Any]:
        """
        Simulates source waste reduction, expanded aerobic composting, and formal recycling recovery.
        """
        # Baseline: 42% recycled, 28% composted, 30% landfill
        b_landfill = baseline_annual_waste_kg * 0.30
        b_compost = baseline_annual_waste_kg * 0.28
        b_recycle = baseline_annual_waste_kg * 0.42
        baseline_emissions = (b_landfill * landfill_ef) + (b_compost * compost_ef) + (b_recycle * recycle_avoided_ef)

        # Proposed
        reduced_total_kg = baseline_annual_waste_kg * (1.0 - (waste_reduction_pct / 100.0))
        p_recycle_kg = reduced_total_kg * (target_recycling_pct / 100.0)
        p_compost_kg = reduced_total_kg * (target_composting_pct / 100.0)
        p_landfill_kg = max(0.0, reduced_total_kg - p_recycle_kg - p_compost_kg)

        projected_emissions = (p_landfill_kg * landfill_ef) + (p_compost_kg * compost_ef) + (p_recycle_kg * recycle_avoided_ef)
        avoided_emissions = baseline_emissions - projected_emissions

        return {
            "intervention": "WASTE_REDUCTION_AND_CIRCULARITY",
            "baseline_total_kg": baseline_annual_waste_kg,
            "projected_total_kg": round(reduced_total_kg, 2),
            "waste_avoided_kg": round(baseline_annual_waste_kg - reduced_total_kg, 2),
            "projected_landfill_kg": round(p_landfill_kg, 2),
            "projected_recycling_kg": round(p_recycle_kg, 2),
            "projected_composting_kg": round(p_compost_kg, 2),
            "landfill_diversion_rate": round(((p_recycle_kg + p_compost_kg) / reduced_total_kg) * 100, 2),
            "baseline_emissions_kgco2e": round(baseline_emissions, 2),
            "projected_emissions_kgco2e": round(projected_emissions, 2),
            "avoided_emissions_kgco2e": round(avoided_emissions, 2),
            "avoided_emissions_tonnes_co2e": round(avoided_emissions / 1000.0, 2)
        }

waste_simulator = WasteSimulator()

