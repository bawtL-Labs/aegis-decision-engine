"""
S.A.M. Decision Engine - Autonomous AI Decision Making System

A maturity-based decision engine that evolves from infant to adult intelligence,
incorporating mental health safeguards and preventing common AI pitfalls.
"""

__version__ = "0.1.0"
__author__ = "BawtL Labs"
__description__ = "S.A.M. Decision Engine for Autonomous AI Systems"

from .decision import DecisionEngine
from .maturity import MaturityTracker
from .mental_health import MentalHealthMonitor
from .core import Orientation, UtilityEngine, PlanGenerator

__all__ = [
    "DecisionEngine",
    "MaturityTracker", 
    "MentalHealthMonitor",
    "Orientation",
    "UtilityEngine",
    "PlanGenerator"
]