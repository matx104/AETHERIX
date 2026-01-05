"""
AETHERIX Security Module

Provides quantum security capabilities including:
- BB84 Quantum Key Distribution
- E91 Entanglement-based QKD
- Quantum repeater modeling
"""

from .qkd import BB84Protocol, E91Protocol, QKDResult, QuantumRepeater, calculate_key_rate

__all__ = [
    'BB84Protocol',
    'E91Protocol',
    'QKDResult',
    'QuantumRepeater',
    'calculate_key_rate',
]
