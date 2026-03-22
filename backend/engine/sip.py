"""
SIP (Systematic Investment Plan) calculations.

Standard Indian mutual fund SIP formulae including step-up SIPs
where the monthly contribution increases annually.
"""

import numpy as np


def sip_future_value(
    monthly_amount: float,
    annual_rate: float,
    years: int,
) -> float:
    """
    Calculate the maturity value of a regular monthly SIP.

    Uses the standard annuity future value formula:
    FV = P × [((1+r)^n - 1) / r] × (1+r)

    where r = monthly rate, n = total months, P = monthly SIP.

    Args:
        monthly_amount: Monthly SIP contribution in INR.
        annual_rate: Expected annual return rate (decimal, e.g., 0.12).
        years: Investment duration in years.

    Returns:
        SIP maturity value in INR, rounded to 2 decimal places.
    """
    if monthly_amount <= 0:
        raise ValueError("Monthly SIP amount must be positive")
    if annual_rate < 0:
        raise ValueError("Annual rate must be non-negative")
    if years <= 0:
        raise ValueError("Years must be positive")

    monthly_rate = annual_rate / 12
    total_months = years * 12

    if monthly_rate == 0:
        return round(monthly_amount * total_months, 2)

    fv = monthly_amount * (
        (np.power(1 + monthly_rate, total_months) - 1) / monthly_rate
    ) * (1 + monthly_rate)

    return round(float(fv), 2)


def sip_required(
    target_amount: float,
    annual_rate: float,
    years: int,
) -> float:
    """
    Calculate the monthly SIP needed to reach a target corpus.

    Inverse of sip_future_value.

    Args:
        target_amount: Desired corpus at maturity in INR.
        annual_rate: Expected annual return rate (decimal).
        years: Investment duration in years.

    Returns:
        Required monthly SIP amount in INR, rounded to nearest rupee.
    """
    if target_amount <= 0:
        raise ValueError("Target amount must be positive")
    if years <= 0:
        raise ValueError("Years must be positive")

    monthly_rate = annual_rate / 12
    total_months = years * 12

    if monthly_rate == 0:
        return round(target_amount / total_months, 2)

    denominator = ((np.power(1 + monthly_rate, total_months) - 1) / monthly_rate) * (
        1 + monthly_rate
    )
    monthly_sip = target_amount / denominator

    return round(float(monthly_sip), 2)


def step_up_sip(
    monthly_amount: float,
    annual_rate: float,
    years: int,
    annual_step_up_pct: float = 0.10,
) -> dict:
    """
    Calculate the maturity value of a step-up SIP where the monthly
    contribution increases by a fixed percentage every year.

    This models the real-world scenario where investors increase their
    SIP amount annually as their salary grows.

    Args:
        monthly_amount: Starting monthly SIP in INR.
        annual_rate: Expected annual return rate (decimal).
        years: Investment duration in years.
        annual_step_up_pct: Annual increase in SIP (decimal, e.g., 0.10 = 10%).

    Returns:
        Dictionary with:
            - total_value: Final corpus in INR
            - total_invested: Sum of all SIP contributions
            - wealth_gained: Corpus minus contributions
            - yearly_breakdown: List of per-year details
    """
    if monthly_amount <= 0:
        raise ValueError("Monthly SIP amount must be positive")
    if years <= 0:
        raise ValueError("Years must be positive")

    monthly_rate = annual_rate / 12
    corpus = 0.0
    total_invested = 0.0
    current_sip = monthly_amount
    yearly_breakdown = []

    for year in range(1, years + 1):
        year_investment = 0.0
        for _month in range(12):
            corpus = (corpus + current_sip) * (1 + monthly_rate)
            year_investment += current_sip
            total_invested += current_sip

        yearly_breakdown.append({
            "year": year,
            "monthly_sip": round(current_sip, 2),
            "year_investment": round(year_investment, 2),
            "corpus_at_year_end": round(corpus, 2),
        })

        # Step up the SIP for the next year
        current_sip *= (1 + annual_step_up_pct)

    return {
        "total_value": round(corpus, 2),
        "total_invested": round(total_invested, 2),
        "wealth_gained": round(corpus - total_invested, 2),
        "yearly_breakdown": yearly_breakdown,
    }
