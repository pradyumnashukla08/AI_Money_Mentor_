"""
tax_calculator.py — Indian Income Tax Calculator for FY 2025-26.

Computes tax liability under both Old and New regimes,
applies Section 87A rebate, surcharge, and 4% cess,
then returns a clean side-by-side comparison with a recommendation.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math

from auditor_agent.config import settings
from auditor_agent.tax_wizard.form16_agent import Form16Data


# ── Intermediate result types ───────────────────────────────────────────────

@dataclass
class SlabBreakdown:
    """Tax computed for a single income slab."""
    slab_label: str
    taxable_in_slab: float
    rate: float
    tax: float


@dataclass
class TaxResult:
    """Full tax computation result for one regime."""
    regime: str                        # "Old" or "New"
    gross_income: float
    total_exemptions: float
    total_deductions: float
    taxable_income: float
    slab_breakdown: List[SlabBreakdown]
    base_tax: float
    rebate_87a: float
    tax_after_rebate: float
    surcharge: float
    cess: float
    total_tax_payable: float
    tds_already_paid: float
    tax_due_or_refund: float           # Negative = refund, Positive = due
    effective_tax_rate: float          # As a percentage


@dataclass
class OptimizationStrategy:
    """Actionable steps to reduce tax further."""
    current_regime: str
    target_regime: str
    additional_investment_needed: float
    investment_category: str           # "80C" or "80CCD(1B)"
    potential_savings: float
    is_feasible: bool                  # True if below caps
    message: str

@dataclass
class TaxComparison:
    """Side-by-side comparison of Old vs. New regime."""
    old_regime: TaxResult
    new_regime: TaxResult
    recommended_regime: str            # "Old" or "New"
    savings_with_recommended: float    # Absolute ₹ savings
    recommendation_reason: str
    optimization_strategy: Optional[OptimizationStrategy] = None


# ── Core calculation helpers ────────────────────────────────────────────────

def _compute_slab_tax(taxable_income: float, slabs: List[Tuple]) -> Tuple[float, List[SlabBreakdown]]:
    """
    Apply progressive slab taxation.

    Args:
        taxable_income: Net taxable income after all deductions.
        slabs: List of (upper_limit, rate) tuples in ascending order.

    Returns:
        (total_base_tax, list_of_slab_breakdowns)
    """
    breakdowns: List[SlabBreakdown] = []
    total_tax = 0.0
    previous_limit = 0.0

    for upper_limit, rate in slabs:
        if taxable_income <= previous_limit:
            break

        slab_income = min(taxable_income, upper_limit) - previous_limit

        if rate == 0.0:
            label = f"Up to ₹{int(upper_limit):,} @ 0%"
        else:
            if upper_limit == float("inf"):
                label = f"Above ₹{int(previous_limit):,} @ {int(rate*100)}%"
            else:
                label = f"₹{int(previous_limit):,}–₹{int(upper_limit):,} @ {int(rate*100)}%"

        slab_tax = slab_income * rate
        breakdowns.append(SlabBreakdown(
            slab_label=label,
            taxable_in_slab=slab_income,
            rate=rate,
            tax=slab_tax,
        ))
        total_tax += slab_tax
        previous_limit = upper_limit if upper_limit != float("inf") else previous_limit

    return round(total_tax, 2), breakdowns


def _compute_surcharge(tax: float, taxable_income: float) -> float:
    """
    Compute surcharge based on total income (FY 2025-26 rates).
    Marginal relief is not applied here for simplicity.
    """
    if taxable_income <= 5_000_000:       # ≤ 50 Lakhs
        return 0.0
    elif taxable_income <= 10_000_000:    # 50L – 1 Cr
        return tax * 0.10
    elif taxable_income <= 20_000_000:    # 1 Cr – 2 Cr
        return tax * 0.15
    elif taxable_income <= 50_000_000:    # 2 Cr – 5 Cr
        return tax * 0.25
    else:                                  # Above 5 Cr
        return tax * 0.37


def _compute_87a_rebate(base_tax: float, taxable_income: float, rebate_limit: int) -> float:
    """Section 87A: Full rebate if taxable income ≤ rebate_limit (max ₹12,500 old, ₹25,000 new)."""
    if taxable_income <= rebate_limit:
        max_rebate = 25_000.0 if rebate_limit == settings.NEW_REGIME_REBATE_LIMIT else 12_500.0
        return min(base_tax, max_rebate)
    return 0.0


# ── Old Regime ──────────────────────────────────────────────────────────────

def calculate_old_regime(data: Form16Data) -> TaxResult:
    """
    Compute tax under the Old Regime with all eligible deductions and exemptions.
    """
    # --- Income adjustments ---
    total_exemptions = data.hra_exempt + data.lta_exempt
    gross_income = data.gross_salary

    # --- Deductions ---
    chapter_via = min(data.deduction_80c, 150_000)          # 80C cap ₹1.5L
    deduction_80d = data.deduction_80d
    deduction_80ccd1b = min(data.deduction_80ccd1b, 50_000) # 80CCD(1B) cap ₹50k
    deduction_80ccd2 = data.deduction_80ccd2
    deduction_80tta = min(data.deduction_80tta, 10_000)     # 80TTA cap ₹10k
    deduction_80e = data.deduction_80e
    home_loan_interest = min(data.deduction_home_loan_interest, 200_000)  # 24(b) cap ₹2L
    other_ded = data.other_deductions

    total_deductions = (
        settings.STANDARD_DEDUCTION_OLD
        + data.professional_tax
        + chapter_via
        + deduction_80d
        + deduction_80ccd1b
        + deduction_80ccd2
        + deduction_80tta
        + deduction_80e
        + data.deduction_80g
        + min(data.deduction_80eea, 150_000) # 80EEA cap ₹1.5L
        + home_loan_interest
        + other_ded
    )

    taxable_income = max(0.0, gross_income - total_exemptions - total_deductions)
    taxable_income = round(taxable_income / 10) * 10  # Round to nearest ₹10

    # --- Slab tax ---
    base_tax, slab_breakdown = _compute_slab_tax(taxable_income, settings.OLD_REGIME_SLABS)

    # --- Rebate 87A ---
    rebate = _compute_87a_rebate(base_tax, taxable_income, settings.OLD_REGIME_REBATE_LIMIT)
    tax_after_rebate = max(0.0, base_tax - rebate)

    # --- Surcharge ---
    surcharge = _compute_surcharge(tax_after_rebate, taxable_income)

    # --- Cess ---
    cess = (tax_after_rebate + surcharge) * settings.CESS_RATE

    total_tax = round(tax_after_rebate + surcharge + cess, 2)
    tds_paid = data.tds_deducted + data.advance_tax_paid
    tax_due_or_refund = round(total_tax - tds_paid, 2)
    effective_rate = round((total_tax / gross_income * 100), 2) if gross_income > 0 else 0.0

    return TaxResult(
        regime="Old",
        gross_income=gross_income,
        total_exemptions=total_exemptions,
        total_deductions=total_deductions,
        taxable_income=taxable_income,
        slab_breakdown=slab_breakdown,
        base_tax=base_tax,
        rebate_87a=rebate,
        tax_after_rebate=tax_after_rebate,
        surcharge=surcharge,
        cess=cess,
        total_tax_payable=total_tax,
        tds_already_paid=tds_paid,
        tax_due_or_refund=tax_due_or_refund,
        effective_tax_rate=effective_rate,
    )


# ── New Regime ──────────────────────────────────────────────────────────────

def calculate_new_regime(data: Form16Data) -> TaxResult:
    """
    Compute tax under the New Regime (FY 2025-26).
    No Chapter VI-A deductions; only standard deduction and 80CCD(2) allowed.
    """
    # Under new regime: No HRA, LTA exemptions. Only employer NPS (80CCD2) allowed.
    total_exemptions = 0.0
    total_deductions = settings.STANDARD_DEDUCTION_NEW + data.deduction_80ccd2

    taxable_income = max(0.0, data.gross_salary - total_deductions)
    taxable_income = round(taxable_income / 10) * 10

    base_tax, slab_breakdown = _compute_slab_tax(taxable_income, settings.NEW_REGIME_SLABS)

    rebate = _compute_87a_rebate(base_tax, taxable_income, settings.NEW_REGIME_REBATE_LIMIT)
    tax_after_rebate = max(0.0, base_tax - rebate)

    surcharge = _compute_surcharge(tax_after_rebate, taxable_income)
    cess = (tax_after_rebate + surcharge) * settings.CESS_RATE

    total_tax = round(tax_after_rebate + surcharge + cess, 2)
    tds_paid = data.tds_deducted + data.advance_tax_paid
    tax_due_or_refund = round(total_tax - tds_paid, 2)
    effective_rate = round((total_tax / data.gross_salary * 100), 2) if data.gross_salary > 0 else 0.0

    return TaxResult(
        regime="New",
        gross_income=data.gross_salary,
        total_exemptions=total_exemptions,
        total_deductions=total_deductions,
        taxable_income=taxable_income,
        slab_breakdown=slab_breakdown,
        base_tax=base_tax,
        rebate_87a=rebate,
        tax_after_rebate=tax_after_rebate,
        surcharge=surcharge,
        cess=cess,
        total_tax_payable=total_tax,
        tds_already_paid=tds_paid,
        tax_due_or_refund=tax_due_or_refund,
        effective_tax_rate=effective_rate,
    )


# ── Comparison ─────────────────────────────────────────────────────────────
def calculate_optimization(data: Form16Data, comparison: TaxComparison) -> Optional[OptimizationStrategy]:
    """
    If New regime is better, check if additional 80C or 80CCD(1B) 
    investments can tip the scale back to Old regime for more savings.
    """
    if comparison.recommended_regime == "Old":
        return None

    # New is currently better. Let's see if we can "bailout" to Old.
    tax_diff = comparison.old_regime.total_tax_payable - comparison.new_regime.total_tax_payable
    
    # 1. Check NPS 80CCD(1B) room (Cap ₹50k)
    current_80ccd1b = min(data.deduction_80ccd1b, 50_000)
    remaining_80ccd1b_room = 50_000 - current_80ccd1b
    
    # 2. Check 80C room (Cap ₹1.5L)
    current_80c = min(data.deduction_80c, 150_000)
    remaining_80c_room = 150_000 - current_80c
    
    if remaining_80ccd1b_room <= 0 and remaining_80c_room <= 0:
        return None # No room to optimize further via these sections

    # Heuristic: If we invest X more in 80CCD1B, we save X * marginal_rate
    # Find marginal rate for Old regime
    marginal_rate = 0.0
    for limit, rate in settings.OLD_REGIME_SLABS:
        if comparison.old_regime.taxable_income <= limit:
            marginal_rate = rate
            break
    if marginal_rate == 0: marginal_rate = 0.05 # Default to lowest if not found
    
    # Try NPS first as it's often the easiest "extra" deduction
    if remaining_80ccd1b_room > 0:
        # How much investment needed to cover the tax_diff?
        # investment * marginal_rate * (1 + cess) ≈ tax_diff
        needed = tax_diff / (marginal_rate * 1.04)
        if needed <= remaining_80ccd1b_room:
            return OptimizationStrategy(
                current_regime="New",
                target_regime="Old",
                additional_investment_needed=round(needed, 0),
                investment_category="NPS (Section 80CCD(1B))",
                potential_savings=round(tax_diff, 0),
                is_feasible=True,
                message=(
                    f"By investing an additional ₹{needed:,.0f} in NPS, you can switch to the Old Regime "
                    f"and potentially save more in total taxes than the New Regime."
                )
            )

    return None

def compare_regimes(data: Form16Data) -> TaxComparison:
    """
    Calculate Old and New regime taxes, compare them, and recommend the best one.
    Also adds an optimization strategy if applicable.
    """
    old = calculate_old_regime(data)
    new = calculate_new_regime(data)

    if old.total_tax_payable <= new.total_tax_payable:
        recommended = "Old"
        savings = round(new.total_tax_payable - old.total_tax_payable, 2)
        reason = (
            f"The Old Regime saves you ₹{savings:,.0f} because your total deductions "
            f"(₹{old.total_deductions:,.0f}) exceed the benefit provided by the New Regime's "
            f"lower slabs."
        )
    else:
        recommended = "New"
        savings = round(old.total_tax_payable - new.total_tax_payable, 2)
        reason = (
            f"The New Regime saves you ₹{savings:,.0f}. Your current deduction claims "
            f"(₹{old.total_deductions:,.0f}) are not enough to beat the lower New Regime rates."
        )

    comparison = TaxComparison(
        old_regime=old,
        new_regime=new,
        recommended_regime=recommended,
        savings_with_recommended=savings,
        recommendation_reason=reason,
    )
    
    comparison.optimization_strategy = calculate_optimization(data, comparison)
    return comparison


# ── CLI demo ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Dummy data for testing
    sample = Form16Data(
        employer_name="TechSoft India Pvt Ltd",
        employee_name="Arjun Sharma",
        pan="ABCDE1234F",
        assessment_year="2025-26",
        gross_salary=1_200_000,
        hra_received=240_000,
        basic_salary=600_000,
        hra_exempt=144_000,
        deduction_80c=150_000,
        deduction_80d=25_000,
        deduction_80ccd1b=50_000,
        professional_tax=2_400,
        tds_deducted=90_000,
    )

    comparison = compare_regimes(sample)
    print(f"\n{'='*60}")
    print(f"TAX COMPARISON FOR {sample.employee_name}")
    print(f"{'='*60}")
    print(f"Old Regime  → Total Tax: ₹{comparison.old_regime.total_tax_payable:>12,.2f}  "
          f"(Effective: {comparison.old_regime.effective_tax_rate}%)")
    print(f"New Regime  → Total Tax: ₹{comparison.new_regime.total_tax_payable:>12,.2f}  "
          f"(Effective: {comparison.new_regime.effective_tax_rate}%)")
    print(f"\n✅ Recommendation: {comparison.recommended_regime} Regime")
    print(f"   Annual Saving: ₹{comparison.savings_with_recommended:,.2f}")
    print(f"\n   Reason: {comparison.recommendation_reason}")
