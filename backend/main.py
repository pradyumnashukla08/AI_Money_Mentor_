"""
The Strategist Agent — FastAPI Application Entrypoint.

AI-powered financial strategist for FIRE planning and life event advisory,
built for Indian users as part of the AI Money Mentor project.
"""

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from auditor_agent.config import settings

from api.routes import router as strategist_router
from api.analyst_routes import router as analyst_router
from auditor_agent.tax_wizard.router import router as tax_router
from auditor_agent.health_score.router import router as health_router

app = FastAPI(
    title="The Strategist Agent — AI Money Mentor",
    description=(
        "An AI-powered financial strategist agent that provides "
        "FIRE (Financial Independence, Retire Early) planning and "
        "personalised life event advisory for Indian users. "
        "Uses open-source LLMs natively integrated via Groq execution layers."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Security: Verify API Key from Frontend
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.BACKEND_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return x_api_key

# CORS middleware — Restrict to our Frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes — Protected by API Key
app.include_router(strategist_router, dependencies=[Depends(verify_api_key)])
app.include_router(analyst_router, dependencies=[Depends(verify_api_key)])
app.include_router(tax_router, dependencies=[Depends(verify_api_key)])
app.include_router(health_router, dependencies=[Depends(verify_api_key)])


@app.get("/")
async def root():
    """Root endpoint — API information."""
    return {
        "agent": "The Strategist",
        "project": "AI Money Mentor",
        "description": "Wealth & Life Planning AI Agent",
        "docs": "/docs",
        "endpoints": {
            "fire_plan": "POST /strategist/fire-plan",
            "life_event": "POST /strategist/life-event",
            "health": "GET /strategist/health",
            "analyst_xirr": "POST /analyst/xirr",
            "tax_upload": "POST /api/tax-wizard/upload",
            "tax_manual": "POST /api/tax-wizard/manual",
            "health_score": "POST /api/health-score/calculate",
        },
    }
