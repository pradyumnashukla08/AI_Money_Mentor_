"""
Life event models for The Strategist Agent.

Defines the taxonomy of major life events that trigger
personalised financial advice.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LifeEventType(str, Enum):
    """Categories of major life events that impact financial planning."""
    BONUS = "bonus"
    MARRIAGE = "marriage"
    NEW_BABY = "new_baby"
    JOB_LOSS = "job_loss"
    HOME_PURCHASE = "home_purchase"
    INHERITANCE = "inheritance"
    SALARY_HIKE = "salary_hike"
    MEDICAL_EMERGENCY = "medical_emergency"
    EDUCATION = "education"
    RELOCATION = "relocation"
    BUSINESS_START = "business_start"
    OTHER = "other"


class LifeEvent(BaseModel):
    """
    Represents a specific life event reported by the user.
    """
    event_type: LifeEventType = Field(
        ..., description="Classified category of the life event"
    )
    description: str = Field(
        ..., description="User's original description of the event"
    )
    amount: Optional[float] = Field(
        default=None, ge=0,
        description="Monetary value associated with the event in INR (if any)"
    )


class LifeEventAdvice(BaseModel):
    """
    Structured advice output for a life event.
    """
    event: LifeEvent = Field(
        ..., description="The classified life event"
    )
    risk_assessment: str = Field(
        ..., description="How this event interacts with the user's risk profile"
    )
    immediate_actions: list[str] = Field(
        default_factory=list,
        description="Actions to take within the next 30 days"
    )
    short_term_plan: list[str] = Field(
        default_factory=list,
        description="Actions to take within the next 3-6 months"
    )
    long_term_impact: str = Field(
        default="",
        description="How this event changes the user's long-term financial trajectory"
    )
    narrative: str = Field(
        default="",
        description="LLM-generated personalised advice narrative"
    )
