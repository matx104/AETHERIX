"""
Tests for AETHERIX RL Training Loop and Multi-Agent Framework.

Validates experience replay, training environment, trainer convergence,
and federated learning across distributed routing agents.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.multi_agent import FederatedLearningConfig, MultiAgentCoordinator
from routing.rl_agent import NetworkState, RLRoutingAgent, RoutingAction
from routing.training import (
    Experience,
    ExperienceReplay,
    Trainer,
    TrainingConfig,
    TrainingEnvironment,
)


class TestExperienceReplay(unittest.TestCase):
    """Test cases for ExperienceReplay buffer."""

    def test_push_and_sample(self) -> None:
        replay = ExperienceReplay(capacity=200)
        state = NetworkState(
            current_node="a", neighbors=["b"], link_qualities={"b": 0.5},
            buffer_occupancy=0.3, bundle_priority=2, bundle_size_mb=10.0,
            bundle_deadline_hours=5.0, destination_node="c",
        )
        for i in range(100):
            replay.push(Experience(
                state=state, action=RoutingAction.FORWARD,
                reward=1.0, next_state=state, done=False,
            ))
        sample = replay.sample(10)
        self.assertEqual(len(sample), 10)

    def test_capacity_limit(self) -> None:
        replay = ExperienceReplay(capacity=100)
        state = NetworkState(
            current_node="a", neighbors=["b"], link_qualities={"b": 0.5},
            buffer_occupancy=0.3, bundle_priority=2, bundle_size_mb=10.0,
            bundle_deadline_hours=5.0, destination_node="c",
        )
        for i in range(200):
            replay.push(Experience(
                state=state, action=RoutingAction.STORE,
                reward=0.5, next_state=state, done=False,
            ))
        self.assertEqual(len(replay), 100)


class TestTrainingEnvironment(unittest.TestCase):
    """Test cases for TrainingEnvironment."""

    def test_reset(self) -> None:
        env = TrainingEnvironment(seed=42)
        state = env.reset()
        self.assertIsInstance(state, NetworkState)
        self.assertTrue(state.current_node)
        self.assertGreater(len(state.neighbors), 0)

    def test_step(self) -> None:
        env = TrainingEnvironment(seed=42)
        state = env.reset()
        next_state, reward, done = env.step(state, RoutingAction.FORWARD)
        self.assertIsInstance(reward, float)
        self.assertIsInstance(done, bool)


class TestTrainer(unittest.TestCase):
    """Test cases for Trainer training loop."""

    def test_short_training(self) -> None:
        agent = RLRoutingAgent(node_id="test-node", epsilon=0.5)
        config = TrainingConfig(
            episodes=10,
            max_steps_per_episode=5,
            batch_size=4,
            replay_capacity=500,
        )
        trainer = Trainer(agent=agent, config=config)
        metrics = trainer.train()
        self.assertIsNotNone(metrics)
        self.assertEqual(len(metrics.episode_rewards), 10)
        self.assertEqual(metrics.total_episodes, 10)


class TestMultiAgentCoordinator(unittest.TestCase):
    """Test cases for MultiAgentCoordinator federated learning."""

    def test_create_agents(self) -> None:
        config = FederatedLearningConfig(num_agents=5)
        coordinator = MultiAgentCoordinator(config)
        node_ids = [f"node-{i}" for i in range(5)]
        coordinator.create_agents(node_ids)
        self.assertEqual(coordinator.get_agent_count(), 5)

    def test_federated_round(self) -> None:
        config = FederatedLearningConfig(
            num_agents=3,
            min_experiences_for_sharing=1,
            sharing_ratio=0.5,
        )
        coordinator = MultiAgentCoordinator(config)
        node_ids = ["agent-a", "agent-b", "agent-c"]
        coordinator.create_agents(node_ids)

        state = NetworkState(
            current_node="a", neighbors=["b"], link_qualities={"b": 0.5},
            buffer_occupancy=0.3, bundle_priority=2, bundle_size_mb=10.0,
            bundle_deadline_hours=5.0, destination_node="c",
        )
        exp = Experience(
            state=state, action=RoutingAction.FORWARD,
            reward=1.0, next_state=state, done=False,
        )
        for nid in node_ids:
            agent_info = coordinator._agents[nid]
            for _ in range(10):
                agent_info.experiences.push(exp)

        coordinator.federated_round()
        self.assertGreater(coordinator.get_total_experiences(), 0)


if __name__ == '__main__':
    unittest.main()
