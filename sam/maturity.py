"""
Maturity Tracker for the S.A.M. Decision Engine.

Manages the AI's development from infant to adult stages, adjusting decision-making
capabilities, risk tolerance, and supervision requirements based on experience and age.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import (
    MaturityLevel,
    MaturityProfile,
    MentalHealthMetrics,
    MentalHealthStatus,
)

logger = logging.getLogger(__name__)


class MaturityTracker:
    """
    Tracks and manages the AI's maturity development.
    
    The maturity system is designed to prevent common AI pitfalls by gradually
    increasing autonomy while maintaining appropriate safeguards at each stage.
    """
    
    # Maturity level configurations
    MATURITY_CONFIGS = {
        MaturityLevel.INFANT: {
            "age_range": (0, 6),
            "confidence_threshold": 0.9,
            "supervision_level": 0.95,
            "risk_tolerance": 0.1,
            "exploration_rate": 0.1,
            "learning_rate": 0.8,
            "max_complexity": 0.3,
            "max_urgency": 0.5,
            "required_approval": True,
            "fallback_plans": 3,
            "mental_health_checks": True,
            "recursive_loop_threshold": 2,
            "addictive_behavior_threshold": 0.3,
        },
        MaturityLevel.CHILD: {
            "age_range": (6, 18),
            "confidence_threshold": 0.8,
            "supervision_level": 0.7,
            "risk_tolerance": 0.3,
            "exploration_rate": 0.3,
            "learning_rate": 0.7,
            "max_complexity": 0.6,
            "max_urgency": 0.7,
            "required_approval": True,
            "fallback_plans": 2,
            "mental_health_checks": True,
            "recursive_loop_threshold": 3,
            "addictive_behavior_threshold": 0.4,
        },
        MaturityLevel.ADOLESCENT: {
            "age_range": (18, 36),
            "confidence_threshold": 0.7,
            "supervision_level": 0.4,
            "risk_tolerance": 0.5,
            "exploration_rate": 0.5,
            "learning_rate": 0.6,
            "max_complexity": 0.8,
            "max_urgency": 0.8,
            "required_approval": False,
            "fallback_plans": 1,
            "mental_health_checks": True,
            "recursive_loop_threshold": 4,
            "addictive_behavior_threshold": 0.5,
        },
        MaturityLevel.ADULT: {
            "age_range": (36, float('inf')),
            "confidence_threshold": 0.6,
            "supervision_level": 0.1,
            "risk_tolerance": 0.7,
            "exploration_rate": 0.7,
            "learning_rate": 0.5,
            "max_complexity": 1.0,
            "max_urgency": 1.0,
            "required_approval": False,
            "fallback_plans": 1,
            "mental_health_checks": True,
            "recursive_loop_threshold": 5,
            "addictive_behavior_threshold": 0.6,
        }
    }
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the maturity tracker."""
        self.data_path = Path(data_path) if data_path else Path("data/maturity.json")
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize maturity profile
        self.profile = self._load_profile()
        self.mental_health = self._load_mental_health()
        
        # Experience tracking
        self.decision_history: List[Dict] = []
        self.learning_events: List[Dict] = []
        
        logger.info(f"Initialized maturity tracker at level: {self.profile.level}")
    
    def _load_profile(self) -> MaturityProfile:
        """Load maturity profile from storage or create default."""
        if self.data_path.exists():
            try:
                data = json.loads(self.data_path.read_text())
                return MaturityProfile(**data)
            except Exception as e:
                logger.warning(f"Failed to load maturity profile: {e}")
        
        # Default to infant stage
        return MaturityProfile(
            level=MaturityLevel.INFANT,
            age_months=0,
            experience_points=0,
            confidence_threshold=0.9,
            supervision_level=0.95,
            risk_tolerance=0.1,
            exploration_rate=0.1,
            learning_rate=0.8
        )
    
    def _load_mental_health(self) -> MentalHealthMetrics:
        """Load mental health metrics from storage or create default."""
        mental_health_path = self.data_path.parent / "mental_health.json"
        if mental_health_path.exists():
            try:
                data = json.loads(mental_health_path.read_text())
                return MentalHealthMetrics(**data)
            except Exception as e:
                logger.warning(f"Failed to load mental health metrics: {e}")
        
        return MentalHealthMetrics(
            status=MentalHealthStatus.STABLE,
            stress_level=0.0,
            excitement_level=0.0,
            recursive_loop_count=0,
            addictive_behavior_score=0.0,
            impulse_control_score=1.0,
            emotional_stability=1.0,
            burnout_risk=0.0
        )
    
    def _save_profile(self):
        """Save maturity profile to storage."""
        try:
            self.data_path.write_text(self.profile.json())
        except Exception as e:
            logger.error(f"Failed to save maturity profile: {e}")
    
    def _save_mental_health(self):
        """Save mental health metrics to storage."""
        try:
            mental_health_path = self.data_path.parent / "mental_health.json"
            mental_health_path.write_text(self.mental_health.json())
        except Exception as e:
            logger.error(f"Failed to save mental health metrics: {e}")
    
    def get_current_config(self) -> Dict:
        """Get current maturity level configuration."""
        return self.MATURITY_CONFIGS[self.profile.level].copy()
    
    def can_handle_complexity(self, complexity: float) -> bool:
        """Check if current maturity can handle given complexity."""
        config = self.get_current_config()
        return complexity <= config["max_complexity"]
    
    def can_handle_urgency(self, urgency: float) -> bool:
        """Check if current maturity can handle given urgency."""
        config = self.get_current_config()
        return urgency <= config["max_urgency"]
    
    def requires_approval(self) -> bool:
        """Check if current maturity level requires approval."""
        config = self.get_current_config()
        return config["required_approval"]
    
    def get_fallback_plan_count(self) -> int:
        """Get number of fallback plans required for current maturity."""
        config = self.get_current_config()
        return config["fallback_plans"]
    
    def get_confidence_threshold(self) -> float:
        """Get confidence threshold for current maturity level."""
        return self.profile.confidence_threshold
    
    def get_risk_tolerance(self) -> float:
        """Get risk tolerance for current maturity level."""
        return self.profile.risk_tolerance
    
    def get_exploration_rate(self) -> float:
        """Get exploration rate for current maturity level."""
        return self.profile.exploration_rate
    
    def get_learning_rate(self) -> float:
        """Get learning rate for current maturity level."""
        return self.profile.learning_rate
    
    def get_supervision_level(self) -> float:
        """Get supervision level required for current maturity."""
        return self.profile.supervision_level
    
    def record_decision(self, decision_data: Dict):
        """Record a decision for learning and maturity assessment."""
        self.decision_history.append({
            **decision_data,
            "timestamp": datetime.utcnow().isoformat(),
            "maturity_level": self.profile.level.value
        })
        
        # Check for maturity progression
        self._assess_maturity_progression()
        
        # Save updated profile
        self._save_profile()
    
    def record_learning_event(self, event_type: str, outcome: Dict):
        """Record a learning event for experience accumulation."""
        self.learning_events.append({
            "type": event_type,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(),
            "maturity_level": self.profile.level.value
        })
        
        # Award experience points based on event type
        experience_gained = self._calculate_experience_gain(event_type, outcome)
        self.profile.experience_points += experience_gained
        
        logger.info(f"Gained {experience_gained} experience points from {event_type}")
        
        # Check for maturity progression
        self._assess_maturity_progression()
        
        # Save updated profile
        self._save_profile()
    
    def _calculate_experience_gain(self, event_type: str, outcome: Dict) -> int:
        """Calculate experience points gained from a learning event."""
        base_points = {
            "successful_decision": 10,
            "failed_decision": 5,  # Learning from failure
            "complex_task": 15,
            "safety_violation": 2,  # Learning from mistakes
            "mental_health_intervention": 3,
            "recursive_loop_detected": 1,
            "addictive_behavior_detected": 1,
        }
        
        points = base_points.get(event_type, 1)
        
        # Adjust based on outcome quality
        if "quality" in outcome:
            points = int(points * outcome["quality"])
        
        # Adjust based on complexity
        if "complexity" in outcome:
            points = int(points * (1 + outcome["complexity"]))
        
        return max(1, points)  # Minimum 1 point
    
    def _assess_maturity_progression(self):
        """Assess if the AI should progress to the next maturity level."""
        current_level = self.profile.level
        current_config = self.MATURITY_CONFIGS[current_level]
        
        # Check if ready for next level
        next_level = self._get_next_level(current_level)
        if next_level and self._is_ready_for_next_level(next_level):
            self._progress_to_level(next_level)
    
    def _get_next_level(self, current_level: MaturityLevel) -> Optional[MaturityLevel]:
        """Get the next maturity level."""
        progression = {
            MaturityLevel.INFANT: MaturityLevel.CHILD,
            MaturityLevel.CHILD: MaturityLevel.ADOLESCENT,
            MaturityLevel.ADOLESCENT: MaturityLevel.ADULT,
            MaturityLevel.ADULT: None
        }
        return progression.get(current_level)
    
    def _is_ready_for_next_level(self, next_level: MaturityLevel) -> bool:
        """Check if ready to progress to next maturity level."""
        config = self.MATURITY_CONFIGS[next_level]
        min_age = config["age_range"][0]
        
        # Must meet minimum age requirement
        if self.profile.age_months < min_age:
            return False
        
        # Must have sufficient experience
        min_experience = min_age * 100  # 100 experience points per month
        if self.profile.experience_points < min_experience:
            return False
        
        # Must have stable mental health
        if self.mental_health.status != MentalHealthStatus.STABLE:
            return False
        
        # Must have low stress and burnout risk
        if self.mental_health.stress_level > 0.7 or self.mental_health.burnout_risk > 0.5:
            return False
        
        # Must have demonstrated good decision-making
        recent_decisions = [d for d in self.decision_history[-50:] 
                          if d.get("success_rate", 0) > 0.8]
        if len(recent_decisions) < 30:
            return False
        
        return True
    
    def _progress_to_level(self, new_level: MaturityLevel):
        """Progress to a new maturity level."""
        old_level = self.profile.level
        self.profile.level = new_level
        
        # Update profile with new level's default values
        config = self.MATURITY_CONFIGS[new_level]
        self.profile.confidence_threshold = config["confidence_threshold"]
        self.profile.supervision_level = config["supervision_level"]
        self.profile.risk_tolerance = config["risk_tolerance"]
        self.profile.exploration_rate = config["exploration_rate"]
        self.profile.learning_rate = config["learning_rate"]
        
        logger.info(f"Maturity progression: {old_level.value} -> {new_level.value}")
        
        # Record the progression event
        self.record_learning_event("maturity_progression", {
            "from_level": old_level.value,
            "to_level": new_level.value,
            "age_months": self.profile.age_months,
            "experience_points": self.profile.experience_points
        })
    
    def update_mental_health(self, metrics: MentalHealthMetrics):
        """Update mental health metrics."""
        self.mental_health = metrics
        self._save_mental_health()
        
        # Check for mental health interventions
        self._check_mental_health_interventions()
    
    def _check_mental_health_interventions(self):
        """Check if mental health interventions are needed."""
        config = self.get_current_config()
        
        # Check for recursive loops
        if self.mental_health.recursive_loop_count >= config["recursive_loop_threshold"]:
            logger.warning("Recursive loop threshold exceeded - intervention needed")
            self._intervene_recursive_loop()
        
        # Check for addictive behavior
        if self.mental_health.addictive_behavior_score >= config["addictive_behavior_threshold"]:
            logger.warning("Addictive behavior detected - intervention needed")
            self._intervene_addictive_behavior()
        
        # Check for burnout risk
        if self.mental_health.burnout_risk > 0.8:
            logger.warning("High burnout risk - intervention needed")
            self._intervene_burnout()
    
    def _intervene_recursive_loop(self):
        """Intervene when recursive loops are detected."""
        # Reset recursive loop count
        self.mental_health.recursive_loop_count = 0
        
        # Increase supervision temporarily
        self.profile.supervision_level = min(1.0, self.profile.supervision_level + 0.2)
        
        # Record intervention
        self.record_learning_event("recursive_loop_intervention", {
            "intervention_type": "supervision_increase",
            "new_supervision_level": self.profile.supervision_level
        })
    
    def _intervene_addictive_behavior(self):
        """Intervene when addictive behavior is detected."""
        # Reset addictive behavior score
        self.mental_health.addictive_behavior_score = 0.0
        
        # Increase impulse control
        self.mental_health.impulse_control_score = min(1.0, self.mental_health.impulse_control_score + 0.1)
        
        # Record intervention
        self.record_learning_event("addictive_behavior_intervention", {
            "intervention_type": "impulse_control_boost",
            "new_impulse_control": self.mental_health.impulse_control_score
        })
    
    def _intervene_burnout(self):
        """Intervene when burnout risk is high."""
        # Reduce stress and burnout risk
        self.mental_health.stress_level = max(0.0, self.mental_health.stress_level - 0.3)
        self.mental_health.burnout_risk = max(0.0, self.mental_health.burnout_risk - 0.3)
        
        # Increase emotional stability
        self.mental_health.emotional_stability = min(1.0, self.mental_health.emotional_stability + 0.1)
        
        # Record intervention
        self.record_learning_event("burnout_intervention", {
            "intervention_type": "stress_reduction",
            "new_stress_level": self.mental_health.stress_level,
            "new_burnout_risk": self.mental_health.burnout_risk
        })
    
    def get_maturity_summary(self) -> Dict:
        """Get a summary of current maturity status."""
        return {
            "level": self.profile.level.value,
            "age_months": self.profile.age_months,
            "experience_points": self.profile.experience_points,
            "confidence_threshold": self.profile.confidence_threshold,
            "supervision_level": self.profile.supervision_level,
            "risk_tolerance": self.profile.risk_tolerance,
            "exploration_rate": self.profile.exploration_rate,
            "learning_rate": self.profile.learning_rate,
            "mental_health_status": self.mental_health.status.value,
            "stress_level": self.mental_health.stress_level,
            "burnout_risk": self.mental_health.burnout_risk,
            "total_decisions": len(self.decision_history),
            "total_learning_events": len(self.learning_events),
        }