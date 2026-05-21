"""
AETHERIX Multi-Agent Distributed Learning Framework
Federated learning across DTN routing nodes.
"""

import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from routing.rl_agent import NetworkState, RLRoutingAgent, RoutingAction
from routing.training import Experience, ExperienceReplay


@dataclass
class AgentInfo:
    agent: RLRoutingAgent
    node_id: str
    experiences: ExperienceReplay
    total_reward: float = 0.0
    episodes_completed: int = 0


@dataclass
class FederatedLearningConfig:
    num_agents: int = 10
    sharing_interval: int = 50
    sharing_ratio: float = 0.1
    min_experiences_for_sharing: int = 100


class MultiAgentCoordinator:
    def __init__(self, config: FederatedLearningConfig):
        self._config = config
        self._agents: Dict[str, AgentInfo] = {}
        self._shared_pool: ExperienceReplay = ExperienceReplay(
            capacity=config.num_agents * 5000
        )

    def create_agents(self, node_ids: List[str]) -> None:
        for node_id in node_ids:
            agent = RLRoutingAgent(node_id=node_id, epsilon=0.1)
            self._agents[node_id] = AgentInfo(
                agent=agent,
                node_id=node_id,
                experiences=ExperienceReplay(capacity=10000),
            )

    def get_agent(self, node_id: str) -> Optional[RLRoutingAgent]:
        info = self._agents.get(node_id)
        return info.agent if info else None

    def share_experiences(self) -> None:
        eligible = {
            nid: info
            for nid, info in self._agents.items()
            if len(info.experiences) >= self._config.min_experiences_for_sharing
        }

        for nid, info in eligible.items():
            num_to_share = max(
                1,
                int(len(info.experiences) * self._config.sharing_ratio),
            )
            shared = info.experiences.sample(num_to_share)
            for exp in shared:
                self._shared_pool.push(exp)

        if len(self._shared_pool) == 0:
            return

        for nid, info in self._agents.items():
            sample_size = max(
                1,
                int(len(self._shared_pool) * self._config.sharing_ratio),
            )
            for exp in self._shared_pool.sample(sample_size):
                info.experiences.push(exp)

    def aggregate_q_tables(self) -> Dict[str, Dict[str, float]]:
        state_action_values: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for info in self._agents.values():
            for state_key, actions in info.agent.q_table.items():
                for action_key, value in actions.items():
                    state_action_values[state_key][action_key].append(value)

        aggregated: Dict[str, Dict[str, float]] = {}
        for state_key, actions in state_action_values.items():
            aggregated[state_key] = {}
            for action_key, values in actions.items():
                aggregated[state_key][action_key] = sum(values) / len(values)

        return aggregated

    def distribute_aggregated(
        self, aggregated: Dict[str, Dict[str, float]]
    ) -> None:
        for info in self._agents.values():
            for state_key, actions in aggregated.items():
                if state_key not in info.agent.q_table:
                    info.agent.q_table[state_key] = {}
                for action_key, avg_value in actions.items():
                    current = info.agent.q_table[state_key].get(action_key, 0.0)
                    info.agent.q_table[state_key][action_key] = (
                        current + avg_value
                    ) / 2.0

    def federated_round(self) -> None:
        self.share_experiences()
        aggregated = self.aggregate_q_tables()
        self.distribute_aggregated(aggregated)

    def get_agent_count(self) -> int:
        return len(self._agents)

    def get_total_experiences(self) -> int:
        return sum(len(info.experiences) for info in self._agents.values())
