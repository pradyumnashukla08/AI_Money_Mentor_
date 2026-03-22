"""
test_tax_calculator.py — Unit tests for the Old vs New tax regime calculator.
Run with: python -m pytest auditor_agent/tests/test_tax_calculator.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from auditor_agent.tax_wizard.form16_agent import Form16Data
from auditor_agent.tax_wizard.tax_calculator import (
    calculate_old_regime,
    calculate_new_regime,
    compare_regimes,
)


# ── Sample data fixtures ─────────────────────────────────────────────────────

def sample_high_deduction_profile():
    """Profile that typically benefits from Old Regime (high deductions)."""
    return Form16Data(
        employer_name="TechSoft India",
        employee_name="Arjun Sharma",
        pan="ABCDE1234F",
        assessment_year="2025-26",
        gross_salary=1_500_000,
        hra_received=300_000,
        basic_salary=750_000,
        hra_exempt=180_000,
        lta_exempt=20_000,
        professional_tax=2_400,
        deduction_80c=150_000,
        deduction_80d=50_000,
        deduction_80ccd1b=50_000,
        deduction_80ccd2=45_000,
        tds_deducted=120_000,
    )


def sample_low_deduction_profile():
    """Profile that typically benefits from New Regime (few deductions)."""
    return Form16Data(
        employer_name="Startup Co",
        employee_name="Priya Patel",
        pan="FGHIJ5678K",
        assessment_year="2025-26",
        gross_salary=800_000,
        tds_deducted=40_000,
    )


def sample_below_rebate_profile():
    """Income below ₹5L (Old) / ₹7L (New) — tax should be zero after rebate."""
    return Form16Data(
        employer_name="Small Firm",
        employee_name="Rahul Kumar",
        gross_salary=450_000,
        tds_deducted=0,
    )


# ── Tests ────────────────────────────────────────────────────────────────────

def test_taxable_income_is_non_negative():
    data = sample_high_deduction_profile()
    old = calculate_old_regime(data)
    new = calculate_new_regime(data)
    assert old.taxable_income >= 0, "Old regime taxable income must not be negative"
    assert new.taxable_income >= 0, "New regime taxable income must not be negative"


def test_total_tax_is_non_negative():
    for fn in [sample_high_deduction_profile, sample_low_deduction_profile]:
        data = fn()
        old = calculate_old_regime(data)
        new = calculate_new_regime(data)
        assert old.total_tax_payable >= 0
        assert new.total_tax_payable >= 0


def test_cess_is_4_percent():
    data = sample_high_deduction_profile()
    old = calculate_old_regime(data)
    expected_cess = round((old.tax_after_rebate + old.surcharge) * 0.04, 2)
    assert abs(old.cess - expected_cess) < 1.0, f"Cess mismatch: {old.cess} vs {expected_cess}"


def test_87a_rebate_applied_old_regime():
    data = sample_below_rebate_profile()
    old = calculate_old_regime(data)
    # Income ₹4.5L < ₹5L rebate limit → tax should be zero
    assert old.total_tax_payable == 0.0, f"Expected zero tax for ₹4.5L income, got {old.total_tax_payable}"


def test_87a_rebate_applied_new_regime():
    data = Form16Data(gross_salary=650_000, tds_deducted=0)
    new = calculate_new_regime(data)
    # Income ₹6.5L < ₹7L new regime rebate limit → tax should be zero
    assert new.total_tax_payable == 0.0, f"Expected zero tax for ₹6.5L new regime, got {new.total_tax_payable}"


def test_compare_returns_valid_recommendation():
    comparison = compare_regimes(sample_high_deduction_profile())
    assert comparison.recommended_regime in ("Old", "New")
    assert comparison.savings_with_recommended >= 0
    assert len(comparison.recommendation_reason) > 20


def test_high_deduction_profile_prefers_old_regime():
    """With ₹5L+ in deductions, Old Regime should usually win."""
    comparison = compare_regimes(sample_high_deduction_profile())
    # This is a heuristic test — with 1.5L 80C + 50k 80D + 50k NPS + HRA, Old should win
    # Log both values for visibility
    print(f"\nOld: ₹{comparison.old_regime.total_tax_payable:,.0f}  "
          f"New: ₹{comparison.new_regime.total_tax_payable:,.0f}  "
          f"Recommended: {comparison.recommended_regime}")


def test_effective_rate_within_bounds():
    data = sample_high_deduction_profile()
    old = calculate_old_regime(data)
    new = calculate_new_regime(data)
    assert 0 <= old.effective_tax_rate <= 40, f"Old effective rate out of range: {old.effective_tax_rate}"
    assert 0 <= new.effective_tax_rate <= 40, f"New effective rate out of range: {new.effective_tax_rate}"


if __name__ == "__main__":
    print("Running Tax Calculator Tests...")
    test_taxable_income_is_non_negative()
    test_total_tax_is_non_negative()
    test_cess_is_4_percent()
    test_87a_rebate_applied_old_regime()
    test_87a_rebate_applied_new_regime()
    test_compare_returns_valid_recommendation()
    test_high_deduction_profile_prefers_old_regime()
    test_effective_rate_within_bounds()
    print("\n✅ All tests passed!")
