# pyre-ignore-all-errors
"""
FIRE (Financial Independence, Retire Early) calculations.

Computes target corpus, time to FIRE, coast FIRE numbers,
and generates detailed month-by-month roadmaps to financial independence.
"""

import numpy as np
from engine.compounding import (
    future_value,
    present_value_of_future_expense,
    real_return,
)


def fire_target_corpus(
    annual_expenses: float,
    withdrawal_rate: float = 0.04,
    inflation_rate: float = 0.06,
    years_to_retirement: int = 0,
) -> dict:
    """
    Calc the FIRE corpus based on SWR, optionally inflation adjusted.
    """
    if annual_expenses <= 0:
        raise ValueError("Annual expenses must be positive")
    if withdrawal_rate <= 0 or withdrawal_rate >= 1:
        raise ValueError("Withdrawal rate must be between 0 and 1")

    corpus_today = annual_expenses / withdrawal_rate

    # If retirement is in the future, account for inflation
    inflated_expense = present_value_of_future_expense(
        annual_expenses, inflation_rate, years_to_retirement
    )
    corpus_at_retirement = inflated_expense / withdrawal_rate

    return {
        "corpus_today": round(corpus_today, 2),  # pyre-ignore
        "corpus_at_retirement": round(corpus_at_retirement, 2),  # pyre-ignore
        "inflated_annual_expense": round(inflated_expense, 2),  # pyre-ignore
    }


def years_to_fire(
    current_savings: float,
    monthly_investment: float,
    annual_return: float,
    fire_corpus: float,
) -> float:
    """
    Estimate years to reach FIRE corpus via monthly simulation.
    """
    if fire_corpus <= current_savings:
        return 0.0

    monthly_rate = annual_return / 12
    corpus = current_savings
    months = 0

    while corpus < fire_corpus and months < 1200:  # Cap at 100 years
        corpus = (corpus + monthly_investment) * (1 + monthly_rate)
        months += 1

    return round(months / 12, 1)  # pyre-ignore


def coast_fire_number(
    target_corpus: float,
    annual_return: float,
    years_to_retirement: int,
) -> float:
    """
    Calculate Coast FIRE number (corpus needed today to reach goal without further deposits).
    """
    if years_to_retirement <= 0:
        return target_corpus

    coast = target_corpus / np.power(1 + annual_return, years_to_retirement)  # pyre-ignore
    return round(float(coast), 2)  # pyre-ignore


def generate_monthly_roadmap(
    current_age: int,
    current_savings: float,
    monthly_sip: float,
    annual_return: float,
    fire_corpus: float,
    annual_step_up_pct: float = 0.0,
    inflation_rate: float = 0.06,
) -> list[dict]:
    """
    Generate month-by-month FIRE roadmap with milestones and real/nominal values.
    """
    monthly_rate = annual_return / 12
    corpus = float(current_savings)
    current_sip = float(monthly_sip)
    roadmap = []

    milestones_hit = set()
    milestone_thresholds = {
        "25% of FIRE goal": 0.25,
        "50% of FIRE goal": 0.50,
        "75% of FIRE goal": 0.75,
        "FIRE achieved!": 1.00,
    }

    max_months = 600  # 50 years cap
    fire_reached = False

    for month in range(1, max_months + 1):
        # Step-up SIP every 12 months (at start of each new year)
        if annual_step_up_pct > 0 and month > 1 and (month - 1) % 12 == 0:
            current_sip *= (1 + annual_step_up_pct)

        # Grow corpus: add SIP then apply monthly return
        corpus = (corpus + current_sip) * (1 + monthly_rate)

        # Calculate progress
        progress = corpus / fire_corpus if fire_corpus > 0 else 0
        year_number = (month - 1) // 12 + 1
        age_at_month = current_age + (month - 1) / 12

        # Inflation-adjusted corpus (real value)
        years_elapsed = month / 12
        real_corpus = corpus / np.power(1 + inflation_rate, years_elapsed)  # pyre-ignore

        # Check for milestones
        milestone = None
        for label, threshold in milestone_thresholds.items():
            if label not in milestones_hit and progress >= threshold:
                milestone = label
                milestones_hit.add(label)
                if label == "FIRE achieved!":
                    fire_reached = True

        snapshot = {
            "month": month,
            "year_number": year_number,
            "age": round(age_at_month, 1),  # pyre-ignore
            "sip_amount": round(current_sip, 2),  # pyre-ignore
            "corpus": round(corpus, 2),  # pyre-ignore
            "real_corpus": round(float(real_corpus), 2),  # pyre-ignore
            "progress_pct": round(progress * 100, 2),  # pyre-ignore
        }
        if milestone:
            snapshot["milestone"] = milestone

        # Only record monthly data for first 2 years, then quarterly,
        # then annually — keeps output manageable
        if month <= 24 or month % 3 == 0 or milestone or fire_reached:
            roadmap.append(snapshot)

        if fire_reached:
            break

    return roadmap
