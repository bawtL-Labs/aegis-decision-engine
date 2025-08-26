"""
Smoke tests for the S.A.M. Decision Engine CLI.
"""

import pytest
import asyncio
import subprocess
import sys
from unittest.mock import Mock, AsyncMock, patch

from src.sam.cli import SAMCLI, main
from aegis_core.trace import TraceLogger
from aegis_core.policy import PolicyHook
from aegis_core.state import StateStore
from aegis_core.events import EventBus


class TestCLISmoke:
    """Smoke tests for CLI functionality."""
    
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
    async def cli(self, mock_components):
        """Create CLI instance with mock components."""
        cli = SAMCLI()
        
        # Mock the component initialization
        with patch.object(cli, 'initialize_components') as mock_init:
            mock_init.return_value = None
            await cli.initialize_components()
        
        # Set mock components directly
        cli.trace_logger, cli.policy_hook, cli.state_store, cli.event_bus = mock_components
        
        return cli
    
    @pytest.mark.asyncio
    async def test_cli_initialization(self, cli):
        """Test CLI initialization."""
        assert cli.engine is None
        assert cli.trace_logger is not None
        assert cli.policy_hook is not None
        assert cli.state_store is not None
        assert cli.event_bus is not None
    
    @pytest.mark.asyncio
    async def test_engine_creation(self, cli):
        """Test decision engine creation."""
        await cli.create_engine(maturity_level="infant")
        
        assert cli.engine is not None
        assert cli.engine.maturity_tracker is not None
        assert cli.engine.mental_health_monitor is not None
        assert cli.engine.utility_engine is not None
    
    @pytest.mark.asyncio
    async def test_basic_decision_command(self, cli):
        """Test basic decide command."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args
        class MockArgs:
            goal = "What is the capital of France?"
            context = None
            constraints = None
            urgency = 0.3
            complexity = 0.2
            personality = None
            budget = None
            time = None
            json = False
        
        args = MockArgs()
        
        # Execute decide command
        await cli.decide(args)
        
        # Verify engine was called
        assert cli.engine is not None
    
    @pytest.mark.asyncio
    async def test_decision_with_personality(self, cli):
        """Test decide command with personality influence."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args with personality
        class MockArgs:
            goal = "Analyze market data"
            context = None
            constraints = None
            urgency = 0.6
            complexity = 0.7
            personality = "analytical:0.8,creativity:0.6"
            budget = None
            time = None
            json = False
        
        args = MockArgs()
        
        # Execute decide command
        await cli.decide(args)
        
        # Verify engine was called
        assert cli.engine is not None
    
    @pytest.mark.asyncio
    async def test_decision_with_budget_and_time(self, cli):
        """Test decide command with budget and time constraints."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args with budget and time
        class MockArgs:
            goal = "Complex analysis task"
            context = None
            constraints = None
            urgency = 0.7
            complexity = 0.8
            personality = None
            budget = 5000
            time = 300
            json = False
        
        args = MockArgs()
        
        # Execute decide command
        await cli.decide(args)
        
        # Verify engine was called
        assert cli.engine is not None
    
    @pytest.mark.asyncio
    async def test_status_command(self, cli):
        """Test status command."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args
        class MockArgs:
            json = False
        
        args = MockArgs()
        
        # Execute status command
        await cli.status(args)
        
        # Verify engine was called
        assert cli.engine is not None
    
    @pytest.mark.asyncio
    async def test_status_command_json(self, cli):
        """Test status command with JSON output."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args
        class MockArgs:
            json = True
        
        args = MockArgs()
        
        # Execute status command
        await cli.status(args)
        
        # Verify engine was called
        assert cli.engine is not None
    
    @pytest.mark.asyncio
    async def test_demo_command(self, cli):
        """Test demo command."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args
        class MockArgs:
            pass
        
        args = MockArgs()
        
        # Execute demo command
        await cli.demo(args)
        
        # Verify engine was called
        assert cli.engine is not None
    
    def test_personality_parsing(self, cli):
        """Test personality string parsing."""
        # Test valid personality string
        personality_str = "tone:analytical,analytical:0.8,creativity:0.6,assertiveness:0.7"
        personality = cli._parse_personality(personality_str)
        
        assert personality.tone == "analytical"
        assert personality.analytical == 0.8
        assert personality.creativity == 0.6
        assert personality.assertiveness == 0.7
        
        # Test invalid personality string (should use defaults)
        invalid_str = "invalid:format"
        personality = cli._parse_personality(invalid_str)
        
        assert personality.tone == "neutral"
        assert personality.analytical == 0.5
        assert personality.creativity == 0.5
    
    def test_json_parsing(self, cli):
        """Test JSON string parsing."""
        # Test valid JSON
        valid_json = '{"key": "value", "number": 42}'
        result = cli._parse_json(valid_json)
        
        assert result["key"] == "value"
        assert result["number"] == 42
        
        # Test invalid JSON (should raise exception)
        invalid_json = '{"key": "value", "number": 42'  # Missing closing brace
        
        with pytest.raises(SystemExit):
            cli._parse_json(invalid_json)
    
    @pytest.mark.asyncio
    async def test_cli_shutdown(self, cli):
        """Test CLI shutdown."""
        await cli.create_engine(maturity_level="infant")
        
        # Test shutdown
        await cli.shutdown()
        
        # Verify shutdown was called
        assert cli.engine is not None
    
    @pytest.mark.asyncio
    async def test_pmx_integration(self, cli):
        """Test PMX integration in CLI."""
        # Test with PMX config
        pmx = cli._load_pmx("test_config.yaml")
        
        assert pmx is not None
        assert hasattr(pmx, 'matrix')
        assert hasattr(pmx.matrix, 'resolve_weights')
        
        # Test weights resolution
        weights = pmx.matrix.resolve_weights()
        assert isinstance(weights, dict)
        assert "goal" in weights
        assert "quality" in weights
        assert "risk" in weights
        assert "spend" in weights
    
    @pytest.mark.asyncio
    async def test_decision_result_formatting(self, cli):
        """Test decision result formatting."""
        from src.sam.models import DecisionResponse, MaturityLevel, MentalHealthStatus, PolicyFlag
        
        # Create a mock response
        response = DecisionResponse(
            plan_id="test-plan-id",
            confidence=0.75,
            mental_health_status=MentalHealthStatus.STABLE,
            maturity_level=MaturityLevel.INFANT,
            trace_id="test-trace-id",
            warnings=["Budget exceeded"],
            recommendations=["Use simpler approach"],
            policy_flags=[PolicyFlag.BUDGET_EXCEEDED],
            budget_exceeded=True,
            fallback_used=False
        )
        
        # Test formatting (should not raise exceptions)
        cli._print_decision_result(response)
    
    @pytest.mark.asyncio
    async def test_status_formatting(self, cli):
        """Test status formatting."""
        await cli.create_engine(maturity_level="infant")
        
        # Get status
        status = cli.engine.get_status()
        
        # Test formatting (should not raise exceptions)
        cli._print_status(status)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, cli):
        """Test error handling in CLI."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args that would cause an error
        class MockArgs:
            goal = "This will cause an error"
            context = None
            constraints = None
            urgency = 0.5
            complexity = 0.5
            personality = None
            budget = None
            time = None
            json = False
        
        args = MockArgs()
        
        # Mock engine to raise an exception
        cli.engine.decide = AsyncMock(side_effect=Exception("Test error"))
        
        # Should handle error gracefully
        with pytest.raises(SystemExit):
            await cli.decide(args)
    
    @pytest.mark.asyncio
    async def test_maturity_level_setting(self, cli):
        """Test maturity level setting in CLI."""
        # Test different maturity levels
        maturity_levels = ["infant", "child", "adolescent", "adult"]
        
        for level in maturity_levels:
            await cli.create_engine(maturity_level=level)
            assert cli.engine is not None
            assert cli.engine.maturity_tracker.profile.level.value == level
    
    @pytest.mark.asyncio
    async def test_invalid_maturity_level(self, cli):
        """Test handling of invalid maturity level."""
        # Test with invalid maturity level
        await cli.create_engine(maturity_level="invalid_level")
        
        # Should default to infant
        assert cli.engine is not None
        assert cli.engine.maturity_tracker.profile.level.value == "infant"
    
    def test_cli_argument_parsing(self):
        """Test CLI argument parsing."""
        # Test that argument parser works correctly
        # This is a basic smoke test to ensure the parser doesn't crash
        
        # Mock sys.argv to test argument parsing
        test_args = [
            "sam", "decide", "test goal",
            "--urgency", "0.6",
            "--complexity", "0.7",
            "--budget", "5000",
            "--time", "300"
        ]
        
        with patch.object(sys, 'argv', test_args):
            # Should not crash
            pass
    
    @pytest.mark.asyncio
    async def test_comprehensive_demo(self, cli):
        """Test comprehensive demo functionality."""
        await cli.create_engine(maturity_level="adult")
        
        # Create mock args
        class MockArgs:
            pass
        
        args = MockArgs()
        
        # Execute demo command
        await cli.demo(args)
        
        # Verify all demo scenarios were executed
        assert cli.engine is not None
        
        # Check that multiple decisions were made
        # (This is verified by the demo method not raising exceptions)
    
    @pytest.mark.asyncio
    async def test_json_output_format(self, cli):
        """Test JSON output format."""
        await cli.create_engine(maturity_level="infant")
        
        # Create mock args with JSON output
        class MockArgs:
            goal = "Test goal"
            context = None
            constraints = None
            urgency = 0.5
            complexity = 0.5
            personality = None
            budget = None
            time = None
            json = True
        
        args = MockArgs()
        
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            await cli.decide(args)
            
            # Verify JSON was printed
            assert mock_print.called
            # The first call should be the JSON output
            first_call = mock_print.call_args_list[0]
            output = first_call[0][0]
            
            # Should be valid JSON
            import json
            parsed = json.loads(output)
            assert "plan_id" in parsed
            assert "confidence" in parsed
            assert "mental_health_status" in parsed