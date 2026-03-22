"""
scorer.py — Money Health Score calculation engine.

Computes a 0–100 wellness score across 6 financial dimensions,
using weighted aggregation and LLM-generated personalised insights.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from groq import Groq

from auditor_agent.config import settings
from auditor_agent.health_score.onboarding_schema import (
    DIMENSION_WEIGHTS,
    ONBOARDING_QUESTIONS,
    Dimension,
    OnboardingAnswers,
    get_score_band,
)

logger = logging.getLogger(__name__)


# ── Result types ────────────────────────────────────────────────────────────

@dataclass
class DimensionScore:
    """Score and analysis for a single dimension."""
    dimension: str
    score: float                   # 0–100
    band_label: str                # "Excellent 🟢" etc.
    band_color: str                # Hex color
    weight: float                  # Share in composite score
    weighted_contribution: float   # score × weight
    insight: str                   # LLM-generated tip


@dataclass
class HealthScoreResult:
    """Overall Money Health Score with dimension breakdown."""
    name: str
    overall_score: float
    overall_band_label: str
    overall_band_color: str
    dimension_scores: List[DimensionScore]
    top_strengths: List[str]        # Names of top 2 dimensions
    top_concerns: List[str]         # Names of bottom 2 dimensions
    executive_summary: str          # 3–4 sentence LLM summary


# ── Scoring helpers ─────────────────────────────────────────────────────────

def _compute_dimension_raw_scores(answers: OnboardingAnswers) -> Dict[Dimension, float]:
    """
    For each dimension, compute a weighted average score (0–100)
    based on the user's selected answer options.
    """
    dimension_totals: Dict[Dimension, float] = {d: 0.0 for d in Dimension}
    dimension_weights: Dict[Dimension, float] = {d: 0.0 for d in Dimension}

    question_map = {q.id: q for q in ONBOARDING_QUESTIONS}

    for q_id, option_index in answers.answers.items():
        question = question_map.get(q_id)
        if question is None:
            logger.warning("Unknown question ID '%s' — skipping.", q_id)
            continue

        # Guard against out-of-range selections
        if not (0 <= option_index < len(question.score_map)):
            logger.warning("Invalid option index %d for question '%s' — using 0.", option_index, q_id)
            option_index = 0

        raw_score = question.score_map[option_index]
        dimension_totals[question.dimension] += raw_score * question.weight
        dimension_weights[question.dimension] += question.weight

    # Compute weighted average per dimension
    dim_scores: Dict[Dimension, float] = {}
    for dim in Dimension:
        total_weight = dimension_weights[dim]
        if total_weight > 0:
            dim_scores[dim] = min(100.0, dimension_totals[dim] / total_weight)
        else:
            dim_scores[dim] = 50.0  # Default if dimension has no questions answered

    return dim_scores


def _generate_insights_with_llm(
    name: str,
    dimension_scores: Dict[Dimension, float],
    monthly_income: Optional[float],
    age: Optional[int],
) -> Tuple[Dict[Dimension, str], str]:
    """
    Use Groq LLM to generate:
    - A 2-sentence personalised insight for each dimension
    - A 3–4 sentence executive summary of the user's financial health

    Returns (dimension_insights dict, executive_summary string)
    """
    client = Groq(api_key=settings.GROQ_API_KEY)

    scores_text = "\n".join(
        f"  - {dim.value}: {score:.0f}/100"
        for dim, score in dimension_scores.items()
    )
    context_parts = [f"User name: {name}"]
    if age:
        context_parts.append(f"Age: {age} years")
    if monthly_income:
        context_parts.append(f"Monthly income: ₹{monthly_income:,.0f}")

    context = ", ".join(context_parts)

    system_prompt = """You are a warm, empathetic Indian personal finance advisor.
Write concise, practical, and encouraging financial insights.
Use simple language — avoid jargon. Always personalise with the user's name.
Refer to Indian financial instruments (EPF, PPF, NPS, ELSS, FD, SIP).
Format: Return ONLY a valid JSON object with keys for each dimension and an 'executive_summary' key.
All values must be plain strings. Do not use markdown inside the strings."""

    user_prompt = f"""Context: {context}

Financial Health Score Breakdown:
{scores_text}

Please generate:
1. A 2-sentence insight for each of these 6 dimensions: Emergency Fund, Debt Management, Insurance Coverage, Investments & Savings, Goal Clarity, Spending Habits
2. A 3-4 sentence executive summary of this person's overall financial health.

