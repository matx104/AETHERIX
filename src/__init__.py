"""
AETHERIX - Autonomous, Quantum-Secure AI Ops for Space Communications

AETHERIX is a comprehensive platform for designing, simulating, and optimizing
deep-space communication networks using AI-driven Delay-Tolerant Networking (DTN)
and Quantum Communication systems.
"""

__version__ = "0.1.0"
__author__ = "AETHERIX Team"

from .infrastructure import LinkBudgetCalculator, OpticalLinkBudget

__all__ = ['LinkBudgetCalculator', 'OpticalLinkBudget']
