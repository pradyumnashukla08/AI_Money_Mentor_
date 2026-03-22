"""
Unit tests for the compounding and inflation calculation engine.

Tests use known financial values to verify correctness
of compound interest and inflation adjustment functions.
"""

import pytest
from engine.compounding import (
    future_value,
    real_return,
    inflation_adjusted_value,
    present_value_of_future_expense,
)


class TestFutureValue:
    """Tests for compound interest future value calculation."""

    def test_basic_annual_compounding(self):
        """₹1,00,000 at 10% for 10 years (annual) ≈ ₹2,59,374.25"""
        result = future_value(100000, 0.10, 10, compounding_freq=1)
        assert abs(result - 259374.25) < 1.0

    def test_monthly_compounding(self):
        """Monthly compounding should yield more than annual."""
        annual = future_value(100000, 0.10, 10, compounding_freq=1)
        monthly = future_value(100000, 0.10, 10, compounding_freq=12)
        assert monthly > annual

    def test_zero_principal(self):
        """Zero principal should return zero."""
        result = future_value(0, 0.12, 10)
        assert result == 0.0

    def test_zero_rate(self):
        """Zero rate means no growth — principal unchanged."""
        result = future_value(100000, 0.0, 10)
        assert result == 100000.0

    def test_zero_years(self):
        """Zero years means no time to grow — principal unchanged."""
        result = future_value(100000, 0.12, 0)
        assert result == 100000.0

    def test_negative_principal_raises(self):
        """Negative principal should raise ValueError."""
        with pytest.raises(ValueError):
            future_value(-1000, 0.10, 5)

    def test_negative_rate_raises(self):
        """Negative rate should raise ValueError."""
        with pytest.raises(ValueError):
            future_value(1000, -0.10, 5)

    def test_large_amount(self):
        """₹1 Crore at 12% for 20 years should grow substantially."""
        result = future_value(10000000, 0.12, 20)
        assert result > 90000000  # Should be ~₹9.6 Crore+


class TestRealReturn:
    """Tests for Fisher equation real return calculation."""

    def test_basic_real_return(self):
        """12% nominal with 6% inflation ≈ 5.66% real return."""
        result = real_return(0.12, 0.06)
        expected = (1.12 / 1.06) - 1
        assert abs(result - expected) < 0.0001

    def test_zero_inflation(self):
        """Zero inflation means real return equals nominal."""
        result = real_return(0.10, 0.0)
        assert abs(result - 0.10) < 0.0001

    def test_equal_rate_and_inflation(self):
        """When rate equals inflation, real return is approximately zero."""
        result = real_return(0.06, 0.06)
        assert abs(result) < 0.0001

    def test_negative_real_return(self):
        """When inflation exceeds nominal return, real return is negative."""
        result = real_return(0.04, 0.07)
        assert result < 0


class TestInflationAdjustedValue:
    """Tests for converting future amounts to present value."""

    def test_basic_deflation(self):
        """₹1,00,000 in 10 years at 6% inflation is worth less today."""
        result = inflation_adjusted_value(100000, 0.06, 10)
        assert result < 100000
        assert result > 50000  # Should be around ₹55,839

    def test_zero_years(self):
        """Zero years means no inflation adjustment — value unchanged."""
        result = inflation_adjusted_value(100000, 0.06, 0)
        assert result == 100000.0

    def test_round_trip(self):
        """Inflating then deflating should return original value."""
        original = 500000
        inflated = present_value_of_future_expense(original, 0.06, 10)
        deflated = inflation_adjusted_value(inflated, 0.06, 10)
        assert abs(deflated - original) < 1.0


class TestPresentValueOfFutureExpense:
    """Tests for projecting current expenses into the future."""

    def test_basic_inflation_projection(self):
        """₹6,00,000/year at 6% inflation for 20 years."""
        result = present_value_of_future_expense(600000, 0.06, 20)
        assert result > 600000  # Must be higher than today
        # At 6% for 20 years: 600000 * (1.06)^20 ≈ ₹19,23,357
        assert abs(result - 1923357) < 5000

    def test_zero_inflation(self):
        """Zero inflation means expense stays the same."""
        result = present_value_of_future_expense(600000, 0.0, 20)
        assert result == 600000.0
