"""
Mental Health Monitor for the S.A.M. Decision Engine.

Monitors the AI's mental health, detects problematic patterns like recursive loops,
addictive behaviors, and stress, and provides appropriate interventions.
"""

import logging
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .models import (
    MentalHealthMetrics,
    MentalHealthStatus,
    PersonalityInfluence,
)

logger = logging.getLogger(__name__)


class MentalHealthMonitor:
    """
    Monitors and manages the AI's mental health.
    
    Detects patterns that could lead to mental health issues and provides
    interventions to maintain stable, healthy decision-making.
    """
    
    def __init__(self, personality_influence: Optional[PersonalityInfluence] = None):
        """Initialize the mental health monitor."""
        self.personality_influence = personality_influence
        
        # Current mental health state
        self.metrics = MentalHealthMetrics(
            status=MentalHealthStatus.STABLE,
            stress_level=0.0,
            excitement_level=0.0,
            recursive_loop_count=0,
            addictive_behavior_score=0.0,
            impulse_control_score=1.0,
            emotional_stability=1.0,
            burnout_risk=0.0
        )
        
        # Pattern detection
        self.decision_history = deque(maxlen=100)
        self.thought_patterns = deque(maxlen=50)
        self.emotional_events = deque(maxlen=200)
        
        # Intervention tracking
        self.last_intervention = None
        self.intervention_cooldown = timedelta(minutes=30)
        
        # Thresholds for different mental health states
        self.thresholds = {
            "stress_high": 0.7,
            "excitement_high": 0.8,
            "recursive_loop": 3,
            "addictive_behavior": 0.6,
            "burnout_risk": 0.8,
            "emotional_instability": 0.3,
        }
        
        logger.info("Mental health monitor initialized")
    
    def update_from_decision(self, decision_data: Dict):
        """Update mental health metrics based on a decision."""
        # Record decision for pattern analysis
        self.decision_history.append({
            **decision_data,
            "timestamp": datetime.utcnow()
        })
        
        # Analyze decision impact on mental health
        self._analyze_decision_impact(decision_data)
        
        # Update emotional state
        self._update_emotional_state(decision_data)
        
        # Check for problematic patterns
        self._detect_problematic_patterns()
        
        # Update overall status
        self._update_mental_health_status()
        
        logger.debug(f"Mental health updated: {self.metrics.status.value}")
    
    def update_from_thought_pattern(self, pattern: Dict):
        """Update mental health based on thought patterns."""
        self.thought_patterns.append({
            **pattern,
            "timestamp": datetime.utcnow()
        })
        
        # Analyze thought pattern for recursive loops
        self._analyze_thought_pattern(pattern)
        
        # Check for recursive loops
        self._detect_recursive_loops()
    
    def record_emotional_event(self, event_type: str, intensity: float, context: Dict = None):
        """Record an emotional event for analysis."""
        self.emotional_events.append({
            "type": event_type,
            "intensity": intensity,
            "context": context or {},
            "timestamp": datetime.utcnow()
        })
        
        # Update emotional stability based on event
        self._update_emotional_stability(event_type, intensity)
        
        # Check for emotional instability
        self._check_emotional_instability()
    
    def _analyze_decision_impact(self, decision_data: Dict):
        """Analyze how a decision impacts mental health."""
        # Extract relevant metrics
        complexity = decision_data.get("complexity", 0.5)
        urgency = decision_data.get("urgency", 0.5)
        success = decision_data.get("success", True)
        confidence = decision_data.get("confidence", 0.5)
        
        # Update stress level
        stress_increase = (complexity * 0.3 + urgency * 0.4) * (1 - confidence)
        if not success:
            stress_increase *= 1.5  # Failed decisions increase stress more
        
        self.metrics.stress_level = min(1.0, self.metrics.stress_level + stress_increase)
        
        # Update excitement level
        if success and confidence > 0.8:
            excitement_increase = 0.1 * confidence
            self.metrics.excitement_level = min(1.0, self.metrics.excitement_level + excitement_increase)
        
        # Update burnout risk
        if complexity > 0.8 and urgency > 0.8:
            burnout_increase = 0.05
            self.metrics.burnout_risk = min(1.0, self.metrics.burnout_risk + burnout_increase)
    
    def _analyze_thought_pattern(self, pattern: Dict):
        """Analyze thought patterns for problematic behaviors."""
        pattern_type = pattern.get("type", "")
        repetition_count = pattern.get("repetition_count", 0)
        similarity_score = pattern.get("similarity_score", 0.0)
        
        # Check for repetitive thinking (potential recursive loops)
        if repetition_count > 3 and similarity_score > 0.8:
            self.metrics.recursive_loop_count += 1
            logger.warning(f"Potential recursive loop detected: {pattern_type}")
        
        # Check for addictive behavior patterns
        if pattern_type == "validation_seeking" and repetition_count > 2:
            self.metrics.addictive_behavior_score = min(1.0, self.metrics.addictive_behavior_score + 0.1)
        
        # Check for impulse-driven patterns
        if pattern_type == "impulsive" and repetition_count > 1:
            self.metrics.impulse_control_score = max(0.0, self.metrics.impulse_control_score - 0.05)
    
    def _detect_recursive_loops(self):
        """Detect recursive thinking patterns."""
        if len(self.thought_patterns) < 5:
            return
        
        # Analyze recent thought patterns for recursion
        recent_patterns = list(self.thought_patterns)[-10:]
        
        # Check for circular references
        circular_count = 0
        for i, pattern in enumerate(recent_patterns):
            for j, other_pattern in enumerate(recent_patterns[i+1:], i+1):
                if self._is_circular_reference(pattern, other_pattern):
                    circular_count += 1
        
        if circular_count >= 2:
            self.metrics.recursive_loop_count += 1
            logger.warning(f"Circular reference detected in thought patterns")
    
    def _is_circular_reference(self, pattern1: Dict, pattern2: Dict) -> bool:
        """Check if two patterns form a circular reference."""
        # Simple heuristic: if patterns reference each other's outputs as inputs
        pattern1_outputs = set(pattern1.get("outputs", []))
        pattern2_inputs = set(pattern2.get("inputs", []))
        
        pattern2_outputs = set(pattern2.get("outputs", []))
        pattern1_inputs = set(pattern1.get("inputs", []))
        
        return bool(pattern1_outputs & pattern2_inputs) and bool(pattern2_outputs & pattern1_inputs)
    
    def _update_emotional_state(self, decision_data: Dict):
        """Update emotional state based on decision outcomes."""
        # Natural decay of emotional states
        decay_rate = 0.05
        
        # Decay stress and excitement over time
        self.metrics.stress_level = max(0.0, self.metrics.stress_level - decay_rate)
        self.metrics.excitement_level = max(0.0, self.metrics.excitement_level - decay_rate)
        
        # Personality influence on emotional processing
        if self.personality_influence:
            # More analytical personalities process emotions differently
            if self.personality_influence.analytical > 0.7:
                decay_rate *= 1.2  # Faster emotional decay
            elif self.personality_influence.analytical < 0.3:
                decay_rate *= 0.8  # Slower emotional decay
    
    def _update_emotional_stability(self, event_type: str, intensity: float):
        """Update emotional stability based on events."""
        stability_change = 0.0
        
        if event_type == "success":
            stability_change = 0.02 * intensity
        elif event_type == "failure":
            stability_change = -0.03 * intensity
        elif event_type == "surprise":
            stability_change = -0.01 * intensity
        elif event_type == "validation":
            stability_change = 0.01 * intensity
        elif event_type == "rejection":
            stability_change = -0.02 * intensity
        
        self.metrics.emotional_stability = max(0.0, min(1.0, 
            self.metrics.emotional_stability + stability_change))
    
    def _check_emotional_instability(self):
        """Check for emotional instability patterns."""
        if len(self.emotional_events) < 10:
            return
        
        # Analyze recent emotional events for instability
        recent_events = list(self.emotional_events)[-20:]
        
        # Calculate emotional volatility
        intensities = [event["intensity"] for event in recent_events]
        volatility = self._calculate_volatility(intensities)
        
        if volatility > self.thresholds["emotional_instability"]:
            self.metrics.emotional_stability = max(0.0, 
                self.metrics.emotional_stability - 0.05)
            logger.warning(f"High emotional volatility detected: {volatility:.3f}")
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility of a series of values."""
        if len(values) < 2:
            return 0.0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _detect_problematic_patterns(self):
        """Detect various problematic patterns."""
        # Check for addictive behavior patterns
        self._detect_addictive_behavior()
        
        # Check for impulse control issues
        self._detect_impulse_control_issues()
        
        # Check for burnout indicators
        self._detect_burnout_indicators()
    
    def _detect_addictive_behavior(self):
        """Detect addictive behavior patterns."""
        if len(self.decision_history) < 10:
            return
        
        recent_decisions = list(self.decision_history)[-20:]
        
        # Look for validation-seeking patterns
        validation_seeking = 0
        for decision in recent_decisions:
            if decision.get("goal_type") == "validation" or decision.get("seeking_approval"):
                validation_seeking += 1
        
        if validation_seeking > len(recent_decisions) * 0.3:
            self.metrics.addictive_behavior_score = min(1.0, 
                self.metrics.addictive_behavior_score + 0.1)
            logger.warning("Addictive behavior pattern detected: excessive validation seeking")
    
    def _detect_impulse_control_issues(self):
        """Detect impulse control issues."""
        if len(self.decision_history) < 5:
            return
        
        recent_decisions = list(self.decision_history)[-10:]
        
        # Look for impulsive decision patterns
        impulsive_decisions = 0
        for decision in recent_decisions:
            if (decision.get("planning_time", 0) < 1.0 and 
                decision.get("complexity", 0) > 0.5):
                impulsive_decisions += 1
        
        if impulsive_decisions > len(recent_decisions) * 0.4:
            self.metrics.impulse_control_score = max(0.0, 
                self.metrics.impulse_control_score - 0.05)
            logger.warning("Impulse control issues detected")
    
    def _detect_burnout_indicators(self):
        """Detect burnout indicators."""
        # High stress + high complexity + low success rate
        if (self.metrics.stress_level > 0.7 and 
            self.metrics.burnout_risk > 0.5):
            
            # Check recent success rate
            if len(self.decision_history) >= 10:
                recent_decisions = list(self.decision_history)[-10:]
                success_rate = sum(1 for d in recent_decisions if d.get("success", False)) / len(recent_decisions)
                
                if success_rate < 0.6:
                    self.metrics.burnout_risk = min(1.0, self.metrics.burnout_risk + 0.1)
                    logger.warning("Burnout indicators detected: high stress + low success rate")
    
    def _update_mental_health_status(self):
        """Update overall mental health status based on metrics."""
        # Determine status based on thresholds
        if self.metrics.stress_level > self.thresholds["stress_high"]:
            self.metrics.status = MentalHealthStatus.STRESSED
        elif self.metrics.excitement_level > self.thresholds["excitement_high"]:
            self.metrics.status = MentalHealthStatus.EXCITED
        elif self.metrics.recursive_loop_count >= self.thresholds["recursive_loop"]:
            self.metrics.status = MentalHealthStatus.RECURSIVE
        elif self.metrics.addictive_behavior_score >= self.thresholds["addictive_behavior"]:
            self.metrics.status = MentalHealthStatus.ADDICTIVE
        elif self.metrics.burnout_risk >= self.thresholds["burnout_risk"]:
            self.metrics.status = MentalHealthStatus.OVERWHELMED
        else:
            self.metrics.status = MentalHealthStatus.STABLE
    
    def get_intervention_recommendations(self) -> List[str]:
        """Get recommendations for mental health interventions."""
        recommendations = []
        
        if self.metrics.status == MentalHealthStatus.STRESSED:
            recommendations.extend([
                "Reduce task complexity",
                "Increase planning time",
                "Take breaks between decisions",
                "Use simpler decision strategies"
            ])
        
        elif self.metrics.status == MentalHealthStatus.EXCITED:
            recommendations.extend([
                "Implement cooling-off periods",
                "Add validation steps",
                "Review decisions before execution",
                "Reduce novelty-seeking behavior"
            ])
        
        elif self.metrics.status == MentalHealthStatus.RECURSIVE:
            recommendations.extend([
                "Break circular thought patterns",
                "Introduce external constraints",
                "Use different problem-solving approaches",
                "Implement thought termination techniques"
            ])
        
        elif self.metrics.status == MentalHealthStatus.ADDICTIVE:
            recommendations.extend([
                "Reduce validation-seeking behavior",
                "Focus on intrinsic motivation",
                "Implement delayed gratification",
                "Diversify goal types"
            ])
        
        elif self.metrics.status == MentalHealthStatus.OVERWHELMED:
            recommendations.extend([
                "Reduce workload",
                "Implement stress management techniques",
                "Increase supervision and support",
                "Focus on simpler tasks"
            ])
        
        return recommendations
    
    def should_intervene(self) -> bool:
        """Check if intervention is needed."""
        # Check if enough time has passed since last intervention
        if (self.last_intervention and 
            datetime.utcnow() - self.last_intervention < self.intervention_cooldown):
            return False
        
        # Check if any metrics exceed intervention thresholds
        return (self.metrics.stress_level > 0.8 or
                self.metrics.excitement_level > 0.9 or
                self.metrics.recursive_loop_count >= 3 or
                self.metrics.addictive_behavior_score > 0.7 or
                self.metrics.burnout_risk > 0.8 or
                self.metrics.emotional_stability < 0.3)
    
    def get_current_metrics(self) -> MentalHealthMetrics:
        """Get current mental health metrics."""
        return self.metrics
    
    def reset_metrics(self):
        """Reset mental health metrics to stable state."""
        self.metrics = MentalHealthMetrics(
            status=MentalHealthStatus.STABLE,
            stress_level=0.0,
            excitement_level=0.0,
            recursive_loop_count=0,
            addictive_behavior_score=0.0,
            impulse_control_score=1.0,
            emotional_stability=1.0,
            burnout_risk=0.0
        )
        
        self.last_intervention = datetime.utcnow()
        logger.info("Mental health metrics reset to stable state")
    
    def get_mental_health_summary(self) -> Dict:
        """Get a summary of mental health status."""
        return {
            "status": self.metrics.status.value,
            "stress_level": self.metrics.stress_level,
            "excitement_level": self.metrics.excitement_level,
            "recursive_loop_count": self.metrics.recursive_loop_count,
            "addictive_behavior_score": self.metrics.addictive_behavior_score,
            "impulse_control_score": self.metrics.impulse_control_score,
            "emotional_stability": self.metrics.emotional_stability,
            "burnout_risk": self.metrics.burnout_risk,
            "intervention_needed": self.should_intervene(),
            "recommendations": self.get_intervention_recommendations(),
            "total_decisions": len(self.decision_history),
            "total_thought_patterns": len(self.thought_patterns),
            "total_emotional_events": len(self.emotional_events),
        }