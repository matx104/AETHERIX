"""Contact Graph for DTN routing in the AETHERIX architecture.

Models scheduled communication contacts between network nodes
and provides graph-based pathfinding for delay-tolerant routing.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class ContactState(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Contact:
    contact_id: str
    source_node: str
    dest_node: str
    start_time: float
    end_time: float
    data_rate_mbps: float
    delay_seconds: float
    state: ContactState = ContactState.PENDING
    volume_megabits: float = 0.0

    @property
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time

    @property
    def is_active(self) -> bool:
        import time
        now = time.time()
        return self.start_time <= now <= self.end_time

    def calculate_volume(self) -> float:
        return self.data_rate_mbps * self.duration_seconds / 8.0


class ContactGraph:
    def __init__(self) -> None:
        self._contacts: List[Contact] = []
        self._outgoing: Dict[str, List[Contact]] = defaultdict(list)
        self._incoming: Dict[str, List[Contact]] = defaultdict(list)

    def add_contact(self, contact: Contact) -> None:
        self._contacts.append(contact)
        self._outgoing[contact.source_node].append(contact)
        self._incoming[contact.dest_node].append(contact)

    def get_contacts_from(self, node_id: str) -> List[Contact]:
        return list(self._outgoing.get(node_id, []))

    def get_contacts_to(self, node_id: str) -> List[Contact]:
        return list(self._incoming.get(node_id, []))

    def get_active_contacts(self, current_time: float) -> List[Contact]:
        return [
            c for c in self._contacts
            if c.start_time <= current_time <= c.end_time
        ]

    def find_path(self, source: str, destination: str) -> List[Contact]:
        if source == destination:
            return []
        queue: deque[tuple[str, List[Contact]]] = deque()
        queue.append((source, []))
        visited: set[str] = {source}
        while queue:
            current, path = queue.popleft()
            for contact in self._outgoing.get(current, []):
                next_node = contact.dest_node
                new_path = path + [contact]
                if next_node == destination:
                    return new_path
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, new_path))
        return []

    def get_reachable_nodes(self, source: str) -> List[str]:
        visited: set[str] = {source}
        queue: deque[str] = deque([source])
        while queue:
            current = queue.popleft()
            for contact in self._outgoing.get(current, []):
                neighbor = contact.dest_node
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return sorted(visited - {source})
