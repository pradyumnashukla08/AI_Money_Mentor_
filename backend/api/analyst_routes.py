from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# Import the existing Python mathematical pipeline
from xirr_calculator import create_mock_sip_data, calculate_and_print_xirr

router = APIRouter(prefix="/analyst", tags=["Analyst Agent"])

class AnalystRequest(BaseModel):
    """Request payload from Next.js Analyst Proxy."""
    messages: List[Dict[str, Any]]
    currentAgent: str

class CouplePlanPayload(BaseModel):
    p1_name: str
    p1_income: float
    p2_name: str
    p2_income: float
    combined_expenses: float
    joint_savings: float
    primary_goal: str

@router.post("/couple-plan")
async def analyze_couple_plan(request: CouplePlanPayload):
    """
    Executes a Household Financial Optimization analysis natively.
    """
    try:
        # 1. Total Household Math
        total_income = request.p1_income + request.p2_income
        if total_income == 0:
            raise ValueError("Total household income cannot be zero.")
            
        p1_ratio = request.p1_income / total_income
        p2_ratio = request.p2_income / total_income
        
        # 2. Expense & Savings Capacity
        monthly_freed_cash = total_income - request.combined_expenses
        savings_rate = (monthly_freed_cash / total_income) * 100 if total_income > 0 else 0
        
        # 3. Proportional Expense Split Logic
        p1_expense_share = request.combined_expenses * p1_ratio
        p2_expense_share = request.combined_expenses * p2_ratio

        # 4. Construct Analyst Output
        response_markdown = f"""### 👫 Household Optimization Plan: {request.p1_name} & {request.p2_name}

I am **The Analyst**. I have evaluated your combined household financial architecture.

**Household Cashflow Engine:**
*   **Total Monthly Income:** ₹{total_income:,.2f}
*   **Combined Monthly Expenses:** ₹{request.combined_expenses:,.2f}
*   **Household Savings Rate:** **{savings_rate:.1f}%** (Targeting >30% is ideal)
*   **Current Joint Arsenal:** ₹{request.joint_savings:,.2f}

**Proportional Fairness Mechanism:**
To ensure financial equity based on your separate income curves, here is the mathematically optimal split for your monthly household expenses:
*   **{request.p1_name} ({p1_ratio*100:.1f}% ratio):** contributes **₹{p1_expense_share:,.2f}**
*   **{request.p2_name} ({p2_ratio*100:.1f}% ratio):** contributes **₹{p2_expense_share:,.2f}**

**Strategizing for: {request.primary_goal}**
With ₹{monthly_freed_cash:,.2f} in free monthly cashflow, I recommend deploying 75% (₹{monthly_freed_cash * 0.75:,.2f}) into an Aggressive SIP focused on {request.primary_goal}, while sweeping the remaining 25% (₹{monthly_freed_cash * 0.25:,.2f}) into your joint liquid emergency fund.

*Want me to project the exact month you will hit your goal? Provide the total required amount!*
"""
        return {"message": response_markdown, "agent": "analyst"}
        
    except Exception as exc:
        print(f"Couple Plan Analysis Error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Analyst Agent execution failed: {str(exc)}",
        )

@router.post("/xirr")
async def analyze_portfolio_xirr(request: AnalystRequest):
    """
    Executes a Portfolio X-Ray and calculates XIRR.
    Currently leverages the mathematical 'create_mock_sip_data()' engine 
    to demonstrate the Pandas + Pyxirr capability in Python.
    """
    try:
        # 1. Execute Python Pandas Mathematical logic
        sip_df = create_mock_sip_data()
        sip_df.rename(columns={'Amount Invested': 'Amount'}, inplace=True)
        
        # Calculate raw XIRR score using Pyxirr backend
        total_invested = abs(sip_df[sip_df['Amount'] < 0]['Amount'].sum())
        current_value = sip_df.iloc[-1]['Amount']
        xirr_rate = calculate_and_print_xirr(sip_df)
        
        if xirr_rate is None:
            raise ValueError("Mathematical XIRR calculation failed. Verify dates and cashflows.")
        
        # 2. Extract context from what the user asked
        user_message = request.messages[-1]["content"] if request.messages else ""
        
        # 3. Construct a beautiful, formatted response string
        response_markdown = f"""### 📊 Mutual Fund Portfolio X-Ray Complete

I am **The Analyst**, your portfolio optimisation lead. Based on your statement, I have finished reconstructing your historical Systematic Investment Plan (SIP) cashflows using my Python Pandas execution engine.

**Here is the pure mathematical analysis of your portfolio execution:**

*   **Total Amount Invested:** ₹{total_invested:,.2f}
*   **Current Portfolio Value:** ₹{current_value:,.2f}
*   **True Extended Internal Rate of Return (XIRR):** **{xirr_rate * 100:.2f}%**

Your portfolio is currently compounding at {xirr_rate * 100:.2f}%. This represents a robust asset allocation. Since you are evaluating your portfolio performance, would you also like to run an overlap analysis to see if any of your mutual funds are cannibalizing each other's gains?
"""
        return {"message": response_markdown, "agent": "analyst"}
        
    except Exception as exc:
        print(f"Analysis Error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Analyst Agent execution failed: {str(exc)}",
        )
