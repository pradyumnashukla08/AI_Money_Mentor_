"""
main.py — FastAPI application entrypoint for the Auditor Agent.

Mounts:
  - Tax Wizard router   → /api/tax-wizard/*
  - Health Score router → /api/health-score/*
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auditor_agent.config import settings
from auditor_agent.tax_wizard.router import router as tax_router
from auditor_agent.health_score.router import router as health_router

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("auditor_agent")


# ── App lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    logger.info("Starting AI Money Mentor — Auditor Agent 🚀")
    settings.validate()
    logger.info("Groq API key validated. Model: %s", settings.GROQ_MODEL)
    yield
    logger.info("Auditor Agent shut down.")


# ── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Money Mentor — Auditor Agent",
    description=(
        "The Auditor Agent handles Form 16 tax analysis (Old vs New regime) "
        "and the 5-minute Money Health Score onboarding for AI Money Mentor."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow requests from Streamlit (localhost:8501) and any dev origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ────────────────────────────────────────────────────────────
app.include_router(tax_router)
app.include_router(health_router)


# ── Root endpoint ────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "AI Money Mentor — Auditor Agent",
        "version": "1.0.0",
        "modules": ["Tax Wizard", "Money Health Score"],
        "docs": "/docs",
        "status": "running",
    }
