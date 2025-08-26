"""
Tests for budget enforcement and fallback functionality in the S.A.M. Decision Engine.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from src.sam.decision import DecisionEngine
from src.sam.models import DecisionRequest, ActionPlan
from aegis_core.trace import TraceLogger
from aegis_core.policy import PolicyHook
from aegis_core.state import StateStore
from aegis_core.events import EventBus


class TestBudgetFallback:
    """Test budget enforcement and fallback functionality."""
    
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
    async def test_budget_enforcement(self, decision_engine, mock_components):
        """Test that budget constraints are properly enforced."""
        _, _, _, _ = mock_components
        
        # Test with very low budget
        response = await decision_engine.decide(
            goal="Analyze complex market data",
            urgency=0.7,
            complexity=0.8,
            budget=500  # Very low budget
        )
        
        # Verify budget exceeded flag is set
        assert response.budget_exceeded
        assert "budget_exceeded" in [flag.value for flag in response.policy_flags]
        
        # Verify warnings about budget
        assert len(response.warnings) > 0
        assert any("budget" in warning.lower() for warning in response.warnings)
    
    @pytest.mark.asyncio
    async def test_time_limit_enforcement(self, decision_engine, mock_components):
        """Test that time limits are properly enforced."""
        _, _, _, _ = mock_components
        
        # Test with very short time limit
        response = await decision_engine.decide(
            goal="Perform comprehensive analysis",
            urgency=0.6,
            complexity=0.7,
            time_limit=10  # Very short time limit
        )
        
        # Verify time limit warnings
        assert len(response.warnings) > 0
        assert any("time limit" in warning.lower() for warning in response.warnings)
    
    @pytest.mark.asyncio
    async def test_fallback_plan_generation(self, decision_engine, mock_components):
        """Test that fallback plans are generated when needed."""
        _, _, _, _ = mock_components
        
        # Test with constraints that would require fallback
        response = await decision_engine.decide(
            goal="Complex task requiring many resources",
            urgency=0.8,
            complexity=0.9,
            budget=1000,
            time_limit=30
        )
        
        # Verify fallback was used
        assert response.fallback_used
        assert "fallback_used" in [flag.value for flag in response.policy_flags]
        
        # Verify fallback warning
        assert len(response.warnings) > 0
        assert any("fallback" in warning.lower() for warning in response.warnings)
    
    @pytest.mark.asyncio
    async def test_budget_and_time_combined_constraints(self, decision_engine, mock_components):
        """Test combined budget and time constraints."""
        _, _, _, _ = mock_components
        
        response = await decision_engine.decide(
            goal="Resource-intensive analysis",
            urgency=0.7,
            complexity=0.8,
            budget=2000,
            time_limit=60
        )
        
        # Verify both constraints are checked
        budget_warnings = [w for w in response.warnings if "budget" in w.lower()]
        time_warnings = [w for w in response.warnings if "time" in w.lower()]
        
        # At least one type of constraint should be enforced
        assert len(budget_warnings) > 0 or len(time_warnings) > 0
    
    @pytest.mark.asyncio
    async def test_fallback_plan_characteristics(self, decision_engine, mock_components):
        """Test that fallback plans have appropriate characteristics."""
        _, _, _, _ = mock_components
        
        # Force fallback by setting very restrictive constraints
        response = await decision_engine.decide(
            goal="Complex analysis task",
            urgency=0.9,
            complexity=0.9,
            budget=100,
            time_limit=5
        )
        
        # Verify fallback was used
        assert response.fallback_used
        
        # Fallback plans should have lower complexity and resource requirements
        # This is tested through the plan generation logic
        assert response.confidence > 0  # Should still have some confidence
    
    @pytest.mark.asyncio
    async def test_budget_trace_information(self, decision_engine, mock_components):
        """Test that budget information is included in decision traces."""
        trace_logger, _, _, _ = mock_components
        
        await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=5000,
            time_limit=300
        )
        
        # Verify budget information in trace
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        assert call_args.budgets is not None
        assert "tokens" in call_args.budgets
        assert "time_seconds" in call_args.budgets
        assert "estimated_tokens" in call_args.budgets
        
        # Verify budget values
        assert call_args.budgets["tokens"] == 5000
        assert call_args.budgets["time_seconds"] == 300
        assert call_args.budgets["estimated_tokens"] > 0
    
    @pytest.mark.asyncio
    async def test_budget_exceeded_trace_flag(self, decision_engine, mock_components):
        """Test that budget exceeded flag is set in trace."""
        trace_logger, _, _, _ = mock_components
        
        await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=100  # Very low budget
        )
        
        # Verify budget exceeded flag in trace
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        assert call_args.budget_exceeded
        assert "budget_exceeded" in [flag.value for flag in call_args.policy_flags]
    
    @pytest.mark.asyncio
    async def test_fallback_used_trace_flag(self, decision_engine, mock_components):
        """Test that fallback used flag is set in trace."""
        trace_logger, _, _, _ = mock_components
        
        await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=100,
            time_limit=5
        )
        
        # Verify fallback used flag in trace
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        assert call_args.fallback_used
        assert "fallback_used" in [flag.value for flag in call_args.policy_flags]
    
    @pytest.mark.asyncio
    async def test_budget_constraint_with_policy_rejection(self, decision_engine, mock_components):
        """Test budget constraints combined with policy rejections."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to reject some plans
        def mock_policy_check(plan_dict):
            # Reject plans with high estimated tokens
            estimated_tokens = sum(step.get("budget", {}).get("tok", 1000) for step in plan_dict["steps"])
            if estimated_tokens > 2000:
                return {"approved": False, "reason": "Too resource intensive"}
            return {"approved": True}
        
        policy_hook.check_plan.side_effect = mock_policy_check
        
        response = await decision_engine.decide(
            goal="Complex analysis",
            urgency=0.7,
            complexity=0.8,
            budget=3000
        )
        
        # Verify both budget and policy constraints were applied
        assert len(response.warnings) > 0
        assert response.fallback_used
    
    @pytest.mark.asyncio
    async def test_maturity_level_budget_influence(self, decision_engine, mock_components):
        """Test that maturity level influences budget handling."""
        _, _, _, _ = mock_components
        
        # Test with infant maturity (more conservative)
        infant_response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=1000
        )
        
        # Test with adult maturity (more flexible)
        # Change maturity level
        decision_engine._set_maturity_level("adult")
        
        adult_response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=1000
        )
        
        # Results should be different due to maturity level
        assert infant_response.confidence != adult_response.confidence
    
    @pytest.mark.asyncio
    async def test_budget_graceful_degradation(self, decision_engine, mock_components):
        """Test graceful degradation when budget constraints are exceeded."""
        _, _, _, _ = mock_components
        
        # Test with extremely restrictive constraints
        response = await decision_engine.decide(
            goal="Complex analysis task",
            urgency=0.8,
            complexity=0.9,
            budget=50,   # Extremely low
            time_limit=1  # Extremely short
        )
        
        # Should still return a response (graceful degradation)
        assert response is not None
        assert response.confidence >= 0  # Should have some confidence
        
        # Should indicate constraints were exceeded
        assert response.budget_exceeded or response.fallback_used
    
    @pytest.mark.asyncio
    async def test_budget_estimation_accuracy(self, decision_engine, mock_components):
        """Test that budget estimations are reasonable."""
        trace_logger, _, _, _ = mock_components
        
        await decision_engine.decide(
            goal="Simple question",
            urgency=0.3,
            complexity=0.2,
            budget=5000
        )
        
        # Get trace to check budget estimation
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        estimated_tokens = call_args.budgets["estimated_tokens"]
        
        # Estimated tokens should be reasonable
        assert estimated_tokens > 0
        assert estimated_tokens <= 5000  # Should not exceed budget
    
    @pytest.mark.asyncio
    async def test_time_estimation_accuracy(self, decision_engine, mock_components):
        """Test that time estimations are reasonable."""
        trace_logger, _, _, _ = mock_components
        
        await decision_engine.decide(
            goal="Simple question",
            urgency=0.3,
            complexity=0.2,
            time_limit=300
        )
        
        # Get trace to check time estimation
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        estimated_time = call_args.budgets.get("estimated_time", 0)
        
        # Estimated time should be reasonable
        assert estimated_time >= 0
        if estimated_time > 0:
            assert estimated_time <= 300  # Should not exceed time limit