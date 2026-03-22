import streamlit as st
import requests
import pandas as pd

# Basic Page Config
st.set_page_config(
    page_title="AI Money Mentor | Strategist",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's default Deploy button, Menu, and footer for a pristine Hackathon demo UI
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        [data-testid="stHeader"] {background-color: transparent !important;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 💰 AI Money Mentor")
    st.markdown("#### The Strategist Agent")
    st.divider()
    
    page = st.radio(
        "Navigation",
        options=["🔥 FIRE Planner", "🧬 Life Event Advisor"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.caption("Powered by Google : Gemma 3 12B")
    st.caption("Financial Logic: NumPy + Pandas")

API_BASE = "http://localhost:8000"

def life_event_page():
    st.title("🧬 Life Event Advisor")
    st.write("Calculate the financial impact of sudden life events and get AI-driven advice mapped to your risk profile.")
    
    with st.form("event_form"):
        event_text = st.text_area("Describe the Life Event", placeholder="e.g., 'I just got a 5 Lakhs bonus', 'I am getting married next year', 'I lost my job'")
        
        cols = st.columns(3)
        with cols[0]:
            age = st.number_input("Age", value=28, min_value=18, max_value=80)
            monthly_income = st.number_input("Monthly Income (₹)", value=100000, step=10000)
            monthly_expenses = st.number_input("Monthly Expenses (₹)", value=40000, step=5000)
        with cols[1]:
            current_savings = st.number_input("Current Savings (₹)", value=500000, step=50000)
            existing_sip = st.number_input("Existing Monthly SIP (₹)", value=20000, step=5000)
        with cols[2]:
            risk_tolerance = st.selectbox("Risk Tolerance", ["conservative", "moderate", "aggressive"], index=1)
            life_stage = st.selectbox("Life Stage", ["student", "early_career", "married", "parent", "pre_retirement"], index=1)
            
        submitted = st.form_submit_button("Analyze Event", type="primary")

    if submitted and event_text:
        with st.spinner("Gemma 3 is analyzing your event with advanced financial metrics..."):
            payload = {
                "profile": {
                    "name": "User",
                    "age": age,
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "current_savings": current_savings,
                    "existing_monthly_sip": existing_sip,
                    "risk_tolerance": risk_tolerance,
                    "life_stage": life_stage
                },
                "event_text": event_text
            }
            
            try:
                # The FastAPI backend must be running on localhost:8000 in another terminal
                res = requests.post(f"{API_BASE}/strategist/life-event", json=payload)
                res.raise_for_status()
                data = res.json()
            except Exception as e:
                st.error(f"Failed to connect to the backend API: {e}\n\nMake sure your FastAPI server (`uvicorn main:app`) is running!")
                return
                
            # -- Display Results Beautifully --
            event_info = data.get("event", {})
            st.subheader(f"Detected Event: {event_info.get('event_type', 'Unknown').replace('_', ' ').capitalize()}")
            
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Financial Impact (Extracted)", f"₹ {event_info.get('amount', 0):,.0f}" if event_info.get('amount') else "N/A")
            mc2.metric("Your Risk Profile", risk_tolerance.capitalize())
            mc3.metric("Life Stage", life_stage.replace("_", " ").capitalize())
            
            st.success(data.get("risk_assessment", ""))
            
            tab1, tab2, tab3 = st.tabs(["Immediate Actions", "Short-Term Plan", "Long-Term Impact"])
            
            with tab1:
                for action in data.get("immediate_actions", []):
                    st.info(f"👉 **Action:** {action}")
            with tab2:
                for plan in data.get("short_term_plan", []):
                    st.warning(f"⏳ **Next 3 Months:** {plan}")
            with tab3:
                st.write(data.get("long_term_impact", ""))
                
            st.divider()
            st.markdown("### 📝 AI Narrative")
            st.markdown(f"> *{data.get('narrative', '')}*")


def fire_planner_page():
    st.title("🔥 FIRE Path Planner")
    st.write("Generate a clear, mathematically sound roadmap to Financial Independence and Early Retirement.")
    
    with st.form("fire_form"):
        cols = st.columns(3)
        with cols[0]:
            age = st.number_input("Age", value=30, min_value=18, max_value=80)
            monthly_income = st.number_input("Monthly Income (₹)", value=150000, step=10000)
            monthly_expenses = st.number_input("Monthly Expenses (₹)", value=50000, step=5000)
        with cols[1]:
            current_savings = st.number_input("Current Savings (₹)", value=1000000, step=100000)
            existing_sip = st.number_input("Existing Monthly SIP (₹)", value=40000, step=5000)
        with cols[2]:
            target_age = st.number_input("Target Retirement Age", value=50, min_value=30, max_value=90)
            desired_expense = st.number_input("Desired Pension (₹/mo, Today's Value)", value=70000, step=10000)
            
        submitted = st.form_submit_button("Generate FIRE Roadmap 🚀", type="primary")
        
    if submitted:
        with st.spinner("Running complex financial compounding arrays & AI narrative integration..."):
            payload = {
                "profile": {
                    "name": "User",
                    "age": age,
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "current_savings": current_savings,
                    "existing_monthly_sip": existing_sip,
                    "risk_tolerance": "moderate",
                    "life_stage": "early_career"
                },
                "goal": {
                    "target_retirement_age": target_age,
                    "desired_monthly_expense": desired_expense,
                    "withdrawal_rate": 0.04
                }
            }
            
            try:
                res = requests.post(f"{API_BASE}/strategist/fire-plan", json=payload)
                res.raise_for_status()
                data = res.json()
            except Exception as e:
                st.error(f"API Error. Check if your backend server is running! Error: {e}")
                return
                
            st.divider()
            
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("FIRE Target Corpus", f"₹ {data.get('fire_target', {}).get('corpus_at_retirement', 0):,.0f}")
            mc2.metric("Target Age", target_age)
            mc3.metric("Projected Monthly Step-up", "10%")
            
            st.markdown("### 📈 Projected Corpus Growth")
            roadmap = data.get("full_roadmap", [])
            if roadmap:
                df = pd.DataFrame(roadmap)
                # Map year_number back to actual Age for the x-axis
                df["Expected Age"] = df["age"]
                df["Total Corpus (₹)"] = df["corpus"]
                # Use a sharp Line Chart
                st.line_chart(data=df, x="Expected Age", y="Total Corpus (₹)", color="#28a745")

            st.markdown("### 🤖 Strategy Narrative")
            st.info(data.get("narrative", ""))

if page == "🧬 Life Event Advisor":
    life_event_page()
else:
    fire_planner_page()
