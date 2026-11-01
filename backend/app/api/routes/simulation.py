from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.api.dependencies import get_db
from app.simulation.scenario_engine import scenario_engine
from app.simulation.scenario_comparator import scenario_comparator

router = APIRouter(prefix="/simulations", tags=["Simulation"])

class RunSimulationRequest(BaseModel):
    scenario_type: str = Field(..., description="SOLAR, TRANSPORT, WASTE, WATER, or COMBINED")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class SaveSimulationRequest(BaseModel):
    name: str = Field(..., description="Custom name for the saved scenario")
    scenario_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

@router.get("")
def list_saved_simulations(db: Session = Depends(get_db)):
    """Lists saved simulation scenarios for multi-scenario comparison."""
    return scenario_comparator.list_scenarios(db)

@router.post("/run")
def run_simulation(payload: RunSimulationRequest, db: Session = Depends(get_db)):
    """Runs deterministic Python calculation for a proposed sustainability scenario."""
    return scenario_engine.run_scenario(
        db=db,
        scenario_type=payload.scenario_type.upper(),
        parameters=payload.parameters
    )

@router.post("/save")
def save_simulation(payload: SaveSimulationRequest, db: Session = Depends(get_db)):
    """Executes and persists a named simulation scenario."""
    return scenario_comparator.save_scenario(
        db=db,
        name=payload.name,
        scenario_type=payload.scenario_type.upper(),
        parameters=payload.parameters
    )

@router.delete("/{simulation_id}")
def delete_simulation(simulation_id: str, db: Session = Depends(get_db)):
    """Deletes a saved simulation scenario."""
    success = scenario_comparator.delete_scenario(db, simulation_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Scenario '{simulation_id}' not found.")
    return {"deleted": True, "simulation_id": simulation_id}

