import sys
import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from routing.rl_agent import RLRoutingAgent, NetworkState
from ..database import get_db
from ..models.models import RoutingDecisionLog
from ..schemas.schemas import RoutingRequest, RoutingResponse

router = APIRouter(prefix="/routing", tags=["routing"])


@router.post("/decide", response_model=RoutingResponse)
def make_routing_decision(req: RoutingRequest, db: Session = Depends(get_db)):
    agent = RLRoutingAgent(node_id=req.current_node)
    state = NetworkState(
        current_node=req.current_node,
        neighbors=req.neighbors,
        link_qualities=req.link_qualities,
        buffer_occupancy=req.buffer_occupancy,
        bundle_priority=req.bundle_priority,
        bundle_size_mb=req.bundle_size_mb,
        bundle_deadline_hours=req.bundle_deadline_hours,
        destination_node=req.destination_node,
    )
    decision = agent.select_action(state)

    log = RoutingDecisionLog(
        current_node=req.current_node,
        action=decision.action.value,
        next_hop=decision.next_hop,
        confidence=decision.confidence,
        reward=0.0,
        bundle_priority=req.bundle_priority,
    )
    db.add(log)
    db.commit()

    return RoutingResponse(
        action=decision.action.value,
        next_hop=decision.next_hop,
        confidence=decision.confidence,
        reasoning=decision.reasoning,
    )


@router.get("/decisions", response_model=list[dict])
def list_decisions(limit: int = 100, db: Session = Depends(get_db)):
    limit = min(limit, 1000)
    logs = (
        db.query(RoutingDecisionLog)
        .order_by(RoutingDecisionLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": l.id,
            "current_node": l.current_node,
            "action": l.action,
            "next_hop": l.next_hop,
            "confidence": l.confidence,
            "reward": l.reward,
            "bundle_priority": l.bundle_priority,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


@router.post("/train/step")
def training_step(
    episodes: int = 100,
    epsilon: float = 0.1,
    db: Session = Depends(get_db),
):
    from routing.training import Trainer, TrainingConfig

    config = TrainingConfig(episodes=episodes, epsilon_start=epsilon)
    agent = RLRoutingAgent(node_id="training")
    trainer = Trainer(agent, config)
    metrics = trainer.train()

    return {
        "episodes": episodes,
        "total_episodes": metrics.total_episodes,
        "avg_reward_last_100": metrics.avg_reward_last_100,
        "convergence_episode": metrics.convergence_episode,
    }
