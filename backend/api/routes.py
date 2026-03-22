"""
API routes for The Strategist Agent.

Exposes HTTP endpoints that Person 1's Orchestrator (or any client)
can call to access FIRE planning and life event advisory.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models.profile import UserProfile, FireGoal
from agent.strategist import StrategistAgent

router = APIRouter(prefix="/strategist", tags=["Strategist Agent"])
agent = StrategistAgent()


# ---------- Request / Response Schemas ----------

class FirePlanRequest(BaseModel):
    """Request body for FIRE plan generation."""
    profile: UserProfile
    goal: FireGoal


class LifeEventRequest(BaseModel):
    """Request body for life event advisory."""
    profile: UserProfile
    event_text: str = Field(
        ...,
        description="Free-text description of the life event",
        min_length=5,
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    agent: str = "The Strategist"
    version: str = "1.0.0"


# ---------- Endpoints ----------

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@router.post("/fire-plan")
async def create_fire_plan(request: FirePlanRequest):
    """
    Generate a complete FIRE (Financial Independence, Retire Early) plan.

    Takes the user's financial profile and FIRE goal parameters,
    computes projections, and returns a roadmap with LLM narrative.
    """
    try:
        result = agent.plan_fire_path(
            profile=request.profile,
            goal=request.goal,
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"FIRE plan generation failed: {str(exc)}",
        )


@router.post("/life-event")
async def advise_life_event(request: LifeEventRequest):
    """
    Get personalised financial advice for a life event.

    Takes the user's financial profile and a free-text event description,
    classifies the event, and returns structured + narrative advice.
    """
    try:
        advice = agent.advise_on_event(
            profile=request.profile,
            event_text=request.event_text,
        )
        return advice.model_dump()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Life event advisory failed: {str(exc)}",
        )
