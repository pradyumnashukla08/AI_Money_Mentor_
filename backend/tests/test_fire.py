"""
Unit tests for FIRE (Financial Independence, Retire Early) calculations.

Validates target corpus, time-to-FIRE, Coast FIRE,
and monthly roadmap generation.
"""

import pytest
from engine.fire import (
    fire_target_corpus,
    years_to_fire,
    coast_fire_number,
    generate_monthly_roadmap,
)


class TestFireTargetCorpus:
    """Tests for FIRE corpus requirement calculation."""

    def test_4_percent_rule(self):
        """4% withdrawal rate → corpus should be 25× annual expenses."""
        result = fire_target_corpus(
            annual_expenses=600000,   # ₹6 Lakhs/year
            withdrawal_rate=0.04,
            inflation_rate=0.0,
            years_to_retirement=0,
        )
        assert result["corpus_today"] == 15000000  # ₹1.5 Crore = 25 × ₹6L

    def test_3_percent_rule(self):
        """3% withdrawal rate → corpus should be ~33.3× annual expenses."""
        result = fire_target_corpus(
            annual_expenses=600000,
            withdrawal_rate=0.03,
            inflation_rate=0.0,
            years_to_retirement=0,
        )
        assert abs(result["corpus_today"] - 20000000) < 1  # ₹2 Crore

    def test_inflation_adjusted_corpus(self):
        """Corpus at retirement should be higher than today's value due to inflation."""
        result = fire_target_corpus(
            annual_expenses=600000,
            withdrawal_rate=0.04,
            inflation_rate=0.06,
            years_to_retirement=20,
        )
        assert result["corpus_at_retirement"] > result["corpus_today"]
        assert result["inflated_annual_expense"] > 600000

    def test_zero_years_to_retirement(self):
        """If retiring now, corpus_today and corpus_at_retirement should be equal."""
        result = fire_target_corpus(
            annual_expenses=600000,
            withdrawal_rate=0.04,
            inflation_rate=0.06,
            years_to_retirement=0,
        )
        assert result["corpus_today"] == result["corpus_at_retirement"]

    def test_invalid_expenses_raises(self):
        """Zero or negative expenses should raise ValueError."""
        with pytest.raises(ValueError):
            fire_target_corpus(0, 0.04)
        with pytest.raises(ValueError):
            fire_target_corpus(-100000, 0.04)


class TestYearsToFire:
    """Tests for time-to-FIRE estimation."""

    def test_already_achieved(self):
        """If savings already exceed corpus, years_to_fire should be 0."""
        result = years_to_fire(
            current_savings=20000000,
            monthly_investment=10000,
            annual_return=0.12,
            fire_corpus=15000000,
        )
        assert result == 0.0

    def test_reasonable_timeline(self):
        """₹50K/month SIP at 12% to reach ₹5 Crore — should be 15-20 years."""
        result = years_to_fire(
            current_savings=500000,
            monthly_investment=50000,
            annual_return=0.12,
            fire_corpus=50000000,
        )
        assert 14 < result < 22

    def test_higher_sip_is_faster(self):
        """Higher monthly investment should result in fewer years."""
        slow = years_to_fire(0, 20000, 0.12, 10000000)
        fast = years_to_fire(0, 50000, 0.12, 10000000)
        assert fast < slow

    def test_existing_savings_help(self):
        """Starting with savings should be faster than starting from zero."""
        from_zero = years_to_fire(0, 30000, 0.12, 10000000)
        with_savings = years_to_fire(2000000, 30000, 0.12, 10000000)
        assert with_savings < from_zero


class TestCoastFireNumber:
    """Tests for Coast FIRE calculation."""

    def test_basic_coast_fire(self):
        """Coast FIRE number should be less than the target corpus."""
        coast = coast_fire_number(
            target_corpus=50000000,
            annual_return=0.12,
            years_to_retirement=20,
        )
        assert coast < 50000000
        assert coast > 0

    def test_zero_years(self):
        """With zero years, coast number equals target corpus."""
        coast = coast_fire_number(50000000, 0.12, 0)
        assert coast == 50000000

    def test_longer_horizon_needs_less(self):
        """More years to retirement → lower coast number needed today."""
        short = coast_fire_number(50000000, 0.12, 10)
        long = coast_fire_number(50000000, 0.12, 25)
        assert long < short


class TestMonthlyRoadmap:
    """Tests for month-by-month FIRE roadmap generation."""

    def test_roadmap_not_empty(self):
        """Roadmap should have entries."""
        roadmap = generate_monthly_roadmap(
            current_age=25,
            current_savings=100000,
            monthly_sip=20000,
            annual_return=0.12,
            fire_corpus=30000000,
        )
        assert len(roadmap) > 0

    def test_corpus_grows_monotonically(self):
        """Corpus should never decrease (assuming positive returns + SIP)."""
        roadmap = generate_monthly_roadmap(
            current_age=30,
            current_savings=0,
            monthly_sip=30000,
            annual_return=0.12,
            fire_corpus=50000000,
        )
        for i in range(1, len(roadmap)):
            assert roadmap[i]["corpus"] >= roadmap[i - 1]["corpus"]

    def test_milestones_present(self):
        """Roadmap should contain milestones (at least 25% marker)."""
        roadmap = generate_monthly_roadmap(
            current_age=25,
            current_savings=0,
            monthly_sip=30000,
            annual_return=0.12,
            fire_corpus=30000000,
        )
        milestones = [e for e in roadmap if "milestone" in e]
        assert len(milestones) >= 1

    def test_fire_achieved_milestone(self):
        """Roadmap should end with 'FIRE achieved!' milestone."""
        roadmap = generate_monthly_roadmap(
            current_age=25,
            current_savings=500000,
            monthly_sip=50000,
            annual_return=0.12,
            fire_corpus=30000000,
        )
        last_milestone = [e for e in roadmap if "milestone" in e][-1]
        assert last_milestone["milestone"] == "FIRE achieved!"

    def test_progress_reaches_100(self):
        """Last entry should show 100%+ progress."""
        roadmap = generate_monthly_roadmap(
            current_age=28,
            current_savings=200000,
            monthly_sip=40000,
            annual_return=0.12,
            fire_corpus=20000000,
        )
        last = roadmap[-1]
        assert last["progress_pct"] >= 100.0

    def test_age_tracking(self):
        """Ages in roadmap should start from current age and increase."""
        roadmap = generate_monthly_roadmap(
            current_age=30,
            current_savings=0,
            monthly_sip=25000,
            annual_return=0.12,
            fire_corpus=20000000,
        )
        assert roadmap[0]["age"] >= 30.0
        assert roadmap[-1]["age"] > 30.0

    def test_step_up_increases_sip(self):
        """With step-up, later SIP amounts should be higher."""
        roadmap = generate_monthly_roadmap(
            current_age=25,
            current_savings=0,
            monthly_sip=10000,
            annual_return=0.12,
            fire_corpus=50000000,
            annual_step_up_pct=0.10,
        )
        first_sip = roadmap[0]["sip_amount"]
        last_sip = roadmap[-1]["sip_amount"]
        assert last_sip > first_sip
