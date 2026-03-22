"""
Compound interest and inflation adjustment calculations.

All functions use standard financial formulae and operate on
annual rates expressed as decimals (e.g., 0.12 for 12%).
"""

import numpy as np


def future_value(
    principal: float,
    annual_rate: float,
    years: int,
    compounding_freq: int = 1,
) -> float:
    """
    Calculate the future value of a lump-sum investment.

    Formula: FV = P × (1 + r/n)^(n×t)

    Args:
        principal: Initial investment amount in INR.
        annual_rate: Annual interest rate (decimal).
        years: Investment duration in years.
        compounding_freq: Times interest compounds per year (1=annual, 12=monthly).

    Returns:
        Future value in INR, rounded to 2 decimal places.
    """
    if principal < 0:
        raise ValueError("Principal must be non-negative")
    if annual_rate < 0:
        raise ValueError("Annual rate must be non-negative")
    if years < 0:
        raise ValueError("Years must be non-negative")

    rate_per_period = annual_rate / compounding_freq
    total_periods = compounding_freq * years
    fv = principal * np.power(1 + rate_per_period, total_periods)
    return round(float(fv), 2)


def real_return(nominal_rate: float, inflation_rate: float) -> float:
    """
    Calculate the inflation-adjusted (real) rate of return
    using the Fisher equation.

    Formula: real = (1 + nominal) / (1 + inflation) - 1

    Args:
        nominal_rate: Nominal annual return rate (decimal).
        inflation_rate: Annual inflation rate (decimal).

    Returns:
        Real return rate as a decimal.
    """
    real = (1 + nominal_rate) / (1 + inflation_rate) - 1
    return round(real, 6)


def inflation_adjusted_value(
    future_amount: float,
    inflation_rate: float,
    years: int,
) -> float:
    """
    Calculate the present-day purchasing power of a future sum.

    Formula: PV = FV / (1 + inflation)^years

    Args:
        future_amount: Amount in future INR.
        inflation_rate: Annual inflation rate (decimal).
        years: Number of years in the future.

    Returns:
        Present value in today's INR, rounded to 2 decimal places.
    """
    if years < 0:
        raise ValueError("Years must be non-negative")

    pv = future_amount / np.power(1 + inflation_rate, years)
    return round(float(pv), 2)


def present_value_of_future_expense(
    current_annual_expense: float,
    inflation_rate: float,
    years: int,
) -> float:
    """
    Project what today's annual expense will cost in the future
    after accounting for inflation.

    Formula: FV = expense × (1 + inflation)^years

    Args:
        current_annual_expense: Today's annual expense in INR.
        inflation_rate: Annual inflation rate (decimal).
        years: Years into the future.

    Returns:
        Inflated annual expense in INR, rounded to 2 decimal places.
    """
    inflated = current_annual_expense * np.power(1 + inflation_rate, years)
    return round(float(inflated), 2)
