# S.A.M. Decision Engine (SDE)

A maturity-based decision engine for autonomous AI systems that works in conjunction with the aegis-scaffolding neural base and personality matrix.

## Overview

The S.A.M. Decision Engine is designed to evolve from infant to adult intelligence, making decisions about what actions to take and how hard to try based on current state, goals, constraints, and learned experience. It incorporates mental health safeguards and prevents common AI pitfalls like recursive loops, addictive behaviors, and impulsive decision-making.

## Core Philosophy

### Maturity-Based Development
- **Infant Stage (0-6 months)**: Conservative decision-making, heavy supervision, basic safety protocols
- **Child Stage (6-18 months)**: Exploration within safe boundaries, learning from outcomes, developing judgment
- **Adolescent Stage (18-36 months)**: Independent decision-making with oversight, complex planning, risk assessment
- **Adult Stage (36+ months)**: Full autonomy with mature judgment, sophisticated planning, self-regulation

### Mental Health Safeguards
- **Recursive Loop Prevention**: Detection and intervention for thought spirals
- **Addiction Prevention**: Monitoring for validation-seeking behaviors
- **Impulse Control**: Managing over-excitement and novelty-driven actions
- **Emotional Regulation**: Balancing enthusiasm with measured responses
- **Stress Management**: Preventing cognitive overload and burnout

## Architecture

### Core Components

1. **Orientation Module**: Sense → Evaluate → Plan → Act → Learn cycle
2. **Utility Engine**: Goal satisfaction, quality, risk, and resource optimization
3. **Plan Generator**: Action plan creation with multiple variants
4. **Scoring System**: Plan evaluation with safety and policy compliance
5. **Budget Manager**: Resource allocation and constraint enforcement
6. **Safety Gates**: Consent and policy enforcement
7. **CDP Integration**: Complex decision protocol escalation
8. **Learning Engine**: Outcome analysis and pattern recognition
9. **Mental Health Monitor**: Emotional state and behavior tracking
10. **Maturity Tracker**: Developmental stage management

### Key Interfaces

- **Aegis Scaffolding**: Neural base integration for state management
- **Personality Matrix**: Individual trait influence on decision-making
- **Firewall**: Safety and policy enforcement
- **SSD**: Schema learning and pattern storage

## Installation

```bash
git clone https://github.com/bawtL-Labs/sam-decision-engine.git
cd sam-decision-engine
pip install -r requirements.txt
```

## Quick Start

```python
from sam.decision import DecisionEngine
from sam.maturity import MaturityTracker

# Initialize with infant maturity level
engine = DecisionEngine(maturity_level="infant")
tracker = MaturityTracker()

# Make a decision
decision = engine.decide(
    goal="answer user question",
    context="user asked about weather",
    constraints={"time_limit": 30, "no_external_calls": True}
)

print(f"Selected plan: {decision.plan_id}")
print(f"Confidence: {decision.confidence}")
print(f"Mental state: {decision.mental_health_status}")
```

## Development Status

- [x] Core architecture design
- [x] Maturity-based decision framework
- [x] Mental health monitoring system
- [ ] Integration with aegis-scaffolding
- [ ] Personality matrix integration
- [ ] Advanced learning algorithms
- [ ] Performance optimization

## Contributing

This project follows the same contribution guidelines as the aegis-scaffolding project. Please ensure all code includes comprehensive tests and documentation.

## License

MIT License - see LICENSE file for details.