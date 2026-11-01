from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.climate.sustainability_metrics import sustainability_metrics

router = APIRouter(prefix="/energy", tags=["Energy"])

@router.get("/summary")
def get_energy_summary(db: Session = Depends(get_db)):
    """Returns total electricity, solar generation, grid consumption, and building breakdown."""
    return sustainability_metrics.get_energy_metrics(db)

