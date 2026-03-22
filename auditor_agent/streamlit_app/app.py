"""
app.py — Streamlit UI for the AI Money Mentor Auditor Agent.

Two-page interactive app:
  🧾 Tax Wizard   — Upload Form 16 PDF → Old vs New regime analysis
  💚 Health Score — 15-question quiz  → 6-dimension wellness score
"""

import sys
import os
import json
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Money Mentor — Auditor Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: white;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .block-container { padding-top: 2rem; }

/* Main background */
.main .block-container {
    background: #0d1117;
    padding: 2rem 2.5rem;
    border-radius: 16px;
}
body { background-color: #0d1117; color: #e6edf3; }

/* Cards */
.metric-card {
    background: linear-gradient(135deg, #1a1f3c 0%, #16213e 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.metric-card h3 { margin: 0; font-size: 0.85rem; color: #8b949e; font-weight: 500; }
.metric-card h2 { margin: 0.3rem 0 0; font-size: 1.6rem; font-weight: 700; color: #e6edf3; }

/* Recommendation box */
.recommend-box {
    background: linear-gradient(135deg, #0d3b2e 0%, #0a4a3a 100%);
    border-left: 4px solid #2ecc71;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin: 1rem 0;
}
.recommend-box.warn {
    background: linear-gradient(135deg, #3b2e0d 0%, #4a3a0a 100%);
    border-left-color: #f1c40f;
}

/* Score badge */
.score-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    margin-left: 0.5rem;
}

/* Progress bar — custom */
.dim-row {
    margin: 0.6rem 0;
}
.dim-label { font-weight: 600; color: #c9d1d9; margin-bottom: 0.25rem; }

/* Section headers */
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e6edf3;
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #30363d;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed #30363d !important;
    border-radius: 12px !important;
    background: #161b22 !important;
}

/* Hide default header */
header[data-testid="stHeader"] { display: none !important; }

/* Quick tip boxes */
.tip-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-top: 0.6rem;
    font-size: 0.88rem;
    color: #8b949e;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar navigation ───────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 💰 AI Money Mentor")
    st.markdown("##### The Auditor Agent")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🧾 Tax Wizard", "💚 Money Health Score"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#8b949e'>Powered by Groq · LLaMA 3 8B<br>"
        "Tax rules: FY 2025-26</small>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — TAX WIZARD
# ════════════════════════════════════════════════════════════════════════════

def fmt_inr(amount: float) -> str:
    """Format a number as Indian Rupees."""
    if amount == 0:
        return "₹0"
    return f"₹{amount:,.0f}"


def tax_wizard_page():
    st.markdown("# 🧾 Tax Wizard")
    st.markdown(
        "Upload your **Form 16 PDF** and instantly discover whether the "
        "**Old** or **New** tax regime saves you more money."
    )

    tab1, tab2 = st.tabs(["📁 Upload Form 16", "✏️ Enter Manually"])

    # ── Tab 1: PDF Upload ────────────────────────────────────────────────────
    with tab1:
        uploaded = st.file_uploader(
            "Drop your Form 16 PDF here",
            type=["pdf"],
            help="Both Part A and Part B are supported. Scanned PDFs are handled via OCR.",
        )

        if uploaded:
            with st.spinner("🔍 Extracting data from your Form 16..."):
                response = requests.post(
                    f"{API_BASE}/api/tax-wizard/upload",
                    files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
                    timeout=120,
                )

            if response.status_code == 200:
                data = response.json()
                _render_tax_results(data["extracted_data"], data["tax_comparison"])
            else:
                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")

    # ── Tab 2: Manual Entry ──────────────────────────────────────────────────
    with tab2:
        st.markdown("##### Enter your income and deduction details")
        with st.form("manual_tax_form"):
            col1, col2 = st.columns(2)
            with col1:
                gross_salary = st.number_input("Annual Gross Salary (₹)", min_value=0, step=10000, value=1200000)
                hra_received = st.number_input("HRA Received (₹)", min_value=0, step=5000, value=240000)
                hra_exempt   = st.number_input("HRA Exempt u/s 10(13A) (₹)", min_value=0, step=5000, value=144000)
                lta_exempt   = st.number_input("LTA Exempt u/s 10(5) (₹)", min_value=0, step=1000, value=0)
                professional_tax = st.number_input("Professional Tax (₹/yr)", min_value=0, step=200, value=2400)
            with col2:
                deduction_80c    = st.number_input("80C (EPF/PPF/ELSS) (₹, max 1.5L)", min_value=0, max_value=150000, step=5000, value=150000)
                deduction_80d    = st.number_input("80D (Health Insurance) (₹)", min_value=0, step=1000, value=25000)
                deduction_80ccd1b= st.number_input("80CCD(1B) NPS (₹, max 50k)", min_value=0, max_value=50000, step=5000, value=50000)
                deduction_80ccd2 = st.number_input("80CCD(2) Employer NPS (₹)", min_value=0, step=5000, value=0)
                home_loan        = st.number_input("Home Loan Interest 24(b) (₹, max 2L)", min_value=0, max_value=200000, step=10000, value=0)
                tds_deducted     = st.number_input("TDS Already Deducted (₹)", min_value=0, step=5000, value=90000)

            submitted = st.form_submit_button("🔍 Calculate Tax Comparison", use_container_width=True)

        if submitted:
            payload = {
                "gross_salary": gross_salary,
                "hra_received": hra_received,
                "hra_exempt": hra_exempt,
                "lta_exempt": lta_exempt,
                "professional_tax": professional_tax,
                "deduction_80c": deduction_80c,
                "deduction_80d": deduction_80d,
                "deduction_80ccd1b": deduction_80ccd1b,
                "deduction_80ccd2": deduction_80ccd2,
                "deduction_home_loan_interest": home_loan,
                "tds_deducted": tds_deducted,
            }
            with st.spinner("🧮 Calculating your tax..."):
                response = requests.post(
                    f"{API_BASE}/api/tax-wizard/manual",
                    json=payload,
                    timeout=30,
                )
            if response.status_code == 200:
                data = response.json()
                _render_tax_results(data["input_data"], data["tax_comparison"])
            else:
                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")


def _render_tax_results(extracted: dict, comparison: dict):
    """Render the Old vs New regime comparison in a rich UI."""
    old = comparison["old_regime"]
    new = comparison["new_regime"]
    recommended = comparison["recommended_regime"]
    savings = comparison["savings_with_recommended"]
    reason  = comparison["recommendation_reason"]

    st.markdown("---")
    st.markdown('<div class="section-title">📊 Tax Regime Comparison</div>', unsafe_allow_html=True)

    # ── Summary metrics ──────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Gross Income</h3>
            <h2>{fmt_inr(old['gross_income'])}</h2>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Old Regime Tax</h3>
            <h2 style="color:#e74c3c">{fmt_inr(old['total_tax_payable'])}</h2>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>New Regime Tax</h3>
            <h2 style="color:#3498db">{fmt_inr(new['total_tax_payable'])}</h2>
        </div>""", unsafe_allow_html=True)
    with col4:
        color = "#2ecc71"
        st.markdown(f"""
        <div class="metric-card">
            <h3>You Save With {recommended}</h3>
            <h2 style="color:{color}">{fmt_inr(savings)}</h2>
        </div>""", unsafe_allow_html=True)

    # ── Recommendation box ───────────────────────────────────────────────────
    st.markdown(f"""
    <div class="recommend-box">
        <strong>✅ Recommended: {recommended} Regime</strong><br>
        <small>{reason}</small>
    </div>""", unsafe_allow_html=True)

    # ── Bar chart comparison ─────────────────────────────────────────────────
    fig = go.Figure()
    categories = ["Gross Income", "Taxable Income", "Total Tax", "Effective Rate (%)"]
    old_vals = [old['gross_income'], old['taxable_income'], old['total_tax_payable'], old['effective_tax_rate']]
    new_vals = [new['gross_income'], new['taxable_income'], new['total_tax_payable'], new['effective_tax_rate']]

    fig_bar = go.Figure(data=[
        go.Bar(name="Old Regime", x=["Taxable Income", "Total Tax Payable"], 
               y=[old['taxable_income'], old['total_tax_payable']],
               marker_color="#e74c3c", text=[fmt_inr(old['taxable_income']), fmt_inr(old['total_tax_payable'])],
               textposition="outside"),
        go.Bar(name="New Regime", x=["Taxable Income", "Total Tax Payable"],
               y=[new['taxable_income'], new['total_tax_payable']],
               marker_color="#3498db", text=[fmt_inr(new['taxable_income']), fmt_inr(new['total_tax_payable'])],
               textposition="outside"),
    ])
    fig_bar.update_layout(
        barmode="group",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3",
        font_family="Inter",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#30363d"),
        height=350,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Detailed slab breakdown ──────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Slab-wise Tax Breakdown</div>', unsafe_allow_html=True)
    col_old, col_new = st.columns(2)

    for col, regime_data, label, color in [
        (col_old, old, "Old Regime", "#e74c3c"),
        (col_new, new, "New Regime", "#3498db"),
    ]:
        with col:
            st.markdown(f"**{label}**")
            rows = []
            for slab in regime_data["slab_breakdown"]:
                if slab["taxable_in_slab"] > 0:
                    rows.append({
                        "Slab": slab["slab_label"],
                        "Income in Slab": fmt_inr(slab["taxable_in_slab"]),
                        "Tax": fmt_inr(slab["tax"]),
                    })
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, hide_index=True, use_container_width=True)

            st.markdown(f"""
            | Component | Amount |
            |---|---|
            | Base Tax | {fmt_inr(regime_data['base_tax'])} |
            | Rebate u/s 87A | -{fmt_inr(regime_data['rebate_87a'])} |
            | Surcharge | {fmt_inr(regime_data['surcharge'])} |
            | Health & Education Cess (4%) | {fmt_inr(regime_data['cess'])} |
            | **Total Tax Payable** | **{fmt_inr(regime_data['total_tax_payable'])}** |
            | TDS Deducted | -{fmt_inr(regime_data['tds_already_paid'])} |
            | **Tax Due / Refund** | **{fmt_inr(regime_data['tax_due_or_refund'])}** |
            | Effective Tax Rate | {regime_data['effective_tax_rate']}% |
            """)

    # ── Extracted data expander ──────────────────────────────────────────────
    with st.expander("🔍 View Extracted Form 16 Data", expanded=False):
        st.json(extracted)


# ════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — MONEY HEALTH SCORE
# ════════════════════════════════════════════════════════════════════════════

def health_score_page():
    st.markdown("# 💚 Money Health Score")
    st.markdown(
        "Answer **15 quick questions** (about 5 minutes) to get your personalised "
        "financial wellness score across **6 key dimensions** of your money life."
    )

    # ── Fetch questions from API ─────────────────────────────────────────────
    try:
        q_resp = requests.get(f"{API_BASE}/api/health-score/questions", timeout=10)
        questions = q_resp.json()["questions"]
    except Exception:
        st.error("⚠️ Could not connect to the backend. Make sure the FastAPI server is running on port 8000.")
        st.code("uvicorn auditor_agent.main:app --reload --port 8000", language="bash")
        return

    # ── Personal details ─────────────────────────────────────────────────────
    st.markdown("##### 👤 A little about you")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Your first name", value="", placeholder="e.g. Ram")
    with col2:
        age = st.number_input("Your age", min_value=18, max_value=75, value=28)
    with col3:
        monthly_income = st.number_input(
            "Monthly take-home income (₹)", min_value=0, step=5000, value=80000
        )

    st.markdown("---")

    # ── Group questions by dimension ─────────────────────────────────────────
    from collections import defaultdict
    dim_questions = defaultdict(list)
    for q in questions:
        dim_questions[q["dimension"]].append(q)

    DIMENSION_ICONS = {
        "Emergency Fund": "🛡️",
        "Debt Management": "💳",
        "Insurance Coverage": "🏥",
        "Investments & Savings": "📈",
        "Goal Clarity": "🎯",
        "Spending Habits": "💸",
    }

    answers = {}
    all_answered = True

    with st.form("health_score_form"):
        for dim_name, qs in dim_questions.items():
            icon = DIMENSION_ICONS.get(dim_name, "📌")
            st.markdown(f"### {icon} {dim_name}")
            for q in qs:
                selected = st.radio(
                    q["text"],
                    options=q["options"],
                    key=q["id"],
                    index=None,
                )
                if selected is None:
                    all_answered = False
                else:
                    answers[q["id"]] = q["options"].index(selected)
            st.markdown("---")

        submitted = st.form_submit_button(
            "🚀 Calculate My Money Health Score",
            use_container_width=True,
        )

    if submitted:
        if not all_answered:
            st.warning("⚠️ Please answer all 15 questions to see your score. Scroll up to find the ones you missed.")
        else:
            payload = {
                "answers": answers,
                "name": name or "Friend",
                "age": int(age),
                "monthly_income": float(monthly_income),
            }
            with st.spinner("🧠 Analysing your financial health with AI..."):
                response = requests.post(
                    f"{API_BASE}/api/health-score/calculate",
                    json=payload,
                    timeout=60,
                )
            if response.status_code == 200:
                result = response.json()["health_score"]
                _render_health_score(result)
            else:
                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")


def _render_health_score(result: dict):
    """Render the Money Health Score results page."""
    st.markdown("---")

    # ── Overall score ────────────────────────────────────────────────────────
    col_score, col_summary = st.columns([1, 2])

    with col_score:
        score = result["overall_score"]
        color = result["overall_band_color"]
        band  = result["overall_band_label"]

        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": f"<b>{result['name']}'s</b><br>Money Health Score", "font": {"color": "#e6edf3", "size": 14}},
            number={"suffix": "/100", "font": {"color": color, "size": 40}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#8b949e"},
                "bar": {"color": color},
                "bgcolor": "#161b22",
                "steps": [
                    {"range": [0, 40],   "color": "#2d1b1b"},
                    {"range": [40, 60],  "color": "#2d2a1b"},
                    {"range": [60, 80],  "color": "#1b2d1e"},
                    {"range": [80, 100], "color": "#1a2b1a"},
                ],
                "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.8, "value": score},
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e6edf3",
            height=280,
            margin=dict(t=30, b=0, l=20, r=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(
            f"<center><span style='font-size:1.2rem;font-weight:700;color:{color}'>{band}</span></center>",
            unsafe_allow_html=True
        )

    with col_summary:
        st.markdown('<div class="section-title">📝 Your Financial Summary</div>', unsafe_allow_html=True)
        st.markdown(
            f"<div class='tip-box'>{result['executive_summary']}</div>",
            unsafe_allow_html=True
        )

        col_s, col_c = st.columns(2)
        with col_s:
            st.markdown("**💪 Your Strengths**")
            for s in result["top_strengths"]:
                st.markdown(f"✅ {s}")
        with col_c:
            st.markdown("**⚠️ Focus Areas**")
            for c in result["top_concerns"]:
                st.markdown(f"🔴 {c}")

    # ── Radar chart ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📡 Financial Health Radar</div>', unsafe_allow_html=True)

    dims = result["dimension_scores"]
    dim_names  = [d["dimension"] for d in dims]
    dim_scores = [d["score"] for d in dims]

    # Close the polygon
    dim_names_closed  = dim_names + [dim_names[0]]
    dim_scores_closed = dim_scores + [dim_scores[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=dim_scores_closed,
        theta=dim_names_closed,
        fill="toself",
        fillcolor="rgba(46, 204, 113, 0.15)",
        line_color="#2ecc71",
        name="Your Score",
        hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
    ))
    # Benchmark line at 70
    fig_radar.add_trace(go.Scatterpolar(
        r=[70] * (len(dim_names) + 1),
        theta=dim_names_closed,
        mode="lines",
        line=dict(color="#f1c40f", dash="dash", width=1.5),
        name="Target (70)",
        hoverinfo="skip",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(range=[0, 100], tickcolor="#8b949e", gridcolor="#30363d", color="#8b949e"),
            angularaxis=dict(tickcolor="#8b949e", gridcolor="#30363d"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3",
        font_family="Inter",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=420,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Dimension cards ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 Dimension Breakdown</div>', unsafe_allow_html=True)

    DIMENSION_ICONS = {
        "Emergency Fund": "🛡️",
        "Debt Management": "💳",
        "Insurance Coverage": "🏥",
        "Investments & Savings": "📈",
        "Goal Clarity": "🎯",
        "Spending Habits": "💸",
    }

    for i in range(0, len(dims), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(dims):
                break
            d = dims[idx]
            icon = DIMENSION_ICONS.get(d["dimension"], "📌")
            with col:
                score_pct = d["score"]
                bar_color = d["band_color"]
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{icon} {d['dimension']}</h3>
                    <h2 style="color:{bar_color}">{score_pct:.0f} <small style="font-size:0.9rem;color:#8b949e">/100</small></h2>
                    <div style="background:#30363d;border-radius:4px;height:6px;margin:0.5rem 0">
                        <div style="background:{bar_color};width:{score_pct}%;height:6px;border-radius:4px"></div>
                    </div>
                    <small style="color:#8b949e">{d['band_label']}</small>
                </div>
                <div class="tip-box">{d['insight']}</div>
                """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTING
# ════════════════════════════════════════════════════════════════════════════

if page == "🧾 Tax Wizard":
    tax_wizard_page()
else:
    health_score_page()
