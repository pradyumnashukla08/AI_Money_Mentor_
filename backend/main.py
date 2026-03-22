"""
The Strategist Agent — FastAPI Application Entrypoint.

AI-powered financial strategist for FIRE planning and life event advisory,
built for Indian users as part of the AI Money Mentor project.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS middleware — allows Person 1's frontend to call this API natively from the Browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(strategist_router)
app.include_router(analyst_router)
app.include_router(tax_router)
app.include_router(health_router)


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
