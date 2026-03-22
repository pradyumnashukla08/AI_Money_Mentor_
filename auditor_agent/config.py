"""
config.py — Central configuration loader for the Auditor Agent.
Reads from .env file and exposes typed settings used across modules.
"""
import os
from dotenv import load_dotenv

# Load .env from the auditor_agent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


class Settings:
    """Application-wide settings loaded from environment variables."""

    # Groq LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # API Server
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Streamlit
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    # Tax constants for FY 2025-26 (AY 2026-27)
    STANDARD_DEDUCTION_OLD: int = 50_000   # ₹50,000
    STANDARD_DEDUCTION_NEW: int = 75_000   # ₹75,000 (Budget 2024)
    CESS_RATE: float = 0.04                # 4% Health & Education Cess

    # Old Regime — Income Tax Slabs
    OLD_REGIME_SLABS = [
        (250_000, 0.00),
        (500_000, 0.05),
        (1_000_000, 0.20),
        (float("inf"), 0.30),
    ]

    # New Regime — Income Tax Slabs (FY 2025-26)
    NEW_REGIME_SLABS = [
        (300_000, 0.00),
        (700_000, 0.05),
        (1_000_000, 0.10),
        (1_200_000, 0.15),
        (1_500_000, 0.20),
        (float("inf"), 0.30),
    ]

    # New regime — Tax rebate u/s 87A (income ≤ ₹7L → zero tax)
    NEW_REGIME_REBATE_LIMIT: int = 700_000
    OLD_REGIME_REBATE_LIMIT: int = 500_000

    def validate(self) -> None:
        """Raise an error if critical config values are missing."""
        if not self.GROQ_API_KEY:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. "
                "Please add it to auditor_agent/.env"
            )


settings = Settings()