Return ONLY this JSON (no markdown, no code fences):
{{
  "Emergency Fund": "...",
  "Debt Management": "...",
  "Insurance Coverage": "...",
  "Investments & Savings": "...",
  "Goal Clarity": "...",
  "Spending Habits": "...",
  "executive_summary": "..."
}}"""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()

        import json, re
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            raise ValueError("LLM did not return JSON")

        data = json.loads(json_match.group())

        dim_insights = {
            Dimension.EMERGENCY_FUND:  data.get("Emergency Fund", "Focus on building your emergency cushion."),
            Dimension.DEBT_MANAGEMENT: data.get("Debt Management", "Work on reducing high-interest debt first."),
            Dimension.INSURANCE:       data.get("Insurance Coverage", "Ensure adequate health and term cover."),
            Dimension.INVESTMENTS:     data.get("Investments & Savings", "Start or increase your SIP contributions."),
            Dimension.GOAL_CLARITY:    data.get("Goal Clarity", "Define your financial goals with clear timelines."),
            Dimension.SPENDING_HABITS: data.get("Spending Habits", "Track spending and maintain a monthly budget."),
        }
        summary = data.get("executive_summary", f"{name}, your financial health has room to grow. Focus on the areas highlighted above.")

        return dim_insights, summary

    except Exception as exc:
        logger.error("LLM insight generation failed: %s", exc)
        default_insights = {
            Dimension.EMERGENCY_FUND:  "Build an emergency fund covering 6 months of expenses in a liquid fund.",
            Dimension.DEBT_MANAGEMENT: "Aim to keep EMIs below 30% of take-home pay and eliminate credit card rollovers.",
            Dimension.INSURANCE:       "Ensure ₹10L+ health cover and a term plan with 10× annual income coverage.",
            Dimension.INVESTMENTS:     "Automate investing with SIPs; target saving at least 20% of monthly income.",
            Dimension.GOAL_CLARITY:    "Write down goals with specific rupee amounts and target dates.",
            Dimension.SPENDING_HABITS: "Use a budgeting app or a simple 50-30-20 rule to control lifestyle inflation.",
        }
        fallback_summary = (
            f"{name}, your financial wellness score reflects your current financial habits. "
            "Focus on strengthening your weakest dimensions first for maximum impact. "
            "Small, consistent improvements compound significantly over time."
        )
        return default_insights, fallback_summary


# ── Master scorer ────────────────────────────────────────────────────────────

def calculate_health_score(answers: OnboardingAnswers) -> HealthScoreResult:
    """
    Primary function: Compute Money Health Score from onboarding answers.

    Args:
        answers: OnboardingAnswers with question_id → option_index mapping.

    Returns:
        HealthScoreResult with full breakdown and AI-generated insights.
    """
    name = answers.name or "User"

    # Step 1: Compute raw dimension scores (0–100)
    dim_scores = _compute_dimension_raw_scores(answers)

    # Step 2: Generate LLM insights per dimension
    dim_insights, executive_summary = _generate_insights_with_llm(
        name=name,
        dimension_scores=dim_scores,
        monthly_income=answers.monthly_income,
        age=answers.age,
    )

    # Step 3: Build DimensionScore objects + weighted composite
    sorted_dims = sorted(dim_scores.items(), key=lambda x: -x[1])
    dimension_result_list: List[DimensionScore] = []
    overall_weighted_sum = 0.0

    for dim, score in dim_scores.items():
        weight = DIMENSION_WEIGHTS[dim]
        weighted_contribution = score * weight
        overall_weighted_sum += weighted_contribution
        band_label, band_color = get_score_band(score)

        dimension_result_list.append(DimensionScore(
            dimension=dim.value,
            score=round(score, 1),
            band_label=band_label,
            band_color=band_color,
            weight=weight,
            weighted_contribution=round(weighted_contribution, 2),
            insight=dim_insights.get(dim, ""),
        ))

    overall_score = round(overall_weighted_sum, 1)
    overall_band_label, overall_band_color = get_score_band(overall_score)

    # Step 4: Identify top strengths and concerns
    dims_sorted_by_score = sorted(
        dimension_result_list, key=lambda d: d.score, reverse=True
    )
    top_strengths = [d.dimension for d in dims_sorted_by_score[:2]]
    top_concerns  = [d.dimension for d in dims_sorted_by_score[-2:]]

    logger.info("Health score computed for %s: %.1f (%s)", name, overall_score, overall_band_label)

    return HealthScoreResult(
        name=name,
        overall_score=overall_score,
        overall_band_label=overall_band_label,
        overall_band_color=overall_band_color,
        dimension_scores=dimension_result_list,
        top_strengths=top_strengths,
        top_concerns=top_concerns,
        executive_summary=executive_summary,
    )
