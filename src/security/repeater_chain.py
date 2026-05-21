"""
AETHERIX Multi-Hop Quantum Repeater Chain

Implements entanglement purification and cascading entanglement swapping
for long-range quantum key distribution across the Earth-Mars link.

Architecture:
    Earth ──hop0── [ES-L4] ──hop1── [ES-L5] ──hop2── Mars

Each hop generates an entangled pair; purification raises fidelity before
cascading Bell-state measurements at each repeater join adjacent pairs
into a single end-to-end entangled link.

References:
    - Briegel, Dür, Cirac, Zoller (1998) — quantum repeaters
    - Deutsch et al. (1996) — entanglement purification
"""

import math
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from security.qkd import Basis, QKDResult, QuantumRepeater, Qubit


@dataclass
class EntanglementPair:
    """A shared entangled pair between two nodes."""

    id: str
    node_a: str
    node_b: str
    fidelity: float
    created_time: float = 0.0
    is_purified: bool = False

    def __post_init__(self):
        self.fidelity = max(0.0, min(1.0, self.fidelity))


@dataclass
class PurificationResult:
    """Outcome of an entanglement purification round."""

    success: bool
    pair_id: str
    initial_fidelity: float
    final_fidelity: float
    attempts: int


@dataclass
class RepeaterHop:
    """One segment of the repeater chain between adjacent nodes."""

    repeater: QuantumRepeater
    hop_index: int
    pair_a: Optional[EntanglementPair] = None
    pair_b: Optional[EntanglementPair] = None
    swap_succeeded: bool = False


class RepeaterChain:
    """
    Ordered chain of quantum repeaters connecting two endpoints.

    The chain splits the total path into *N+1* hops (where *N* is the
    number of repeaters).  Entangled pairs are created per-hop,
    optionally purified, then merged via cascading entanglement swapping.
    """

    def __init__(self, endpoints: Tuple[str, str], repeaters: List[QuantumRepeater]):
        if len(endpoints) != 2:
            raise ValueError("endpoints must be a 2-tuple (source, destination)")
        self.endpoints = endpoints
        self.repeaters = list(repeaters)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _node_sequence(self) -> List[str]:
        """Return ordered nodes: endpoint_a, repeater_0, …, endpoint_b."""
        return [self.endpoints[0]] + [r.location for r in self.repeaters] + [self.endpoints[1]]

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def get_total_hops(self) -> int:
        """Number of hops (segments) in the chain."""
        return len(self.repeaters) + 1

    def generate_entanglement_pairs(self) -> List[EntanglementPair]:
        """
        Generate one entangled pair per hop.

        Base fidelity is 0.95 for short range and degrades proportionally
        with ``distance_km / 1000``.  Distance is approximated from the
        hop index mapped onto the Earth-Mars baseline.
        """
        nodes = self._node_sequence()
        pairs: List[EntanglementPair] = []
        base_fidelity = 0.95
        per_hop_km = 400_000_000 / max(self.get_total_hops(), 1)

        for i in range(self.get_total_hops()):
            degradation = per_hop_km / 1000
            fidelity = max(0.0, base_fidelity - degradation)
            pair = EntanglementPair(
                id=str(uuid.uuid4()),
                node_a=nodes[i],
                node_b=nodes[i + 1],
                fidelity=fidelity,
                created_time=time.time(),
            )
            pairs.append(pair)

        return pairs

    def purify_pair(
        self, pair: EntanglementPair, target_fidelity: float = 0.99
    ) -> PurificationResult:
        """
        Simulate double-selection entanglement purification.

        Each round succeeds with probability ``pair.fidelity ** 2``.
        On success the fidelity improves.  Rounds continue until the
        target is reached or a round fails.
        """
        initial_fidelity = pair.fidelity
        current = pair.fidelity
        attempts = 0

        while current < target_fidelity:
            attempts += 1
            success_prob = current ** 2

            if _coin() >= success_prob:
                return PurificationResult(
                    success=False,
                    pair_id=pair.id,
                    initial_fidelity=initial_fidelity,
                    final_fidelity=current,
                    attempts=attempts,
                )

            improvement = (target_fidelity - current) * 0.5
            current = min(1.0, current + improvement)

        pair.fidelity = current
        pair.is_purified = True
        return PurificationResult(
            success=True,
            pair_id=pair.id,
            initial_fidelity=initial_fidelity,
            final_fidelity=current,
            attempts=attempts,
        )

    def perform_entanglement_swapping(
        self, pairs: List[EntanglementPair]
    ) -> Optional[EntanglementPair]:
        """
        Perform cascading entanglement swapping through all repeaters.

        At each repeater a Bell-state measurement joins the two adjacent
        pairs.  Overall success probability is the product of individual
        repeater success rates.  The resulting fidelity is the product of
        all constituent pair fidelities.
        """
        if not pairs or not self.repeaters:
            return None

        current_fidelity = 1.0
        cumulative_success = True

        for idx, repeater in enumerate(self.repeaters):
            if idx < len(pairs):
                current_fidelity *= pairs[idx].fidelity
            if idx + 1 < len(pairs):
                current_fidelity *= pairs[idx + 1].fidelity

            if not repeater.swap_entanglement():
                cumulative_success = False

        if not cumulative_success:
            return None

        return EntanglementPair(
            id=str(uuid.uuid4()),
            node_a=self.endpoints[0],
            node_b=self.endpoints[1],
            fidelity=current_fidelity,
            created_time=time.time(),
            is_purified=True,
        )

    def establish_connection(
        self, target_fidelity: float = 0.95
    ) -> Tuple[bool, Optional[EntanglementPair]]:
        """
        Full pipeline: generate pairs → purify → swap.

        Returns ``(success, final_pair)`` where *success* is ``True``
        only when a pair exists **and** its fidelity meets the target.
        """
        pairs = self.generate_entanglement_pairs()

        for pair in pairs:
            result = self.purify_pair(pair, target_fidelity=target_fidelity)
            if not result.success:
                pair.fidelity = result.final_fidelity

        final_pair = self.perform_entanglement_swapping(pairs)

        if final_pair is None:
            return (False, None)

        return (final_pair.fidelity >= target_fidelity, final_pair)

    def get_chain_fidelity(self) -> float:
        """Theoretical maximum fidelity assuming perfect swapping."""
        pairs = self.generate_entanglement_pairs()
        if not pairs:
            return 0.0
        return math.prod(p.fidelity for p in pairs)


# ------------------------------------------------------------------
# standard chain factory
# ------------------------------------------------------------------

def create_earth_mars_chain() -> RepeaterChain:
    """
    Create the AETHERIX standard Earth-Mars repeater chain.

    Topology::

        Earth ── ES-L4 (0.7) ── ES-L5 (0.7) ── Mars

    Three hops via Lagrange-point relays.
    """
    repeater_l4 = QuantumRepeater(
        location="ES-L4",
        input_link_a="Earth",
        input_link_b="ES-L5",
        success_rate=0.7,
    )
    repeater_l5 = QuantumRepeater(
        location="ES-L5",
        input_link_a="ES-L4",
        input_link_b="Mars",
        success_rate=0.7,
    )
    return RepeaterChain(
        endpoints=("Earth", "Mars"),
        repeaters=[repeater_l4, repeater_l5],
    )


EARTH_MARS_REPEATER_CHAIN = create_earth_mars_chain


def _coin() -> float:
    """Return a random float in [0, 1)."""
    import random

    return random.random()
