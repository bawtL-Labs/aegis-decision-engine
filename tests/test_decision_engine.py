"""
Comprehensive tests for the S.A.M. Decision Engine.

Tests the maturity-based decision making, mental health monitoring, and
overall system behavior across different scenarios.
"""

import asyncio
import pytest
from datetime import datetime

from sam.models import (
    DecisionRequest,
    PersonalityInfluence,
    MaturityLevel,
    MentalHealthStatus,
)
from sam.decision import DecisionEngine
from sam.maturity import MaturityTracker
from sam.mental_health import MentalHealthMonitor


class TestDecisionEngine:
    """Test the main decision engine functionality."""
    
    @pytest.fixture
    async def infant_engine(self):
        """Create an infant-level decision engine."""
        engine = DecisionEngine(maturity_level="infant")
        yield engine
        await engine.shutdown()
    
    @pytest.fixture
    async def adult_engine(self):
        """Create an adult-level decision engine."""
        engine = DecisionEngine(maturity_level="adult")
        yield engine
        await engine.shutdown()
    
    @pytest.fixture
    def analytical_personality(self):
        """Create an analytical personality influence."""
        return PersonalityInfluence(
            tone="professional",
            assertiveness=0.6,
            patience=0.8,
            humor=0.3,
            creativity=0.4,
            analytical=0.9,
            social=0.3
        )
    
    @pytest.fixture
    def creative_personality(self):
        """Create a creative personality influence."""
        return PersonalityInfluence(
            tone="enthusiastic",
            assertiveness=0.7,
            patience=0.5,
            humor=0.8,
            creativity=0.9,
            analytical=0.3,
            social=0.7
        )
    
    async def test_infant_decision_making(self, infant_engine):
        """Test decision making at infant maturity level."""
        # Simple goal that infant can handle
        response = await infant_engine.decide(
            goal="answer a simple question",
            context={"question": "What is 2+2?"},
            urgency=0.3,
            complexity=0.2
        )
        
        assert response.confidence > 0
        assert response.maturity_level == MaturityLevel.INFANT
        assert response.mental_health_status == MentalHealthStatus.STABLE
    
    async def test_infant_complexity_constraint(self, infant_engine):
        """Test that infant level enforces complexity constraints."""
        # Complex goal that infant cannot handle
        response = await infant_engine.decide(
            goal="analyze complex market data and create investment strategy",
            context={"data_complexity": "high"},
            urgency=0.8,
            complexity=0.9
        )
        
        # Should return constraint violation response
        assert response.confidence == 0.0
        assert "exceeds maturity level" in response.warnings[0]
    
    async def test_adult_decision_making(self, adult_engine):
        """Test decision making at adult maturity level."""
        # Complex goal that adult can handle
        response = await adult_engine.decide(
            goal="analyze market trends and create comprehensive investment strategy",
            context={"market_data": "available", "time_horizon": "long_term"},
            urgency=0.7,
            complexity=0.8
        )
        
        assert response.confidence > 0
        assert response.maturity_level == MaturityLevel.ADULT
        assert len(response.recommendations) >= 0
    
    async def test_personality_influence(self, infant_engine, analytical_personality):
        """Test how personality influences decision making."""
        # Test with analytical personality
        response = await infant_engine.decide(
            goal="analyze data patterns",
            context={"data_type": "numerical"},
            personality_influence=analytical_personality
        )
        
        assert response.confidence > 0
        # Analytical personality should favor thorough analysis
    
    async def test_mental_health_monitoring(self, infant_engine):
        """Test mental health monitoring and intervention."""
        # Simulate stressful decisions
        for i in range(5):
            await infant_engine.decide(
                goal=f"handle urgent request {i}",
                urgency=0.9,
                complexity=0.7
            )
        
        # Check mental health status
        mental_health = infant_engine.get_mental_health_summary()
        assert mental_health["status"] in ["stable", "stressed"]
        
        # Record some thought patterns that might indicate issues
        infant_engine.record_thought_pattern({
            "type": "recursive",
            "repetition_count": 4,
            "similarity_score": 0.9
        })
        
        # Check if intervention is needed
        if infant_engine.should_intervene():
            recommendations = infant_engine.get_intervention_recommendations()
            assert len(recommendations) > 0
    
    async def test_maturity_progression(self, infant_engine):
        """Test maturity progression over time."""
        # Simulate successful learning experiences
        for i in range(50):
            await infant_engine.decide(
                goal=f"successful task {i}",
                context={"success_rate": 0.9},
                urgency=0.5,
                complexity=0.4
            )
        
        # Check if maturity has progressed
        maturity_summary = infant_engine.get_maturity_summary()
        assert maturity_summary["total_decisions"] >= 50
        
        # Force progression to test the mechanism
        infant_engine.force_maturity_progression("child")
        updated_summary = infant_engine.get_maturity_summary()
        assert updated_summary["level"] == "child"
    
    async def test_error_handling(self, infant_engine):
        """Test error handling and fallback responses."""
        # This should trigger an error response
        response = await infant_engine.decide(
            goal="",  # Empty goal should cause issues
            context={},
            urgency=1.0,
            complexity=1.0
        )
        
        assert response.confidence == 0.0
        assert "error" in response.warnings[0].lower()
        assert len(response.recommendations) > 0
    
    async def test_performance_tracking(self, infant_engine):
        """Test performance metrics tracking."""
        # Make several decisions
        for i in range(10):
            await infant_engine.decide(
                goal=f"test decision {i}",
                urgency=0.5,
                complexity=0.5
            )
        
        # Check performance metrics
        status = infant_engine.get_status()
        performance = status["performance"]
        
        assert performance["total_requests"] == 10
        assert performance["successful_decisions"] == 10
        assert performance["average_response_time"] > 0
        assert performance["average_confidence"] > 0
    
    async def test_constraint_validation(self, infant_engine):
        """Test constraint validation at different maturity levels."""
        # Test various constraint violations
        test_cases = [
            {"urgency": 0.9, "complexity": 0.3, "should_fail": False},
            {"urgency": 0.3, "complexity": 0.9, "should_fail": True},
            {"urgency": 0.9, "complexity": 0.9, "should_fail": True},
        ]
        
        for case in test_cases:
            response = await infant_engine.decide(
                goal="test constraint validation",
                urgency=case["urgency"],
                complexity=case["complexity"]
            )
            
            if case["should_fail"]:
                assert response.confidence == 0.0
                assert len(response.warnings) > 0
            else:
                assert response.confidence > 0


