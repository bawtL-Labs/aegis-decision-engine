"""
Utility Engine for the S.A.M. Decision Engine.

Calculates utility scores for action plans using the formula:
U = w_g*G + w_q*Q - w_r*R - w_s*S

Where:
- G = Goal satisfaction
- Q = Quality
- R = Risk
- S = Spend (resource cost)
"""

import logging
from typing import Dict, List, Optional, Tuple

from ..models import ActionPlan, MaturityLevel, PersonalityInfluence

logger = logging.getLogger(__name__)


class UtilityEngine:
    """
    Utility engine for scoring action plans.
    
    Implements the core utility function and provides methods for calculating
    each component based on plan characteristics and maturity level.
    """
    
    def __init__(self):
        """Initialize the utility engine."""
        # Default weights for different maturity levels
        self.maturity_weights = {
            MaturityLevel.INFANT: {
                "goal": 0.4,      # High goal focus, conservative
                "quality": 0.3,   # Good quality important
                "risk": 0.2,      # Risk averse
                "spend": 0.1      # Low resource concern
            },
            MaturityLevel.CHILD: {
                "goal": 0.35,     # Still goal-focused
                "quality": 0.3,   # Maintain quality
                "risk": 0.2,      # Still risk averse
                "spend": 0.15     # Some resource awareness
            },
            MaturityLevel.ADOLESCENT: {
                "goal": 0.3,      # Balanced approach
                "quality": 0.3,   # Quality maintained
                "risk": 0.2,      # Moderate risk tolerance
                "spend": 0.2      # Resource efficiency important
            },
            MaturityLevel.ADULT: {
                "goal": 0.25,     # Efficient goal achievement
                "quality": 0.3,   # Quality standard
                "risk": 0.2,      # Calculated risk taking
                "spend": 0.25     # Resource optimization
            }
        }
        
        # Quality heuristics for different goal types
        self.quality_heuristics = {
            "answer": {
                "accuracy_weight": 0.4,
                "completeness_weight": 0.3,
                "relevance_weight": 0.2,
                "clarity_weight": 0.1
            },
            "retrieve": {
                "precision_weight": 0.4,
                "recall_weight": 0.3,
                "freshness_weight": 0.2,
                "accessibility_weight": 0.1
            },
            "create": {
                "creativity_weight": 0.3,
                "usefulness_weight": 0.3,
                "completeness_weight": 0.2,
                "originality_weight": 0.2
            },
            "analyze": {
                "depth_weight": 0.4,
                "accuracy_weight": 0.3,
                "insight_weight": 0.2,
                "actionability_weight": 0.1
            },
            "plan": {
                "feasibility_weight": 0.3,
                "completeness_weight": 0.3,
                "efficiency_weight": 0.2,
                "robustness_weight": 0.2
            },
            "tool": {
                "effectiveness_weight": 0.4,
                "efficiency_weight": 0.3,
                "reliability_weight": 0.2,
                "safety_weight": 0.1
            }
        }
        
        logger.info("Utility engine initialized")
    
    def calculate_utility(self, 
                         plan: ActionPlan,
                         maturity_level: MaturityLevel,
                         personality_influence: Optional[PersonalityInfluence] = None,
                         context: Optional[Dict] = None) -> Dict[str, float]:
        """
        Calculate utility score for an action plan.
        
        Args:
            plan: The action plan to score
            maturity_level: Current maturity level
            personality_influence: Personality traits that influence scoring
            context: Additional context for scoring
            
        Returns:
            Dictionary with utility components and final score
        """
        # Get weights for maturity level
        weights = self._get_weights(maturity_level, personality_influence)
        
        # Calculate components
        G = self._calculate_goal_satisfaction(plan, context)
        Q = self._calculate_quality(plan, context)
        R = self._calculate_risk(plan, context)
        S = self._calculate_spend(plan, context)
        
        # Calculate utility
        utility = (weights["goal"] * G + 
                  weights["quality"] * Q - 
                  weights["risk"] * R - 
                  weights["spend"] * S)
        
        # Ensure utility is bounded
        utility = max(0.0, min(1.0, utility))
        
        return {
            "utility": utility,
            "components": {
                "goal_satisfaction": G,
                "quality": Q,
                "risk": R,
                "spend": S
            },
            "weights": weights,
            "explanation": self._generate_utility_explanation(G, Q, R, S, weights, utility)
        }
    
    def _get_weights(self, maturity_level: MaturityLevel, 
                    personality_influence: Optional[PersonalityInfluence] = None) -> Dict[str, float]:
        """Get utility weights adjusted for personality influence."""
        base_weights = self.maturity_weights[maturity_level].copy()
        
        if personality_influence:
            # Adjust weights based on personality traits
            base_weights = self._adjust_weights_for_personality(base_weights, personality_influence)
        
        return base_weights
    
    def _adjust_weights_for_personality(self, weights: Dict[str, float], 
                                      personality: PersonalityInfluence) -> Dict[str, float]:
        """Adjust utility weights based on personality traits."""
        adjusted_weights = weights.copy()
        
        # Analytical personality values quality and risk assessment more
        if personality.analytical > 0.7:
            adjusted_weights["quality"] *= 1.2
            adjusted_weights["risk"] *= 1.1
            adjusted_weights["goal"] *= 0.9
        
        # Creative personality values goal achievement and quality over efficiency
        if personality.creativity > 0.7:
            adjusted_weights["goal"] *= 1.1
            adjusted_weights["quality"] *= 1.1
            adjusted_weights["spend"] *= 0.9
        
        # Social personality may value different aspects
        if personality.social > 0.7:
            adjusted_weights["goal"] *= 1.05
            adjusted_weights["spend"] *= 0.95
        
        # Assertive personality may be more risk-tolerant
        if personality.assertiveness > 0.7:
            adjusted_weights["risk"] *= 0.9
            adjusted_weights["goal"] *= 1.05
        
        # Patient personality may value quality over speed
        if personality.patience > 0.7:
            adjusted_weights["quality"] *= 1.1
            adjusted_weights["spend"] *= 0.9
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        for key in adjusted_weights:
            adjusted_weights[key] /= total_weight
        
        return adjusted_weights
    
    def _calculate_goal_satisfaction(self, plan: ActionPlan, context: Optional[Dict] = None) -> float:
        """Calculate goal satisfaction score."""
        goal_type = plan.goal.get("type", "tool")
        goal_spec = plan.goal.get("spec", "")
        
        # Base satisfaction from plan characteristics
        base_satisfaction = 0.5
        
        # Adjust based on goal type
        if goal_type == "answer":
            # Answer goals benefit from thorough analysis
            if len(plan.steps) >= 3:
                base_satisfaction += 0.2
            if plan.estimates.get("quality", 0) > 0.7:
                base_satisfaction += 0.1
        
        elif goal_type == "retrieve":
            # Retrieval goals benefit from multiple search strategies
            search_steps = sum(1 for step in plan.steps if step.get("type") == "tool")
            if search_steps >= 2:
                base_satisfaction += 0.15
            if plan.estimates.get("quality", 0) > 0.6:
                base_satisfaction += 0.1
        
        elif goal_type == "create":
            # Creation goals benefit from creative approaches
            creative_steps = sum(1 for step in plan.steps if step.get("type") == "llm")
            if creative_steps >= 2:
                base_satisfaction += 0.2
            if plan.estimates.get("quality", 0) > 0.6:
                base_satisfaction += 0.1
        
        elif goal_type == "analyze":
            # Analysis goals benefit from depth
            if len(plan.steps) >= 4:
                base_satisfaction += 0.2
            if plan.estimates.get("quality", 0) > 0.7:
                base_satisfaction += 0.15
        
        elif goal_type == "plan":
            # Planning goals benefit from comprehensive approaches
            if len(plan.steps) >= 3:
                base_satisfaction += 0.15
            if plan.estimates.get("quality", 0) > 0.6:
                base_satisfaction += 0.1
        
        # Adjust based on context requirements
        if context:
            if context.get("requires_external_data") and any(
                step.get("type") == "tool" for step in plan.steps
            ):
                base_satisfaction += 0.1
            
            if context.get("time_sensitive") and plan.estimates.get("spend", 1.0) < 0.8:
                base_satisfaction += 0.1
        
        return min(1.0, base_satisfaction)
    
    def _calculate_quality(self, plan: ActionPlan, context: Optional[Dict] = None) -> float:
        """Calculate quality score based on plan characteristics."""
        goal_type = plan.goal.get("type", "tool")
        heuristics = self.quality_heuristics.get(goal_type, self.quality_heuristics["tool"])
        
        # Base quality from plan estimates
        base_quality = plan.estimates.get("quality", 0.5)
        
        # Adjust based on plan characteristics
        quality_factors = {}
        
        if goal_type == "answer":
            quality_factors["accuracy"] = self._assess_answer_accuracy(plan)
            quality_factors["completeness"] = self._assess_completeness(plan)
            quality_factors["relevance"] = self._assess_relevance(plan, context)
            quality_factors["clarity"] = self._assess_clarity(plan)
        
        elif goal_type == "retrieve":
            quality_factors["precision"] = self._assess_precision(plan)
            quality_factors["recall"] = self._assess_recall(plan)
            quality_factors["freshness"] = self._assess_freshness(plan)
            quality_factors["accessibility"] = self._assess_accessibility(plan)
        
        elif goal_type == "create":
            quality_factors["creativity"] = self._assess_creativity(plan)
            quality_factors["usefulness"] = self._assess_usefulness(plan)
            quality_factors["completeness"] = self._assess_completeness(plan)
            quality_factors["originality"] = self._assess_originality(plan)
        
        elif goal_type == "analyze":
            quality_factors["depth"] = self._assess_analysis_depth(plan)
            quality_factors["accuracy"] = self._assess_analysis_accuracy(plan)
            quality_factors["insight"] = self._assess_insight_potential(plan)
            quality_factors["actionability"] = self._assess_actionability(plan)
        
        elif goal_type == "plan":
            quality_factors["feasibility"] = self._assess_feasibility(plan)
            quality_factors["completeness"] = self._assess_completeness(plan)
            quality_factors["efficiency"] = self._assess_efficiency(plan)
            quality_factors["robustness"] = self._assess_robustness(plan)
        
        else:  # tool
            quality_factors["effectiveness"] = self._assess_effectiveness(plan)
            quality_factors["efficiency"] = self._assess_efficiency(plan)
            quality_factors["reliability"] = self._assess_reliability(plan)
            quality_factors["safety"] = self._assess_safety(plan)
        
        # Calculate weighted quality score
        weighted_quality = 0.0
        for factor, weight in heuristics.items():
            if factor in quality_factors:
                weighted_quality += weight * quality_factors[factor]
        
        # Combine base quality with calculated factors
        final_quality = 0.7 * base_quality + 0.3 * weighted_quality
        
        return min(1.0, final_quality)
    
    def _calculate_risk(self, plan: ActionPlan, context: Optional[Dict] = None) -> float:
        """Calculate risk score for the plan."""
        # Base risk from plan estimates
        base_risk = plan.estimates.get("risk", 0.5)
        
        # Additional risk factors
        risk_factors = []
        
        # External tool usage increases risk
        external_tools = sum(1 for step in plan.steps if step.get("type") == "tool")
        if external_tools > 0:
            risk_factors.append(0.1 * external_tools)
        
        # High complexity increases risk
        if len(plan.steps) > 5:
            risk_factors.append(0.1)
        
        # High resource usage increases risk
        if plan.estimates.get("spend", 0) > 0.8:
            risk_factors.append(0.1)
        
        # Policy violations increase risk
        if "no_pii_exfil" in plan.policies:
            # Check if plan might involve PII
            if any("data" in str(step).lower() for step in plan.steps):
                risk_factors.append(0.2)
        
        # Context-specific risks
        if context:
            if context.get("sensitive_data"):
                risk_factors.append(0.2)
            if context.get("high_stakes"):
                risk_factors.append(0.15)
        
        # Calculate total risk
        total_risk = base_risk + sum(risk_factors)
        
        return min(1.0, total_risk)
    
    def _calculate_spend(self, plan: ActionPlan, context: Optional[Dict] = None) -> float:
        """Calculate resource spend score."""
        # Base spend from plan estimates
        base_spend = plan.estimates.get("spend", 0.5)
        
        # Adjust based on plan characteristics
        spend_factors = []
        
        # More steps generally cost more
        step_cost = len(plan.steps) * 0.05
        spend_factors.append(min(0.2, step_cost))
        
        # External tools may have costs
        external_tools = sum(1 for step in plan.steps if step.get("type") == "tool")
        if external_tools > 0:
            spend_factors.append(0.1 * external_tools)
        
        # High quality often costs more
        if plan.estimates.get("quality", 0) > 0.8:
            spend_factors.append(0.1)
        
        # Calculate total spend
        total_spend = base_spend + sum(spend_factors)
        
        return min(1.0, total_spend)
    
    # Quality assessment methods
    def _assess_answer_accuracy(self, plan: ActionPlan) -> float:
        """Assess accuracy for answer goals."""
        # More analysis steps generally improve accuracy
        analysis_steps = sum(1 for step in plan.steps if step.get("type") == "llm")
        return min(1.0, 0.5 + 0.1 * analysis_steps)
    
    def _assess_completeness(self, plan: ActionPlan) -> float:
        """Assess completeness of the plan."""
        # More comprehensive plans are more complete
        return min(1.0, 0.4 + 0.1 * len(plan.steps))
    
    def _assess_relevance(self, plan: ActionPlan, context: Optional[Dict] = None) -> float:
        """Assess relevance to the goal."""
        # Simple heuristic based on goal alignment
        return 0.7  # Base relevance score
    
    def _assess_clarity(self, plan: ActionPlan) -> float:
        """Assess clarity of the plan."""
        # Well-structured plans are clearer
        if len(plan.steps) <= 5:
            return 0.8
        else:
            return 0.6
    
    def _assess_precision(self, plan: ActionPlan) -> float:
        """Assess precision for retrieval goals."""
        # Multiple search strategies improve precision
        search_steps = sum(1 for step in plan.steps if step.get("type") == "tool")
        return min(1.0, 0.5 + 0.1 * search_steps)
    
    def _assess_recall(self, plan: ActionPlan) -> float:
        """Assess recall for retrieval goals."""
        # Multiple sources improve recall
        return 0.7  # Base recall score
    
    def _assess_freshness(self, plan: ActionPlan) -> float:
        """Assess freshness of retrieved information."""
        return 0.6  # Base freshness score
    
    def _assess_accessibility(self, plan: ActionPlan) -> float:
        """Assess accessibility of the plan."""
        return 0.8  # Base accessibility score
    
    def _assess_creativity(self, plan: ActionPlan) -> float:
        """Assess creativity for creation goals."""
        # Creative steps improve creativity
        creative_steps = sum(1 for step in plan.steps if step.get("type") == "llm")
        return min(1.0, 0.4 + 0.15 * creative_steps)
    
    def _assess_usefulness(self, plan: ActionPlan) -> float:
        """Assess usefulness of created content."""
        return 0.7  # Base usefulness score
    
    def _assess_originality(self, plan: ActionPlan) -> float:
        """Assess originality of the plan."""
        return 0.6  # Base originality score
    
    def _assess_analysis_depth(self, plan: ActionPlan) -> float:
        """Assess depth of analysis."""
        # More analysis steps indicate deeper analysis
        analysis_steps = sum(1 for step in plan.steps if step.get("type") == "llm")
        return min(1.0, 0.4 + 0.15 * analysis_steps)
    
    def _assess_analysis_accuracy(self, plan: ActionPlan) -> float:
        """Assess accuracy of analysis."""
        return 0.7  # Base accuracy score
    
    def _assess_insight_potential(self, plan: ActionPlan) -> float:
        """Assess potential for generating insights."""
        return 0.6  # Base insight potential
    
    def _assess_actionability(self, plan: ActionPlan) -> float:
        """Assess actionability of the plan."""
        return 0.7  # Base actionability score
    
    def _assess_feasibility(self, plan: ActionPlan) -> float:
        """Assess feasibility of the plan."""
        # Simpler plans are more feasible
        if len(plan.steps) <= 4:
            return 0.8
        else:
            return 0.6
    
    def _assess_efficiency(self, plan: ActionPlan) -> float:
        """Assess efficiency of the plan."""
        # Lower spend indicates higher efficiency
        spend = plan.estimates.get("spend", 0.5)
        return max(0.0, 1.0 - spend)
    
    def _assess_robustness(self, plan: ActionPlan) -> float:
        """Assess robustness of the plan."""
        # More steps can indicate robustness
        return min(1.0, 0.5 + 0.1 * len(plan.steps))
    
    def _assess_effectiveness(self, plan: ActionPlan) -> float:
        """Assess effectiveness of tool usage."""
        return 0.7  # Base effectiveness score
    
    def _assess_reliability(self, plan: ActionPlan) -> float:
        """Assess reliability of the plan."""
        return 0.7  # Base reliability score
    
    def _assess_safety(self, plan: ActionPlan) -> float:
        """Assess safety of the plan."""
        # Lower risk indicates higher safety
        risk = plan.estimates.get("risk", 0.5)
        return max(0.0, 1.0 - risk)
    
    def _generate_utility_explanation(self, G: float, Q: float, R: float, S: float,
                                    weights: Dict[str, float], utility: float) -> str:
        """Generate explanation for utility score."""
        explanations = []
        
        if G > 0.7:
            explanations.append("high goal satisfaction")
        elif G < 0.4:
            explanations.append("low goal satisfaction")
        
        if Q > 0.7:
            explanations.append("high quality")
        elif Q < 0.4:
            explanations.append("low quality")
        
        if R > 0.6:
            explanations.append("high risk")
        elif R < 0.3:
            explanations.append("low risk")
        
        if S > 0.7:
            explanations.append("high resource cost")
        elif S < 0.3:
            explanations.append("low resource cost")
        
        if utility > 0.7:
            overall = "high utility"
        elif utility > 0.4:
            overall = "moderate utility"
        else:
            overall = "low utility"
        
        if explanations:
            return f"{overall} due to {', '.join(explanations)}"
        else:
            return f"{overall} with balanced characteristics"