"""
AETHERIX Policy Engine
Configuration-driven routing policies for AETHERIX Forge.

Evaluates declarative rules against a forwarding context to produce
routing decisions (forward / store / drop / split) without requiring
the RL agent.  Policies are ordered by priority so operators can layer
overrides on top of learned behaviour.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PolicyRule:
    """
    A single condition → action rule.

    ``condition_field`` is matched against the forwarding context dict
    using ``operator`` and ``value``.  When the condition holds the
    ``action`` is returned.
    """

    condition_field: str
    operator: str
    value: Any
    action: str
    target: str = ""

    _VALID_FIELDS = frozenset({
        "priority", "buffer_occupancy", "link_quality",
        "bundle_size", "destination_tier", "source_tier",
        "current_node", "neighbors",
    })
    _VALID_OPERATORS = frozenset({
        "eq", "ne", "gt", "lt", "gte", "lte", "in", "not_in",
    })
    _VALID_ACTIONS = frozenset({
        "forward", "store", "drop", "split",
    })


@dataclass
class RoutingPolicy:
    """
    A named collection of :class:`PolicyRule` instances.

    Policies with higher ``priority`` are evaluated first.
    """

    name: str
    description: str
    rules: List[PolicyRule] = field(default_factory=list)
    priority: int = 0


@dataclass
class PolicyDecision:
    """
    Outcome of policy evaluation for a single forwarding context.
    """

    action: str
    target: str
    matched_rule: Optional[PolicyRule] = None
    policy_name: str = ""
    confidence: float = 1.0


class PolicyEngine:
    """
    Ordered policy evaluator.

    Add :class:`RoutingPolicy` instances via :meth:`add_policy`.  When
    :meth:`evaluate` is called the engine iterates policies from
    highest to lowest priority and returns the *first* matching rule's
    action as a :class:`PolicyDecision`.
    """

    def __init__(self) -> None:
        self._policies: List[RoutingPolicy] = []

    def add_policy(self, policy: RoutingPolicy) -> None:
        self._policies.append(policy)
        self._policies.sort(key=lambda p: p.priority, reverse=True)

    def remove_policy(self, name: str) -> bool:
        before = len(self._policies)
        self._policies = [p for p in self._policies if p.name != name]
        return len(self._policies) < before

    def get_policies(self) -> List[RoutingPolicy]:
        return list(self._policies)

    def evaluate(self, context: Dict[str, Any]) -> PolicyDecision:
        """
        Evaluate all policies against *context*.

        Returns the first matching rule's action.  If nothing matches
        the default decision is ``("store", "")`` — safe for DTN.
        """
        for policy in self._policies:
            for rule in policy.rules:
                if self._evaluate_rule(rule, context):
                    return PolicyDecision(
                        action=rule.action,
                        target=rule.target,
                        matched_rule=rule,
                        policy_name=policy.name,
                        confidence=1.0,
                    )

        return PolicyDecision(
            action="store",
            target="",
            matched_rule=None,
            policy_name="",
            confidence=0.5,
        )

    def _evaluate_rule(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        field_value = context.get(rule.condition_field)
        if field_value is None:
            return False

        op = rule.operator
        target = rule.value

        try:
            if op == "eq":
                return field_value == target
            if op == "ne":
                return field_value != target
            if op == "gt":
                return field_value > target
            if op == "lt":
                return field_value < target
            if op == "gte":
                return field_value >= target
            if op == "lte":
                return field_value <= target
            if op == "in":
                return field_value in target
            if op == "not_in":
                return field_value not in target
        except TypeError:
            return False

        return False

    def load_default_policies(self) -> None:
        """
        Load the standard AETHERIX routing policy set.

        Policies (highest priority first):
            1. **emergency_fast_path** — priority ≤ 1 → forward to best link.
            2. **congestion_control** — buffer > 0.9 AND priority ≥ 3 → drop.
            3. **deep_space_store** — best link quality < 0.3 → store.
            4. **bulk_defer** — priority 4 AND buffer > 0.5 → store.
            5. **tier_aware_routing** — destination tier < current tier →
               forward toward lower-tier neighbour.
        """
        self.add_policy(RoutingPolicy(
            name="emergency_fast_path",
            description="Expedite EMERGENCY and HIGH_SCIENCE bundles on the best available link",
            rules=[
                PolicyRule(
                    condition_field="priority",
                    operator="lte",
                    value=1,
                    action="forward",
                    target="best_link",
                ),
            ],
            priority=100,
        ))

        self.add_policy(RoutingPolicy(
            name="congestion_control",
            description="Drop low-priority bundles when buffer is critically full",
            rules=[
                PolicyRule(
                    condition_field="buffer_occupancy",
                    operator="gt",
                    value=0.9,
                    action="drop",
                ),
                PolicyRule(
                    condition_field="priority",
                    operator="gte",
                    value=3,
                    action="drop",
                ),
            ],
            priority=90,
        ))

        self.add_policy(RoutingPolicy(
            name="deep_space_store",
            description="Store bundles when link quality is too poor for reliable transmission",
            rules=[
                PolicyRule(
                    condition_field="link_quality",
                    operator="lt",
                    value=0.3,
                    action="store",
                ),
            ],
            priority=80,
        ))

        self.add_policy(RoutingPolicy(
            name="bulk_defer",
            description="Defer bulk transfers when the buffer is moderately loaded",
            rules=[
                PolicyRule(
                    condition_field="priority",
                    operator="eq",
                    value=4,
                    action="store",
                ),
                PolicyRule(
                    condition_field="buffer_occupancy",
                    operator="gt",
                    value=0.5,
                    action="store",
                ),
            ],
            priority=70,
        ))

        self.add_policy(RoutingPolicy(
            name="tier_aware_routing",
            description="Forward bundles toward lower-tier (Earth-ward) neighbours",
            rules=[
                PolicyRule(
                    condition_field="destination_tier",
                    operator="lt",
                    value=0,
                    action="forward",
                    target="lower_tier_neighbor",
                ),
            ],
            priority=60,
        ))
