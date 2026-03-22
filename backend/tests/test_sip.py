"""
Unit tests for SIP (Systematic Investment Plan) calculations.

Validates standard SIP maturity, inverse SIP, and step-up SIP
against known financial calculator values.
"""

import pytest
from engine.sip import sip_future_value, sip_required, step_up_sip


class TestSipFutureValue:
    """Tests for standard SIP maturity value calculation."""

    def test_basic_sip(self):
        """₹10,000/month SIP at 12% for 10 years.
        Standard SIP calculators give approximately ₹23.2-23.5 Lakhs."""
        result = sip_future_value(10000, 0.12, 10)
        assert 2300000 < result < 2400000

    def test_small_sip(self):
        """₹500/month for 5 years at 10% — basic validation."""
        result = sip_future_value(500, 0.10, 5)
        assert result > 500 * 60  # Must be more than just sum of deposits

    def test_high_return_rate(self):
        """Higher return rate should give higher maturity value."""
        low_return = sip_future_value(10000, 0.08, 10)
        high_return = sip_future_value(10000, 0.14, 10)
        assert high_return > low_return

    def test_longer_duration(self):
        """Longer duration should give higher maturity (power of compounding)."""
        short = sip_future_value(10000, 0.12, 5)
        long = sip_future_value(10000, 0.12, 20)
        assert long > short * 3  # Compounding effect

    def test_zero_rate(self):
        """Zero return means just sum of deposits."""
        result = sip_future_value(10000, 0.0, 5)
        expected = 10000 * 60  # 5 years × 12 months
        assert abs(result - expected) < 1.0

    def test_invalid_amount_raises(self):
        """Zero or negative SIP amount should raise ValueError."""
        with pytest.raises(ValueError):
            sip_future_value(0, 0.12, 10)
        with pytest.raises(ValueError):
            sip_future_value(-1000, 0.12, 10)

    def test_invalid_years_raises(self):
        """Zero or negative years should raise ValueError."""
        with pytest.raises(ValueError):
            sip_future_value(10000, 0.12, 0)


class TestSipRequired:
    """Tests for inverse SIP calculation — finding monthly amount needed."""

    def test_inverse_of_future_value(self):
        """sip_required should be the inverse of sip_future_value.
        If SIP of X gives FV, then sip_required(FV) should return X."""
        original_sip = 10000
        fv = sip_future_value(original_sip, 0.12, 10)
        required = sip_required(fv, 0.12, 10)
        assert abs(required - original_sip) < 10  # Within ₹10

    def test_higher_target_needs_more_sip(self):
        """Higher target should require higher monthly SIP."""
        sip_1cr = sip_required(10000000, 0.12, 15)   # ₹1 Crore
        sip_2cr = sip_required(20000000, 0.12, 15)   # ₹2 Crore
        assert abs(sip_2cr - 2 * sip_1cr) < 10  # Linear relationship

    def test_more_time_needs_less_sip(self):
        """More time to grow means smaller monthly SIP needed."""
        short_sip = sip_required(10000000, 0.12, 10)
        long_sip = sip_required(10000000, 0.12, 20)
        assert long_sip < short_sip


class TestStepUpSip:
    """Tests for step-up SIP (yearly increment) calculation."""

    def test_step_up_beats_regular(self):
        """Step-up SIP should outperform regular SIP with same starting amount."""
        regular = sip_future_value(10000, 0.12, 15)
        stepped = step_up_sip(10000, 0.12, 15, annual_step_up_pct=0.10)
        assert stepped["total_value"] > regular

    def test_output_structure(self):
        """Validate the output dictionary structure."""
        result = step_up_sip(5000, 0.12, 10, 0.10)
        assert "total_value" in result
        assert "total_invested" in result
        assert "wealth_gained" in result
        assert "yearly_breakdown" in result
        assert len(result["yearly_breakdown"]) == 10

    def test_wealth_gained_consistency(self):
        """wealth_gained should equal total_value minus total_invested."""
        result = step_up_sip(5000, 0.12, 10, 0.10)
        computed_gain = result["total_value"] - result["total_invested"]
        assert abs(result["wealth_gained"] - computed_gain) < 1.0

    def test_yearly_sip_increases(self):
        """Monthly SIP in each year should be higher than the previous year."""
        result = step_up_sip(5000, 0.12, 10, 0.10)
        breakdown = result["yearly_breakdown"]
        for i in range(1, len(breakdown)):
            assert breakdown[i]["monthly_sip"] > breakdown[i - 1]["monthly_sip"]

    def test_zero_step_up_equals_regular(self):
        """Zero step-up should give same result as regular SIP."""
        regular = sip_future_value(10000, 0.12, 10)
        stepped = step_up_sip(10000, 0.12, 10, annual_step_up_pct=0.0)
        # Allow small difference due to different computation paths
        assert abs(stepped["total_value"] - regular) / regular < 0.01
