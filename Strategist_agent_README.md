# 🧠 The Strategist Agent — AI Money Mentor

**Project:** AI Money Mentor — An AI-powered personal finance mentor for India.

This module represents **"The Strategist"** agent. It acts as the core financial planning math and scenario modeling engine. It combines deterministic financial math (compounding, SIP, inflation adjustments) with an open-source LLM (Google Gemma 3 via Cloud API) to generate highly personalized financial storytelling.

---

## 🎯 Core Responsibilities Built

1. **🔥 FIRE Path Planner**
   - **Math Engine:** Uses NumPy/Pandas to calculate compound interest, inflation-adjusted future values, required SIP amounts, Coast FIRE numbers, and a month-by-month financial projection.
   - **LLM Integration:** Feeds the mathematical roadmap into the Gemma 3 model to generate a motivating, personalized narrative explaining the user's journey to Financial Independence and Early Retirement.
   
2. **🧬 Life Event Advisor**
   - **Event Classification:** AI detects and categorizes major life events (e.g., getting married, receiving a bonus, having a baby, losing a job).
   - **Risk Profiling:** Checks the user's current risk profile (Conservative, Moderate, Aggressive) before making recommendations.
   - **Actionable Advice:** Generates precise advice focusing on Indian financial instruments (PPF, NPS, FDs, Mutual Funds, ELSS) split into Immediate Actions, Short-Term Plans, and Long-Term Impacts.

---

## 🛠 Tech Stack
- **Dashboard / Frontend:** `Streamlit` (Interactive charts & dark mode UI)
- **API Framework:** `FastAPI` + `Uvicorn`
- **Data Validation:** `Pydantic`
- **Math Engine:** pure Python + `NumPy` + `Pandas`
- **AI / LLM:** `Google Gemma 3` (Open-source weights, accessed securely via cloud API for instant "plug-and-play" performance without heavy local downloads)

---

## 🚀 Installation & Setup

### 1. Install Dependencies
Ensure you have Python 3.10+ installed. Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key
We use the open-source Gemma 3 model hosted on Google's cloud to ensure the app runs instantly on any laptop without needing heavy local GPU downloads.
1. Copy `.env.example` and rename it to `.env`.
2. Add your `GEMINI_API_KEY` to the `.env` file.

### 3. Start the Application (Dual Terminal Setup)
Because this is a full-stack application, you need to run the Backend and the Frontend in two separate terminal windows simultaneously.

**Terminal 1 (The Backend Engine):**
```bash
python -m uvicorn main:app --reload
```
*(Leave this running in the background. If you want to see the automatic API documentation, visit http://127.0.0.1:8000/docs)*

**Terminal 2 (The Frontend Dashboard):**
Open a new terminal tab and run:
```bash
python -m streamlit run streamlit_app.py
```
*(This will automatically open your web browser to the beautiful, interactive dashboard at http://localhost:8501)*

---

## 📖 How to Use FastAPI Documentation
If you want to test the math engine directly without the UI dashboard:
1. Navigate to 👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
2. This provides an interactive Swagger UI to test the POST endpoints (`/strategist/fire-plan` and `/strategist/life-event`).

---

## 🧪 Testing

The math engine has been rigorously tested against known financial calculators. To run the 51 unit tests:
```bash
python -m pytest tests/ -v
```

---
*Built for the AI Money Mentor India team.*
