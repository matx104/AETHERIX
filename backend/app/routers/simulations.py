import json
import sys
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from ..database import get_db
from ..models.models import SimulationRun
from ..schemas.schemas import SimulationRunCreate, SimulationRunResponse

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.get("/", response_model=list[SimulationRunResponse])
def list_simulations(db: Session = Depends(get_db)):
    runs = db.query(SimulationRun).order_by(SimulationRun.created_at.desc()).all()
    result = []
    for r in runs:
        resp = SimulationRunResponse(
            id=r.id,
            name=r.name,
            scenario=r.scenario,
            status=r.status,
            created_at=r.created_at,
            completed_at=r.completed_at,
            result=json.loads(r.result_json) if r.result_json else None,
            seed=r.seed,
        )
        result.append(resp)
    return result


@router.post("/", response_model=SimulationRunResponse, status_code=201)
def create_simulation(run_in: SimulationRunCreate, db: Session = Depends(get_db)):
    run = SimulationRun(
        name=run_in.name,
        scenario=run_in.scenario,
        status="pending",
        config_json=json.dumps(run_in.config) if run_in.config else None,
        seed=run_in.seed,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return SimulationRunResponse(
        id=run.id,
        name=run.name,
        scenario=run.scenario,
        status=run.status,
        created_at=run.created_at,
        completed_at=run.completed_at,
        seed=run.seed,
    )


@router.get("/{run_id}", response_model=SimulationRunResponse)
def get_simulation(run_id: str, db: Session = Depends(get_db)):
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return SimulationRunResponse(
        id=run.id,
        name=run.name,
        scenario=run.scenario,
        status=run.status,
        created_at=run.created_at,
        completed_at=run.completed_at,
        result=json.loads(run.result_json) if run.result_json else None,
        seed=run.seed,
    )


@router.delete("/{run_id}", status_code=204)
def delete_simulation(run_id: str, db: Session = Depends(get_db)):
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    db.delete(run)
    db.commit()
