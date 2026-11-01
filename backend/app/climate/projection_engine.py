import math
from typing import Dict, Any, List

class ProjectionEngine:
    @staticmethod
    def calculate_linear_projection(
        baseline_emissions: float,
        baseline_year: int,
        annual_reduction_rate_kg: float,
        target_year: int = 2040,
        projection_horizon_years: int = 25
    ) -> Dict[str, Any]:
        """
        Calculates linear decarbonization trajectory:
        E(t) = E0 - r * (t - t0)
        """
        trajectory: List[Dict[str, Any]] = []
        projected_net_zero_year = None

        if annual_reduction_rate_kg > 0:
            years_to_zero = baseline_emissions / annual_reduction_rate_kg
            projected_net_zero_year = int(math.ceil(baseline_year + years_to_zero))

        for offset in range(projection_horizon_years + 1):
            y = baseline_year + offset
            e_t = max(0.0, baseline_emissions - (annual_reduction_rate_kg * offset))
            trajectory.append({
                "year": y,
                "emissions_kgco2e": round(e_t, 2),
                "emissions_tonnes_co2e": round(e_t / 1000.0, 2),
                "is_net_zero": e_t == 0.0
            })

        achieves_target_by_deadline = (
            projected_net_zero_year is not None and projected_net_zero_year <= target_year
        )

        return {
            "model_type": "LINEAR",
            "formula": "E(t) = E0 - r * (t - t0)",
            "baseline_emissions_kgco2e": baseline_emissions,
            "baseline_year": baseline_year,
            "target_year": target_year,
            "annual_reduction_kgco2e": annual_reduction_rate_kg,
            "projected_net_zero_year": projected_net_zero_year,
            "reaches_net_zero": projected_net_zero_year is not None and projected_net_zero_year <= (baseline_year + projection_horizon_years),
            "achieves_target_by_deadline": achieves_target_by_deadline,
            "trajectory": trajectory
        }

    @staticmethod
    def calculate_compound_projection(
        baseline_emissions: float,
        baseline_year: int,
        annual_percentage_rate: float,
        target_year: int = 2040,
        projection_horizon_years: int = 25,
        threshold_kgco2e: float = 10000.0 # Residual threshold considered de-minimis net zero
    ) -> Dict[str, Any]:
        """
        Calculates compound annual reduction trajectory:
        E(t) = E0 * (1 - p)^(t - t0)
        """
        trajectory: List[Dict[str, Any]] = []
        p = annual_percentage_rate / 100.0
        projected_net_zero_year = None

        for offset in range(projection_horizon_years + 1):
            y = baseline_year + offset
            e_t = baseline_emissions * math.pow(max(0.0, 1.0 - p), offset)
            if e_t <= threshold_kgco2e and projected_net_zero_year is None:
                projected_net_zero_year = y

            trajectory.append({
                "year": y,
                "emissions_kgco2e": round(e_t, 2),
                "emissions_tonnes_co2e": round(e_t / 1000.0, 2),
                "is_net_zero": e_t <= threshold_kgco2e
            })

        achieves_target_by_deadline = (
            projected_net_zero_year is not None and projected_net_zero_year <= target_year
        )

        return {
            "model_type": "COMPOUND",
            "formula": "E(t) = E0 * (1 - p)^(t - t0)",
            "baseline_emissions_kgco2e": baseline_emissions,
            "baseline_year": baseline_year,
            "target_year": target_year,
            "annual_reduction_percentage": annual_percentage_rate,
            "projected_net_zero_year": projected_net_zero_year,
            "reaches_net_zero": projected_net_zero_year is not None,
            "achieves_target_by_deadline": achieves_target_by_deadline,
            "trajectory": trajectory
        }

projection_engine = ProjectionEngine()

