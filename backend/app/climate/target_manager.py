from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.schema import SustainabilityTargetModel

class TargetManager:
    @staticmethod
    def get_all_targets(db: Session) -> List[Dict[str, Any]]:
        targets = db.query(SustainabilityTargetModel).all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "category": t.category,
                "baseline_year": t.baseline_year,
                "target_year": t.target_year,
                "baseline_value": t.baseline_value,
                "target_value": t.target_value,
                "unit": t.unit,
                "status": t.status,
                "source_type": t.source_type
            }
            for t in targets
        ]

    @staticmethod
    def update_or_create_target(
        db: Session,
        target_id: str,
        title: str,
        category: str,
        target_year: int,
        target_value: float,
        baseline_value: float,
        unit: str,
        baseline_year: int = 2024,
        status: str = "IN_PROGRESS"
    ) -> Dict[str, Any]:
        target = db.query(SustainabilityTargetModel).filter(SustainabilityTargetModel.id == target_id).first()
        if not target:
            target = SustainabilityTargetModel(
                id=target_id,
                title=title,
                category=category,
                baseline_year=baseline_year,
                target_year=target_year,
                baseline_value=baseline_value,
                target_value=target_value,
                unit=unit,
                status=status,
                source_type="USER_DEFINED"
            )
            db.add(target)
        else:
            target.title = title
            target.category = category
            target.target_year = target_year
            target.target_value = target_value
            target.baseline_value = baseline_value
            target.unit = unit
            target.status = status
            target.source_type = "USER_DEFINED"

        db.commit()
        return {
            "id": target.id,
            "title": target.title,
            "category": target.category,
            "target_year": target.target_year,
            "target_value": target.target_value,
            "unit": target.unit,
            "status": target.status
        }

target_manager = TargetManager()

