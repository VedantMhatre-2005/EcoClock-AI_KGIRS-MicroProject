from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.api.dependencies import get_db
from app.climate.climate_clock import climate_clock_service
from app.climate.projection_engine import projection_engine
from app.climate.target_manager import target_manager
from app.climate.carbon_calculator import carbon_calculator
from app.config import settings

router = APIRouter(prefix="/climate", tags=["Climate"])

class TargetUpdateRequest(BaseModel):
    id: str
    title: str
    category: str = "CARBON"
    target_year: int = 2040
    target_value: float = 0.0
    baseline_value: float = 2450000.0
    unit: str = "kg CO2e/year"
    status: str = "IN_PROGRESS"

@router.get("/clock")
def get_climate_clock(
    target_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """Returns dynamic Institutional Climate Clock countdown and Global Context state."""
    target_val = target_date if isinstance(target_date, str) else None
    return climate_clock_service.get_clock_state(db, target_date_str=target_val)

@router.get("/projection")
def get_climate_projection(
    model: str = Query("LINEAR", description="LINEAR or COMPOUND"),
    target_year: int = Query(2040),
    annual_rate: Optional[float] = Query(None, description="Annual kg reduction for linear, or % for compound"),
    db: Session = Depends(get_db)
):
    """Computes transparent mathematical decarbonization projection."""
    inv = carbon_calculator.get_annual_inventory(db, year=settings.BASELINE_YEAR)
    baseline_emissions = inv["total_emissions_kgco2e"]

    if model.upper() == "COMPOUND":
        rate_pct = annual_rate if annual_rate is not None else 14.5
        return projection_engine.calculate_compound_projection(
            baseline_emissions=baseline_emissions,
            baseline_year=settings.BASELINE_YEAR,
            annual_percentage_rate=rate_pct,
            target_year=target_year
        )
    else:
        rate_kg = annual_rate if annual_rate is not None else 153125.0
        return projection_engine.calculate_linear_projection(
            baseline_emissions=baseline_emissions,
            baseline_year=settings.BASELINE_YEAR,
            annual_reduction_rate_kg=rate_kg,
            target_year=target_year
        )

@router.post("/targets")
def update_target(payload: TargetUpdateRequest, db: Session = Depends(get_db)):
    """Updates or creates an institutional sustainability target."""
    return target_manager.update_or_create_target(
        db=db,
        target_id=payload.id,
        title=payload.title,
        category=payload.category,
        target_year=payload.target_year,
        target_value=payload.target_value,
        baseline_value=payload.baseline_value,
        unit=payload.unit,
        status=payload.status
    )
