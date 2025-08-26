"""
Tests for personality influence on utility calculation in the S.A.M. Decision Engine.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from src.sam.core.utility import UtilityEngine
from src.sam.models import (
    ActionPlan, 
    MaturityLevel, 
    PersonalityInfluence,
    PersonalityWeights
)


class TestPersonalityTiltsUtility:
    """Test personality influence on utility calculation."""
    
    @pytest.fixture
    def utility_engine(self):
        """Create utility engine instance."""
        return UtilityEngine()
    
    @pytest.fixture
    def sample_plan(self):
        """Create a sample action plan."""
        return ActionPlan(
            request_id="test-request",
            goal={"type": "answer", "spec": "What is the capital of France?"},
            steps=[
                {"id": "s1", "type": "llm", "tool_id": "local_llm", "args": {"prompt": "What is the capital of France?"}},
            ],
            estimates={"quality": 0.7, "risk": 0.2, "spend": 0.4},
            profile={"mode": "flow", "llm": "local_20B"},
            explanations="Sample plan for testing",
            status="proposed"
        )
    
    def test_analytical_personality_tilts_weights(self, utility_engine, sample_plan):
        """Test that analytical personality tilts weights toward quality and rigor."""
        personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.5,
            patience=0.5,
            humor=0.3,
            creativity=0.3,
            analytical=0.9,  # High analytical
            social=0.4
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality
        )
        
        weights = result["weights"]
        
        # Analytical personality should increase quality and rigor weights
        assert weights.quality > 0.3  # Base weight is 0.3
        assert weights.rigor > 0.5    # Base weight is 0.5
        assert weights.novelty < 0.6  # Base weight is 0.6, should be reduced
    
    def test_creative_personality_tilts_weights(self, utility_engine, sample_plan):
        """Test that creative personality tilts weights toward novelty and goal achievement."""
        personality = PersonalityInfluence(
            tone="creative",
            assertiveness=0.5,
            patience=0.5,
            humor=0.7,
            creativity=0.9,  # High creativity
            analytical=0.3,
            social=0.6
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality
        )
        
        weights = result["weights"]
        
        # Creative personality should increase novelty and goal weights
        assert weights.novelty > 0.6  # Base weight is 0.6, should be increased
        assert weights.goal > 0.25    # Base weight is 0.25, should be increased
        assert weights.rigor < 0.5    # Base weight is 0.5, should be reduced
    
    def test_assertive_personality_tilts_weights(self, utility_engine, sample_plan):
        """Test that assertive personality tilts weights toward risk tolerance."""
        personality = PersonalityInfluence(
            tone="assertive",
            assertiveness=0.9,  # High assertiveness
            patience=0.5,
            humor=0.5,
            creativity=0.5,
            analytical=0.5,
            social=0.5
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality
        )
        
        weights = result["weights"]
        
        # Assertive personality should reduce risk weight (more risk tolerant)
        assert weights.risk < 0.2  # Base weight is 0.2, should be reduced
        assert weights.safety < 0.6  # Base weight is 0.6, should be reduced
    
    def test_patient_personality_tilts_weights(self, utility_engine, sample_plan):
        """Test that patient personality tilts weights toward quality and rigor."""
        personality = PersonalityInfluence(
            tone="patient",
            assertiveness=0.5,
            patience=0.9,  # High patience
            humor=0.5,
            creativity=0.5,
            analytical=0.5,
            social=0.5
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality
        )
        
        weights = result["weights"]
        
        # Patient personality should increase quality and rigor weights
        assert weights.quality > 0.3  # Base weight is 0.3, should be increased
        assert weights.rigor > 0.5    # Base weight is 0.5, should be increased
        assert weights.spend < 0.25   # Base weight is 0.25, should be reduced
    
    def test_social_personality_tilts_weights(self, utility_engine, sample_plan):
        """Test that social personality tilts weights appropriately."""
        personality = PersonalityInfluence(
            tone="social",
            assertiveness=0.5,
            patience=0.5,
            humor=0.7,
            creativity=0.5,
            analytical=0.4,
            social=0.9  # High social
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality
        )
        
        weights = result["weights"]
        
        # Social personality should increase goal and safety weights
        assert weights.goal > 0.25    # Base weight is 0.25, should be increased
        assert weights.safety > 0.6   # Base weight is 0.6, should be increased
        assert weights.spend < 0.25   # Base weight is 0.25, should be reduced
    
    def test_personality_influence_on_utility_score(self, utility_engine, sample_plan):
        """Test that personality influence affects the final utility score."""
        # Test with analytical personality
        analytical_personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.5,
            patience=0.5,
            humor=0.3,
            creativity=0.3,
            analytical=0.9,
            social=0.4
        )
        
        analytical_result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=analytical_personality
        )
        
        # Test with creative personality
        creative_personality = PersonalityInfluence(
            tone="creative",
            assertiveness=0.5,
            patience=0.5,
            humor=0.7,
            creativity=0.9,
            analytical=0.3,
            social=0.6
        )
        
        creative_result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=creative_personality
        )
        
        # Utility scores should be different due to personality influence
        assert analytical_result["utility"] != creative_result["utility"]
    
    def test_personality_factor_breakdown(self, utility_engine, sample_plan):
        """Test that personality factors are included in factor breakdown."""
        personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.8,
            patience=0.7,
            humor=0.3,
            creativity=0.4,
            analytical=0.9,
            social=0.5
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality
        )
        
        factor_breakdown = result["factor_breakdown"]
        
        # Verify personality factors are included
        assert "personality_factors" in factor_breakdown
        personality_factors = factor_breakdown["personality_factors"]
        
        assert "novelty" in personality_factors
        assert "rigor" in personality_factors
        assert "safety" in personality_factors
        
        # Verify personality influence on these factors
        assert personality_factors["novelty"] < 0.6  # Reduced by analytical personality
        assert personality_factors["rigor"] > 0.5    # Increased by analytical personality
    
    def test_maturity_level_interaction_with_personality(self, utility_engine, sample_plan):
        """Test interaction between maturity level and personality influence."""
        personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.5,
            patience=0.5,
            humor=0.3,
            creativity=0.3,
            analytical=0.9,
            social=0.4
        )
        
        # Test with infant maturity
        infant_result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.INFANT,
            personality_influence=personality
        )
        
        # Test with adult maturity
        adult_result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality
        )
        
        # Results should be different due to maturity level
        assert infant_result["utility"] != adult_result["utility"]
        
        # Infant should have higher safety and rigor weights
        assert infant_result["weights"].safety > adult_result["weights"].safety
        assert infant_result["weights"].rigor > adult_result["weights"].rigor
    
    def test_context_influence_with_personality(self, utility_engine, sample_plan):
        """Test that context influences utility calculation alongside personality."""
        personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.5,
            patience=0.5,
            humor=0.3,
            creativity=0.3,
            analytical=0.9,
            social=0.4
        )
        
        # Test with high-stakes context
        high_stakes_result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality,
            context={"high_stakes": True}
        )
        
        # Test with time-sensitive context
        time_sensitive_result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality,
            context={"time_sensitive": True}
        )
        
        # Results should be different due to context
        assert high_stakes_result["utility"] != time_sensitive_result["utility"]
        
        # High-stakes should increase safety and quality weights
        assert high_stakes_result["weights"].safety > time_sensitive_result["weights"].safety
        assert high_stakes_result["weights"].quality > time_sensitive_result["weights"].quality
    
    def test_pmx_integration_with_personality(self, utility_engine, sample_plan):
        """Test PMX integration with personality influence."""
        # Mock PMX object
        class MockPMX:
            class Matrix:
                def resolve_weights(self):
                    return {
                        "goal": 0.4,
                        "quality": 0.4,
                        "risk": 0.1,
                        "spend": 0.1,
                        "novelty": 0.3,
                        "rigor": 0.8,
                        "safety": 0.9
                    }
            
            def __init__(self):
                self.matrix = self.Matrix()
        
        pmx = MockPMX()
        
        personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.5,
            patience=0.5,
            humor=0.3,
            creativity=0.3,
            analytical=0.9,
            social=0.4
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=personality,
            pmx=pmx
        )
        
        weights = result["weights"]
        
        # PMX should influence the weights
        # The weights should be a blend of base, personality, and PMX weights
        assert weights.goal > 0.25  # Should be influenced by PMX (0.4)
        assert weights.quality > 0.3  # Should be influenced by PMX (0.4)
        assert weights.risk < 0.2   # Should be influenced by PMX (0.1)
        assert weights.safety > 0.6  # Should be influenced by PMX (0.9)
    
    def test_personality_explanation_generation(self, utility_engine, sample_plan):
        """Test that personality influence affects explanation generation."""
        analytical_personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.5,
            patience=0.5,
            humor=0.3,
            creativity=0.3,
            analytical=0.9,
            social=0.4
        )
        
        result = utility_engine.calculate_utility(
            plan=sample_plan,
            maturity_level=MaturityLevel.ADULT,
            personality_influence=analytical_personality
        )
        
        # Verify explanation is generated
        assert "explanation" in result
        assert len(result["explanation"]) > 0
        
        # Explanation should reflect the utility characteristics
        explanation = result["explanation"].lower()
        if result["utility"] > 0.7:
            assert "high utility" in explanation
        elif result["utility"] < 0.4:
            assert "low utility" in explanation