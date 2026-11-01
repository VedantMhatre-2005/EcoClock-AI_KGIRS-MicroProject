from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.climate.carbon_calculator import carbon_calculator
from app.climate.sustainability_metrics import sustainability_metrics

router = APIRouter(prefix="/emissions", tags=["Emissions"])

@router.get("/summary")
def get_emissions_summary(
    year: int = Query(2024, description="Reporting year"),
    db: Session = Depends(get_db)
):
    """Returns annual greenhouse gas emission inventory by Scope 1, 2, and 3."""
    return carbon_calculator.get_annual_inventory(db, year=year)

@router.get("/trends")
def get_emissions_trends(db: Session = Depends(get_db)):
    """Returns 24-month category emissions trends and annual comparisons."""
    inv_2024 = carbon_calculator.get_annual_inventory(db, year=2024)
    inv_2025 = carbon_calculator.get_annual_inventory(db, year=2025)
    energy_data = sustainability_metrics.get_energy_metrics(db)
    waste_data = sustainability_metrics.get_waste_metrics(db)

    return {
        "annual_comparison": {
            "2024": inv_2024,
            "2025": inv_2025
        },
        "monthly_grid_emissions": [
            {"date": m["date"], "emissions_kgco2e": m["emissions_kgco2e"]}
            for m in energy_data["monthly_trends"]
        ],
        "monthly_waste_emissions": [
            {"date": m["date"], "emissions_kgco2e": m["emissions_kgco2e"]}
            for m in waste_data["monthly_trends"]
        ]
    }

