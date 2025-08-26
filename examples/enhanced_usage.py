#!/usr/bin/env python3
"""
Enhanced Usage Example for S.A.M. Decision Engine v2.0

Demonstrates the new aegis-core integration features including:
- Personality-aware decision making
- Policy enforcement
- Trace emission
- Budget management
- Mental health monitoring
"""

import asyncio
import json
from datetime import datetime

# Mock aegis-core components for demonstration
class MockTraceLogger:
    async def log_decision_trace(self, trace):
        print(f"📊 Trace logged: {trace.id}")
        print(f"   Mode: {trace.mode}")
        print(f"   Candidates: {len(trace.candidates)}")
        print(f"   Policy flags: {[f.value for f in trace.policy_flags]}")

class MockPolicyHook:
    async def check_plan(self, plan_dict):
        # Simple policy: reject plans with external tools
        if any(step.get("type") == "tool" for step in plan_dict["steps"]):
            return {
                "approved": False,
                "reason": "External tool usage not allowed in demo mode"
            }
        return {"approved": True}

class MockStateStore:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    async def set(self, key, value):
        self.data[key] = value
        print(f"💾 State saved: {key}")

class MockEventBus:
    def __init__(self):
        self.events = []
    
    def emit(self, event_type, data):
        self.events.append({"type": event_type, "data": data, "timestamp": datetime.utcnow()})
        print(f"📡 Event emitted: {event_type}")
    
    def subscribe(self, event_type, handler):
        print(f"📡 Subscribed to: {event_type}")

# Mock PMX for personality integration
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

async def demonstrate_basic_decision():
    """Demonstrate basic decision making."""
    print("\n🎯 Basic Decision Making")
    print("=" * 50)
    
    from src.sam.decision import DecisionEngine
    
    # Initialize mock components
    trace_logger = MockTraceLogger()
    policy_hook = MockPolicyHook()
    state_store = MockStateStore()
    event_bus = MockEventBus()
    
    # Create decision engine
    engine = DecisionEngine(
        trace_logger=trace_logger,
        policy_hook=policy_hook,
        state_store=state_store,
        event_bus=event_bus,
        maturity_level="infant"
    )
    
    # Make a simple decision
    response = await engine.decide(
        goal="What is the capital of France?",
        urgency=0.3,
        complexity=0.2
    )
    
    print(f"✅ Decision made!")
    print(f"   Plan ID: {response.plan_id}")
    print(f"   Confidence: {response.confidence:.3f}")
    print(f"   Mental Health: {response.mental_health_status.value}")
    print(f"   Maturity Level: {response.maturity_level.value}")
    print(f"   Trace ID: {response.trace_id}")
    
    if response.warnings:
        print(f"   ⚠️  Warnings: {response.warnings}")
    
    return engine

async def demonstrate_personality_influence(engine):
    """Demonstrate personality influence on decisions."""
    print("\n🧠 Personality-Aware Decision Making")
    print("=" * 50)
    
    from src.sam.models import PersonalityInfluence
    
    # Define different personalities
    analytical_personality = PersonalityInfluence(
        tone="analytical",
        assertiveness=0.8,
        patience=0.9,
        humor=0.2,
        creativity=0.3,
        analytical=0.9,
        social=0.4
    )
    
    creative_personality = PersonalityInfluence(
        tone="creative",
        assertiveness=0.6,
        patience=0.5,
        humor=0.8,
        creativity=0.9,
        analytical=0.3,
        social=0.7
    )
    
    # Make decisions with different personalities
    print("🤖 Analytical Personality Decision:")
    analytical_response = await engine.decide(
        goal="Analyze market trends and provide detailed report",
        urgency=0.6,
        complexity=0.7,
        personality_influence=analytical_personality
    )
    print(f"   Confidence: {analytical_response.confidence:.3f}")
    print(f"   Plan ID: {analytical_response.plan_id}")
    
    print("\n🎨 Creative Personality Decision:")
    creative_response = await engine.decide(
        goal="Create an innovative marketing campaign",
        urgency=0.5,
        complexity=0.6,
        personality_influence=creative_personality
    )
    print(f"   Confidence: {creative_response.confidence:.3f}")
    print(f"   Plan ID: {creative_response.plan_id}")
    
    # Compare results
    print(f"\n📊 Comparison:")
    print(f"   Analytical confidence: {analytical_response.confidence:.3f}")
    print(f"   Creative confidence: {creative_response.confidence:.3f}")

async def demonstrate_budget_constraints(engine):
    """Demonstrate budget and time constraint enforcement."""
    print("\n💰 Budget and Time Constraint Management")
    print("=" * 50)
    
    # Test with generous budget
    print("💳 Generous Budget Decision:")
    generous_response = await engine.decide(
        goal="Perform comprehensive data analysis",
        urgency=0.7,
        complexity=0.8,
        budget=10000,
        time_limit=600
    )
    print(f"   Budget exceeded: {generous_response.budget_exceeded}")
    print(f"   Fallback used: {generous_response.fallback_used}")
    print(f"   Confidence: {generous_response.confidence:.3f}")
    
    # Test with restrictive budget
    print("\n🔒 Restrictive Budget Decision:")
    restrictive_response = await engine.decide(
        goal="Perform comprehensive data analysis",
        urgency=0.7,
        complexity=0.8,
        budget=500,
        time_limit=30
    )
    print(f"   Budget exceeded: {restrictive_response.budget_exceeded}")
    print(f"   Fallback used: {restrictive_response.fallback_used}")
    print(f"   Confidence: {restrictive_response.confidence:.3f}")
    
    if restrictive_response.warnings:
        print(f"   ⚠️  Warnings: {restrictive_response.warnings}")

