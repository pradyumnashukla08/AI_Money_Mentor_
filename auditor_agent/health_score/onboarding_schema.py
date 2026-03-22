"""
onboarding_schema.py — Defines the 15-question Money Health Score onboarding quiz.

6 Dimensions:
  1. Emergency Fund
  2. Debt Management
  3. Insurance Coverage
  4. Investments & Savings
  5. Goal Clarity
  6. Spending Habits

Each question maps to a dimension and has a weight.
Answers are scored 0–100 per dimension, then aggregated into an overall score.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Dimension definitions ───────────────────────────────────────────────────

class Dimension(str, Enum):
    EMERGENCY_FUND = "Emergency Fund"
    DEBT_MANAGEMENT = "Debt Management"
    INSURANCE = "Insurance Coverage"
    INVESTMENTS = "Investments & Savings"
    GOAL_CLARITY = "Goal Clarity"
    SPENDING_HABITS = "Spending Habits"


# Dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS = {
    Dimension.EMERGENCY_FUND: 0.20,
    Dimension.DEBT_MANAGEMENT: 0.20,
    Dimension.INSURANCE:       0.15,
    Dimension.INVESTMENTS:     0.25,
    Dimension.GOAL_CLARITY:    0.10,
    Dimension.SPENDING_HABITS: 0.10,
}

# Ideal colour coding thresholds
SCORE_BANDS = {
    (80, 100): ("Excellent 🟢", "#2ecc71"),
    (60, 79):  ("Good 🟡",      "#f1c40f"),
    (40, 59):  ("Fair 🟠",      "#e67e22"),
    (0, 39):   ("Needs Work 🔴","#e74c3c"),
}


def get_score_band(score: float):
    for (lo, hi), (label, color) in SCORE_BANDS.items():
        if lo <= score <= hi:
            return label, color
    return "Needs Work 🔴", "#e74c3c"


# ── Onboarding questions ────────────────────────────────────────────────────

class Question(BaseModel):
    """A single onboarding question."""
    id: str
    dimension: Dimension
    text: str
    options: List[str]        # Human-readable answer options
    score_map: List[int]      # Score (0-100) for each option in the same order
    weight: float = 1.0       # Relative weight within the dimension


ONBOARDING_QUESTIONS: List[Question] = [

    # ── Dimension 1: Emergency Fund ─────────────────────────────────────────
    Question(
        id="ef_1",
        dimension=Dimension.EMERGENCY_FUND,
        text="How many months of living expenses do you have saved as an emergency fund?",
        options=[
            "I have no emergency fund",
            "Less than 1 month",
            "1–2 months",
            "3–5 months",
            "6 months or more"
        ],
        score_map=[0, 15, 35, 70, 100],
        weight=1.5,
    ),
    Question(
        id="ef_2",
        dimension=Dimension.EMERGENCY_FUND,
        text="Where is your emergency fund held?",
        options=[
            "I don't have one",
            "In my savings account (mixed with daily expenses)",
            "In a separate savings account",
            "In a liquid mutual fund or sweep FD"
        ],
        score_map=[0, 30, 60, 100],
        weight=0.8,
    ),
    Question(
        id="ef_3",
        dimension=Dimension.EMERGENCY_FUND,
        text="If you lost your primary income source today, for how long could you sustain your current lifestyle?",
        options=[
            "Less than a month",
            "1–3 months",
            "3–6 months",
            "More than 6 months"
        ],
        score_map=[0, 25, 60, 100],
        weight=1.0,
    ),

    # ── Dimension 2: Debt Management ────────────────────────────────────────
    Question(
        id="dm_1",
        dimension=Dimension.DEBT_MANAGEMENT,
        text="What percentage of your monthly take-home income goes towards EMIs?",
        options=[
            "More than 50%",
            "36%–50%",
            "21%–35%",
            "10%–20%",
            "Less than 10% or no EMIs"
        ],
        score_map=[0, 20, 45, 70, 100],
        weight=1.5,
    ),
    Question(
        id="dm_2",
        dimension=Dimension.DEBT_MANAGEMENT,
        text="Do you have any high-interest unsecured debt (credit card dues, personal loans)?",
        options=[
            "Yes, and I am struggling to pay it off",
            "Yes, but I am paying minimum dues each month",
            "Yes, but I have a clear plan to eliminate it within 12 months",
            "No unsecured high-interest debt"
        ],
        score_map=[0, 20, 60, 100],
        weight=1.2,
    ),

    # ── Dimension 3: Insurance Coverage ─────────────────────────────────────
    Question(
        id="ins_1",
        dimension=Dimension.INSURANCE,
        text="What is your total health insurance cover (including employer + personal policy)?",
        options=[
            "No coverage",
            "Less than ₹3 Lakh",
            "₹3–5 Lakh",
            "₹5–10 Lakh",
            "More than ₹10 Lakh"
        ],
        score_map=[0, 20, 45, 75, 100],
        weight=1.2,
    ),
    Question(
        id="ins_2",
        dimension=Dimension.INSURANCE,
        text="Do you have a pure term life insurance policy?",
        options=[
            "No, I have no life insurance",
            "Only employer-provided group cover",
            "Yes, with coverage less than 10x my annual income",
            "Yes, with coverage 10x or more of my annual income"
        ],
        score_map=[0, 25, 60, 100],
        weight=1.0,
    ),
    Question(
        id="ins_3",
        dimension=Dimension.INSURANCE,
        text="Does your health insurance policy cover critical illness or have a super top-up?",
        options=[
            "No",
            "I am not sure",
            "Yes, partial critical illness cover",
            "Yes, comprehensive critical illness and super top-up"
        ],
        score_map=[10, 30, 65, 100],
        weight=0.8,
    ),

    # ── Dimension 4: Investments & Savings ──────────────────────────────────
    Question(
        id="inv_1",
        dimension=Dimension.INVESTMENTS,
        text="What percentage of your monthly income do you invest or save?",
        options=[
            "I am not able to save right now",
            "Less than 5%",
            "5%–15%",
            "16%–25%",
            "More than 25%"
        ],
        score_map=[0, 15, 45, 75, 100],
        weight=1.5,
    ),
    Question(
        id="inv_2",
        dimension=Dimension.INVESTMENTS,
        text="How would you describe your current investment portfolio?",
        options=[
            "All in savings account / FDs",
            "Mostly FDs with some mutual funds",
            "Mix of equity mutual funds, debt, and FDs",
            "Well-diversified: equity, debt, gold, and real estate"
        ],
        score_map=[10, 35, 70, 100],
        weight=1.2,
    ),
    Question(
        id="inv_3",
        dimension=Dimension.INVESTMENTS,
        text="Do you have active SIPs (Systematic Investment Plans)?",
        options=[
            "No",
            "Yes, less than ₹2,000/month",
            "Yes, ₹2,000–₹10,000/month",
            "Yes, more than ₹10,000/month"
        ],
        score_map=[0, 30, 65, 100],
        weight=1.0,
    ),

    # ── Dimension 5: Goal Clarity ────────────────────────────────────────────
    Question(
        id="gc_1",
        dimension=Dimension.GOAL_CLARITY,
        text="Do you have clearly defined financial goals with specific target amounts and timelines?",
        options=[
            "I have no specific goals",
            "I have vague goals but no written plan",
            "I have 1–2 goals with rough timelines",
            "I have multiple goals with defined amounts, timelines, and investment plans"
        ],
        score_map=[0, 25, 60, 100],
        weight=1.2,
    ),
    Question(
        id="gc_2",
        dimension=Dimension.GOAL_CLARITY,
        text="Are you investing / saving specifically for retirement?",
        options=[
            "No, not yet",
            "I contribute to EPF only",
            "EPF + NPS or PPF",
            "EPF/NPS + dedicated mutual fund portfolio for retirement"
        ],
        score_map=[0, 30, 65, 100],
        weight=1.0,
    ),

    # ── Dimension 6: Spending Habits ─────────────────────────────────────────
    Question(
        id="sh_1",
        dimension=Dimension.SPENDING_HABITS,
        text="Do you track your monthly spending and have a budget?",
        options=[
            "No, I spend freely and have no idea where money goes",
            "I roughly know but don't track",
            "I track occasionally",
            "Yes, I follow a structured budget every month"
        ],
        score_map=[0, 25, 55, 100],
        weight=1.2,
    ),
    Question(
        id="sh_2",
        dimension=Dimension.SPENDING_HABITS,
        text="Have your lifestyle expenses (dining out, subscriptions, travel) grown significantly faster than your income over the past 2 years?",
        options=[
            "Yes, much faster than income",
            "Somewhat — moderate lifestyle inflation",
            "Roughly in line with income growth",
            "No — I maintain spending discipline"
        ],
        score_map=[0, 30, 65, 100],
        weight=1.0,
    ),
]


# ── Onboarding input model (API request body) ───────────────────────────────

class OnboardingAnswers(BaseModel):
    """
    Maps each question ID to the index of the selected answer option (0-based).
    Example: {"ef_1": 4, "ef_2": 3, ...}
    """
    answers: dict = Field(
        ...,
        description="Dict mapping question_id -> selected_option_index (0-based)",
        example={
            "ef_1": 3, "ef_2": 2, "ef_3": 2,
            "dm_1": 3, "dm_2": 3,
            "ins_1": 3, "ins_2": 3, "ins_3": 1,
            "inv_1": 2, "inv_2": 2, "inv_3": 2,
            "gc_1": 2, "gc_2": 1,
            "sh_1": 2, "sh_2": 1,
        }
    )
    name: Optional[str] = Field(default="User", description="User's first name for personalisation")
    monthly_income: Optional[float] = Field(default=None, description="Monthly take-home income (₹)")
    age: Optional[int] = Field(default=None, description="User's age in years")
