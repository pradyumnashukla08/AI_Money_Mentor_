"""
The Strategist Agent — Wealth & Life Planning Lead.

Orchestrates the financial math engine and LLM to provide:
1. FIRE Path Planning with personalised narrative roadmaps
2. Life Event Advisory with risk-aware recommendations

This is the main agent class that Person 1's Orchestrator will interact with.
"""

import json
import logging
from typing import Optional, TypedDict, List

from models.profile import UserProfile, FireGoal, RiskTolerance  # type: ignore
from models.events import LifeEvent, LifeEventType, LifeEventAdvice  # type: ignore
from engine.compounding import future_value, real_return, inflation_adjusted_value  # type: ignore
from engine.sip import sip_future_value, sip_required, step_up_sip  # type: ignore
from engine.fire import (  # type: ignore
    fire_target_corpus,
    years_to_fire,
    coast_fire_number,
    generate_monthly_roadmap,
)
from llm.client import generate_response, generate_structured_response  # type: ignore
from llm.prompts import (  # type: ignore
    FIRE_ROADMAP_SYSTEM_PROMPT,
    FIRE_ROADMAP_USER_PROMPT,
    LIFE_EVENT_ADVISOR_SYSTEM_PROMPT,
    LIFE_EVENT_ADVISOR_USER_PROMPT,
    EVENT_CLASSIFIER_SYSTEM_PROMPT,
    EVENT_CLASSIFIER_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def format_inr(amount: float) -> str:
    """Format a large number into Indian system (Lakhs/Crores) for the LLM."""
    if amount >= 10_000_000:
        return f"{amount/10_000_000:.2f} Crores"
    elif amount >= 100_000:
        return f"{amount/100_000:.2f} Lakhs"
    return f"{amount:,.0f}"


class RiskProfileData(TypedDict):
    equity_pct: float
    expected_return: float
    instruments: List[str]


class StrategistAgent:
    """
    The Strategist AI Agent for wealth management and life planning.

    Combines deterministic financial calculations with LLM-powered
    personalised storytelling to deliver actionable financial advice.
    """

    # Risk-appropriate return rate assumptions for India
    RISK_RETURN_MAP: dict[RiskTolerance, RiskProfileData] = {
        RiskTolerance.CONSERVATIVE: {
            "equity_pct": 0.20,
            "expected_return": 0.08,
            "instruments": [
                "PPF (Public Provident Fund)",
                "Bank Fixed Deposits",
                "Debt Mutual Funds",
                "RBI Bonds",
                "Post Office Schemes",
            ],
        },
        RiskTolerance.MODERATE: {
            "equity_pct": 0.60,
            "expected_return": 0.11,
            "instruments": [
                "Hybrid / Balanced Mutual Funds",
                "Large-Cap Equity Funds",
                "NPS (National Pension System)",
                "ELSS Tax Saver Funds",
                "Corporate Bonds",
            ],
        },
        RiskTolerance.AGGRESSIVE: {
            "equity_pct": 0.80,
            "expected_return": 0.14,
            "instruments": [
                "Small-Cap & Mid-Cap Funds",
                "Index Funds (Nifty 50, Nifty Next 50)",
                "Sectoral / Thematic Funds",
                "Direct Equity",
                "ELSS with high-growth orientation",
            ],
        },
    }

    def plan_fire_path(
        self,
        profile: UserProfile,
        goal: FireGoal,
    ) -> dict:
        """
        Generates a complete FIRE plan with math projections and narrative.
        """
        years_until_fire = goal.target_retirement_age - profile.age
        if years_until_fire <= 0:
            return {
                "error": "Target retirement age must be greater than current age.",
                "current_age": profile.age,
                "target_age": goal.target_retirement_age,
            }

        # target corpus
        corpus_data = fire_target_corpus(
            annual_expenses=profile.annual_expenses,
            withdrawal_rate=goal.withdrawal_rate,
            inflation_rate=goal.inflation_rate,
            years_to_retirement=years_until_fire,
        )

        # years to FIRE
        monthly_investment = max(
            profile.existing_monthly_sip,
            profile.monthly_surplus * 0.5,  # Suggest investing at least 50% of surplus
        )
        estimated_years = years_to_fire(
            current_savings=profile.current_savings,
            monthly_investment=monthly_investment,
            annual_return=goal.expected_return_rate,
            fire_corpus=corpus_data["corpus_at_retirement"],
        )

        # coast FIRE
        coast_fire = coast_fire_number(
            target_corpus=corpus_data["corpus_at_retirement"],
            annual_return=goal.expected_return_rate,
            years_to_retirement=years_until_fire,
        )

        # generate roadmap
        roadmap = generate_monthly_roadmap(
            current_age=profile.age,
            current_savings=profile.current_savings,
            monthly_sip=monthly_investment,
            annual_return=goal.expected_return_rate,
            fire_corpus=corpus_data["corpus_at_retirement"],
            annual_step_up_pct=0.10,  # Assume 10% annual SIP step-up
            inflation_rate=goal.inflation_rate,
        )

        # Extract milestones for the LLM prompt
        milestones = [
            entry for entry in roadmap if "milestone" in entry
        ]
        milestones_text = "\n".join(
            f"- Month {m['month']} (Age {m['age']}): {m['milestone']} "
            f"— Corpus: ₹{format_inr(m['corpus'])}"
            for m in milestones
        )
        if not milestones_text:
            milestones_text = "No milestones reached within projection period."

        fire_age = round(profile.age + estimated_years, 1)

        # LLM narrative
        try:
            prompt = FIRE_ROADMAP_USER_PROMPT.format(
                name=profile.name,
                age=profile.age,
                monthly_income=profile.monthly_income,
                monthly_expenses=profile.monthly_expenses,
                monthly_surplus=profile.monthly_surplus,
                savings_rate=profile.savings_rate,
                current_savings=profile.current_savings,
                existing_monthly_sip=profile.existing_monthly_sip,
                risk_tolerance=profile.risk_tolerance.value,
                life_stage=profile.life_stage.value,
                target_retirement_age=goal.target_retirement_age,
                desired_monthly_expense=goal.desired_monthly_expense,
                withdrawal_rate=goal.withdrawal_rate,
                expected_return_rate=goal.expected_return_rate,
                inflation_rate=goal.inflation_rate,
                corpus_today=format_inr(corpus_data["corpus_today"]),
                corpus_at_retirement=format_inr(corpus_data["corpus_at_retirement"]),
                inflated_annual_expense=format_inr(corpus_data["inflated_annual_expense"]),
                years_to_fire=estimated_years,
                fire_age=fire_age,
                coast_fire=format_inr(coast_fire),
                milestones=milestones_text,
            )
            narrative = generate_response(
                prompt=prompt,
                system_prompt=FIRE_ROADMAP_SYSTEM_PROMPT,
                temperature=0.7,
            )
        except Exception as exc:
            logger.warning("LLM narrative generation failed: %s", exc)
            narrative = (
                "Unable to generate personalised narrative at this time. "
                "Please review the computed data below."
            )

        # Compute additional insights
        risk_info = self.RISK_RETURN_MAP.get(
            profile.risk_tolerance, self.RISK_RETURN_MAP[RiskTolerance.MODERATE]
        )
        sip_needed = sip_required(
            target_amount=corpus_data["corpus_at_retirement"],
            annual_rate=goal.expected_return_rate,
            years=years_until_fire,
        )

        return {
            "profile_summary": {
                "name": profile.name,
                "age": profile.age,
                "monthly_surplus": round(profile.monthly_surplus, 2),
                "savings_rate": round(profile.savings_rate, 2),
            },
            "fire_target": corpus_data,
            "estimated_years_to_fire": estimated_years,
            "fire_achievement_age": fire_age,
            "coast_fire_number": coast_fire,
            "suggested_monthly_sip": round(monthly_investment, 2),  # pyre-ignore
            "minimum_sip_needed": sip_needed,
            "recommended_instruments": risk_info["instruments"],
            "roadmap_summary": {
                "total_months": len(roadmap),
                "milestones": milestones,
                "first_entry": roadmap[0] if roadmap else None,
                "last_entry": roadmap[-1] if roadmap else None,
            },
            "full_roadmap": roadmap,
            "narrative": narrative,
        }

    def advise_on_event(
        self,
        profile: UserProfile,
        event_text: str,
    ) -> LifeEventAdvice:
        """
        Provide personalised financial advice for a life event.
        """
        event = self._classify_event(event_text)

        risk_assessment = self._assess_risk_impact(profile, event)


        event_amount_str = (
            f"₹{event.amount:,.0f}" if event.amount else "Not specified"
        )

        try:
            prompt = LIFE_EVENT_ADVISOR_USER_PROMPT.format(
                event_description=event.description,
                event_type=event.event_type.value,
                event_amount=event_amount_str,
                name=profile.name,
                age=profile.age,
                monthly_income=profile.monthly_income,
                monthly_expenses=profile.monthly_expenses,
                monthly_surplus=profile.monthly_surplus,
                current_savings=profile.current_savings,
                existing_monthly_sip=profile.existing_monthly_sip,
                risk_tolerance=profile.risk_tolerance.value,
                life_stage=profile.life_stage.value,
            )
            narrative = generate_response(
                prompt=prompt,
                system_prompt=LIFE_EVENT_ADVISOR_SYSTEM_PROMPT,
                temperature=0.7,
            )
        except Exception as exc:
            logger.warning("LLM event advice generation failed: %s", exc)
            narrative = (
                "Unable to generate detailed advice at this time. "
                "Please consult a certified financial planner."
            )

        immediate_actions = self._get_immediate_actions(profile, event)
        short_term_plan = self._get_short_term_plan(profile, event)
        long_term_impact = self._get_long_term_impact(profile, event)

        return LifeEventAdvice(
            event=event,
            risk_assessment=risk_assessment,
            immediate_actions=immediate_actions,
            short_term_plan=short_term_plan,
            long_term_impact=long_term_impact,
            narrative=narrative,
        )

    def _classify_event(self, event_text: str) -> LifeEvent:
        """
        Use the LLM to classify free-text into a structured LifeEvent.

        Falls back to LifeEventType.OTHER if classification fails.
        """
        try:
            response = generate_structured_response(
                prompt=EVENT_CLASSIFIER_USER_PROMPT.format(
                    user_message=event_text
                ),
                system_prompt=EVENT_CLASSIFIER_SYSTEM_PROMPT,
                temperature=0.1,
            )

            # Parse the JSON response
            # Strip any markdown code fences the LLM might add
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)

            event_type = LifeEventType(parsed.get("event_type", "other"))
            summary = parsed.get("summary", event_text)
            
            amount_val = None
            amount_text = parsed.get("amount_text") or parsed.get("amount")
            if amount_text:
                text_lower = str(amount_text).lower().replace(",", "")
                import re
                match = re.search(r"([\d\.]+)\s*(lakh|lak|l|crore|cr|k)", text_lower)
                if match:
                    val = float(match.group(1))
                    unit = match.group(2)
                    if unit in ("lakh", "lak", "l"):
                        amount_val = val * 100000
                    elif unit in ("crore", "cr"):
                        amount_val = val * 10000000
                    elif unit == "k":
                        amount_val = val * 1000
                else:
                    num_match = re.search(r"([\d]+)", text_lower)
                    if num_match:
                        amount_val = float(num_match.group(1))

            return LifeEvent(
                event_type=event_type,
                description=summary,
                amount=amount_val,
            )
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning("Event classification failed: %s", exc)
            return LifeEvent(
                event_type=LifeEventType.OTHER,
                description=event_text,
                amount=None,
            )

    def _assess_risk_impact(
        self, profile: UserProfile, event: LifeEvent
    ) -> str:
        """
        Evaluate how the life event interacts with the user's risk profile.
        Returns a human-readable risk assessment.
        """
        risk = profile.risk_tolerance
        event_type = event.event_type

        # Events that should trigger risk reassessment
        risk_increasing_events = {
            LifeEventType.BONUS,
            LifeEventType.INHERITANCE,
            LifeEventType.SALARY_HIKE,
        }
        risk_decreasing_events = {
            LifeEventType.JOB_LOSS,
            LifeEventType.MEDICAL_EMERGENCY,
            LifeEventType.NEW_BABY,
            LifeEventType.MARRIAGE,
        }

        if event_type in risk_decreasing_events:
            if risk == RiskTolerance.AGGRESSIVE:
                return (
                    f"Given this {event_type.value} event, your current AGGRESSIVE "
                    f"risk profile may need temporary adjustment. Consider shifting "
                    f"some equity allocation to safer instruments (debt funds, FDs) "
                    f"until your situation stabilises. Your emergency fund should "
                    f"cover at least 6 months of expenses."
                )
            elif risk == RiskTolerance.MODERATE:
                return (
                    f"Your MODERATE risk profile is reasonable, but this "
                    f"{event_type.value} event warrants building a larger emergency "
                    f"buffer. Ensure you have 6-9 months' expenses in liquid form "
                    f"before continuing equity SIPs."
                )
            else:
                return (
                    f"Your CONSERVATIVE risk profile is well-suited for this period. "
                    f"Focus on maintaining liquidity and your emergency fund. "
                    f"This is the right time to stay the course with safe instruments."
                )

        elif event_type in risk_increasing_events:
            amount_context = ""
            if event.amount:
                months_of_expenses = event.amount / profile.monthly_expenses
                amount_context = (
                    f" This amount covers approximately "
                    f"{months_of_expenses:.1f} months of your expenses."
                )

            if risk == RiskTolerance.CONSERVATIVE:
                return (
                    f"This {event_type.value} is a great opportunity!{amount_context} "
                    f"While your CONSERVATIVE profile suggests safety-first, consider "
                    f"allocating a portion to equity (e.g., 20-30%) for better "
                    f"long-term growth, while keeping the majority in PPF/FDs."
                )
            elif risk == RiskTolerance.MODERATE:
                return (
                    f"Excellent — this {event_type.value} strengthens your position."
                    f"{amount_context} Your MODERATE profile allows a balanced "
                    f"deployment: consider 60% in equity SIPs and 40% in debt "
                    f"instruments."
                )
            else:
                return (
                    f"Great news! This {event_type.value} accelerates your journey."
                    f"{amount_context} With your AGGRESSIVE profile, you can deploy "
                    f"this into growth-oriented equity funds, but ensure your "
                    f"emergency fund (6 months' expenses) is fully funded first."
                )

        else:
            return (
                f"This {event_type.value} event requires careful planning. "
                f"Given your {risk.value} risk profile, maintain your current "
                f"investment allocation while addressing the specific financial "
                f"needs of this event."
            )

    def _get_immediate_actions(
        self, profile: UserProfile, event: LifeEvent
    ) -> list[str]:
        """
        Generate rule-based immediate action items (within 30 days)
        based on event type and risk profile.
        """
        actions = []
        risk = profile.risk_tolerance
        risk_info = self.RISK_RETURN_MAP.get(risk, self.RISK_RETURN_MAP[RiskTolerance.MODERATE])

        # Emergency fund check (universal)
        emergency_fund_months = (
            profile.current_savings / profile.monthly_expenses
            if profile.monthly_expenses > 0
            else 0
        )

        if event.event_type == LifeEventType.BONUS:
            amount = event.amount or profile.monthly_income
            actions.append(
                f"Park the bonus in a liquid fund or savings account immediately "
                f"— do not make impulsive large purchases."
            )
            if emergency_fund_months < 6:
                shortfall = (6 * profile.monthly_expenses) - profile.current_savings
                actions.append(
                    f"Top up your emergency fund by ₹{shortfall:,.0f} to reach "
                    f"6 months' coverage."
                )
            actions.append(
                f"Allocate funds across: {', '.join(risk_info['instruments'][:3])}"  # type: ignore
            )
            actions.append(
                "If you have any high-interest debt (credit cards, personal loans), "
                "pay it off first."
            )

        elif event.event_type == LifeEventType.JOB_LOSS:
            actions.append(
                "Immediately review your monthly expenses and cut non-essentials."
            )
            actions.append(
                "Pause all equity SIPs — redirect that amount to your "
                "emergency fund."
            )
            actions.append(
                "Do NOT redeem long-term investments impulsively. Use your "
                "emergency fund first."
            )
            actions.append(
                "Review your health insurance — ensure it remains active "
                "even without employer coverage."
            )

        elif event.event_type == LifeEventType.MARRIAGE:
            actions.append(
                "Create a combined budget with your partner to understand "
                "joint monthly cash flows."
            )
            actions.append(
                "Review and update nominee details on all financial instruments "
                "(MFs, insurance, bank accounts)."
            )
            actions.append(
                "Get term life insurance (if not already covered) — both partners."
            )
            actions.append(
                "Start a joint emergency fund targeting 6 months of "
                "combined expenses."
            )

        elif event.event_type == LifeEventType.NEW_BABY:
            actions.append(
                "Start a dedicated child education fund — consider a "
                "Sukanya Samriddhi Yojana (for daughters) or an ELSS SIP."
            )
            actions.append(
                "Review health insurance to add the newborn as a dependent."
            )
            actions.append(
                "Increase term life insurance coverage to account for "
                "the child's future needs."
            )
            actions.append(
                f"Adjust monthly budget — new baby expenses typically add "
                f"₹10,000-₹25,000/month."
            )

        elif event.event_type == LifeEventType.SALARY_HIKE:
            actions.append(
                "Increase SIP amounts proportionally to your salary hike — "
                "avoid lifestyle inflation."
            )
            actions.append(
                "If your new salary crosses ₹50,000/month, review NPS "
                "contribution for additional 80CCD(1B) benefit."
            )
            actions.append(
                f"Recommended instruments: {', '.join(risk_info['instruments'][:3])}"  # type: ignore
            )

        elif event.event_type == LifeEventType.HOME_PURCHASE:
            actions.append(
                "Compare home loan interest rates across at least 3-4 lenders."
            )
            actions.append(
                "Ensure the EMI does not exceed 40% of your net monthly income."
            )
            actions.append(
                "Maintain your emergency fund — do not liquidate it for "
                "the down payment."
            )
            actions.append(
                "Claim HRA exemption if applicable, and plan for Section 24 "
                "home loan interest deduction."
            )

        elif event.event_type == LifeEventType.MEDICAL_EMERGENCY:
            actions.append(
                "Use your health insurance first. File claims immediately."
            )
            actions.append(
                "If insurance is insufficient, use emergency fund before "
                "touching investments."
            )
            actions.append(
                "As a last resort, withdraw from FDs or debt funds "
                "(not equity — avoid selling at a loss)."
            )
            actions.append(
                "After recovery, review and upgrade your health insurance "
                "coverage."
            )

        else:
            actions.append(
                "Review your current financial plan in light of this event."
            )
            actions.append(
                "Ensure your emergency fund is adequately funded (6 months' expenses)."
            )
            actions.append(
                "Consult a certified financial planner for personalised advice."
            )

        return actions

    def _get_short_term_plan(
        self, profile: UserProfile, event: LifeEvent
    ) -> list[str]:
        """
        Generate rule-based short-term actions (3-6 months)
        based on event type and risk profile.
        """
        plans = []
        risk_info = self.RISK_RETURN_MAP.get(
            profile.risk_tolerance,
            self.RISK_RETURN_MAP[RiskTolerance.MODERATE],
        )

        if event.event_type == LifeEventType.BONUS:
            plans.append(
                "Stagger the bonus investment over 3 months via STP "
                "(Systematic Transfer Plan) from liquid fund to equity."
            )
            plans.append(
                "Re-evaluate your FIRE timeline — this bonus could "
                "accelerate it significantly."
            )

        elif event.event_type == LifeEventType.JOB_LOSS:
            plans.append(
                "Renegotiate any existing loans for lower EMIs or moratorium."
            )
            plans.append(
                "Once re-employed, gradually restart SIPs with a 20% "
                "step-up to catch up."
            )
            plans.append(
                "Review your skill set and consider upskilling investments."
            )

        elif event.event_type == LifeEventType.MARRIAGE:
            plans.append(
                "Optimise tax filing — check if spouse's income allows "
                "HRA / Section 80C splitting."
            )
            plans.append(
                "Set joint financial goals and plan SIPs together."
            )
            plans.append(
                "Review and consolidate duplicate insurance policies."
            )

        elif event.event_type == LifeEventType.NEW_BABY:
            plans.append(
                "Start a ₹5,000-₹10,000/month SIP in a large-cap or "
                "flexi-cap fund for the child's education (15-18 year horizon)."
            )
            plans.append(
                "Look into Sukanya Samriddhi or PPF for guaranteed-return "
                "component of the education fund."
            )

        elif event.event_type == LifeEventType.SALARY_HIKE:
            plans.append(
                "Redirect at least 50% of the salary increment to investments."
            )
            plans.append(
                "Consider starting NPS for additional tax benefits under "
                "Section 80CCD(1B) — up to ₹50,000 extra deduction."
            )

        elif event.event_type == LifeEventType.HOME_PURCHASE:
            plans.append(
                "Set up a dedicated home loan prepayment fund — even "
                "₹5,000/month extra can save years of interest."
            )
            plans.append(
                "Rebuild your emergency fund if it was used for the down payment."
            )

        else:
            plans.append(
                "Monitor your investments monthly for the next quarter."
            )
            plans.append(
                f"Consider diversifying into: {', '.join(risk_info['instruments'][:2])}"  # type: ignore
            )

        return plans

    def _get_long_term_impact(
        self, profile: UserProfile, event: LifeEvent
    ) -> str:
        """
        Assess the long-term financial impact of the event.
        """
        if event.event_type == LifeEventType.BONUS and event.amount:
            # Calculate how this bonus grows if invested
            growth = future_value(event.amount, 0.12, 10)
            return (
                f"If invested wisely, this bonus of ₹{event.amount:,.0f} could "
                f"grow to approximately ₹{growth:,.0f} in 10 years at 12% returns. "
                f"This could significantly accelerate your FIRE timeline."
            )

        elif event.event_type == LifeEventType.JOB_LOSS:
            months_covered = (
                profile.current_savings / profile.monthly_expenses
                if profile.monthly_expenses > 0
                else 0
            )
            return (
                f"Your emergency fund currently covers {months_covered:.1f} months. "
                f"A job loss temporarily pauses wealth building, but the key is to "
                f"protect existing investments. Historical data shows that those who "
                f"don't panic-sell recover fully within 1-2 years."
            )

        elif event.event_type == LifeEventType.MARRIAGE:
            return (
                "Marriage is a financial multiplier — dual incomes can dramatically "
                "accelerate your FIRE journey. Combined tax planning (HRA splits, "
                "Section 80C optimisation across both PAN cards) can save "
                "₹50,000-₹1,00,000 annually."
            )

        elif event.event_type == LifeEventType.NEW_BABY:
            education_cost = future_value(2000000, 0.08, 18)  # ₹20L today inflated
            return (
                f"A child's higher education in India could cost approximately "
                f"₹{education_cost:,.0f} in 18 years (assuming ₹20 Lakhs today "
                f"at 8% education inflation). Starting early makes the SIP "
                f"requirement very manageable."
            )

        elif event.event_type == LifeEventType.HOME_PURCHASE and event.amount:
            return (
                f"A home purchase of ₹{event.amount:,.0f} shifts your net worth "
                f"composition heavily towards real estate. Ensure you maintain "
                f"financial asset allocation (MFs, stocks) alongside the property. "
                f"Property is illiquid and should not be your only wealth."
            )

        elif event.event_type == LifeEventType.SALARY_HIKE:
            return (
                "A salary hike is the best opportunity to increase your savings rate "
                "without feeling the pinch. If you redirect 50-70% of the increment "
                "to investments, you maintain your lifestyle while accelerating "
                "wealth creation."
            )

        else:
            return (
                "Every life event is an opportunity to reassess and optimise your "
                "financial plan. Stay disciplined with your SIPs and ensure your "
                "emergency fund remains healthy."
            )
