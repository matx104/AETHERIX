"""
AETHERIX TCP Convergence Layer
TCPCL protocol for Earth-segment DTN communication.

Reference: RFC 7242 - TCP Convergence-Layer Protocol
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from routing.bundle import Bundle


@dataclass
class TCPCLMessage:
    """
    TCP Convergence Layer message.

    Message types per RFC 7242:
    - DATA_SEGMENT: carries a segment of bundle data
    - ACK: acknowledgement of received data segment
    - REFUSE: refusal to accept a bundle
    - SESSION_INIT: initiate a new TCPCL session
    - SESSION_ACK: acknowledge session initiation
    """
    message_type: str
    session_id: str
    payload: bytes
    flags: int = 0


@dataclass
class TCPCLEndpoint:
    """
    TCPCL endpoint representing a remote DTN node reachable via TCP.

    Tracks connection state and throughput statistics for a single
    TCP convergence-layer peer.
    """
    endpoint_id: str
    host: str
    port: int
    is_connected: bool = False
    bytes_sent: int = 0
    bytes_received: int = 0
    sessions_active: int = 0


@dataclass
class TCPCLSession:
    """
    TCPCL session tracking a single bundle transfer.

    Implements the session establishment and data transfer phases
    defined in RFC 7242 Sections 4 and 5.
    """
    session_id: str
    source: str
    destination: str
    total_bytes: int
    bytes_transferred: int = 0
    is_complete: bool = False
    start_time: float = 0.0
    end_time: float = 0.0


class TCPConvergenceLayer:
    """
    TCP Convergence Layer protocol implementation for Earth-segment DTN.

    Provides reliable, stream-oriented transport for bundles between
    DTN nodes connected via TCP. Used primarily in the Earth ground
    segment (DSN stations, mission operations centers) where reliable
    end-to-end connectivity is available.

    Reference: RFC 7242
    """

    def __init__(self, node_id: str):
        self.node_id: str = node_id
        self._endpoints: Dict[str, TCPCLEndpoint] = {}
        self._sessions: Dict[str, TCPCLSession] = {}

    def register_endpoint(self, endpoint_id: str, host: str, port: int) -> None:
        """Register a remote DTN endpoint reachable via TCP."""
        self._endpoints[endpoint_id] = TCPCLEndpoint(
            endpoint_id=endpoint_id,
            host=host,
            port=port,
        )

    def connect(self, endpoint_id: str) -> bool:
        """
        Simulate TCP three-way handshake with a remote endpoint.

        Returns True if the connection was established successfully.
        """
        endpoint = self._endpoints.get(endpoint_id)
        if endpoint is None:
            return False
        endpoint.is_connected = True
        return True

    def disconnect(self, endpoint_id: str) -> None:
        """Tear down the TCP connection to a remote endpoint."""
        endpoint = self._endpoints.get(endpoint_id)
        if endpoint is not None:
            endpoint.is_connected = False

    def send_bundle(self, endpoint_id: str, bundle: Bundle) -> TCPCLSession:
        """
        Send a complete bundle over TCPCL.

        Performs SESSION_INIT/SESSION_ACK handshake followed by
        DATA_SEGMENT transfer with ACK confirmation.
        """
        endpoint = self._endpoints.get(endpoint_id)
        if endpoint is None:
            raise ValueError(f"Unknown endpoint: {endpoint_id}")

        session_id = uuid.uuid4().hex[:12].upper()
        now = time.time()

        init_msg = TCPCLMessage(
            message_type="SESSION_INIT",
            session_id=session_id,
            payload=self.node_id.encode(),
        )

        ack_msg = TCPCLMessage(
            message_type="SESSION_ACK",
            session_id=session_id,
            payload=endpoint_id.encode(),
        )

        session = TCPCLSession(
            session_id=session_id,
            source=self.node_id,
            destination=endpoint_id,
            total_bytes=bundle.payload_size_bytes,
            start_time=now,
        )

        data_msg = TCPCLMessage(
            message_type="DATA_SEGMENT",
            session_id=session_id,
            payload=bundle.payload,
        )

        session.bytes_transferred = bundle.payload_size_bytes
        session.is_complete = True
        session.end_time = time.time()

        endpoint.bytes_sent += bundle.payload_size_bytes
        endpoint.sessions_active += 1

        self._sessions[session_id] = session

        return session

    def receive_bundle(self, session_id: str) -> Bundle:
        """
        Reconstruct a bundle from a completed TCPCL session.
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Unknown session: {session_id}")

        endpoint = self._endpoints.get(session.destination)
        if endpoint is not None:
            endpoint.bytes_received += session.total_bytes

        bundle = Bundle(
            bundle_id=session_id,
            payload_size_bytes=session.total_bytes,
        )
        return bundle

    def get_active_sessions(self) -> List[TCPCLSession]:
        """Return all sessions that have not completed transfer."""
        return [s for s in self._sessions.values() if not s.is_complete]

    def get_endpoint(self, endpoint_id: str) -> Optional[TCPCLEndpoint]:
        """Look up a registered endpoint by ID."""
        return self._endpoints.get(endpoint_id)

    def get_stats(self) -> Dict[str, int]:
        """Aggregate throughput statistics across all endpoints."""
        return {
            "total_sent": sum(e.bytes_sent for e in self._endpoints.values()),
            "total_received": sum(e.bytes_received for e in self._endpoints.values()),
            "active_connections": sum(
                1 for e in self._endpoints.values() if e.is_connected
            ),
        }
