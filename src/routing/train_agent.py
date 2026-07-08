#!/usr/bin/env python3
"""
AETHERIX RL Routing Agent Trainer
=================================

Trains the Q-learning routing agent from a YAML configuration file.

    python src/routing/train_agent.py --config config/training.yaml
    python src/routing/train_agent.py --episodes 5000
    python src/routing/train_agent.py --config config/training.yaml --quiet

The training config specifies epsilon schedule, learning rate, discount
factor, reward weights, and convergence criteria.  Results are printed
as a summary table.

Zero external dependencies.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..")
_ROOT = os.path.join(_SRC, "..")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from routing.rl_agent import RLRoutingAgent
from routing.training import Trainer, TrainingConfig, TrainingMetrics

from simulation.run_scenario import _parse_yaml, load_config


def build_training_config(cfg: Dict[str, Any]) -> TrainingConfig:
    train = cfg.get("training", {})
    agent_cfg = cfg.get("agent", {})
    conv = cfg.get("convergence", {})

    return TrainingConfig(
        episodes=int(train.get("episodes", 10000)),
        max_steps_per_episode=int(train.get("max_steps_per_episode", 100)),
        epsilon_start=float(train.get("epsilon_start", 1.0)),
        epsilon_end=float(train.get("epsilon_min", 0.01)),
        epsilon_decay=float(train.get("epsilon_decay", 0.995)),
        learning_rate=float(train.get("learning_rate", 0.1)),
        discount_factor=float(train.get("discount_factor", 0.95)),
        replay_capacity=int(train.get("experience_replay_capacity", 10000)),
        batch_size=int(train.get("batch_size", 32)),
        target_update_frequency=int(train.get("target_update_frequency", 100)),
    )


def train_agent(config_path: str | None, verbose: bool = True,
                episodes_override: int | None = None) -> TrainingMetrics:
    cfg: Dict[str, Any] = {}
    if config_path and os.path.isfile(config_path):
        cfg = load_config(config_path)

    train_cfg = build_training_config(cfg)
    if episodes_override is not None:
        train_cfg.episodes = episodes_override

    agent_cfg = cfg.get("agent", {})
    node_id = agent_cfg.get("node_id", "MARS_ORBIT_1")
    agent = RLRoutingAgent(node_id=node_id)
    agent.learning_rate = train_cfg.learning_rate
    agent.discount_factor = train_cfg.discount_factor
    agent.epsilon = train_cfg.epsilon_start

    trainer = Trainer(agent, train_cfg)

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"  RL ROUTING AGENT TRAINING")
        print(f"{'=' * 60}")
        print(f"  Episodes:          {train_cfg.episodes}")
        print(f"  Epsilon start:     {train_cfg.epsilon_start}")
        print(f"  Epsilon min:       {train_cfg.epsilon_end}")
        print(f"  Epsilon decay:     {train_cfg.epsilon_decay}")
        print(f"  Learning rate:     {train_cfg.learning_rate}")
        print(f"  Discount factor:   {train_cfg.discount_factor}")
        print(f"  Batch size:        {train_cfg.batch_size}")
        print(f"  Replay capacity:   {train_cfg.replay_capacity}")
        print(f"  Max steps/episode: {train_cfg.max_steps_per_episode}")
        print(f"{'─' * 60}")
        print("  Training...")

    metrics = trainer.train()

    if verbose:
        _print_metrics(metrics, agent)

    return metrics


def _print_metrics(metrics: TrainingMetrics, agent: RLRoutingAgent) -> None:
    print(f"\n{'─' * 60}")
    print(f"  TRAINING COMPLETE")
    print(f"{'─' * 60}")
    print(f"  Total episodes:           {metrics.total_episodes}")
    print(f"  Convergence episode:      {metrics.convergence_episode or 'not detected'}")
    print(f"  Avg reward (last 100):    {metrics.avg_reward_last_100:.4f}")

    all_rewards = metrics.episode_rewards
    if all_rewards:
        first_100 = all_rewards[:min(100, len(all_rewards))]
        last_100 = all_rewards[-min(100, len(all_rewards)):]
        import statistics
        avg_first = statistics.mean(first_100)
        avg_last = statistics.mean(last_100)
        print(f"  Avg reward (first 100):   {avg_first:.4f}")
        print(f"  Avg reward (last 100):    {avg_last:.4f}")
        improvement = avg_last - avg_first
        print(f"  Improvement:              {improvement:+.4f}")

    print(f"  Final epsilon:            {metrics.epsilon_history[-1]:.6f}")
    print(f"  Q-table states:           {len(agent.q_table)}")
    print(f"  Q-table entries:          {sum(len(v) for v in agent.q_table.values())}")
    print(f"{'=' * 60}\n")


_CONFIG_DIR = os.path.join(_ROOT, "config")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the AETHERIX RL routing agent from a YAML config."
    )
    parser.add_argument(
        "--config", "-c",
        default=os.path.join(_CONFIG_DIR, "training.yaml"),
        help="Path to training YAML file (default: config/training.yaml)",
    )
    parser.add_argument(
        "--episodes", "-e",
        type=int, default=None,
        help="Override episode count from config",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress detailed output",
    )
    args = parser.parse_args()

    train_agent(
        config_path=args.config,
        verbose=not args.quiet,
        episodes_override=args.episodes,
    )


if __name__ == "__main__":
    main()
