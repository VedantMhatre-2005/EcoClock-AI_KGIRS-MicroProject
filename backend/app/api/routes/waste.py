from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.climate.sustainability_metrics import sustainability_metrics

router = APIRouter(prefix="/waste", tags=["Waste"])

@router.get("/summary")
def get_waste_summary(db: Session = Depends(get_db)):
    """Returns solid waste generation, recycling, composting, and landfill diversion."""
    return sustainability_metrics.get_waste_metrics(db)

