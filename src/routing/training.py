"""
AETHERIX RL Training Loop
Experience replay and convergence tracking for RL routing agent training.
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from routing.rl_agent import (NetworkState, RLRoutingAgent, RoutingAction,
                              RoutingDecision)


@dataclass
class Experience:
    state: NetworkState
    action: RoutingAction
    reward: float
    next_state: Optional[NetworkState]
    done: bool


class ExperienceReplay:
    def __init__(self, capacity: int = 10000):
        self._capacity = capacity
        self._buffer: List[Experience] = []
        self._position = 0

    def push(self, experience: Experience) -> None:
        if len(self._buffer) < self._capacity:
            self._buffer.append(experience)
        else:
            self._buffer[self._position] = experience
        self._position = (self._position + 1) % self._capacity

    def sample(self, batch_size: int) -> List[Experience]:
        return random.sample(self._buffer, min(batch_size, len(self._buffer)))

    def __len__(self) -> int:
        return len(self._buffer)


@dataclass
class TrainingConfig:
    episodes: int = 1000
    max_steps_per_episode: int = 100
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay: float = 0.995
    learning_rate: float = 0.001
    discount_factor: float = 0.99
    replay_capacity: int = 10000
    batch_size: int = 32
    target_update_frequency: int = 100


@dataclass
class TrainingMetrics:
    episode_rewards: List[float] = field(default_factory=list)
    episode_lengths: List[int] = field(default_factory=list)
    epsilon_history: List[float] = field(default_factory=list)
    avg_reward_last_100: float = 0.0
    total_episodes: int = 0
    convergence_episode: Optional[int] = None


class TrainingEnvironment:
    _NODE_IDS = [
        "earth.dsn.goldstone",
        "earth.dsn.madrid",
        "earth.dsn.canberra",
        "earth.geo.relay-01",
        "earth.geo.relay-02",
        "leo.sat-001",
        "leo.sat-002",
        "transit.esl4.relay",
        "transit.esl5.relay",
        "mars.areo.alpha",
        "mars.areo.beta",
        "mars.polar.gamma",
        "mars.surface.base-01",
        "mars.surface.rover-01",
        "mars.surface.drone-01",
    ]

    _DESTINATIONS = [
        "earth.dsn.goldstone",
        "mars.surface.base-01",
        "mars.surface.rover-01",
        "earth.control.moc",
    ]

    def __init__(self, seed: int = 42):
        self._seed = seed
        self._rng = random.Random(seed)
        self._step_count = 0
        self._max_steps = 20

    def reset(self) -> NetworkState:
        self._step_count = 0
        return self._generate_random_state()

    def step(
        self, state: NetworkState, action: RoutingAction
    ) -> Tuple[NetworkState, float, bool]:
        self._step_count += 1

        reward = self._compute_reward(state, action)
        next_state = self._generate_random_state()
        done = self._step_count >= self._max_steps

        if action == RoutingAction.DROP:
            done = True

        return (next_state if not done else None, reward, done)

    def _compute_reward(self, state: NetworkState, action: RoutingAction) -> float:
        if action == RoutingAction.FORWARD:
            if state.link_qualities:
                best_quality = max(state.link_qualities.values())
                if best_quality > 0.6:
                    return 1.0
                elif best_quality > 0.3:
                    return 0.3
                else:
                    return -0.5
            return -0.5

        if action == RoutingAction.STORE:
            has_good_neighbor = any(
                q > 0.6 for q in state.link_qualities.values()
            )
            if not has_good_neighbor:
                return 0.5
            return -0.5

        if action == RoutingAction.DROP:
            if state.bundle_deadline_hours <= 0:
                return 0.0
            return -2.0

        if action == RoutingAction.SPLIT:
            return 0.2

        return 0.0

    def _generate_random_state(self) -> NetworkState:
        node = self._rng.choice(self._NODE_IDS)
        num_neighbors = self._rng.randint(1, 3)
        possible_neighbors = [n for n in self._NODE_IDS if n != node]
        neighbors = self._rng.sample(
            possible_neighbors, min(num_neighbors, len(possible_neighbors))
        )
        link_qualities = {
            n: self._rng.uniform(0.1, 0.95) for n in neighbors
        }
        return NetworkState(
            current_node=node,
            neighbors=neighbors,
            link_qualities=link_qualities,
            buffer_occupancy=self._rng.uniform(0.05, 0.95),
            bundle_priority=self._rng.randint(0, 4),
            bundle_size_mb=self._rng.uniform(10, 1000),
            bundle_deadline_hours=self._rng.uniform(0.5, 48.0),
            destination_node=self._rng.choice(self._DESTINATIONS),
        )


class Trainer:
    def __init__(self, agent: RLRoutingAgent, config: TrainingConfig):
        self._agent = agent
        self._config = config
        self._replay = ExperienceReplay(capacity=config.replay_capacity)
        self._metrics = TrainingMetrics()
        self._epsilon = config.epsilon_start

    def train(self) -> TrainingMetrics:
        env = TrainingEnvironment(seed=42)

        for episode in range(self._config.episodes):
            state = env.reset()
            episode_reward = 0.0
            steps = 0

            for step in range(self._config.max_steps_per_episode):
                action = self._select_action_epsilon_greedy(state)
                next_state, reward, done = env.step(state, action)

                self._replay.push(
                    Experience(
                        state=state,
                        action=action,
                        reward=reward,
                        next_state=next_state,
                        done=done,
                    )
                )

                episode_reward += reward
                steps += 1

                if len(self._replay) >= self._config.batch_size:
                    batch = self._replay.sample(self._config.batch_size)
                    self._update_from_batch(batch)

                state = next_state if next_state is not None else env.reset()

                if done:
                    break

            self._epsilon = max(
                self._config.epsilon_end,
                self._epsilon * self._config.epsilon_decay,
            )
            self._agent.epsilon = self._epsilon

            self._metrics.episode_rewards.append(episode_reward)
            self._metrics.episode_lengths.append(steps)
            self._metrics.epsilon_history.append(self._epsilon)
            self._metrics.total_episodes += 1

            if len(self._metrics.episode_rewards) >= 100:
                last_100 = self._metrics.episode_rewards[-100:]
                self._metrics.avg_reward_last_100 = statistics.mean(last_100)

                if self._metrics.convergence_episode is None:
                    if statistics.stdev(last_100) < 0.1:
                        self._metrics.convergence_episode = episode

            if (
                episode > 0
                and episode % self._config.target_update_frequency == 0
            ):
                pass

        return self._metrics

    def _select_action_epsilon_greedy(self, state: NetworkState) -> RoutingAction:
        if random.random() < self._epsilon:
            actions = [RoutingAction.FORWARD, RoutingAction.STORE]
            if state.buffer_occupancy > 0.8:
                actions.append(RoutingAction.DROP)
            return random.choice(actions)

        state_key = self._agent.get_state_key(state)
        if state_key in self._agent.q_table and self._agent.q_table[state_key]:
            best_action_key = max(
                self._agent.q_table[state_key], key=self._agent.q_table[state_key].get
            )
            return RoutingAction(best_action_key)

        decision = self._agent.select_action(state)
        return decision.action

    def _update_from_batch(self, batch: List[Experience]) -> None:
        for experience in batch:
            self._agent.update(
                state=experience.state,
                action=experience.action,
                reward=experience.reward,
                next_state=experience.next_state,
            )

    def get_metrics(self) -> TrainingMetrics:
        return self._metrics