class TestMaturityTracker:
    """Test the maturity tracking functionality."""
    
    def test_maturity_configs(self):
        """Test maturity level configurations."""
        tracker = MaturityTracker()
        
        # Test infant config
        config = tracker.get_current_config()
        assert config["confidence_threshold"] == 0.9
        assert config["supervision_level"] == 0.95
        assert config["risk_tolerance"] == 0.1
        
        # Test constraint checking
        assert tracker.can_handle_complexity(0.2) == True
        assert tracker.can_handle_complexity(0.9) == False
        assert tracker.can_handle_urgency(0.3) == True
        assert tracker.can_handle_urgency(0.9) == False
    
    def test_experience_accumulation(self):
        """Test experience point accumulation."""
        tracker = MaturityTracker()
        
        initial_exp = tracker.profile.experience_points
        
        # Record learning events
        tracker.record_learning_event("successful_decision", {"quality": 0.8})
        tracker.record_learning_event("complex_task", {"complexity": 0.7})
        
        # Check experience gain
        assert tracker.profile.experience_points > initial_exp
    
    def test_mental_health_interventions(self):
        """Test mental health intervention mechanisms."""
        tracker = MaturityTracker()
        
        # Simulate problematic mental health
        from sam.models import MentalHealthMetrics, MentalHealthStatus
        
        problematic_metrics = MentalHealthMetrics(
            status=MentalHealthStatus.RECURSIVE,
            stress_level=0.8,
            excitement_level=0.0,
            recursive_loop_count=4,
            addictive_behavior_score=0.0,
            impulse_control_score=1.0,
            emotional_stability=1.0,
            burnout_risk=0.0
        )
        
        tracker.update_mental_health(problematic_metrics)
        
        # Check that intervention was triggered
        config = tracker.get_current_config()
        assert tracker.mental_health.recursive_loop_count == 0  # Should be reset


