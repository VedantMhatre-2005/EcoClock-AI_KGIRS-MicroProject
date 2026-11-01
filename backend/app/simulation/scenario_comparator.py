import json
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.schema import SimulationRecord
from app.simulation.scenario_engine import scenario_engine

class ScenarioComparator:
    @staticmethod
    def save_scenario(
        db: Session,
        name: str,
        scenario_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Runs simulation and saves results as a persistent record."""
        sim_res = scenario_engine.run_scenario(db, scenario_type, parameters)
        record_id = f"SIM_{uuid.uuid4().hex[:8]}"

        sim_rec = SimulationRecord(
            id=record_id,
            name=name,
            scenario_type=scenario_type,
            parameters_json=json.dumps(parameters),
            baseline_emissions_kgco2e=sim_res["baseline_emissions_kgco2e"],
            projected_emissions_kgco2e=sim_res["projected_emissions_kgco2e"],
            reduction_kgco2e=sim_res["reduction_kgco2e"],
            percentage_reduction=sim_res["percentage_reduction"],
            resource_savings_json=json.dumps(sim_res["resource_savings"])
        )
        db.add(sim_rec)
        db.commit()

        return {
            "id": record_id,
            "name": name,
            **sim_res
        }

    @staticmethod
    def list_scenarios(db: Session) -> List[Dict[str, Any]]:
        records = db.query(SimulationRecord).order_by(SimulationRecord.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "scenario_type": r.scenario_type,
                "parameters": json.loads(r.parameters_json),
                "baseline_emissions_kgco2e": r.baseline_emissions_kgco2e,
                "projected_emissions_kgco2e": r.projected_emissions_kgco2e,
                "reduction_kgco2e": r.reduction_kgco2e,
                "percentage_reduction": r.percentage_reduction,
                "resource_savings": json.loads(r.resource_savings_json),
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]

    @staticmethod
    def delete_scenario(db: Session, scenario_id: str) -> bool:
        record = db.query(SimulationRecord).filter(SimulationRecord.id == scenario_id).first()
        if not record:
            return False
        db.delete(record)
        db.commit()
        return True

scenario_comparator = ScenarioComparator()

