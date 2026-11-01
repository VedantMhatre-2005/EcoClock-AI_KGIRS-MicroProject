from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.climate.carbon_calculator import carbon_calculator
from app.climate.projection_engine import projection_engine

class ClimateClockService:
    @staticmethod
    def get_clock_state(db: Session, target_date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Computes dynamic College Climate Clock parameters backed by persisted data.
        """
        target_str = target_date_str or settings.CLIMATE_TARGET_DATE
        target_dt = datetime.strptime(target_str, "%Y-%m-%d")
        now = datetime.utcnow()

        # Compute remaining duration
        if target_dt > now:
            time_diff = target_dt - now
            days = time_diff.days
            seconds = time_diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            years = days // 365
            remaining_days = days % 365
            months = remaining_days // 30
            rem_days = remaining_days % 30
            is_passed = False
        else:
            years = months = rem_days = hours = minutes = secs = 0
            is_passed = True

        # Inventory baseline (2024) and current (2025)
        baseline_inv = carbon_calculator.get_annual_inventory(db, year=settings.BASELINE_YEAR)
        current_inv = carbon_calculator.get_annual_inventory(db, year=2025)

        e0 = baseline_inv["total_emissions_kgco2e"]
        e_curr = current_inv["total_emissions_kgco2e"]
        annual_reduction = max(0.0, round(e0 - e_curr, 2))

        # Project achievement year under linear model
        target_year = target_dt.year
        proj = projection_engine.calculate_linear_projection(
            baseline_emissions=e0,
            baseline_year=settings.BASELINE_YEAR,
            annual_reduction_rate_kg=annual_reduction if annual_reduction > 0 else 153125.0, # Required rate
            target_year=target_year
        )

        return {
            "institution_clock": {
                "institution_name": settings.INSTITUTION_NAME,
                "target_date": target_str,
                "target_year": target_year,
                "baseline_year": settings.BASELINE_YEAR,
                "baseline_emissions_kgco2e": e0,
                "baseline_emissions_tonnes_co2e": round(e0 / 1000.0, 2),
                "current_annual_emissions_kgco2e": e_curr,
                "current_annual_emissions_tonnes_co2e": round(e_curr / 1000.0, 2),
                "annual_reduction_kgco2e": annual_reduction,
                "annual_reduction_tonnes_co2e": round(annual_reduction / 1000.0, 2),
                "projected_net_zero_year": proj["projected_net_zero_year"],
                "achieves_target_by_deadline": proj["achieves_target_by_deadline"],
                "countdown": {
                    "years": years,
                    "months": months,
                    "days": rem_days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": secs,
                    "total_days": days if not is_passed else 0,
                    "is_target_reached": is_passed
                },
                "data_source_type": "SYNTHETIC_PERSISTED",
                "methodology_notes": "Based on Scope 1, 2, and 3 accounting for VESIT Green Campus. Calculated using linear decarbonization trajectory from 2024 baseline."
            },
            "global_context_clock": {
                "status": "UNAVAILABLE",
                "message": "Global climate-budget countdown requires a configured external real-time IPCC/MCC API. No external unverified data is fabricated.",
                "external_source_configured": False
            }
        }

climate_clock_service = ClimateClockService()