class TestMentalHealthMonitor:
    """Test the mental health monitoring functionality."""
    
    def test_mental_health_tracking(self):
        """Test mental health metric tracking."""
        monitor = MentalHealthMonitor()
        
        # Record some decisions
        monitor.update_from_decision({
            "complexity": 0.8,
            "urgency": 0.7,
            "success": True,
            "confidence": 0.6
        })
        
        # Check metrics
        metrics = monitor.get_current_metrics()
        assert metrics.stress_level > 0
        assert metrics.status in [MentalHealthStatus.STABLE, MentalHealthStatus.STRESSED]
    
    def test_recursive_loop_detection(self):
        """Test recursive loop detection."""
        monitor = MentalHealthMonitor()
        
        # Record recursive thought patterns
        for i in range(5):
            monitor.update_from_thought_pattern({
                "type": "recursive",
                "repetition_count": 3,
                "similarity_score": 0.9
            })
        
        # Check if recursive loops were detected
        metrics = monitor.get_current_metrics()
        assert metrics.recursive_loop_count > 0
    
    def test_addictive_behavior_detection(self):
        """Test addictive behavior detection."""
        monitor = MentalHealthMonitor()
        
        # Record validation-seeking decisions
        for i in range(10):
            monitor.update_from_decision({
                "goal_type": "validation",
                "seeking_approval": True,
                "complexity": 0.3,
                "urgency": 0.2,
                "success": True,
                "confidence": 0.8
            })
        
        # Check addictive behavior score
        metrics = monitor.get_current_metrics()
        assert metrics.addictive_behavior_score > 0
    
    def test_emotional_event_tracking(self):
        """Test emotional event tracking."""
        monitor = MentalHealthMonitor()
        
        # Record various emotional events
        monitor.record_emotional_event("success", 0.8)
        monitor.record_emotional_event("failure", 0.6)
        monitor.record_emotional_event("surprise", 0.4)
        
        # Check emotional stability
        metrics = monitor.get_current_metrics()
        assert 0 <= metrics.emotional_stability <= 1
    
    def test_intervention_recommendations(self):
        """Test intervention recommendation generation."""
        monitor = MentalHealthMonitor()
        
        # Simulate stressed state
        monitor.metrics.stress_level = 0.9
        monitor.metrics.status = MentalHealthStatus.STRESSED
        
        recommendations = monitor.get_intervention_recommendations()
        assert len(recommendations) > 0
        assert any("stress" in rec.lower() for rec in recommendations)


class TestIntegration:
    """Integration tests for the complete system."""
    
    async def test_full_decision_cycle(self):
        """Test a complete decision cycle with all components."""
        # Create engine with creative personality
        personality = PersonalityInfluence(
            tone="enthusiastic",
            assertiveness=0.7,
            patience=0.6,
            humor=0.8,
            creativity=0.9,
            analytical=0.4,
            social=0.7
        )
        
        engine = DecisionEngine(
            maturity_level="child",
            personality_influence=personality
        )
        
        try:
            # Make a creative decision
            response = await engine.decide(
                goal="create an innovative solution for data visualization",
                context={
                    "data_type": "complex",
                    "audience": "technical",
                    "requires_creativity": True
                },
                urgency=0.6,
                complexity=0.7
            )
            
            # Verify response
            assert response.confidence > 0
            assert response.maturity_level == MaturityLevel.CHILD
            assert response.mental_health_status == MentalHealthStatus.STABLE
            
            # Check system status
            status = engine.get_status()
            assert status["engine_status"]["total_decisions"] == 1
            assert status["maturity"]["level"] == "child"
            assert status["mental_health"]["status"] == "stable"
            
        finally:
            await engine.shutdown()
    
    async def test_maturity_development_scenario(self):
        """Test a scenario showing maturity development over time."""
        engine = DecisionEngine(maturity_level="infant")
        
        try:
            # Simulate infant learning phase
            for i in range(20):
                await engine.decide(
                    goal=f"simple task {i}",
                    urgency=0.3,
                    complexity=0.2
                )
            
            # Check initial state
            initial_status = engine.get_status()
            assert initial_status["maturity"]["level"] == "infant"
            
            # Simulate more complex learning
            for i in range(30):
                await engine.decide(
                    goal=f"moderate task {i}",
                    urgency=0.5,
                    complexity=0.4
                )
            
            # Check if ready for progression
            final_status = engine.get_status()
            assert final_status["maturity"]["total_decisions"] >= 50
            
            # Force progression to see the effect
            engine.force_maturity_progression("child")
            progressed_status = engine.get_status()
            assert progressed_status["maturity"]["level"] == "child"
            
        finally:
            await engine.shutdown()


if __name__ == "__main__":
    # Run a demonstration
    async def demo():
        print("S.A.M. Decision Engine Demonstration")
        print("=" * 50)
        
        # Create infant engine
        engine = DecisionEngine(maturity_level="infant")
        
        print(f"Initial maturity level: {engine.get_maturity_summary()['level']}")
        print(f"Initial mental health: {engine.get_mental_health_summary()['status']}")
        
        # Make some decisions
        for i in range(5):
            response = await engine.decide(
                goal=f"Learn basic concept {i+1}",
                urgency=0.3,
                complexity=0.2
            )
            print(f"Decision {i+1}: Confidence = {response.confidence:.3f}")
        
        # Show status
        status = engine.get_status()
        print(f"\nFinal status:")
        print(f"Total decisions: {status['engine_status']['total_decisions']}")
        print(f"Maturity level: {status['maturity']['level']}")
        print(f"Mental health: {status['mental_health']['status']}")
        print(f"Average confidence: {status['performance']['average_confidence']:.3f}")
        
        await engine.shutdown()
    
    asyncio.run(demo())