"""
Tests for policy gate functionality in the S.A.M. Decision Engine.
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


class TestPolicyGate:
    """Test policy gate functionality."""
    
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
    async def test_policy_approval(self, decision_engine, mock_components):
        """Test that plans are approved when policy allows."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to approve plans
        policy_hook.check_plan.return_value = {"approved": True}
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify plan was approved
        assert response.confidence > 0
        assert "denied" not in [flag.value for flag in response.policy_flags]
    
    @pytest.mark.asyncio
    async def test_policy_rejection(self, decision_engine, mock_components):
        """Test that plans are rejected when policy denies."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to reject plans
        policy_hook.check_plan.return_value = {
            "approved": False,
            "reason": "Policy violation: external API access not allowed"
        }
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify plan was rejected and fallback used
        assert response.fallback_used
        assert "denied" in [flag.value for flag in response.policy_flags]
        assert len(response.warnings) > 0
    
    @pytest.mark.asyncio
    async def test_budget_constraint_enforcement(self, decision_engine, mock_components):
        """Test that budget constraints are enforced."""
        _, _, _, _ = mock_components
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=100  # Very low budget
        )
        
        # Verify budget constraint was applied
        assert response.budget_exceeded
        assert "budget_exceeded" in [flag.value for flag in response.policy_flags]
    
    @pytest.mark.asyncio
    async def test_time_constraint_enforcement(self, decision_engine, mock_components):
        """Test that time constraints are enforced."""
        _, _, _, _ = mock_components
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            time_limit=1  # Very short time limit
        )
        
        # Verify time constraint was applied
        assert len(response.warnings) > 0
        assert any("time limit" in warning.lower() for warning in response.warnings)
    
    @pytest.mark.asyncio
    async def test_policy_flags_in_trace(self, decision_engine, mock_components):
        """Test that policy flags are included in decision trace."""
        trace_logger, policy_hook, _, _ = mock_components
        
        # Mock policy hook to return flags
        policy_hook.check_plan.return_value = {
            "approved": True,
            "flags": ["safety_check_passed", "budget_approved", "external_access_denied"]
        }
        
        await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify flags are in trace
        call_args = trace_logger.log_decision_trace.call_args[0][0]
        assert len(call_args.policy_flags) > 0
    
    @pytest.mark.asyncio
    async def test_fallback_plan_selection(self, decision_engine, mock_components):
        """Test that fallback plans are selected when all plans are rejected."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to reject all plans
        policy_hook.check_plan.return_value = {
            "approved": False,
            "reason": "All plans violate policy"
        }
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify fallback was used
        assert response.fallback_used
        assert "fallback_used" in [flag.value for flag in response.policy_flags]
        assert len(response.warnings) > 0
        assert "fallback plan" in response.warnings[0].lower()
    
    @pytest.mark.asyncio
    async def test_policy_hook_failure_handling(self, decision_engine, mock_components):
        """Test handling of policy hook failures."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to raise exception
        policy_hook.check_plan.side_effect = Exception("Policy hook failed")
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify decision still succeeds (graceful degradation)
        assert response.confidence > 0
        assert not response.fallback_used
    
    @pytest.mark.asyncio
    async def test_multiple_policy_violations(self, decision_engine, mock_components):
        """Test handling of multiple policy violations."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to reject with multiple reasons
        policy_hook.check_plan.return_value = {
            "approved": False,
            "reason": "Multiple violations: external API, high risk, budget exceeded"
        }
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5,
            budget=100
        )
        
        # Verify multiple warnings
        assert len(response.warnings) > 1
        assert response.fallback_used
    
    @pytest.mark.asyncio
    async def test_policy_conditional_approval(self, decision_engine, mock_components):
        """Test conditional policy approval."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to conditionally approve
        policy_hook.check_plan.return_value = {
            "approved": True,
            "flags": ["conditional_approval"],
            "conditions": ["require_supervision", "log_all_actions"]
        }
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify conditional approval
        assert response.confidence > 0
        assert "conditional" in [flag.value for flag in response.policy_flags]
    
    @pytest.mark.asyncio
    async def test_policy_with_recommendations(self, decision_engine, mock_components):
        """Test that policy recommendations are included in response."""
        _, policy_hook, _, _ = mock_components
        
        # Mock policy hook to return recommendations
        policy_hook.check_plan.return_value = {
            "approved": True,
            "recommendations": [
                "Use local processing instead of external APIs",
                "Implement additional validation steps",
                "Consider reducing complexity"
            ]
        }
        
        response = await decision_engine.decide(
            goal="Test decision",
            urgency=0.5,
            complexity=0.5
        )
        
        # Verify recommendations are included
        assert len(response.recommendations) > 0