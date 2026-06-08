"""
AETHERIX RL Routing Agent
Reinforcement Learning agent for DTN routing decisions.

This module implements a simplified RL agent for demonstration purposes.
In production, this would use a full Deep Q-Network (DQN) implementation.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RoutingAction(Enum):
    """Possible routing actions for the RL agent."""
    FORWARD = "forward"      # Forward to specified neighbor
    STORE = "store"          # Store locally, defer routing
    DROP = "drop"            # Drop bundle (expired/undeliverable)
    SPLIT = "split"          # Split for multipath routing


@dataclass
class NetworkState:
    """
    State representation for the RL routing agent.

    State space includes:
    - Node position and connectivity
    - Link quality metrics
    - Bundle metadata
    - Buffer occupancy
    """
    current_node: str
    neighbors: List[str]
    link_qualities: Dict[str, float]  # neighbor -> quality (0-1)
    buffer_occupancy: float           # 0-1
    bundle_priority: int              # 0-4
    bundle_size_mb: float
    bundle_deadline_hours: float
    destination_node: str


@dataclass
class RoutingDecision:
    """Result of a routing decision."""
    action: RoutingAction
    next_hop: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""


class RLRoutingAgent:
    """
    Reinforcement Learning Routing Agent for AETHERIX.

    This is a simplified demonstration agent. Key concepts:
    - State: node info, link quality, bundle metadata, buffer status
    - Actions: forward, store, drop, split
    - Reward: delivery success - delay - hops - drops - energy

    In production:
    - Multi-Agent DQN (MADQN) architecture
    - Experience replay with 1M transitions
    - Training on JPL Horizons + historical telemetry
    - Federated learning across network nodes
    """

    # Reward function weights
    ALPHA_DELIVERY = 1.0      # Delivery reward
    BETA_DELAY = 0.001        # Per-second delay penalty
    GAMMA_HOPS = 0.1          # Per-hop penalty
    DELTA_DROPS = 10.0        # Drop penalty
    EPSILON_ENERGY = 0.01     # Per-Wh energy penalty

    # Thresholds
    MIN_LINK_QUALITY = 0.3    # Minimum quality to attempt forward
    HIGH_BUFFER_THRESHOLD = 0.8
    URGENT_PRIORITY = 1       # P0 and P1 are urgent

    def __init__(self, node_id: str, epsilon: float = 0.1):
        """
        Initialize the RL routing agent.

        Args:
            node_id: ID of the node this agent runs on
            epsilon: Exploration rate for epsilon-greedy policy
        """
        self.node_id = node_id
        self.epsilon = epsilon
        self.q_table: Dict[str, Dict[str, float]] = {}
        self.learning_rate = 0.001
        self.discount_factor = 0.99

    def get_state_key(self, state: NetworkState) -> str:
        """Convert state to string key for Q-table lookup."""
        # Discretize continuous values
        buffer_level = "high" if state.buffer_occupancy > 0.7 else "low"
        if not state.link_qualities:
            link_level = "none"
        else:
            best_link = max(state.link_qualities.values())
            link_level = "good" if best_link > 0.5 else "poor"
        priority_level = "urgent" if state.bundle_priority <= self.URGENT_PRIORITY else "normal"

        return f"{state.current_node}|{buffer_level}|{link_level}|{priority_level}"

    def select_action(self, state: NetworkState) -> RoutingDecision:
        """
        Select routing action using epsilon-greedy policy.

        Args:
            state: Current network state

        Returns:
            RoutingDecision with action and next hop
        """
        # Handle edge cases
        if not state.neighbors:
            return RoutingDecision(
                action=RoutingAction.STORE,
                confidence=1.0,
                reasoning="No neighbors available, storing locally"
            )

        # Check if destination is a direct neighbor
        if state.destination_node in state.neighbors:
            quality = state.link_qualities.get(state.destination_node, 0)
            if quality >= self.MIN_LINK_QUALITY:
                return RoutingDecision(
                    action=RoutingAction.FORWARD,
                    next_hop=state.destination_node,
                    confidence=0.95,
                    reasoning=f"Destination reachable directly, quality={quality:.2f}"
                )

        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            return self._explore(state)

        # Exploit: use learned policy
        return self._exploit(state)

    def _explore(self, state: NetworkState) -> RoutingDecision:
        """Random exploration action."""
        actions = [RoutingAction.FORWARD, RoutingAction.STORE]

        if state.buffer_occupancy > self.HIGH_BUFFER_THRESHOLD:
            actions.append(RoutingAction.DROP)

        action = random.choice(actions)

        if action == RoutingAction.FORWARD:
            # Select random neighbor with acceptable link quality
            valid_neighbors = [
                n for n, q in state.link_qualities.items()
                if q >= self.MIN_LINK_QUALITY
            ]
            if valid_neighbors:
                next_hop = random.choice(valid_neighbors)
                return RoutingDecision(
                    action=action,
                    next_hop=next_hop,
                    confidence=0.3,
                    reasoning=f"Exploration: random forward to {next_hop}"
                )
            else:
                action = RoutingAction.STORE

        return RoutingDecision(
            action=action,
            confidence=0.3,
            reasoning=f"Exploration: {action.value}"
        )

    def _exploit(self, state: NetworkState) -> RoutingDecision:
        """Exploit learned policy to select best action."""
        # Simplified policy based on heuristics
        # In production, this would query the neural network

        # Priority-based decision
        if state.bundle_priority <= self.URGENT_PRIORITY:
            # Urgent: find fastest path
            return self._find_fastest_forward(state)

        # Buffer management
        if state.buffer_occupancy > self.HIGH_BUFFER_THRESHOLD:
            if state.bundle_priority >= 3:  # Low priority
                return RoutingDecision(
                    action=RoutingAction.DROP,
                    confidence=0.7,
                    reasoning="High buffer, dropping low-priority bundle"
                )

        # Normal routing: balance quality and progress
        return self._find_best_forward(state)

    def _find_fastest_forward(self, state: NetworkState) -> RoutingDecision:
        """Find the neighbor with best link quality for urgent bundles."""
        if not state.link_qualities:
            return RoutingDecision(
                action=RoutingAction.STORE,
                confidence=0.5,
                reasoning="No link quality data, storing"
            )

        # Sort neighbors by link quality
        sorted_neighbors = sorted(
            state.link_qualities.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for neighbor, quality in sorted_neighbors:
            if quality >= self.MIN_LINK_QUALITY:
                return RoutingDecision(
                    action=RoutingAction.FORWARD,
                    next_hop=neighbor,
                    confidence=0.8,
                    reasoning=f"Urgent bundle: best link to {neighbor} (q={quality:.2f})"
                )

        return RoutingDecision(
            action=RoutingAction.STORE,
            confidence=0.6,
            reasoning="No acceptable links for urgent bundle, storing"
        )

    def _find_best_forward(self, state: NetworkState) -> RoutingDecision:
        """Find best neighbor considering multiple factors."""
        if not state.link_qualities:
            return RoutingDecision(
                action=RoutingAction.STORE,
                confidence=0.5,
                reasoning="No link quality data available"
            )

        # Score each neighbor
        scores = {}
        for neighbor, quality in state.link_qualities.items():
            if quality < self.MIN_LINK_QUALITY:
                continue

            # Simple scoring: link quality + progress toward destination
            # In production, this would use the trained Q-values
            score = quality * 0.7  # Link quality component

            # Prefer neighbors that are "closer" to destination
            # (simplified: check if neighbor name suggests progress)
            if "earth" in state.destination_node and "earth" in neighbor:
                score += 0.2
            elif "mars" in state.destination_node and "mars" in neighbor:
                score += 0.2
            elif "transit" in neighbor:
                score += 0.1  # Relay nodes are often good choices

            scores[neighbor] = score

        if not scores:
            return RoutingDecision(
                action=RoutingAction.STORE,
                confidence=0.5,
                reasoning="No acceptable neighbors found"
            )

        best_neighbor = max(scores, key=scores.get)
        return RoutingDecision(
            action=RoutingAction.FORWARD,
            next_hop=best_neighbor,
            confidence=0.75,
            reasoning=f"Best score for {best_neighbor} (score={scores[best_neighbor]:.2f})"
        )

    def calculate_reward(self, delivered: bool, delay_seconds: float,
                         hops: int, dropped: bool, energy_wh: float) -> float:
        """
        Calculate reward for a completed routing episode.

        Reward function: R = α(delivered) - β(delay) - γ(hops) - δ(drops) - ε(energy)

        Args:
            delivered: Whether bundle was successfully delivered
            delay_seconds: Total end-to-end delay
            hops: Number of hops taken
            dropped: Whether bundle was dropped
            energy_wh: Total energy consumed (watt-hours)

        Returns:
            Calculated reward value
        """
        reward = 0.0

        if delivered:
            reward += self.ALPHA_DELIVERY

        reward -= self.BETA_DELAY * delay_seconds
        reward -= self.GAMMA_HOPS * hops

        if dropped:
            reward -= self.DELTA_DROPS

        reward -= self.EPSILON_ENERGY * energy_wh

        return reward

    def update(self, state: NetworkState, action: RoutingAction,
               reward: float, next_state: Optional[NetworkState]):
        """
        Update Q-values based on experience.

        In production, this would update the neural network weights.
        Here we use a simple tabular Q-learning update.
        """
        state_key = self.get_state_key(state)
        action_key = action.value

        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if action_key not in self.q_table[state_key]:
            self.q_table[state_key][action_key] = 0.0

        # Q-learning update
        current_q = self.q_table[state_key][action_key]

        if next_state is None:
            # Terminal state
            max_next_q = 0
        else:
            next_state_key = self.get_state_key(next_state)
            if next_state_key in self.q_table:
                max_next_q = max(self.q_table[next_state_key].values())
            else:
                max_next_q = 0

        # Q-learning formula
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[state_key][action_key] = new_q


# Example usage
if __name__ == "__main__":
    # Create agent for a Mars relay node
    agent = RLRoutingAgent(node_id="mars.areo.alpha", epsilon=0.1)

    # Create example state
    state = NetworkState(
        current_node="mars.areo.alpha",
        neighbors=["mars.polar.gamma", "transit.esl4.relay", "mars.surface.rover-01"],
        link_qualities={
            "mars.polar.gamma": 0.85,
            "transit.esl4.relay": 0.72,
            "mars.surface.rover-01": 0.95
        },
        buffer_occupancy=0.35,
        bundle_priority=2,
        bundle_size_mb=500.0,
        bundle_deadline_hours=24.0,
        destination_node="earth.control.moc"
    )

    # Get routing decision
    decision = agent.select_action(state)

    print(f"Current Node: {state.current_node}")
    print(f"Destination: {state.destination_node}")
    print(f"Decision: {decision.action.value}")
    print(f"Next Hop: {decision.next_hop}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"Reasoning: {decision.reasoning}")
