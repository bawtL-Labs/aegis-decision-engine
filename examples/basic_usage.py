#!/usr/bin/env python3
"""
Basic usage example for the S.A.M. Decision Engine.

This example demonstrates how to use the decision engine with different
maturity levels and personality influences.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import sam
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sam.decision import DecisionEngine
from sam.models import PersonalityInfluence


async def demonstrate_infant_behavior():
    """Demonstrate infant-level decision making."""
    print("\n=== Infant Level Demonstration ===")
    
    engine = DecisionEngine(maturity_level="infant")
    
    try:
        # Simple task that infant can handle
        print("Making a simple decision...")
        response = await engine.decide(
            goal="answer a basic question",
            context={"question": "What is the capital of France?"},
            urgency=0.2,
            complexity=0.1
        )
        
        print(f"✅ Decision made with confidence: {response.confidence:.3f}")
        print(f"   Mental health: {response.mental_health_status.value}")
        print(f"   Warnings: {response.warnings}")
        
        # Complex task that infant cannot handle
        print("\nTrying a complex task...")
        response = await engine.decide(
            goal="analyze global economic trends and create investment portfolio",
            context={"complexity": "very_high"},
            urgency=0.9,
            complexity=0.9
        )
        
        print(f"❌ Decision blocked: {response.warnings[0]}")
        print(f"   Recommendations: {response.recommendations}")
        
    finally:
        await engine.shutdown()


async def demonstrate_adult_behavior():
    """Demonstrate adult-level decision making."""
    print("\n=== Adult Level Demonstration ===")
    
    engine = DecisionEngine(maturity_level="adult")
    
    try:
        # Complex task that adult can handle
        print("Making a complex decision...")
        response = await engine.decide(
            goal="analyze market data and create investment strategy",
            context={
                "market_data": "available",
                "time_horizon": "long_term",
                "risk_tolerance": "moderate"
            },
            urgency=0.7,
            complexity=0.8
        )
        
        print(f"✅ Decision made with confidence: {response.confidence:.3f}")
        print(f"   Mental health: {response.mental_health_status.value}")
        print(f"   Recommendations: {response.recommendations}")
        
    finally:
        await engine.shutdown()


async def demonstrate_personality_influence():
    """Demonstrate how personality influences decision making."""
    print("\n=== Personality Influence Demonstration ===")
    
    # Create analytical personality
    analytical_personality = PersonalityInfluence(
        tone="professional",
        assertiveness=0.6,
        patience=0.8,
        humor=0.3,
        creativity=0.4,
        analytical=0.9,
        social=0.3
    )
    
    # Create creative personality
    creative_personality = PersonalityInfluence(
        tone="enthusiastic",
        assertiveness=0.7,
        patience=0.5,
        humor=0.8,
        creativity=0.9,
        analytical=0.3,
        social=0.7
    )
    
    engine = DecisionEngine(maturity_level="adolescent")
    
    try:
        # Test with analytical personality
        print("Testing with analytical personality...")
        response = await engine.decide(
            goal="analyze data patterns and create report",
            context={"data_type": "numerical", "requires_analysis": True},
            personality_influence=analytical_personality
        )
        
        print(f"📊 Analytical decision confidence: {response.confidence:.3f}")
        
        # Test with creative personality
        print("\nTesting with creative personality...")
        response = await engine.decide(
            goal="create innovative solution for data visualization",
            context={"requires_creativity": True, "audience": "creative"},
            personality_influence=creative_personality
        )
        
        print(f"🎨 Creative decision confidence: {response.confidence:.3f}")
        
    finally:
        await engine.shutdown()


async def demonstrate_mental_health_monitoring():
    """Demonstrate mental health monitoring."""
    print("\n=== Mental Health Monitoring Demonstration ===")
    
    engine = DecisionEngine(maturity_level="child")
    
    try:
        # Show initial mental health
        initial_health = engine.get_mental_health_summary()
        print(f"Initial mental health: {initial_health['status']}")
        print(f"Stress level: {initial_health['stress_level']:.3f}")
        
        # Simulate stressful decisions
        print("\nMaking stressful decisions...")
        for i in range(3):
            response = await engine.decide(
                goal=f"handle urgent crisis {i+1}",
                urgency=0.9,
                complexity=0.7
            )
            print(f"   Decision {i+1}: Stress impact recorded")
        
        # Show updated mental health
        updated_health = engine.get_mental_health_summary()
        print(f"\nUpdated mental health: {updated_health['status']}")
        print(f"Stress level: {updated_health['stress_level']:.3f}")
        
        # Record some thought patterns
        print("\nRecording thought patterns...")
        engine.record_thought_pattern({
            "type": "recursive",
            "repetition_count": 3,
            "similarity_score": 0.8
        })
        
        # Check for interventions
        if engine.should_intervene():
            recommendations = engine.get_intervention_recommendations()
            print(f"⚠️  Intervention needed: {recommendations[0]}")
        
    finally:
        await engine.shutdown()


async def demonstrate_maturity_progression():
    """Demonstrate maturity progression over time."""
    print("\n=== Maturity Progression Demonstration ===")
    
    engine = DecisionEngine(maturity_level="infant")
    
    try:
        # Show initial maturity
        initial_maturity = engine.get_maturity_summary()
        print(f"Initial maturity level: {initial_maturity['level']}")
        print(f"Experience points: {initial_maturity['experience_points']}")
        
        # Simulate learning experiences
        print("\nSimulating learning experiences...")
        for i in range(10):
            response = await engine.decide(
                goal=f"learn new concept {i+1}",
                context={"learning_outcome": "successful"},
                urgency=0.3,
                complexity=0.3
            )
            print(f"   Learning experience {i+1}: +{response.confidence:.3f} confidence")
        
        # Show updated maturity
        updated_maturity = engine.get_maturity_summary()
        print(f"\nUpdated maturity level: {updated_maturity['level']}")
        print(f"Experience points: {updated_maturity['experience_points']}")
        print(f"Total decisions: {updated_maturity['total_decisions']}")
        
        # Force progression to see the effect
        print("\nForcing maturity progression...")
        engine.force_maturity_progression("child")
        
        final_maturity = engine.get_maturity_summary()
        print(f"New maturity level: {final_maturity['level']}")
        print(f"New confidence threshold: {final_maturity['confidence_threshold']:.3f}")
        print(f"New risk tolerance: {final_maturity['risk_tolerance']:.3f}")
        
    finally:
        await engine.shutdown()


async def demonstrate_system_status():
    """Demonstrate comprehensive system status."""
    print("\n=== System Status Demonstration ===")
    
    engine = DecisionEngine(maturity_level="adolescent")
    
    try:
        # Make some decisions
        for i in range(5):
            await engine.decide(
                goal=f"system test {i+1}",
                urgency=0.5,
                complexity=0.5
            )
        
        # Get comprehensive status
        status = engine.get_status()
        
        print("System Status:")
        print(f"  Engine initialized: {status['engine_status']['initialized']}")
        print(f"  Total decisions: {status['engine_status']['total_decisions']}")
        print(f"  Uptime: {status['engine_status']['uptime_seconds']:.1f} seconds")
        
        print(f"\nMaturity:")
        print(f"  Level: {status['maturity']['level']}")
        print(f"  Experience points: {status['maturity']['experience_points']}")
        print(f"  Confidence threshold: {status['maturity']['confidence_threshold']:.3f}")
        print(f"  Risk tolerance: {status['maturity']['risk_tolerance']:.3f}")
        
        print(f"\nMental Health:")
        print(f"  Status: {status['mental_health']['status']}")
        print(f"  Stress level: {status['mental_health']['stress_level']:.3f}")
        print(f"  Emotional stability: {status['mental_health']['emotional_stability']:.3f}")
        
        print(f"\nPerformance:")
        print(f"  Average confidence: {status['performance']['average_confidence']:.3f}")
        print(f"  Average response time: {status['performance']['average_response_time']:.3f} seconds")
        print(f"  Success rate: {status['performance']['successful_decisions']}/{status['performance']['total_requests']}")
        
        print(f"\nCurrent Constraints:")
        print(f"  Max complexity: {status['current_constraints']['max_complexity']:.3f}")
        print(f"  Max urgency: {status['current_constraints']['max_urgency']:.3f}")
        print(f"  Supervision level: {status['current_constraints']['supervision_level']:.3f}")
        
    finally:
        await engine.shutdown()


async def main():
    """Run all demonstrations."""
    print("S.A.M. Decision Engine - Basic Usage Examples")
    print("=" * 60)
    
    # Run all demonstrations
    await demonstrate_infant_behavior()
    await demonstrate_adult_behavior()
    await demonstrate_personality_influence()
    await demonstrate_mental_health_monitoring()
    await demonstrate_maturity_progression()
    await demonstrate_system_status()
    
    print("\n" + "=" * 60)
    print("All demonstrations completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Maturity-based decision making")
    print("✅ Personality influence on decisions")
    print("✅ Mental health monitoring and intervention")
    print("✅ Constraint validation and enforcement")
    print("✅ Experience accumulation and learning")
    print("✅ Comprehensive system status tracking")


if __name__ == "__main__":
    asyncio.run(main())