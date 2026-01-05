"""
AETHERIX Infrastructure Modeling Module

This module provides infrastructure modeling capabilities for interplanetary
communication networks, including link budget calculations and topology management.
"""

from .link_budget import LinkBudgetCalculator, OpticalLinkBudget

__all__ = ['LinkBudgetCalculator', 'OpticalLinkBudget']