async def demonstrate_policy_enforcement(engine):
    """Demonstrate policy enforcement."""
    print("\n🛡️ Policy Enforcement")
    print("=" * 50)
    
    # Test policy that allows external tools
    print("✅ Policy-Compliant Decision:")
    compliant_response = await engine.decide(
        goal="Answer a simple question",
        urgency=0.4,
        complexity=0.3
    )
    print(f"   Policy flags: {[f.value for f in compliant_response.policy_flags]}")
    print(f"   Confidence: {compliant_response.confidence:.3f}")
    
    # Test policy that might reject external tools
    print("\n❌ Policy-Violating Decision (simulated):")
    # Note: In real usage, this would be rejected by the policy hook
    # For demo purposes, we'll just show the structure
    print("   Would be rejected if external tools were used")
    print("   Fallback plan would be selected")

async def demonstrate_maturity_progression(engine):
    """Demonstrate maturity level progression."""
    print("\n👶 Maturity Level Progression")
    print("=" * 50)
    
    maturity_levels = ["infant", "child", "adolescent", "adult"]
    
    for level in maturity_levels:
        print(f"\n{level.upper()} Level Decision:")
        
        # Set maturity level
        engine._set_maturity_level(level)
        
        # Make decision
        response = await engine.decide(
            goal="Analyze complex problem",
            urgency=0.6,
            complexity=0.7
        )
        
        print(f"   Maturity Level: {response.maturity_level.value}")
        print(f"   Confidence: {response.confidence:.3f}")
        print(f"   Plan ID: {response.plan_id}")

async def demonstrate_mental_health_monitoring(engine):
    """Demonstrate mental health monitoring."""
    print("\n💚 Mental Health Monitoring")
    print("=" * 50)
    
    # Get current mental health status
    status = engine.get_status()
    mental_health = status["mental_health"]
    
    print(f"Current Mental Health Status:")
    print(f"   Status: {mental_health['status']}")
    print(f"   Stress Level: {mental_health['stress_level']:.3f}")
    print(f"   Excitement Level: {mental_health['excitement_level']:.3f}")
    print(f"   Emotional Stability: {mental_health['emotional_stability']:.3f}")
    print(f"   Burnout Risk: {mental_health['burnout_risk']:.3f}")
    
    if mental_health['intervention_needed']:
        print(f"   ⚠️  Intervention needed!")
        print(f"   Recommendations: {mental_health['recommendations']}")

async def demonstrate_system_status(engine):
    """Demonstrate comprehensive system status."""
    print("\n📊 Comprehensive System Status")
    print("=" * 50)
    
    status = engine.get_status()
    
    print("Maturity Information:")
    maturity = status["maturity"]
    print(f"   Level: {maturity['level']}")
    print(f"   Age: {maturity['age_months']} months")
    print(f"   Experience Points: {maturity['experience_points']}")
    print(f"   Confidence Threshold: {maturity['confidence_threshold']:.3f}")
    print(f"   Risk Tolerance: {maturity['risk_tolerance']:.3f}")
    
    print("\nMental Health Information:")
    mental_health = status["mental_health"]
    print(f"   Status: {mental_health['status']}")
    print(f"   Stress Level: {mental_health['stress_level']:.3f}")
    print(f"   Burnout Risk: {mental_health['burnout_risk']:.3f}")
    
    print("\nPerformance Metrics:")
    performance = status["performance"]
    print(f"   Total Decisions: {performance['total_decisions']}")
    print(f"   Successful Decisions: {performance['successful_decisions']}")
    print(f"   Average Confidence: {performance['average_confidence']:.3f}")
    
    print("\nComponent Status:")
    components = status["components"]
    for component, available in components.items():
        status_icon = "✅" if available else "❌"
        print(f"   {status_icon} {component}")
    
    print(f"\n🤖 PMX Available: {'✅' if status['pmx_available'] else '❌'}")

async def demonstrate_pmx_integration(engine):
    """Demonstrate PMX integration."""
    print("\n🤖 PMX Integration")
    print("=" * 50)
    
    # Create engine with PMX
    from src.sam.decision import DecisionEngine
    
    pmx = MockPMX()
    
    pmx_engine = DecisionEngine(
        trace_logger=engine.trace_logger,
        policy_hook=engine.policy_hook,
        state_store=engine.state_store,
        event_bus=engine.event_bus,
        pmx=pmx,
        maturity_level="adult"
    )
    
    # Make decision with PMX influence
    response = await pmx_engine.decide(
        goal="Create detailed analysis with PMX influence",
        urgency=0.6,
        complexity=0.7
    )
    
    print(f"✅ PMX-influenced decision made!")
    print(f"   Plan ID: {response.plan_id}")
    print(f"   Confidence: {response.confidence:.3f}")
    print(f"   Trace ID: {response.trace_id}")

async def main():
    """Main demonstration function."""
    print("🚀 S.A.M. Decision Engine v2.0 - Enhanced Usage Demonstration")
    print("=" * 70)
    
    try:
        # Run all demonstrations
        engine = await demonstrate_basic_decision()
        await demonstrate_personality_influence(engine)
        await demonstrate_budget_constraints(engine)
        await demonstrate_policy_enforcement(engine)
        await demonstrate_maturity_progression(engine)
        await demonstrate_mental_health_monitoring(engine)
        await demonstrate_system_status(engine)
        await demonstrate_pmx_integration(engine)
        
        print("\n🎉 Demonstration completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Basic decision making with trace emission")
        print("✅ Personality-aware utility calculation")
        print("✅ Budget and time constraint enforcement")
        print("✅ Policy enforcement and safety gates")
        print("✅ Maturity-based development stages")
        print("✅ Mental health monitoring and intervention")
        print("✅ Comprehensive system status monitoring")
        print("✅ PMX integration for personality matrix")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())