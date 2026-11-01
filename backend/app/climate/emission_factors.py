from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.schema import EmissionFactorModel

class EmissionFactorManager:
    @staticmethod
    def get_all_factors(db: Session) -> List[Dict[str, Any]]:
        factors = db.query(EmissionFactorModel).all()
        return [
            {
                "id": f.id,
                "category": f.category,
                "name": f.name,
                "value": f.value,
                "unit": f.unit,
                "reference_year": f.reference_year,
                "region": f.region,
                "source": f.source,
                "source_type": f.source_type,
                "version": f.version
            }
            for f in factors
        ]

    @staticmethod
    def get_factor(db: Session, factor_id: str) -> Optional[Dict[str, Any]]:
        f = db.query(EmissionFactorModel).filter(EmissionFactorModel.id == factor_id).first()
        if not f:
            return None
        return {
            "id": f.id,
            "category": f.category,
            "name": f.name,
            "value": f.value,
            "unit": f.unit,
            "reference_year": f.reference_year,
            "region": f.region,
            "source": f.source,
            "source_type": f.source_type,
            "version": f.version
        }

