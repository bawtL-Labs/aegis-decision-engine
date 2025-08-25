"""
Orientation Module for the S.A.M. Decision Engine.

Implements the core Sense → Evaluate → Plan → Act → Learn cycle that drives
all decision-making in the system.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..models import (
    ActionPlan,
    DecisionRequest,
    DecisionResponse,
    DecisionTrace,
    DecodingMode,
    MentalHealthStatus,
    MaturityLevel,
    PersonalityInfluence,
)
from ..maturity import MaturityTracker
from ..mental_health import MentalHealthMonitor

logger = logging.getLogger(__name__)


class Orientation:
    """
    Core orientation module implementing the SEPA cycle.
    
    Sense → Evaluate → Plan → Act → Learn
    """
    
    def __init__(self, maturity_tracker: MaturityTracker, 
                 mental_health_monitor: MentalHealthMonitor):
        """Initialize the orientation module."""
        self.maturity_tracker = maturity_tracker
        self.mental_health_monitor = mental_health_monitor
        
        # Current state
        self.current_state: Dict[str, Any] = {}
        self.vsp_level: float = 0.0  # V_SP perturbation level
        self.current_mode: DecodingMode = DecodingMode.FLOW
        
        # Cycle tracking
        self.cycle_count = 0
        self.last_cycle_time = datetime.utcnow()
        
        logger.info("Orientation module initialized")
    
    async def process_request(self, request: DecisionRequest) -> DecisionResponse:
        """
        Process a decision request through the full SEPA cycle.
        
        Args:
            request: The decision request to process
            
        Returns:
            DecisionResponse with the selected action plan and metadata
        """
        cycle_start = datetime.utcnow()
        self.cycle_count += 1
        
        logger.info(f"Starting SEPA cycle {self.cycle_count} for goal: {request.goal}")
        
        try:
            # SENSE: Gather current state and context
            state = await self._sense(request)
            
            # EVALUATE: Assess the situation and requirements
            evaluation = await self._evaluate(request, state)
            
            # PLAN: Generate and select action plans
            plan_result = await self._plan(request, state, evaluation)
            
            # ACT: Execute the selected plan (or prepare for execution)
            action_result = await self._act(plan_result)
            
            # LEARN: Update knowledge and improve future decisions
            learning_result = await self._learn(request, state, evaluation, plan_result, action_result)
            
            # Create decision response
            response = DecisionResponse(
                plan_id=plan_result["selected_plan"].id,
                confidence=plan_result["confidence"],
                mental_health_status=self.mental_health_monitor.get_current_metrics().status,
                maturity_level=self.maturity_tracker.profile.level,
                trace_id=plan_result["trace_id"],
                warnings=plan_result.get("warnings", []),
                recommendations=learning_result.get("recommendations", [])
            )
            
            # Update cycle tracking
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self.last_cycle_time = datetime.utcnow()
            
            logger.info(f"SEPA cycle {self.cycle_count} completed in {cycle_duration:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in SEPA cycle: {e}")
            # Return a safe fallback response
            return self._create_fallback_response(request, str(e))
    
    async def _sense(self, request: DecisionRequest) -> Dict[str, Any]:
        """
        SENSE: Gather current state and context information.
        
        This includes:
        - Current system state
        - V_SP perturbation level
        - Available resources and constraints
        - Mental health status
        - Maturity level constraints
        """
        logger.debug("SENSE: Gathering current state and context")
        
        # Get current mental health status
        mental_health = self.mental_health_monitor.get_current_metrics()
        
        # Get maturity constraints
        maturity_config = self.maturity_tracker.get_current_config()
        
        # Assess V_SP perturbation level
        vsp_level = self._assess_vsp_level(request, mental_health)
        
        # Gather available resources
        resources = await self._gather_resources()
        
        # Build comprehensive state
        state = {
            "mental_health": {
                "status": mental_health.status.value,
                "stress_level": mental_health.stress_level,
                "excitement_level": mental_health.excitement_level,
                "emotional_stability": mental_health.emotional_stability,
            },
            "maturity": {
                "level": self.maturity_tracker.profile.level.value,
                "constraints": maturity_config,
                "can_handle_complexity": self.maturity_tracker.can_handle_complexity(request.complexity),
                "can_handle_urgency": self.maturity_tracker.can_handle_urgency(request.urgency),
            },
            "vsp_level": vsp_level,
            "resources": resources,
            "context": request.context,
            "constraints": request.constraints,
            "personality_influence": request.personality_influence.dict() if request.personality_influence else None,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.current_state = state
        self.vsp_level = vsp_level
        
        logger.debug(f"SENSE: V_SP level = {vsp_level:.3f}, Mental health = {mental_health.status.value}")
        
        return state
    
    async def _evaluate(self, request: DecisionRequest, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        EVALUATE: Assess the situation and determine requirements.
        
        This includes:
        - Goal analysis and decomposition
        - Risk assessment
        - Resource requirements
        - Success criteria
        - Mental health considerations
        """
        logger.debug("EVALUATE: Assessing situation and requirements")
        
        # Analyze goal complexity and requirements
        goal_analysis = self._analyze_goal(request.goal, request.context)
        
        # Assess risks
        risk_assessment = self._assess_risks(request, state)
        
        # Determine resource requirements
        resource_requirements = self._determine_resource_requirements(request, goal_analysis)
        
        # Check mental health constraints
        mental_health_constraints = self._check_mental_health_constraints(state)
        
        # Determine success criteria
        success_criteria = self._define_success_criteria(request, goal_analysis)
        
        # Select appropriate decoding mode
        decoding_mode = self._select_decoding_mode(request, state, goal_analysis)
        
        evaluation = {
            "goal_analysis": goal_analysis,
            "risk_assessment": risk_assessment,
            "resource_requirements": resource_requirements,
            "mental_health_constraints": mental_health_constraints,
            "success_criteria": success_criteria,
            "decoding_mode": decoding_mode,
            "complexity_score": goal_analysis["complexity"],
            "urgency_score": request.urgency,
            "confidence_required": self.maturity_tracker.get_confidence_threshold(),
        }
        
        self.current_mode = decoding_mode
        
        logger.debug(f"EVALUATE: Mode = {decoding_mode.value}, Complexity = {goal_analysis['complexity']:.3f}")
        
        return evaluation
    
    async def _plan(self, request: DecisionRequest, state: Dict[str, Any], 
                   evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        PLAN: Generate and select action plans.
        
        This includes:
        - Generating multiple candidate plans
        - Scoring plans based on utility function
        - Selecting the best plan
        - Preparing fallback plans
        """
        logger.debug("PLAN: Generating and selecting action plans")
        
        # Generate candidate plans
        candidate_plans = await self._generate_candidate_plans(request, state, evaluation)
        
        # Score plans using utility function
        scored_plans = await self._score_plans(candidate_plans, state, evaluation)
        
        # Select best plan
        selected_plan = self._select_best_plan(scored_plans, evaluation)
        
        # Prepare fallback plans if required
        fallback_plans = self._prepare_fallback_plans(scored_plans, selected_plan)
        
        # Create decision trace
        trace = DecisionTrace(
            vsp=self.vsp_level,
            mode=self.current_mode,
            candidates=[{"id": p["plan"].id, "U": p["utility_score"]} for p in scored_plans],
            winner=selected_plan["plan"].id,
            reasons=selected_plan["reasons"],
            guards=selected_plan.get("guards", []),
            budgets=selected_plan["plan"].estimates,
            mental_health=state["mental_health"]["status"],
            maturity_level=self.maturity_tracker.profile.level
        )
        
        plan_result = {
            "candidate_plans": candidate_plans,
            "scored_plans": scored_plans,
            "selected_plan": selected_plan["plan"],
            "confidence": selected_plan["confidence"],
            "fallback_plans": fallback_plans,
            "trace_id": trace.id,
            "trace": trace,
            "warnings": selected_plan.get("warnings", []),
        }
        
        logger.debug(f"PLAN: Selected plan {selected_plan['plan'].id} with confidence {selected_plan['confidence']:.3f}")
        
        return plan_result
    
    async def _act(self, plan_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT: Execute the selected plan or prepare for execution.
        
        This includes:
        - Plan validation
        - Resource allocation
        - Execution preparation
        - Safety checks
        """
        logger.debug("ACT: Preparing for plan execution")
        
        selected_plan = plan_result["selected_plan"]
        
        # Validate plan
        validation_result = await self._validate_plan(selected_plan)
        
        # Allocate resources
        allocation_result = await self._allocate_resources(selected_plan)
        
        # Perform safety checks
        safety_result = await self._perform_safety_checks(selected_plan)
        
        # Prepare execution context
        execution_context = {
            "plan_id": selected_plan.id,
            "validation": validation_result,
            "allocation": allocation_result,
            "safety": safety_result,
            "ready_for_execution": (
                validation_result["valid"] and 
                allocation_result["allocated"] and 
                safety_result["safe"]
            ),
        }
        
        logger.debug(f"ACT: Plan {selected_plan.id} ready for execution: {execution_context['ready_for_execution']}")
        
        return execution_context
    
    async def _learn(self, request: DecisionRequest, state: Dict[str, Any], 
                    evaluation: Dict[str, Any], plan_result: Dict[str, Any], 
                    action_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        LEARN: Update knowledge and improve future decisions.
        
        This includes:
        - Recording decision outcomes
        - Updating mental health metrics
        - Learning from experience
        - Adjusting maturity parameters
        """
        logger.debug("LEARN: Updating knowledge and improving future decisions")
        
        # Record decision for learning
        decision_data = {
            "goal": request.goal,
            "complexity": evaluation["complexity_score"],
            "urgency": request.urgency,
            "selected_plan_id": plan_result["selected_plan"].id,
            "confidence": plan_result["confidence"],
            "mental_health_status": state["mental_health"]["status"],
            "maturity_level": self.maturity_tracker.profile.level.value,
            "vsp_level": self.vsp_level,
            "ready_for_execution": action_result["ready_for_execution"],
        }
        
        # Update maturity tracker
        self.maturity_tracker.record_decision(decision_data)
        
        # Update mental health monitor
        self.mental_health_monitor.update_from_decision(decision_data)
        
        # Update maturity tracker with mental health
        self.maturity_tracker.update_mental_health(
            self.mental_health_monitor.get_current_metrics()
        )
        
        # Generate learning recommendations
        recommendations = self._generate_learning_recommendations(
            request, state, evaluation, plan_result, action_result
        )
        
        learning_result = {
            "decision_recorded": True,
            "mental_health_updated": True,
            "maturity_updated": True,
            "recommendations": recommendations,
        }
        
        logger.debug("LEARN: Knowledge updated successfully")
        
        return learning_result
    
    def _assess_vsp_level(self, request: DecisionRequest, mental_health) -> float:
        """Assess V_SP perturbation level based on request and mental health."""
        base_vsp = 0.0
        
        # Increase V_SP for high complexity
        if request.complexity > 0.8:
            base_vsp += 0.3
        
        # Increase V_SP for high urgency
        if request.urgency > 0.8:
            base_vsp += 0.2
        
        # Increase V_SP for mental health issues
        if mental_health.status != MentalHealthStatus.STABLE:
            base_vsp += 0.2
        
        # Increase V_SP for high stress
        if mental_health.stress_level > 0.7:
            base_vsp += 0.15
        
        # Increase V_SP for low emotional stability
        if mental_health.emotional_stability < 0.5:
            base_vsp += 0.1
        
        return min(1.0, base_vsp)
    
    async def _gather_resources(self) -> Dict[str, Any]:
        """Gather information about available resources."""
        # This would typically interface with resource management systems
        return {
            "compute": {"available": True, "capacity": 0.8},
            "memory": {"available": True, "capacity": 0.7},
            "time": {"available": True, "budget": 300},  # seconds
            "tools": {"available": True, "count": 15},
            "external_apis": {"available": True, "rate_limit": 0.9},
        }
    
    def _analyze_goal(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goal complexity and requirements."""
        # Simple heuristic-based analysis
        complexity = 0.5  # Base complexity
        
        # Increase complexity for certain goal types
        if "analyze" in goal.lower() or "complex" in goal.lower():
            complexity += 0.2
        if "create" in goal.lower() or "generate" in goal.lower():
            complexity += 0.15
        if "plan" in goal.lower() or "strategy" in goal.lower():
            complexity += 0.1
        
        # Adjust based on context
        if context.get("requires_external_data"):
            complexity += 0.1
        if context.get("requires_multiple_steps"):
            complexity += 0.15
        if context.get("time_sensitive"):
            complexity += 0.1
        
        return {
            "complexity": min(1.0, complexity),
            "type": self._classify_goal_type(goal),
            "estimated_steps": max(1, int(complexity * 5)),
            "requires_external_tools": complexity > 0.6,
        }
    
    def _classify_goal_type(self, goal: str) -> str:
        """Classify the type of goal."""
        goal_lower = goal.lower()
        
        if any(word in goal_lower for word in ["answer", "what", "how", "why"]):
            return "answer"
        elif any(word in goal_lower for word in ["find", "search", "retrieve", "get"]):
            return "retrieve"
        elif any(word in goal_lower for word in ["create", "generate", "make", "build"]):
            return "create"
        elif any(word in goal_lower for word in ["analyze", "examine", "study", "investigate"]):
            return "analyze"
        elif any(word in goal_lower for word in ["plan", "strategy", "approach"]):
            return "plan"
        else:
            return "tool"
    
    def _assess_risks(self, request: DecisionRequest, state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with the request."""
        risk_score = 0.0
        risk_factors = []
        
        # High complexity increases risk
        if request.complexity > 0.8:
            risk_score += 0.3
            risk_factors.append("high_complexity")
        
        # High urgency increases risk
        if request.urgency > 0.8:
            risk_score += 0.2
            risk_factors.append("high_urgency")
        
        # Mental health issues increase risk
        if state["mental_health"]["status"] != "stable":
            risk_score += 0.2
            risk_factors.append("mental_health_concern")
        
        # Low maturity increases risk
        if state["maturity"]["level"] == "infant":
            risk_score += 0.15
            risk_factors.append("low_maturity")
        
        # High V_SP increases risk
        if state["vsp_level"] > 0.7:
            risk_score += 0.15
            risk_factors.append("high_vsp")
        
        return {
            "risk_score": min(1.0, risk_score),
            "risk_factors": risk_factors,
            "acceptable_risk": risk_score <= self.maturity_tracker.get_risk_tolerance(),
        }
    
    def _determine_resource_requirements(self, request: DecisionRequest, 
                                       goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine resource requirements for the request."""
        base_tokens = 1000
        base_time = 30  # seconds
        
        # Scale based on complexity
        complexity_multiplier = 1 + goal_analysis["complexity"]
        
        return {
            "tokens": int(base_tokens * complexity_multiplier),
            "time_seconds": int(base_time * complexity_multiplier),
            "compute_gpu": min(1.0, 0.1 * complexity_multiplier),
            "external_calls": goal_analysis["requires_external_tools"],
            "memory_mb": int(100 * complexity_multiplier),
        }
    
    def _check_mental_health_constraints(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check mental health constraints for decision-making."""
        mental_health = state["mental_health"]
        constraints = {}
        
        # High stress may limit complexity
        if mental_health["stress_level"] > 0.8:
            constraints["max_complexity"] = 0.5
            constraints["max_urgency"] = 0.6
        
        # Low emotional stability may require simpler approaches
        if mental_health["emotional_stability"] < 0.4:
            constraints["require_validation"] = True
            constraints["max_risk"] = 0.3
        
        return constraints
    
    def _define_success_criteria(self, request: DecisionRequest, 
                                goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Define success criteria for the request."""
        return {
            "completion": True,
            "quality_threshold": 0.7,
            "time_limit": request.constraints.get("time_limit", 300),
            "accuracy_threshold": 0.8 if goal_analysis["type"] == "answer" else 0.6,
            "safety_compliance": True,
            "user_satisfaction": True,
        }
    
    def _select_decoding_mode(self, request: DecisionRequest, state: Dict[str, Any], 
                            goal_analysis: Dict[str, Any]) -> DecodingMode:
        """Select appropriate decoding mode based on request and state."""
        # High urgency or crisis situations
        if request.urgency > 0.9 or state["vsp_level"] > 0.8:
            return DecodingMode.CRISIS
        
        # Complex analysis or planning tasks
        if goal_analysis["complexity"] > 0.7 or goal_analysis["type"] in ["analyze", "plan"]:
            return DecodingMode.DEEP
        
        # Default to flow mode for most tasks
        return DecodingMode.FLOW
    
    async def _generate_candidate_plans(self, request: DecisionRequest, state: Dict[str, Any], 
                                      evaluation: Dict[str, Any]) -> List[ActionPlan]:
        """Generate candidate action plans."""
        # This is a simplified implementation
        # In practice, this would use more sophisticated plan generation
        
        plans = []
        
        # Generate conservative plan
        conservative_plan = self._create_plan(
            request, state, evaluation, "conservative", 
            steps=3, quality=0.8, risk=0.2, spend=0.6
        )
        plans.append(conservative_plan)
        
        # Generate balanced plan
        balanced_plan = self._create_plan(
            request, state, evaluation, "balanced",
            steps=5, quality=0.7, risk=0.4, spend=0.8
        )
        plans.append(balanced_plan)
        
        # Generate aggressive plan (if maturity allows)
        if self.maturity_tracker.profile.level.value in ["adolescent", "adult"]:
            aggressive_plan = self._create_plan(
                request, state, evaluation, "aggressive",
                steps=7, quality=0.6, risk=0.6, spend=1.0
            )
            plans.append(aggressive_plan)
        
        return plans
    
    def _create_plan(self, request: DecisionRequest, state: Dict[str, Any], 
                    evaluation: Dict[str, Any], strategy: str, 
                    steps: int, quality: float, risk: float, spend: float) -> ActionPlan:
        """Create an action plan with the specified strategy."""
        from uuid import uuid4
        
        # Create steps based on strategy
        plan_steps = []
        for i in range(steps):
            step = {
                "id": f"s{i+1}",
                "type": "llm" if i % 2 == 0 else "tool",
                "tool_id": f"tool_{i}" if i % 2 == 1 else None,
                "args": {},
                "budget": {"tok": 500, "sec": 10, "gpu": 0.1}
            }
            plan_steps.append(step)
        
        return ActionPlan(
            request_id=uuid4(),
            goal={"type": evaluation["goal_analysis"]["type"], "spec": request.goal},
            steps=plan_steps,
            estimates={"quality": quality, "risk": risk, "spend": spend},
            profile={"mode": evaluation["decoding_mode"].value, "llm": "local_20B"},
            policies=["no_pii_exfil"],
            explanations=f"Strategy: {strategy} - {steps} steps, quality {quality}, risk {risk}",
            status="proposed"
        )
    
    async def _score_plans(self, plans: List[ActionPlan], state: Dict[str, Any], 
                          evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score plans using the utility function."""
        scored_plans = []
        
        for plan in plans:
            # Calculate utility components
            G = self._calculate_goal_satisfaction(plan, evaluation)
            Q = plan.estimates["quality"]
            R = plan.estimates["risk"]
            S = plan.estimates["spend"]
            
            # Get weights from maturity level
            weights = self._get_utility_weights()
            
            # Calculate utility
            utility = (weights["goal"] * G + 
                      weights["quality"] * Q - 
                      weights["risk"] * R - 
                      weights["spend"] * S)
            
            scored_plans.append({
                "plan": plan,
                "utility_score": utility,
                "components": {"G": G, "Q": Q, "R": R, "S": S},
                "weights": weights,
            })
        
        # Sort by utility score
        scored_plans.sort(key=lambda x: x["utility_score"], reverse=True)
        
        return scored_plans
    
    def _calculate_goal_satisfaction(self, plan: ActionPlan, evaluation: Dict[str, Any]) -> float:
        """Calculate goal satisfaction score for a plan."""
        # Simple heuristic based on plan characteristics
        goal_type = evaluation["goal_analysis"]["type"]
        
        if goal_type == "answer":
            return min(1.0, plan.estimates["quality"] * 1.2)
        elif goal_type == "retrieve":
            return min(1.0, plan.estimates["quality"] * 1.1)
        elif goal_type == "create":
            return min(1.0, plan.estimates["quality"] * 0.9)
        else:
            return plan.estimates["quality"]
    
    def _get_utility_weights(self) -> Dict[str, float]:
        """Get utility function weights based on maturity level."""
        level = self.maturity_tracker.profile.level.value
        
        weights = {
            "infant": {"goal": 0.4, "quality": 0.3, "risk": 0.2, "spend": 0.1},
            "child": {"goal": 0.35, "quality": 0.3, "risk": 0.2, "spend": 0.15},
            "adolescent": {"goal": 0.3, "quality": 0.3, "risk": 0.2, "spend": 0.2},
            "adult": {"goal": 0.25, "quality": 0.3, "risk": 0.2, "spend": 0.25},
        }
        
        return weights.get(level, weights["adult"])
    
    def _select_best_plan(self, scored_plans: List[Dict[str, Any]], 
                         evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best plan based on scoring and constraints."""
        if not scored_plans:
            raise ValueError("No plans available for selection")
        
        best_plan = scored_plans[0]
        plan = best_plan["plan"]
        
        # Check if plan meets confidence threshold
        confidence = best_plan["utility_score"]
        required_confidence = evaluation["confidence_required"]
        
        if confidence < required_confidence:
            # Add warning about low confidence
            best_plan["warnings"] = [f"Low confidence ({confidence:.3f} < {required_confidence:.3f})"]
        
        # Generate selection reasons
        reasons = []
        if best_plan["utility_score"] > 0.7:
            reasons.append("high utility score")
        if plan.estimates["quality"] > 0.7:
            reasons.append("high quality estimate")
        if plan.estimates["risk"] < 0.5:
            reasons.append("low risk estimate")
        
        best_plan["reasons"] = reasons
        best_plan["confidence"] = confidence
        
        return best_plan
    
    def _prepare_fallback_plans(self, scored_plans: List[Dict[str, Any]], 
                               selected_plan: Dict[str, Any]) -> List[ActionPlan]:
        """Prepare fallback plans if required by maturity level."""
        fallback_count = self.maturity_tracker.get_fallback_plan_count()
        
        if fallback_count <= 1:
            return []
        
        # Return next best plans as fallbacks
        fallbacks = []
        for plan_data in scored_plans[1:fallback_count]:
            fallbacks.append(plan_data["plan"])
        
        return fallbacks
    
    async def _validate_plan(self, plan: ActionPlan) -> Dict[str, Any]:
        """Validate the selected plan."""
        # Simple validation checks
        valid = True
        issues = []
        
        # Check if plan has steps
        if not plan.steps:
            valid = False
            issues.append("No steps defined")
        
        # Check if estimates are reasonable
        if plan.estimates["risk"] > 0.9:
            valid = False
            issues.append("Risk too high")
        
        if plan.estimates["quality"] < 0.3:
            valid = False
            issues.append("Quality too low")
        
        return {"valid": valid, "issues": issues}
    
    async def _allocate_resources(self, plan: ActionPlan) -> Dict[str, Any]:
        """Allocate resources for plan execution."""
        # Simplified resource allocation
        return {
            "allocated": True,
            "tokens": plan.estimates.get("spend", 0.5) * 2000,
            "time_seconds": plan.estimates.get("spend", 0.5) * 60,
            "compute_gpu": plan.estimates.get("spend", 0.5) * 0.2,
        }
    
    async def _perform_safety_checks(self, plan: ActionPlan) -> Dict[str, Any]:
        """Perform safety checks on the plan."""
        # Simple safety checks
        safe = True
        warnings = []
        
        # Check for policy violations
        if "no_pii_exfil" in plan.policies:
            # Would check for PII in plan steps
            pass
        
        # Check for high-risk operations
        if plan.estimates["risk"] > 0.7:
            warnings.append("High-risk plan requires additional review")
        
        return {"safe": safe, "warnings": warnings}
    
    def _generate_learning_recommendations(self, request: DecisionRequest, state: Dict[str, Any],
                                         evaluation: Dict[str, Any], plan_result: Dict[str, Any],
                                         action_result: Dict[str, Any]) -> List[str]:
        """Generate learning recommendations based on the decision process."""
        recommendations = []
        
        # Mental health recommendations
        if state["mental_health"]["status"] != "stable":
            recommendations.extend(self.mental_health_monitor.get_intervention_recommendations())
        
        # Maturity-based recommendations
        if self.maturity_tracker.profile.level.value == "infant":
            recommendations.append("Consider simpler approaches for complex tasks")
        
        # Performance recommendations
        if plan_result["confidence"] < 0.7:
            recommendations.append("Consider gathering more information before deciding")
        
        return recommendations
    
    def _create_fallback_response(self, request: DecisionRequest, error: str) -> DecisionResponse:
        """Create a fallback response when the SEPA cycle fails."""
        from uuid import uuid4
        
        return DecisionResponse(
            plan_id=uuid4(),
            confidence=0.1,
            mental_health_status=self.mental_health_monitor.get_current_metrics().status,
            maturity_level=self.maturity_tracker.profile.level,
            trace_id=uuid4(),
            warnings=[f"SEPA cycle failed: {error}"],
            recommendations=["Use simpler approach", "Request human assistance"]
        )