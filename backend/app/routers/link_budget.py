import sys
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from infrastructure.link_budget import LinkBudgetCalculator
from infrastructure.rf_link_budget import (
    KA_BAND_FREQ_HZ,
    RFLinkBudgetCalculator,
    S_BAND_FREQ_HZ,
    UHF_FREQ_HZ,
    X_BAND_FREQ_HZ,
)
from ..database import get_db
from ..models.models import LinkBudgetResult
from ..schemas.schemas import LinkBudgetRequest, LinkBudgetResponse

router = APIRouter(prefix="/link-budget", tags=["link-budget"])

BAND_FREQUENCIES = {
    "ka": KA_BAND_FREQ_HZ,
    "x": X_BAND_FREQ_HZ,
    "s": S_BAND_FREQ_HZ,
    "uhf": UHF_FREQ_HZ,
}


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
    valid_bands = ("ka", "x", "s", "uhf")
    if band.lower() not in valid_bands:
        raise HTTPException(status_code=400, detail=f"Band must be one of {valid_bands}")

    calc = RFLinkBudgetCalculator(BAND_FREQUENCIES[band.lower()])

    if req.distance_km is not None:
        result = calc.calculate_rf_link_budget(
            distance_km=req.distance_km,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
        )
    else:
        result = calc.calculate_mars_earth_link(scenario=req.scenario)

    row = LinkBudgetResult(
        link_type=f"rf_{band.lower()}",
        scenario=req.scenario,
        distance_km=result.distance_km,
        free_space_loss_db=result.free_space_loss_db,
        eirp_dbm=result.eirp_dbm,
        received_power_dbm=result.received_power_dbm,
        link_margin_db=result.link_margin_db,
        data_rate_mbps=result.data_rate_bps / 1e6,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/history", response_model=list[LinkBudgetResponse])
def link_budget_history(limit: int = 50, db: Session = Depends(get_db)):
    limit = min(limit, 1000)
    rows = (
        db.query(LinkBudgetResult)
        .order_by(LinkBudgetResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return rows
