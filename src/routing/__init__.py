"""
AETHERIX Routing Module

Provides DTN routing capabilities including:
- Bundle Protocol v7 data structures
- RL-based routing agent
- Contact graph routing (baseline)
"""

from .bundle import Bundle, BundlePriority, EndpointID, create_science_bundle
from .rl_agent import (NetworkState, RLRoutingAgent, RoutingAction,
                       RoutingDecision)

__all__ = [
    'Bundle',
    'BundlePriority',
    'EndpointID',
    'create_science_bundle',
    'RLRoutingAgent',
    'RoutingAction',
    'NetworkState',
    'RoutingDecision',
]
