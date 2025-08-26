#!/usr/bin/env python3
"""
Command-line interface for the S.A.M. Decision Engine.
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any

from .decision import DecisionEngine
from .models import PersonalityInfluence


def create_personality_from_args(args) -> PersonalityInfluence:
    """Create personality influence from command line arguments."""
    return PersonalityInfluence(
        tone=args.tone or "neutral",
        assertiveness=args.assertiveness or 0.5,
        patience=args.patience or 0.5,
        humor=args.humor or 0.5,
        creativity=args.creativity or 0.5,
        analytical=args.analytical or 0.5,
        social=args.social or 0.5
    )


async def make_decision(args):
    """Make a decision using the decision engine."""
    # Create personality influence if specified
    personality = None
    if any([args.tone, args.assertiveness, args.patience, args.humor, 
            args.creativity, args.analytical, args.social]):
        personality = create_personality_from_args(args)
    
    # Create decision engine
    engine = DecisionEngine(
        maturity_level=args.maturity_level,
        personality_influence=personality
    )
    
    try:
        # Parse context if provided
        context = {}
        if args.context:
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in context argument", file=sys.stderr)
                return 1
        
        # Parse constraints if provided
        constraints = {}
        if args.constraints:
            try:
                constraints = json.loads(args.constraints)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in constraints argument", file=sys.stderr)
                return 1
        
        # Make decision
        response = await engine.decide(
            goal=args.goal,
            context=context,
            constraints=constraints,
            urgency=args.urgency,
            complexity=args.complexity,
            personality_influence=personality
        )
        
        # Output result
        if args.json:
            result = {
                "plan_id": str(response.plan_id),
                "confidence": response.confidence,
                "mental_health_status": response.mental_health_status.value,
                "maturity_level": response.maturity_level.value,
                "trace_id": str(response.trace_id),
                "warnings": response.warnings,
                "recommendations": response.recommendations,
                "created_at": response.created_at.isoformat()
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Decision Result:")
            print(f"  Plan ID: {response.plan_id}")
            print(f"  Confidence: {response.confidence:.3f}")
            print(f"  Mental Health: {response.mental_health_status.value}")
            print(f"  Maturity Level: {response.maturity_level.value}")
            print(f"  Trace ID: {response.trace_id}")
            
            if response.warnings:
                print(f"  Warnings: {', '.join(response.warnings)}")
            
            if response.recommendations:
                print(f"  Recommendations: {', '.join(response.recommendations)}")
        
        return 0
        
    finally:
        await engine.shutdown()


async def show_status(args):
    """Show system status."""
    engine = DecisionEngine(maturity_level=args.maturity_level)
    
    try:
        status = engine.get_status()
        
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print("System Status:")
            print(f"  Engine: {'Initialized' if status['engine_status']['initialized'] else 'Not initialized'}")
            print(f"  Total Decisions: {status['engine_status']['total_decisions']}")
            print(f"  Uptime: {status['engine_status']['uptime_seconds']:.1f} seconds")
            print(f"  Maturity Level: {status['maturity']['level']}")
            print(f"  Experience Points: {status['maturity']['experience_points']}")
            print(f"  Mental Health: {status['mental_health']['status']}")
            print(f"  Stress Level: {status['mental_health']['stress_level']:.3f}")
            print(f"  Average Confidence: {status['performance']['average_confidence']:.3f}")
        
        return 0
        
    finally:
        await engine.shutdown()


async def run_demo(args):
    """Run demonstration scenarios."""
    print("S.A.M. Decision Engine - CLI Demonstration")
    print("=" * 50)
    
    # Create engine
    engine = DecisionEngine(maturity_level=args.maturity_level)
    
    try:
        # Demo 1: Simple decision
        print("\n1. Simple Decision:")
        response = await engine.decide(
            goal="answer a basic question",
            context={"question": "What is 2+2?"},
            urgency=0.2,
            complexity=0.1
        )
        print(f"   Confidence: {response.confidence:.3f}")
        
        # Demo 2: Complex decision
        print("\n2. Complex Decision:")
        response = await engine.decide(
            goal="analyze data and create report",
            context={"data_type": "numerical", "requires_analysis": True},
            urgency=0.6,
            complexity=0.7
        )
        print(f"   Confidence: {response.confidence:.3f}")
        
        # Demo 3: Show status
        print("\n3. System Status:")
        status = engine.get_status()
        print(f"   Total decisions: {status['engine_status']['total_decisions']}")
        print(f"   Mental health: {status['mental_health']['status']}")
        print(f"   Average confidence: {status['performance']['average_confidence']:.3f}")
        
        print("\nDemonstration completed!")
        return 0
        
    finally:
        await engine.shutdown()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="S.A.M. Decision Engine - Maturity-based decision making for autonomous AI systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Make a simple decision
  sam-decision decide "answer a question" --urgency 0.3 --complexity 0.2

  # Make a complex decision with context
  sam-decision decide "analyze market data" --urgency 0.7 --complexity 0.8 --context '{"data_type": "financial"}'

  # Show system status
  sam-decision status

  # Run demonstration
  sam-decision demo

  # Use with personality influence
  sam-decision decide "create solution" --analytical 0.9 --creativity 0.7
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Decide command
    decide_parser = subparsers.add_parser('decide', help='Make a decision')
    decide_parser.add_argument('goal', help='The goal to achieve')
    decide_parser.add_argument('--context', help='JSON context information')
    decide_parser.add_argument('--constraints', help='JSON constraints')
    decide_parser.add_argument('--urgency', type=float, default=0.5, help='Urgency level (0-1)')
    decide_parser.add_argument('--complexity', type=float, default=0.5, help='Complexity level (0-1)')
    decide_parser.add_argument('--maturity-level', default='infant', 
                              choices=['infant', 'child', 'adolescent', 'adult'],
                              help='Maturity level')
    decide_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Personality arguments
    decide_parser.add_argument('--tone', help='Communication tone')
    decide_parser.add_argument('--assertiveness', type=float, help='Assertiveness level (0-1)')
    decide_parser.add_argument('--patience', type=float, help='Patience level (0-1)')
    decide_parser.add_argument('--humor', type=float, help='Humor preference (0-1)')
    decide_parser.add_argument('--creativity', type=float, help='Creativity preference (0-1)')
    decide_parser.add_argument('--analytical', type=float, help='Analytical thinking preference (0-1)')
    decide_parser.add_argument('--social', type=float, help='Social interaction preference (0-1)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.add_argument('--maturity-level', default='infant',
                              choices=['infant', 'child', 'adolescent', 'adult'],
                              help='Maturity level')
    status_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstration scenarios')
    demo_parser.add_argument('--maturity-level', default='infant',
                            choices=['infant', 'child', 'adolescent', 'adult'],
                            help='Maturity level')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run appropriate command
    try:
        if args.command == 'decide':
            return asyncio.run(make_decision(args))
        elif args.command == 'status':
            return asyncio.run(show_status(args))
        elif args.command == 'demo':
            return asyncio.run(run_demo(args))
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())