"""
Tests for trace emission functionality in the S.A.M. Decision Engine.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.sam.decision import DecisionEngine
from src.sam.models import DecisionRequest, PersonalityInfluence
from aegis_core.trace import TraceLogger
from aegis_core.policy import PolicyHook
from aegis_core.state import StateStore
from aegis_core.events import EventBus


class TestTraceEmission:
    """Test trace emission functionality."""
    
    @pytest.fixture
    async def mock_components(self):
        """Create mock aegis-core components."""
        trace_logger = Mock(spec=TraceLogger)
        trace_logger.log_decision_trace = AsyncMock()
        
        policy_hook = Mock(spec=PolicyHook)
        policy_hook.check_plan = AsyncMock(return_value={"approved": True})
        
        state_store = Mock(spec=StateStore)
        state_store.get = Mock(return_value=None)
        state_store.set = AsyncMock()
        
        event_bus = Mock(spec=EventBus)
        event_bus.emit = Mock()
        event_bus.subscribe = Mock()
        
        return trace_logger, policy_hook, state_store, event_bus
    
    @pytest.fixture
    async def decision_engine(self, mock_components):
        """Create decision engine with mock components."""
        trace_logger, policy_hook, state_store, event_bus = mock_components
        
        engine = DecisionEngine(
            trace_logger=trace_logger,
            policy_hook=policy_hook,
            state_store=state_store,
            event_bus=event_bus,
            maturity_level="infant"
        )
        
        return engine
    
    @pytest.mark.asyncio
    async def test_decision_trace_emission(self, decision_engine, mock_components):
        """Test that decision traces are properly emitted."""
        trace_logger, _, _, _ = mock_components
        
        # Make a decision
        response = await decision_engine.decide(
            goal="What is the capital of France?",
            urgency=0.3,
            complexity=0.2
        )
        
        # Verify trace was logged
        assert trace_logger.log_decision_trace.called
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        
        # Verify trace structure
        assert hasattr(call_args, 'id')
        assert hasattr(call_args, 'timestamp')
        assert hasattr(call_args, 'vsp')
        assert hasattr(call_args, 'mode')
        assert hasattr(call_args, 'candidates')
        assert hasattr(call_args, 'winner')
        assert hasattr(call_args, 'reasons')
        assert hasattr(call_args, 'mental_health')
        assert hasattr(call_args, 'maturity_level')
        assert hasattr(call_args, 'personality_weights')
        assert hasattr(call_args, 'policy_flags')
    
    @pytest.mark.asyncio
    async def test_trace_contains_candidates_with_factor_breakdown(self, decision_engine, mock_components):
        """Test that trace contains candidates with factor breakdowns."""
        trace_logger, _, _, _ = mock_components
        
        # Make a decision
        await decision_engine.decide(
            goal="Analyze market data",
            urgency=0.6,
            complexity=0.7
        )
        
        # Get the logged trace
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        
        # Verify candidates contain factor breakdowns
        assert len(call_args.candidates) > 0
        for candidate in call_args.candidates:
            assert "utility" in candidate
            assert "factor_breakdown" in candidate
            assert "explanation" in candidate
            
            # Verify factor breakdown structure
            factor_breakdown = candidate["factor_breakdown"]
            assert "goal_satisfaction" in factor_breakdown
            assert "quality" in factor_breakdown
            assert "risk" in factor_breakdown
            assert "spend" in factor_breakdown
            assert "personality_factors" in factor_breakdown
    
    @pytest.mark.asyncio
    async def test_trace_contains_personality_weights(self, decision_engine, mock_components):
        """Test that trace contains personality weights."""
        trace_logger, _, _, _ = mock_components
        
        # Make a decision with personality influence
        personality = PersonalityInfluence(
            tone="analytical",
            assertiveness=0.8,
            patience=0.7,
            humor=0.3,
            creativity=0.6,
            analytical=0.9,
            social=0.4
        )
        
        await decision_engine.decide(
            goal="Create a detailed report",
            urgency=0.5,
            complexity=0.6,
            personality_influence=personality
        )
        
        # Get the logged trace
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        
        # Verify personality weights are present
        assert call_args.personality_weights is not None
        assert hasattr(call_args.personality_weights, 'goal')
        assert hasattr(call_args.personality_weights, 'quality')
        assert hasattr(call_args.personality_weights, 'risk')
        assert hasattr(call_args.personality_weights, 'spend')
        assert hasattr(call_args.personality_weights, 'novelty')
        assert hasattr(call_args.personality_weights, 'rigor')
        assert hasattr(call_args.personality_weights, 'safety')
    
    @pytest.mark.asyncio
    async def test_trace_contains_decoding_mode(self, decision_engine, mock_components):
        """Test that trace contains appropriate decoding mode."""
        trace_logger, _, _, _ = mock_components
        
        # Test different urgency levels
        test_cases = [
            (0.2, "flow"),      # Low urgency -> flow
            (0.6, "deep"),      # Medium urgency -> deep
            (0.9, "crisis"),    # High urgency -> crisis
        ]
        
        for urgency, expected_mode in test_cases:
            await decision_engine.decide(
                goal="Test decision",
                urgency=urgency,
                complexity=0.5
            )
            
            call_args = trace_logger.log_decision_trace.call_args[0][0]
            assert call_args.mode == expected_mode
    
    @pytest.mark.asyncio
    async def test_trace_contains_policy_flags(self, decision_engine, mock_components):
        """Test that trace contains policy flags."""
        trace_logger, policy_hook, _, _ = mock_components
        
        # Mock policy hook to return flags
        policy_hook.check_plan.return_value = {
            "approved": True,
            "flags": ["safety_check_passed", "budget_approved"]
        }
        
        await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        assert len(call_args.policy_flags) > 0
    
    @pytest.mark.asyncio
    async def test_trace_contains_budget_information(self, decision_engine, mock_components):
        """Test that trace contains budget information."""
        trace_logger, _, _, _ = mock_components
        
        await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=5000,
            time_limit=300
        )
        
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        assert call_args.budgets is not None
        assert "tokens" in call_args.budgets
        assert "time_seconds" in call_args.budgets
        assert "estimated_tokens" in call_args.budgets
    
    @pytest.mark.asyncio
    async def test_error_trace_emission(self, decision_engine, mock_components):
        """Test that error traces are emitted when decisions fail."""
        trace_logger, _, _, _ = mock_components
        
        # Mock a failure by making the engine raise an exception
        decision_engine._generate_action_plans = AsyncMock(return_value=[])
        
        response = await decision_engine.decide(
            goal="This will fail",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify error trace was logged
        assert trace_logger.log_decision_trace.called
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        
        # Verify it's an error trace
        assert "Error:" in call_args.reasons[0]
        assert call_args.policy_flags[0] == "denied"