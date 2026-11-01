from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.climate.sustainability_metrics import sustainability_metrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Returns high-level KPI cards for the main campus sustainability overview."""
    return sustainability_metrics.get_dashboard_summary(db)

@router.get("/trends")
def get_dashboard_trends(db: Session = Depends(get_db)):
    """Returns monthly energy, water, and waste trends for dashboard charts."""
    energy_data = sustainability_metrics.get_energy_metrics(db)
    water_data = sustainability_metrics.get_water_metrics(db)
    waste_data = sustainability_metrics.get_waste_metrics(db)

    return {
        "energy_monthly": energy_data["monthly_trends"],
        "water_monthly": water_data["monthly_trends"],
        "waste_monthly": waste_data["monthly_trends"]
    }

