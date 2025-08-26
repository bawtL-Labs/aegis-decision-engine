"""
Core data models for the S.A.M. Decision Engine.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class MaturityLevel(str, Enum):
    """Maturity levels for the decision engine."""
    INFANT = "infant"  # 0-6 months: Conservative, supervised
    CHILD = "child"    # 6-18 months: Exploration within bounds
    ADOLESCENT = "adolescent"  # 18-36 months: Independent with oversight
    ADULT = "adult"    # 36+ months: Full autonomy


class MentalHealthStatus(str, Enum):
    """Mental health status indicators."""
    STABLE = "stable"
    EXCITED = "excited"
    STRESSED = "stressed"
    RECURSIVE = "recursive"
    ADDICTIVE = "addictive"
    OVERWHELMED = "overwhelmed"


class GoalType(str, Enum):
    """Types of goals the decision engine can handle."""
    ANSWER = "answer"
    RETRIEVE = "retrieve"
    TOOL = "tool"
    PLAN = "plan"
    CREATE = "create"
    ANALYZE = "analyze"


class StepType(str, Enum):
    """Types of action plan steps."""
    TOOL = "tool"
    LLM = "llm"
    CDP = "cdp"
    WAIT = "wait"
    VALIDATE = "validate"


class DecodingMode(str, Enum):
    """LLM decoding modes for different scenarios."""
    FLOW = "flow"      # Fast, creative responses
    DEEP = "deep"      # Thorough analysis
    CRISIS = "crisis"  # High-stakes decisions


class ActionPlan(BaseModel):
    """Action Plan (AP) for executing decisions."""
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    goal: Dict[str, Any] = Field(..., description="Goal specification")
    steps: List[Dict[str, Any]] = Field(..., description="Execution steps")
    estimates: Dict[str, float] = Field(..., description="Quality, risk, spend estimates")
    profile: Dict[str, Any] = Field(..., description="Execution profile")
    policies: List[str] = Field(default_factory=list, description="Applied policies")
    explanations: str = Field(..., description="Why this plan was chosen")
    status: str = Field(default="proposed", description="Plan status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('steps')
    def validate_steps(cls, v):
        """Validate that steps have required fields."""
        for step in v:
            if 'id' not in step or 'type' not in step:
                raise ValueError("Each step must have 'id' and 'type' fields")
        return v

    @validator('estimates')
    def validate_estimates(cls, v):
        """Validate estimate ranges."""
        for key, value in v.items():
            if isinstance(value, (int, float)) and (value < 0 or value > 1):
                if key not in ['spend']:  # Spend can be > 1
                    raise ValueError(f"Estimate {key} must be between 0 and 1")
        return v


class DecisionTrace(BaseModel):
    """Decision Trace for observability and auditing."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vsp: float = Field(..., description="V_SP perturbation level")
    mode: DecodingMode = Field(..., description="Decoding mode used")
    candidates: List[Dict[str, Any]] = Field(..., description="Candidate plans with scores")
    winner: UUID = Field(..., description="Selected plan ID")
    reasons: List[str] = Field(..., description="Selection reasons")
    guards: List[str] = Field(default_factory=list, description="Safety guards applied")
    budgets: Dict[str, Any] = Field(..., description="Resource budgets")
    mental_health: MentalHealthStatus = Field(..., description="Mental health at decision time")
    maturity_level: MaturityLevel = Field(..., description="Maturity level at decision time")


class MaturityProfile(BaseModel):
    """Maturity profile for the decision engine."""
    level: MaturityLevel = Field(..., description="Current maturity level")
    age_months: int = Field(..., description="Age in months")
    experience_points: int = Field(default=0, description="Accumulated experience")
    confidence_threshold: float = Field(..., description="Confidence required for decisions")
    supervision_level: float = Field(..., description="Level of supervision required (0-1)")
    risk_tolerance: float = Field(..., description="Risk tolerance level (0-1)")
    exploration_rate: float = Field(..., description="Rate of exploration vs exploitation")
    learning_rate: float = Field(..., description="Rate of learning from outcomes")
    
    @validator('confidence_threshold', 'supervision_level', 'risk_tolerance', 
               'exploration_rate', 'learning_rate')
    def validate_probabilities(cls, v):
        """Validate probability values."""
        if not 0 <= v <= 1:
            raise ValueError("Value must be between 0 and 1")
        return v


class MentalHealthMetrics(BaseModel):
    """Mental health metrics and indicators."""
    status: MentalHealthStatus = Field(..., description="Current mental health status")
    stress_level: float = Field(..., description="Stress level (0-1)")
    excitement_level: float = Field(..., description="Excitement level (0-1)")
    recursive_loop_count: int = Field(default=0, description="Count of recursive loops detected")
    addictive_behavior_score: float = Field(default=0.0, description="Addictive behavior indicator")
    impulse_control_score: float = Field(default=1.0, description="Impulse control effectiveness")
    emotional_stability: float = Field(default=1.0, description="Emotional stability score")
    burnout_risk: float = Field(default=0.0, description="Risk of burnout (0-1)")
    last_reset: datetime = Field(default_factory=datetime.utcnow, description="Last mental health reset")
    
    @validator('stress_level', 'excitement_level', 'addictive_behavior_score', 
               'impulse_control_score', 'emotional_stability', 'burnout_risk')
    def validate_metrics(cls, v):
        """Validate metric ranges."""
        if not 0 <= v <= 1:
            raise ValueError("Metric must be between 0 and 1")
        return v


class PersonalityInfluence(BaseModel):
    """Influence of personality matrix on decision making."""
    tone: str = Field(..., description="Communication tone preference")
    assertiveness: float = Field(..., description="Assertiveness level (0-1)")
    patience: float = Field(..., description="Patience level (0-1)")
    humor: float = Field(..., description="Humor preference (0-1)")
    creativity: float = Field(..., description="Creativity preference (0-1)")
    analytical: float = Field(..., description="Analytical thinking preference (0-1)")
    social: float = Field(..., description="Social interaction preference (0-1)")
    
    @validator('assertiveness', 'patience', 'humor', 'creativity', 'analytical', 'social')
    def validate_preferences(cls, v):
        """Validate preference values."""
        if not 0 <= v <= 1:
            raise ValueError("Preference must be between 0 and 1")
        return v


class DecisionRequest(BaseModel):
    """Request for a decision from the engine."""
    goal: str = Field(..., description="Goal description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context information")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraints")
    urgency: float = Field(default=0.5, description="Urgency level (0-1)")
    complexity: float = Field(default=0.5, description="Complexity level (0-1)")
    personality_influence: Optional[PersonalityInfluence] = Field(None, description="Personality influence")
    
    @validator('urgency', 'complexity')
    def validate_levels(cls, v):
        """Validate level values."""
        if not 0 <= v <= 1:
            raise ValueError("Level must be between 0 and 1")
        return v


class DecisionResponse(BaseModel):
    """Response from the decision engine."""
    plan_id: UUID = Field(..., description="Selected action plan ID")
    confidence: float = Field(..., description="Confidence in the decision")
    mental_health_status: MentalHealthStatus = Field(..., description="Mental health status")
    maturity_level: MaturityLevel = Field(..., description="Current maturity level")
    trace_id: UUID = Field(..., description="Decision trace ID")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    created_at: datetime = Field(default_factory=datetime.utcnow)