"""
router.py — FastAPI router for the Money Health Score module.

Endpoints:
  POST /api/health-score/calculate     → Submit quiz answers, get full health score
  GET  /api/health-score/questions     → Return all onboarding questions
  GET  /api/health-score/health        → Module health check
"""

import logging
from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from auditor_agent.health_score.onboarding_schema import (
    ONBOARDING_QUESTIONS,
    OnboardingAnswers,
)
from auditor_agent.health_score.scorer import calculate_health_score, HealthScoreResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health-score", tags=["Money Health Score"])


# ── Helper: convert result dataclass to JSON-safe dict ─────────────────────

def _result_to_dict(result: HealthScoreResult) -> dict:
    return {
        "name": result.name,
        "overall_score": result.overall_score,
        "overall_band_label": result.overall_band_label,
        "overall_band_color": result.overall_band_color,
        "executive_summary": result.executive_summary,
        "actionable_roadmap": result.actionable_roadmap,
        "top_strengths": result.top_strengths,
        "top_concerns": result.top_concerns,
        "dimension_scores": [
            {
                "dimension": d.dimension,
                "score": d.score,
                "band_label": d.band_label,
                "band_color": d.band_color,
                "weight": d.weight,
                "weighted_contribution": d.weighted_contribution,
                "insight": d.insight,
            }
            for d in result.dimension_scores
        ],
    }


# ── GET /api/health-score/questions ────────────────────────────────────────

@router.get("/questions", summary="Fetch all onboarding questions")
async def get_questions():
    """
    Returns the full list of onboarding questions with their options.
    Use this to dynamically render the quiz in your frontend.
    """
    questions = [
        {
            "id": q.id,
            "dimension": q.dimension.value,
            "text": q.text,
            "options": q.options,
        }
        for q in ONBOARDING_QUESTIONS
    ]
    return JSONResponse(content={"questions": questions, "total": len(questions)})


# ── POST /api/health-score/calculate ───────────────────────────────────────

@router.post("/calculate", summary="Submit quiz answers and get your Money Health Score")
async def calculate(payload: OnboardingAnswers):
    """
    Submit your onboarding quiz answers and receive a personalised
    Money Health Score across 6 financial dimensions with AI-generated insights.

    - **answers**: dict mapping question_id → selected_option_index (0-based)
    - **name**: Optional first name for personalised tips
    - **monthly_income**: Optional monthly take-home income in ₹
    - **age**: Optional age for context-aware insights
    """
    try:
        result = calculate_health_score(payload)
        return JSONResponse(content={
            "status": "success",
            "health_score": _result_to_dict(result),
        })
    except Exception as exc:
        logger.error("Health score calculation error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(exc)}")


# ── GET /api/health-score/health ───────────────────────────────────────────

@router.get("/health", summary="Health check for Money Health Score module")
async def health_check():
    return {"status": "ok", "module": "Money Health Score", "version": "1.0.0"}
