import sys
import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from orbital.contact_windows import (
    calculate_earth_mars_distance,
    calculate_light_time,
    get_distance_timeline,
    predict_contact_windows,
)
from ..database import get_db
from ..models.models import ContactWindowRecord
from ..schemas.schemas import (
    ContactWindowRequest,
    ContactWindowResponse,
    DistanceTimelineResponse,
)

router = APIRouter(prefix="/orbital", tags=["orbital"])


@router.get("/distance")
def get_distance(true_anomaly_deg: float = 0.0):
    dist = calculate_earth_mars_distance(true_anomaly_deg)
    delay = calculate_light_time(dist)
    return {
        "true_anomaly_deg": true_anomaly_deg,
        "distance_km": dist,
        "light_time_seconds": delay,
        "light_time_minutes": delay / 60,
    }


@router.get("/timeline", response_model=DistanceTimelineResponse)
def distance_timeline(num_points: int = 780):
    raw = get_distance_timeline(num_points=num_points)
    distances = []
    for entry in raw:
        if isinstance(entry, dict):
            distances.append({"day": entry["day"], "distance_km": entry["distance_km"], "light_time_min": entry["light_time_min"]})
        else:
            day, dist_km, lt_min = entry
            distances.append({"day": day, "distance_km": dist_km, "light_time_min": lt_min})
    dists = [d["distance_km"] for d in distances]
    if not dists:
        return DistanceTimelineResponse(
            distances=[], min_distance_km=0, max_distance_km=0, avg_distance_km=0
        )
    return DistanceTimelineResponse(
        distances=distances,
        min_distance_km=min(dists),
        max_distance_km=max(dists),
        avg_distance_km=sum(dists) / len(dists),
    )


@router.post("/contact-windows", response_model=list[ContactWindowResponse])
def compute_contact_windows(
    req: ContactWindowRequest, db: Session = Depends(get_db)
):
    windows = predict_contact_windows(
        duration_days=req.duration_days,
        min_elevation_deg=req.min_elevation_deg,
    )

    records = []
    for w in windows:
        rec = ContactWindowRecord(
            start_time_jd=w.start_time_jd,
            end_time_jd=w.end_time_jd,
            duration_hours=w.duration_hours,
            max_elevation_deg=w.max_elevation_deg,
            average_distance_km=w.average_distance_km,
            max_data_rate_mbps=w.max_data_rate_mbps,
            window_type=w.window_type,
        )
        db.add(rec)
        records.append(rec)
    db.commit()

    for rec in records:
        db.refresh(rec)
    return records


@router.get("/contact-windows/history", response_model=list[ContactWindowResponse])
def contact_window_history(limit: int = 50, db: Session = Depends(get_db)):
    limit = min(limit, 1000)
    rows = (
        db.query(ContactWindowRecord)
        .order_by(ContactWindowRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return rows
