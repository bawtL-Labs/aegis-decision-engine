"""
Updated Utility Engine for the S.A.M. Decision Engine.

Integrates with PMX for personality-aware weight calculation and provides
enhanced utility scoring with factor breakdowns.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any

from ..models import (
    ActionPlan, 
    MaturityLevel, 
    PersonalityInfluence,
    PersonalityWeights,
    DecodingMode
)

logger = logging.getLogger(__name__)


class UtilityEngine:
    """
    Enhanced utility engine with personality-aware scoring.
    
    Integrates with PMX for personality influence and provides detailed
    factor breakdowns for decision traces.
    """
    
    def __init__(self):
        """Initialize the utility engine."""
        # Base weights for different maturity levels
        self.maturity_weights = {
            MaturityLevel.INFANT: {
                "goal": 0.4,      # High goal focus, conservative
                "quality": 0.3,   # Good quality important
                "risk": 0.2,      # Risk averse
                "spend": 0.1,     # Low resource concern
                "novelty": 0.1,   # Low novelty preference
                "rigor": 0.8,     # High rigor preference
                "safety": 0.9     # High safety preference
            },
            MaturityLevel.CHILD: {
                "goal": 0.35,     # Still goal-focused
                "quality": 0.3,   # Maintain quality
                "risk": 0.2,      # Still risk averse
                "spend": 0.15,    # Some resource awareness
                "novelty": 0.2,   # Some novelty exploration
                "rigor": 0.7,     # Good rigor preference
                "safety": 0.8     # High safety preference
            },
            MaturityLevel.ADOLESCENT: {
                "goal": 0.3,      # Balanced approach
                "quality": 0.3,   # Quality maintained
                "risk": 0.2,      # Moderate risk tolerance
                "spend": 0.2,     # Resource efficiency important
                "novelty": 0.4,   # Moderate novelty preference
                "rigor": 0.6,     # Moderate rigor preference
                "safety": 0.7     # Moderate safety preference
            },
            MaturityLevel.ADULT: {
                "goal": 0.25,     # Efficient goal achievement
                "quality": 0.3,   # Quality standard
                "risk": 0.2,      # Calculated risk taking
                "spend": 0.25,    # Resource optimization
                "novelty": 0.6,   # High novelty preference
                "rigor": 0.5,     # Balanced rigor preference
                "safety": 0.6     # Balanced safety preference
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
        
        logger.info("Enhanced utility engine initialized")
    
    def calculate_utility(self, 
                         plan: ActionPlan,
                         maturity_level: MaturityLevel,
                         personality_influence: Optional[PersonalityInfluence] = None,
                         pmx: Optional[Any] = None,
                         context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Calculate utility score with personality-aware weights and factor breakdown.
        
        Args:
            plan: The action plan to score
            maturity_level: Current maturity level
            personality_influence: Personality traits that influence scoring
            pmx: PMX object for personality matrix integration
            context: Additional context for scoring
            
        Returns:
            Dictionary with utility components, weights, and factor breakdown
        """
        # Get personality-aware weights
        weights = self._get_weights(maturity_level, personality_influence, pmx, context)
        
        # Calculate components
        G = self._calculate_goal_satisfaction(plan, context)
        Q = self._calculate_quality(plan, context)
        R = self._calculate_risk(plan, context)
        S = self._calculate_spend(plan, context)
        
        # Calculate utility
        utility = (weights.goal * G + 
                  weights.quality * Q - 
                  weights.risk * R - 
                  weights.spend * S)
        
        # Ensure utility is bounded
        utility = max(0.0, min(1.0, utility))
        
        # Create factor breakdown
        factor_breakdown = {
            "goal_satisfaction": {
                "value": G,
                "weight": weights.goal,
                "contribution": weights.goal * G
            },
            "quality": {
                "value": Q,
                "weight": weights.quality,
                "contribution": weights.quality * Q
            },
            "risk": {
                "value": R,
                "weight": weights.risk,
                "contribution": -weights.risk * R
            },
            "spend": {
                "value": S,
                "weight": weights.spend,
                "contribution": -weights.spend * S
            },
            "personality_factors": {
                "novelty": weights.novelty,
                "rigor": weights.rigor,
                "safety": weights.safety
            }
        }
        
        return {
            "utility": utility,
            "components": {
                "goal_satisfaction": G,
                "quality": Q,
                "risk": R,
                "spend": S
            },
            "weights": weights,
            "factor_breakdown": factor_breakdown,
            "explanation": self._generate_utility_explanation(G, Q, R, S, weights, utility)
        }
    
    def _get_weights(self, maturity_level: MaturityLevel, 
                    personality_influence: Optional[PersonalityInfluence] = None,
                    pmx: Optional[Any] = None,
                    context: Optional[Dict] = None) -> PersonalityWeights:
        """Get personality-aware utility weights with PMX integration."""
        base_weights = self.maturity_weights[maturity_level].copy()
        
        # Apply PMX personality matrix influence if available
        if pmx and hasattr(pmx, 'matrix') and hasattr(pmx.matrix, 'resolve_weights'):
            try:
                pmx_weights = pmx.matrix.resolve_weights()
                # Merge PMX weights with base weights
                for key, value in pmx_weights.items():
                    if key in base_weights:
                        base_weights[key] = (base_weights[key] + value) / 2
            except Exception as e:
                logger.warning(f"Failed to resolve PMX weights: {e}")
        
        # Apply personality influence adjustments
        if personality_influence:
            base_weights = self._adjust_weights_for_personality(base_weights, personality_influence)
        
        # Apply context-based adjustments
        if context:
            base_weights = self._adjust_weights_for_context(base_weights, context)
        
        # Create PersonalityWeights object
        return PersonalityWeights(
            goal=base_weights["goal"],
            quality=base_weights["quality"],
            risk=base_weights["risk"],
            spend=base_weights["spend"],
            novelty=base_weights["novelty"],
            rigor=base_weights["rigor"],
            safety=base_weights["safety"]
        )
    
    def _adjust_weights_for_personality(self, weights: Dict[str, float], 
                                      personality: PersonalityInfluence) -> Dict[str, float]:
        """Adjust utility weights based on personality traits."""
        adjusted_weights = weights.copy()
        
        # Analytical personality values quality and rigor more
        if personality.analytical > 0.7:
            adjusted_weights["quality"] *= 1.2
            adjusted_weights["rigor"] *= 1.3
            adjusted_weights["goal"] *= 0.9
            adjusted_weights["novelty"] *= 0.8
        
        # Creative personality values novelty and goal achievement
        if personality.creativity > 0.7:
            adjusted_weights["goal"] *= 1.1
            adjusted_weights["novelty"] *= 1.4
            adjusted_weights["quality"] *= 1.1
            adjusted_weights["spend"] *= 0.9
            adjusted_weights["rigor"] *= 0.8
        
        # Social personality may value different aspects
        if personality.social > 0.7:
            adjusted_weights["goal"] *= 1.05
            adjusted_weights["spend"] *= 0.95
            adjusted_weights["safety"] *= 1.1
        
        # Assertive personality may be more risk-tolerant
        if personality.assertiveness > 0.7:
            adjusted_weights["risk"] *= 0.8
            adjusted_weights["goal"] *= 1.05
            adjusted_weights["safety"] *= 0.9
        
        # Patient personality may value quality and rigor over speed
        if personality.patience > 0.7:
            adjusted_weights["quality"] *= 1.1
            adjusted_weights["rigor"] *= 1.2
            adjusted_weights["spend"] *= 0.9
            adjusted_weights["novelty"] *= 0.9
        
        # Normalize weights to reasonable ranges
        for key in adjusted_weights:
            adjusted_weights[key] = max(0.0, min(1.0, adjusted_weights[key]))
        
        return adjusted_weights
    
    def _adjust_weights_for_context(self, weights: Dict[str, float], 
                                  context: Dict[str, Any]) -> Dict[str, float]:
        """Adjust weights based on context requirements."""
        adjusted_weights = weights.copy()
        
        # High-stakes context increases safety and quality
        if context.get("high_stakes"):
            adjusted_weights["safety"] *= 1.3
            adjusted_weights["quality"] *= 1.2
            adjusted_weights["risk"] *= 0.7
        
        # Time-sensitive context increases spend tolerance
        if context.get("time_sensitive"):
            adjusted_weights["spend"] *= 1.2
            adjusted_weights["rigor"] *= 0.8
        
        # Creative context increases novelty preference
        if context.get("requires_creativity"):
            adjusted_weights["novelty"] *= 1.3
            adjusted_weights["goal"] *= 1.1
        
        # Analytical context increases rigor preference
        if context.get("requires_analysis"):
            adjusted_weights["rigor"] *= 1.3
            adjusted_weights["quality"] *= 1.2
        
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
    
    # Quality assessment methods (same as before)
    def _assess_answer_accuracy(self, plan: ActionPlan) -> float:
        """Assess accuracy for answer goals."""
        analysis_steps = sum(1 for step in plan.steps if step.get("type") == "llm")
        return min(1.0, 0.5 + 0.1 * analysis_steps)
    
    def _assess_completeness(self, plan: ActionPlan) -> float:
        """Assess completeness of the plan."""
        return min(1.0, 0.4 + 0.1 * len(plan.steps))
    
    def _assess_relevance(self, plan: ActionPlan, context: Optional[Dict] = None) -> float:
        """Assess relevance to the goal."""
        return 0.7
    
    def _assess_clarity(self, plan: ActionPlan) -> float:
        """Assess clarity of the plan."""
        if len(plan.steps) <= 5:
            return 0.8
        else:
            return 0.6
    
    def _assess_precision(self, plan: ActionPlan) -> float:
        """Assess precision for retrieval goals."""
        search_steps = sum(1 for step in plan.steps if step.get("type") == "tool")
        return min(1.0, 0.5 + 0.1 * search_steps)
    
    def _assess_recall(self, plan: ActionPlan) -> float:
        """Assess recall for retrieval goals."""
        return 0.7
    
    def _assess_freshness(self, plan: ActionPlan) -> float:
        """Assess freshness of retrieved information."""
        return 0.6
    
    def _assess_accessibility(self, plan: ActionPlan) -> float:
        """Assess accessibility of the plan."""
        return 0.8
    
    def _assess_creativity(self, plan: ActionPlan) -> float:
        """Assess creativity for creation goals."""
        creative_steps = sum(1 for step in plan.steps if step.get("type") == "llm")
        return min(1.0, 0.4 + 0.15 * creative_steps)
    
    def _assess_usefulness(self, plan: ActionPlan) -> float:
        """Assess usefulness of created content."""
        return 0.7
    
    def _assess_originality(self, plan: ActionPlan) -> float:
        """Assess originality of the plan."""
        return 0.6
    
    def _assess_analysis_depth(self, plan: ActionPlan) -> float:
        """Assess depth of analysis."""
        analysis_steps = sum(1 for step in plan.steps if step.get("type") == "llm")
        return min(1.0, 0.4 + 0.15 * analysis_steps)
    
    def _assess_analysis_accuracy(self, plan: ActionPlan) -> float:
        """Assess accuracy of analysis."""
        return 0.7
    
    def _assess_insight_potential(self, plan: ActionPlan) -> float:
        """Assess potential for generating insights."""
        return 0.6
    
    def _assess_actionability(self, plan: ActionPlan) -> float:
        """Assess actionability of the plan."""
        return 0.7
    
    def _assess_feasibility(self, plan: ActionPlan) -> float:
        """Assess feasibility of the plan."""
        if len(plan.steps) <= 4:
            return 0.8
        else:
            return 0.6
    
    def _assess_efficiency(self, plan: ActionPlan) -> float:
        """Assess efficiency of the plan."""
        spend = plan.estimates.get("spend", 0.5)
        return max(0.0, 1.0 - spend)
    
    def _assess_robustness(self, plan: ActionPlan) -> float:
        """Assess robustness of the plan."""
        return min(1.0, 0.5 + 0.1 * len(plan.steps))
    
    def _assess_effectiveness(self, plan: ActionPlan) -> float:
        """Assess effectiveness of tool usage."""
        return 0.7
    
    def _assess_reliability(self, plan: ActionPlan) -> float:
        """Assess reliability of the plan."""
        return 0.7
    
    def _assess_safety(self, plan: ActionPlan) -> float:
        """Assess safety of the plan."""
        risk = plan.estimates.get("risk", 0.5)
        return max(0.0, 1.0 - risk)
    
    def _generate_utility_explanation(self, G: float, Q: float, R: float, S: float,
                                    weights: PersonalityWeights, utility: float) -> str:
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