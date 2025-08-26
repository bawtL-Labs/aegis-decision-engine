# S.A.M. Decision Engine v2.0

**Enhanced S.A.M. Decision Engine with aegis-core integration for personality-aware, policy-enforced, and trace-emitted decisions.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-beta-green.svg)](https://github.com/bawtL-Labs/aegis-decision-engine)

## 🎯 Overview

The S.A.M. Decision Engine is a comprehensive decision-making system designed for autonomous AI systems. Version 2.0 integrates with **aegis-core** components to provide:

- **Personality-aware decision making** with PMX integration
- **Policy enforcement** with comprehensive safety gates
- **Trace emission** for auditable decision processes
- **Budget and time constraint management**
- **Mental health monitoring** and intervention
- **Maturity-based development** from infant to adult stages

## 🏗️ Architecture

### Core Components

- **DecisionEngine**: Main orchestrator with aegis-core integration
- **MaturityTracker**: Developmental management using StateStore
- **MentalHealthMonitor**: Well-being monitoring with EventBus
- **UtilityEngine**: Personality-aware utility calculation
- **PolicyHook**: Safety and policy enforcement
- **TraceLogger**: Comprehensive decision tracing

### Aegis-Core Integration

The engine integrates with all aegis-core components:

```python
from aegis_core.trace import TraceLogger
from aegis_core.policy import PolicyHook
from aegis_core.state import StateStore
from aegis_core.events import EventBus

# Initialize components
trace_logger = TraceLogger()
policy_hook = PolicyHook()
state_store = StateStore()
event_bus = EventBus()

# Create decision engine
engine = DecisionEngine(
    trace_logger=trace_logger,
    policy_hook=policy_hook,
    state_store=state_store,
    event_bus=event_bus,
    pmx=pmx_object,  # Optional PMX integration
    maturity_level="infant"
)
```

## 🚀 Quick Start

### Installation

```bash
# Install with aegis-core dependencies
pip install sam-decision-engine

# Or install from source
git clone https://github.com/bawtL-Labs/aegis-decision-engine.git
cd aegis-decision-engine
pip install -e .
```

### Basic Usage

```python
import asyncio
from src.sam.decision import DecisionEngine
from src.sam.models import PersonalityInfluence

async def main():
    # Initialize aegis-core components
    from aegis_core.trace import TraceLogger
    from aegis_core.policy import PolicyHook
    from aegis_core.state import StateStore
    from aegis_core.events import EventBus
    
    trace_logger = TraceLogger()
    policy_hook = PolicyHook()
    state_store = StateStore()
    event_bus = EventBus()
    
    # Create decision engine
    engine = DecisionEngine(
        trace_logger=trace_logger,
        policy_hook=policy_hook,
        state_store=state_store,
        event_bus=event_bus,
        maturity_level="infant"
    )
    
    # Make a decision
    response = await engine.decide(
        goal="What is the capital of France?",
        urgency=0.3,
        complexity=0.2
    )
    
    print(f"Decision made with confidence: {response.confidence}")
    print(f"Plan ID: {response.plan_id}")
    print(f"Trace ID: {response.trace_id}")

asyncio.run(main())
```

### CLI Usage

```bash
# Basic decision
sam-decision decide "What is the weather like?" --urgency 0.3 --complexity 0.2

# Decision with personality influence
sam-decision decide "Analyze market data" \
  --urgency 0.6 \
  --complexity 0.7 \
  --personality "analytical:0.8,creativity:0.6"

# Decision with budget and time constraints
sam-decision decide "Complex analysis" \
  --budget 5000 \
  --time 300 \
  --urgency 0.7 \
  --complexity 0.8

# Show system status
sam-decision status --json

# Run demonstration
sam-decision demo
```

## 🧠 Core Philosophy

### Maturity-Based Development

The system supports four developmental stages:

- **Infant Stage (0-6 months)**: Conservative decision-making, heavy supervision, basic safety protocols
- **Child Stage (6-18 months)**: Exploration within safe boundaries, learning from outcomes, developing judgment
- **Adolescent Stage (18-36 months)**: Independent decision-making with oversight, complex planning, risk assessment
- **Adult Stage (36+ months)**: Full autonomy with mature judgment, sophisticated planning, self-regulation

### Mental Health Safeguards

The engine includes comprehensive mental health monitoring:

- **Recursive Loop Prevention**: Detects and breaks circular thinking patterns
- **Addiction Prevention**: Monitors validation-seeking behaviors
- **Impulse Control**: Manages over-excitement and novelty-driven actions
- **Stress Management**: Prevents cognitive overload and burnout
- **Emotional Regulation**: Balances enthusiasm with measured responses

## 🔧 Features

### Personality Integration

```python
# Define personality influence
personality = PersonalityInfluence(
    tone="analytical",
    assertiveness=0.8,
    patience=0.7,
    humor=0.3,
    creativity=0.6,
    analytical=0.9,
    social=0.4
)

# Make personality-aware decision
response = await engine.decide(
    goal="Create detailed analysis",
    personality_influence=personality,
    urgency=0.6,
    complexity=0.7
)
```

### Policy Enforcement

The engine enforces policies through the PolicyHook:

- **Safety Gates**: Prevents dangerous or inappropriate actions
- **Budget Constraints**: Enforces compute and time limits
- **Access Control**: Manages external API and tool usage
- **Data Protection**: Prevents PII and sensitive data exposure

### Trace Emission

Every decision generates a comprehensive trace:

```python
# Decision traces include:
{
    "id": "uuid",
    "timestamp": "2024-01-01T12:00:00Z",
    "vsp": 0.31,
    "mode": "flow",
    "candidates": [
        {
            "id": "plan-1",
            "utility": 0.66,
            "factor_breakdown": {...},
            "explanation": "High quality, low risk"
        }
    ],
    "winner": "plan-1",
    "reasons": ["higher quality", "lower risk"],
    "personality_weights": {...},
    "policy_flags": ["approved"],
    "budget_exceeded": false,
    "fallback_used": false
}
```

### Budget Management

```python
# Set budget and time constraints
response = await engine.decide(
    goal="Complex analysis",
    budget=5000,      # Token budget
    time_limit=300,   # Time limit in seconds
    urgency=0.7,
    complexity=0.8
)

if response.budget_exceeded:
    print("Budget exceeded, using fallback plan")
if response.fallback_used:
    print("Fallback plan used due to constraints")
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_trace_emission.py
pytest tests/test_policy_gate.py
pytest tests/test_personality_tilts_utility.py
pytest tests/test_budget_fallback.py
pytest tests/test_cli_smoke.py

# Run with coverage
pytest --cov=src/sam tests/
```

## 📊 Monitoring

The engine provides comprehensive monitoring:

```python
# Get system status
status = engine.get_status()

print(f"Maturity Level: {status['maturity']['level']}")
print(f"Mental Health: {status['mental_health']['status']}")
print(f"Total Decisions: {status['performance']['total_decisions']}")
print(f"Average Confidence: {status['performance']['average_confidence']}")
```

## 🔗 Integration

### With Aegis Core

The engine is designed to work seamlessly with the aegis-core ecosystem:

- **Core Integrator**: Blends the functional trilogy
- **Scaffolding**: Central identity and memory
- **Personality Matrix**: Survivable personality layer

### With External Systems

```python
# Custom policy hook
class CustomPolicyHook:
    async def check_plan(self, plan_dict):
        # Custom policy logic
        return {"approved": True, "flags": ["custom_check"]}

# Custom trace logger
class CustomTraceLogger:
    async def log_decision_trace(self, trace):
        # Custom logging logic
        pass

# Use custom components
engine = DecisionEngine(
    trace_logger=CustomTraceLogger(),
    policy_hook=CustomPolicyHook(),
    state_store=state_store,
    event_bus=event_bus
)
```

## 📈 Performance

The engine is optimized for:

- **Low Latency**: Fast decision-making for real-time applications
- **High Throughput**: Efficient processing of multiple concurrent decisions
- **Memory Efficiency**: Minimal memory footprint with StateStore integration
- **Scalability**: Horizontal scaling with EventBus and distributed state

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BawtL Labs** for the core architecture
- **Aegis Core** team for the foundational components
- **Open Source Community** for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/bawtL-Labs/aegis-decision-engine/issues)
- **Documentation**: [README](README.md) and inline code documentation
- **Email**: info@bawtlabs.com

---

**S.A.M. Decision Engine v2.0** - Empowering autonomous AI with personality-aware, policy-enforced, and trace-emitted decisions.