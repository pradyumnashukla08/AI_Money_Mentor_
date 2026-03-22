"""
User profile and risk tolerance models for The Strategist Agent.

These schemas define the core data structures used across FIRE planning
and life event advisory workflows.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RiskTolerance(str, Enum):
    """Investment risk appetite classification."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class LifeStage(str, Enum):
    """Current life stage of the user."""
    STUDENT = "student"
    EARLY_CAREER = "early_career"
    MID_CAREER = "mid_career"
    PRE_RETIREMENT = "pre_retirement"
    RETIRED = "retired"


class UserProfile(BaseModel):
    """
    Captures the financial snapshot of a user.
    All monetary values are in INR (Indian Rupees).
    """
    name: str = Field(..., description="User's display name")
    age: int = Field(..., ge=18, le=100, description="Current age in years")
    monthly_income: float = Field(
        ..., gt=0, description="Gross monthly income in INR"
    )
    monthly_expenses: float = Field(
        ..., gt=0, description="Total monthly expenses in INR"
    )
    current_savings: float = Field(
        default=0.0, ge=0,
        description="Total current savings / investments in INR"
    )
    existing_monthly_sip: float = Field(
        default=0.0, ge=0,
        description="Monthly SIP amount already being invested in INR"
    )
    risk_tolerance: RiskTolerance = Field(
        default=RiskTolerance.MODERATE,
        description="Investment risk appetite"
    )
    life_stage: LifeStage = Field(
        default=LifeStage.EARLY_CAREER,
        description="Current life stage"
    )

    @property
    def monthly_surplus(self) -> float:
        """Disposable income available after expenses."""
        return self.monthly_income - self.monthly_expenses

    @property
    def annual_expenses(self) -> float:
        """Annualised expenses for FIRE calculations."""
        return self.monthly_expenses * 12

    @property
    def savings_rate(self) -> float:
        """Percentage of income being saved."""
        if self.monthly_income == 0:
            return 0.0
        return (self.monthly_surplus / self.monthly_income) * 100


class FireGoal(BaseModel):
    """
    FIRE (Financial Independence, Retire Early) goal parameters.
    """
    target_retirement_age: int = Field(
        ..., ge=25, le=80,
        description="Age at which the user wants to achieve FIRE"
    )
    desired_monthly_expense: float = Field(
        ..., gt=0,
        description="Monthly expense the user wants in retirement (today's INR)"
    )
    withdrawal_rate: float = Field(
        default=0.04, gt=0, lt=0.15,
        description="Annual withdrawal rate from corpus (e.g., 0.04 = 4%%)"
    )
    expected_return_rate: float = Field(
        default=0.12, gt=0, lt=0.30,
        description="Expected annual return on investments"
    )
    inflation_rate: float = Field(
        default=0.06, gt=0, lt=0.20,
        description="Expected annual inflation rate"
    )
