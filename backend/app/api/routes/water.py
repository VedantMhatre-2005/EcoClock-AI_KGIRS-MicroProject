from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.climate.sustainability_metrics import sustainability_metrics

router = APIRouter(prefix="/water", tags=["Water"])

@router.get("/summary")
def get_water_summary(db: Session = Depends(get_db)):
    """Returns water consumption, rainwater harvesting yield, and building breakdown."""
    return sustainability_metrics.get_water_metrics(db)

