import streamlit as st
import pandas as pd
from datetime import datetime
import pyxirr
import os

# Set page configuration
st.set_page_config(page_title="AI Portfolio Mentor", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for styling the metrics cards exactly like the screenshot
st.markdown("""
<style>
/* Hide Streamlit Deploy button and Menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton {display:none;}

div[data-testid="metric-container"] {
    background-color: #1F2937;
    border: 1px solid #374151;
    padding: 20px;
    border-radius: 10px;
}
div[data-testid="metric-container"] > div {
    color: #9CA3AF;
}
div[data-testid="metric-container"] label {
    font-size: 16px !important;
    font-weight: 500 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #F9FAFB !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.subheader("💰 AI Portfolio Mentor")
    st.caption("The Investment Agent")
    st.divider()
    
    st.radio("Navigation", ["📄 XIRR Calculator", "💚 Portfolio Health Score"])
    st.divider()
    
    st.caption("Powered by Groq • LLaMA 3 8B")
    st.caption("Tax rules: FY 2025-26")

# Main Header
st.title("📄 XIRR Calculator")
st.markdown("Upload your mutual fund statement and instantly discover your true return rate.")

# Upload Section
st.subheader("Drop your Statement here")
uploaded_file = st.file_uploader("Limit 200MB per file • CSV or PDF", type=['csv', 'pdf'], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

if uploaded_file is not None:
    # Current value input is needed for XIRR
    current_value = st.number_input("What is the **Current Portfolio Value** as of today? (₹)", min_value=0.0, value=70000.0, step=1000.0)
    
    if uploaded_file.name.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file)
            
            with st.expander("View Uploaded Transactions"):
                st.dataframe(df)

            # Standardize date and compute
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Outflows (Investments) are negative, inflows (Redemptions) are positive
            total_invested = abs(df[df['Amount'] < 0]['Amount'].sum())

            # Append today's valuation as a cash inflow to calculate XIRR
            today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
            current_value_row = pd.DataFrame([{'Date': today, 'Transaction Type': 'Current Value', 'Amount': current_value}])
            calc_df = pd.concat([df, current_value_row], ignore_index=True)

            xirr_rate = pyxirr.xirr(calc_df['Date'], calc_df['Amount'])
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Portfolio Return Comparison")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Invested", f"₹{total_invested:,.0f}")
            with col2:
                st.metric("Current Value", f"₹{current_value:,.0f}")
            with col3:
                if xirr_rate is not None:
                    xirr_pct = xirr_rate * 100
                    st.metric("Calculated XIRR", f"{xirr_pct:.2f}%")
                else:
                    st.metric("Calculated XIRR", "N/A")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Recommendation Box (similar to the green Recommended box in the image)
            if xirr_rate is not None and xirr_pct > 0:
                st.success(f"**Recommended: Continue SIPs**\n\nThe calculated XIRR is {xirr_pct:.2f}%. Your investments are growing steadily and compounding effectively. Keep up the discipline!")
            elif xirr_rate is not None:
                st.warning(f"**Notice: Negative Returns**\n\nYour portfolio is currently down by {xirr_pct:.2f}%. Mutual funds are subject to market risks; consider continuing investments to average your purchasing costs.")

        except Exception as e:
            st.error(f"Could not parse the CSV file. Please make sure it has 'Date' and 'Amount' columns. Error: {e}")
            
    elif uploaded_file.name.endswith('.pdf'):
        st.info("PDF upload detected. The system successfully received the file, but we still need to add the regex parsing logic for your specific broker's PDF format to calculate the XIRR.")
else:
    # Show placeholder empty state if no file is uploaded
    st.info("👆 Please upload your mutual fund statement (CSV) above to calculate your returns.")
