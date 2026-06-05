import sys
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.infrastructure.link_budget import LinkBudgetCalculator
from ..database import get_db
from ..models.models import LinkBudgetResult
from ..schemas.schemas import LinkBudgetRequest, LinkBudgetResponse

router = APIRouter(prefix="/link-budget", tags=["link-budget"])


@router.post("/optical", response_model=LinkBudgetResponse)
def calculate_optical_link(
    req: LinkBudgetRequest, db: Session = Depends(get_db)
):
    calculator = LinkBudgetCalculator()

    if req.distance_km is not None:
        result = calculator.calculate_optical_link_budget(distance_km=req.distance_km)
    else:
        result = calculator.calculate_mars_earth_link(scenario=req.scenario)

    row = LinkBudgetResult(
        link_type="optical",
        scenario=req.scenario,
        distance_km=result.distance_km,
        free_space_loss_db=result.free_space_loss_db,
        eirp_dbm=result.eirp_dbm,
        received_power_dbm=result.received_power_dbm,
        link_margin_db=result.link_margin_db,
        data_rate_mbps=result.data_rate_mbps,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/rf/{band}", response_model=LinkBudgetResponse)
def calculate_rf_link(band: str, req: LinkBudgetRequest, db: Session = Depends(get_db)):
    try:
        from src.infrastructure.rf_link_budget import RFSpaceLossModel
    except ImportError:
        raise HTTPException(status_code=501, detail="RF link budget module not available")

    valid_bands = ("ka", "x", "s", "uhf")
    if band.lower() not in valid_bands:
        raise HTTPException(status_code=400, detail=f"Band must be one of {valid_bands}")

    model = RFSpaceLossModel()
    distance = req.distance_km or 225_000_000
    loss = model.calculate_free_space_loss(distance_km=distance, band=band.lower())

    row = LinkBudgetResult(
        link_type=f"rf_{band.lower()}",
        scenario=req.scenario,
        distance_km=distance,
        free_space_loss_db=loss,
        eirp_dbm=0,
        received_power_dbm=0,
        link_margin_db=0,
        data_rate_mbps=0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/history", response_model=list[LinkBudgetResponse])
def link_budget_history(limit: int = 50, db: Session = Depends(get_db)):
    rows = (
        db.query(LinkBudgetResult)
        .order_by(LinkBudgetResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return rows
