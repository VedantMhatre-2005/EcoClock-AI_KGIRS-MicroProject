from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.climate.sustainability_metrics import sustainability_metrics

router = APIRouter(prefix="/transport", tags=["Transport"])

@router.get("/summary")
def get_transport_summary(db: Session = Depends(get_db)):
    """Returns commuter passenger-km, trip counts, modal split, and emissions."""
    return sustainability_metrics.get_transport_metrics(db)

