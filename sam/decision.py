"""
Main Decision Engine for the S.A.M. system.

Orchestrates all components and provides the primary interface for decision-making.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import (
    DecisionRequest,
    DecisionResponse,
    MaturityLevel,
    MentalHealthStatus,
    PersonalityInfluence,
)
from .maturity import MaturityTracker
from .mental_health import MentalHealthMonitor
from .core.orientation import Orientation

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Main decision engine that orchestrates all S.A.M. components.
    
    Provides a unified interface for decision-making while managing maturity,
    mental health, and learning throughout the AI's development.
    """
    
    def __init__(self, 
                 maturity_level: str = "infant",
                 personality_influence: Optional[PersonalityInfluence] = None,
                 data_path: Optional[str] = None):
        """
        Initialize the decision engine.
        
        Args:
            maturity_level: Starting maturity level ("infant", "child", "adolescent", "adult")
            personality_influence: Personality traits that influence decision-making
            data_path: Path for storing maturity and mental health data
        """
        # Initialize core components
        self.maturity_tracker = MaturityTracker(data_path)
        self.mental_health_monitor = MentalHealthMonitor(personality_influence)
        self.orientation = Orientation(self.maturity_tracker, self.mental_health_monitor)
        
        # Set initial maturity level if different from default
        if maturity_level != self.maturity_tracker.profile.level.value:
            self._set_maturity_level(maturity_level)
        
        # Engine state
        self.is_initialized = True
        self.total_decisions = 0
        self.start_time = datetime.utcnow()
        
        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "average_confidence": 0.0,
            "average_response_time": 0.0,
        }
        
        logger.info(f"Decision engine initialized at maturity level: {self.maturity_tracker.profile.level.value}")
    
    async def decide(self, 
                    goal: str,
                    context: Optional[Dict[str, Any]] = None,
                    constraints: Optional[Dict[str, Any]] = None,
                    urgency: float = 0.5,
                    complexity: float = 0.5,
                    personality_influence: Optional[PersonalityInfluence] = None) -> DecisionResponse:
        """
        Make a decision based on the given goal and context.
        
        Args:
            goal: The goal to achieve
            context: Additional context information
            constraints: Constraints to consider
            urgency: Urgency level (0-1)
            complexity: Complexity level (0-1)
            personality_influence: Personality influence for this decision
            
        Returns:
            DecisionResponse with the selected action plan and metadata
        """
        start_time = datetime.utcnow()
        self.performance_metrics["total_requests"] += 1
        
        try:
            # Create decision request
            request = DecisionRequest(
                goal=goal,
                context=context or {},
                constraints=constraints or {},
                urgency=urgency,
                complexity=complexity,
                personality_influence=personality_influence or self.mental_health_monitor.personality_influence
            )
            
            # Validate request against maturity constraints
            validation_result = self._validate_request(request)
            if not validation_result["valid"]:
                return self._create_constraint_violation_response(request, validation_result["reasons"])
            
            # Check mental health before processing
            if self.mental_health_monitor.should_intervene():
                return self._create_mental_health_intervention_response(request)
            
            # Process request through orientation module
            response = await self.orientation.process_request(request)
            
            # Update performance metrics
            self._update_performance_metrics(response, start_time)
            
            # Record successful decision
            self.total_decisions += 1
            self.performance_metrics["successful_decisions"] += 1
            
            logger.info(f"Decision made successfully: {response.plan_id} (confidence: {response.confidence:.3f})")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in decision making: {e}")
            self.performance_metrics["failed_decisions"] += 1
            
            # Return fallback response
            return self._create_error_response(goal, str(e))
    
    def _validate_request(self, request: DecisionRequest) -> Dict[str, Any]:
        """Validate request against maturity and mental health constraints."""
        valid = True
        reasons = []
        
        # Check complexity constraints
        if not self.maturity_tracker.can_handle_complexity(request.complexity):
            valid = False
            reasons.append(f"Complexity {request.complexity:.2f} exceeds maturity level {self.maturity_tracker.profile.level.value}")
        
        # Check urgency constraints
        if not self.maturity_tracker.can_handle_urgency(request.urgency):
            valid = False
            reasons.append(f"Urgency {request.urgency:.2f} exceeds maturity level {self.maturity_tracker.profile.level.value}")
        
        # Check mental health constraints
        mental_health = self.mental_health_monitor.get_current_metrics()
        if mental_health.status == MentalHealthStatus.OVERWHELMED:
            valid = False
            reasons.append("Mental health status is overwhelmed")
        
        # Check for recursive loops
        if mental_health.recursive_loop_count >= 3:
            valid = False
            reasons.append("Too many recursive loops detected")
        
        return {"valid": valid, "reasons": reasons}
    
    def _create_constraint_violation_response(self, request: DecisionRequest, 
                                            reasons: List[str]) -> DecisionResponse:
        """Create a response for constraint violations."""
        from uuid import uuid4
        
        return DecisionResponse(
            plan_id=uuid4(),
            confidence=0.0,
            mental_health_status=self.mental_health_monitor.get_current_metrics().status,
            maturity_level=self.maturity_tracker.profile.level,
            trace_id=uuid4(),
            warnings=reasons,
            recommendations=[
                "Reduce complexity or urgency",
                "Wait for mental health to stabilize",
                "Request human assistance"
            ]
        )
    
    def _create_mental_health_intervention_response(self, request: DecisionRequest) -> DecisionResponse:
        """Create a response when mental health intervention is needed."""
        from uuid import uuid4
        
        recommendations = self.mental_health_monitor.get_intervention_recommendations()
        
        return DecisionResponse(
            plan_id=uuid4(),
            confidence=0.0,
            mental_health_status=self.mental_health_monitor.get_current_metrics().status,
            maturity_level=self.maturity_tracker.profile.level,
            trace_id=uuid4(),
            warnings=["Mental health intervention required"],
            recommendations=recommendations
        )
    
    def _create_error_response(self, goal: str, error: str) -> DecisionResponse:
        """Create a response for errors."""
        from uuid import uuid4
        
        return DecisionResponse(
            plan_id=uuid4(),
            confidence=0.0,
            mental_health_status=self.mental_health_monitor.get_current_metrics().status,
            maturity_level=self.maturity_tracker.profile.level,
            trace_id=uuid4(),
            warnings=[f"Decision engine error: {error}"],
            recommendations=[
                "Retry with simpler request",
                "Check system status",
                "Request human assistance"
            ]
        )
    
    def _update_performance_metrics(self, response: DecisionResponse, start_time: datetime):
        """Update performance metrics based on the response."""
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Update average response time
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Update average confidence
        current_avg_confidence = self.performance_metrics["average_confidence"]
        self.performance_metrics["average_confidence"] = (
            (current_avg_confidence * (total_requests - 1) + response.confidence) / total_requests
        )
    
    def _set_maturity_level(self, level: str):
        """Set the maturity level (for initialization only)."""
        try:
            maturity_level = MaturityLevel(level)
            self.maturity_tracker.profile.level = maturity_level
            
            # Update profile with new level's default values
            config = self.maturity_tracker.MATURITY_CONFIGS[maturity_level]
            self.maturity_tracker.profile.confidence_threshold = config["confidence_threshold"]
            self.maturity_tracker.profile.supervision_level = config["supervision_level"]
            self.maturity_tracker.profile.risk_tolerance = config["risk_tolerance"]
            self.maturity_tracker.profile.exploration_rate = config["exploration_rate"]
            self.maturity_tracker.profile.learning_rate = config["learning_rate"]
            
            logger.info(f"Maturity level set to: {level}")
            
        except ValueError:
            logger.warning(f"Invalid maturity level: {level}. Using default: infant")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the decision engine."""
        return {
            "engine_status": {
                "initialized": self.is_initialized,
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "total_decisions": self.total_decisions,
            },
            "maturity": self.maturity_tracker.get_maturity_summary(),
            "mental_health": self.mental_health_monitor.get_mental_health_summary(),
            "performance": self.performance_metrics,
            "current_constraints": {
                "max_complexity": self.maturity_tracker.get_current_config().get("max_complexity", 1.0),
                "max_urgency": self.maturity_tracker.get_current_config().get("max_urgency", 1.0),
                "confidence_threshold": self.maturity_tracker.get_confidence_threshold(),
                "risk_tolerance": self.maturity_tracker.get_risk_tolerance(),
                "supervision_level": self.maturity_tracker.get_supervision_level(),
            }
        }
    
    def get_maturity_summary(self) -> Dict[str, Any]:
        """Get maturity summary."""
        return self.maturity_tracker.get_maturity_summary()
    
    def get_mental_health_summary(self) -> Dict[str, Any]:
        """Get mental health summary."""
        return self.mental_health_monitor.get_mental_health_summary()
    
    def record_thought_pattern(self, pattern: Dict[str, Any]):
        """Record a thought pattern for mental health monitoring."""
        self.mental_health_monitor.update_from_thought_pattern(pattern)
    
    def record_emotional_event(self, event_type: str, intensity: float, context: Dict = None):
        """Record an emotional event for mental health monitoring."""
        self.mental_health_monitor.record_emotional_event(event_type, intensity, context)
    
    def force_maturity_progression(self, new_level: str):
        """Force progression to a new maturity level (for testing/development)."""
        try:
            maturity_level = MaturityLevel(new_level)
            self.maturity_tracker._progress_to_level(maturity_level)
            logger.info(f"Forced maturity progression to: {new_level}")
        except ValueError:
            logger.error(f"Invalid maturity level: {new_level}")
    
    def reset_mental_health(self):
        """Reset mental health metrics to stable state."""
        self.mental_health_monitor.reset_metrics()
        logger.info("Mental health metrics reset to stable state")
    
    def get_intervention_recommendations(self) -> List[str]:
        """Get current intervention recommendations."""
        return self.mental_health_monitor.get_intervention_recommendations()
    
    def should_intervene(self) -> bool:
        """Check if mental health intervention is needed."""
        return self.mental_health_monitor.should_intervene()
    
    async def shutdown(self):
        """Gracefully shutdown the decision engine."""
        logger.info("Shutting down decision engine...")
        
        # Save final state
        self.maturity_tracker._save_profile()
        self.mental_health_monitor._save_mental_health()
        
        # Log final statistics
        logger.info(f"Final statistics: {self.total_decisions} decisions made")
        logger.info(f"Final maturity level: {self.maturity_tracker.profile.level.value}")
        logger.info(f"Final mental health status: {self.mental_health_monitor.get_current_metrics().status.value}")
        
        self.is_initialized = False
        logger.info("Decision engine shutdown complete")


# Convenience function for quick decision making
async def make_decision(goal: str, 
                       context: Optional[Dict[str, Any]] = None,
                       maturity_level: str = "infant",
                       personality_influence: Optional[PersonalityInfluence] = None) -> DecisionResponse:
    """
    Convenience function for making a single decision.
    
    Args:
        goal: The goal to achieve
        context: Additional context information
        maturity_level: Maturity level for the decision engine
        personality_influence: Personality influence
        
    Returns:
        DecisionResponse with the decision result
    """
    engine = DecisionEngine(
        maturity_level=maturity_level,
        personality_influence=personality_influence
    )
    
    try:
        response = await engine.decide(goal, context)
        return response
    finally:
        await engine.shutdown()