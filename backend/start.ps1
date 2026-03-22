# AI Money Mentor — Auditor Agent
# Quick-start script (PowerShell)

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  AI Money Mentor — Auditor Agent" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# 1. Go into auditor_agent folder
Set-Location "$PSScriptRoot\auditor_agent"

# 2. Install dependencies
Write-Host "`n[1/3] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# 3. Start FastAPI backend in background
Write-Host "`n[2/3] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process python -ArgumentList "-m uvicorn auditor_agent.main:app --reload --port 8000" -WorkingDirectory "$PSScriptRoot"

Start-Sleep -Seconds 3

# 4. Start Streamlit frontend
Write-Host "`n[3/3] Starting Streamlit UI on http://localhost:8501 ..." -ForegroundColor Green
Start-Process python -ArgumentList "-m streamlit run auditor_agent\streamlit_app\app.py" -WorkingDirectory "$PSScriptRoot"

Write-Host "`n✅ Both services are starting!" -ForegroundColor Green
Write-Host "   FastAPI docs → http://localhost:8000/docs"
Write-Host "   Streamlit UI → http://localhost:8501"
