import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.database.schema import SDGModel, SustainabilityInitiativeModel

router = APIRouter(prefix="/sdg", tags=["SDG"])

@router.get("")
def list_sdgs(db: Session = Depends(get_db)):
    """Returns all 17 UN Sustainable Development Goals with connected initiative counts."""
    sdgs = db.query(SDGModel).order_by(SDGModel.sdg_number).all()
    initiatives = db.query(SustainabilityInitiativeModel).all()

    result = []
    for s in sdgs:
        linked_inits = [
            {
                "id": init.id,
                "name": init.name,
                "status": init.status,
                "carbon_reduction_estimate_kgco2e": init.carbon_reduction_estimate_kgco2e
            }
            for init in initiatives
            if s.id in json.loads(init.sdg_ids_json)
        ]

        result.append({
            "id": s.id,
            "sdg_number": s.sdg_number,
            "name": s.name,
            "description": s.description,
            "color": s.color,
            "initiative_count": len(linked_inits),
            "initiatives": linked_inits,
            "has_initiatives": len(linked_inits) > 0
        })

    return result

@router.get("/{sdg_id}")
def get_sdg_details(sdg_id: str, db: Session = Depends(get_db)):
    """Returns detailed information and supporting initiatives for a specific SDG."""
    sdg = db.query(SDGModel).filter(
        (SDGModel.id == sdg_id.upper()) | (SDGModel.sdg_number == (int(sdg_id) if sdg_id.isdigit() else -1))
    ).first()

    if not sdg:
        raise HTTPException(status_code=404, detail=f"SDG '{sdg_id}' not found.")

    initiatives = db.query(SustainabilityInitiativeModel).all()
    linked_inits = [
        {
            "id": init.id,
            "name": init.name,
            "description": init.description,
            "lead_department": init.lead_department,
            "status": init.status,
            "carbon_reduction_estimate_kgco2e": init.carbon_reduction_estimate_kgco2e
        }
        for init in initiatives
        if sdg.id in json.loads(init.sdg_ids_json)
    ]

    return {
        "id": sdg.id,
        "sdg_number": sdg.sdg_number,
        "name": sdg.name,
        "description": sdg.description,
        "color": sdg.color,
        "initiative_count": len(linked_inits),
        "initiatives": linked_inits
    }

