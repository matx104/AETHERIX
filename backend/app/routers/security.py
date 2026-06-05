import sys
import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.security.qkd import BB84Protocol, E91Protocol
from ..database import get_db
from ..models.models import QKDSession
from ..schemas.schemas import QKDRequest, QKDResponse

router = APIRouter(prefix="/security", tags=["security"])


@router.post("/qkd", response_model=QKDResponse)
def run_qkd(req: QKDRequest, db: Session = Depends(get_db)):
    effective_error = req.channel_error
    if req.eavesdropper:
        effective_error = max(req.channel_error, 0.15)

    if req.protocol.lower() == "e91":
        proto = E91Protocol(num_pairs=req.num_qubits, channel_error=effective_error)
    else:
        proto = BB84Protocol(num_qubits=req.num_qubits, channel_error=effective_error)
    result = proto.execute()

    session = QKDSession(
        protocol=req.protocol.lower(),
        num_qubits=req.num_qubits,
        channel_error=req.channel_error,
        eavesdropper=req.eavesdropper,
        qber=result.qber,
        secure=result.secure,
        sifted_key_length=result.sifted_key_length,
        efficiency=result.efficiency,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return QKDResponse(
        id=session.id,
        protocol=session.protocol,
        num_qubits=session.num_qubits,
        channel_error=session.channel_error,
        eavesdropper=session.eavesdropper,
        qber=result.qber,
        secure=result.secure,
        sifted_key_length=result.sifted_key_length,
        efficiency=result.efficiency,
        alice_key=result.alice_key[:32],
        bob_key=result.bob_key[:32],
        created_at=session.created_at,
    )


@router.get("/qkd/sessions", response_model=list[QKDResponse])
def qkd_sessions(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(QKDSession).order_by(QKDSession.created_at.desc()).limit(limit).all()
    return rows
