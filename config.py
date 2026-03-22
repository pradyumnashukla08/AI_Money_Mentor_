"""
Centralised configuration for The Strategist Agent.
Loads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # (Hot-Reload trigger so that uvicorn automatically picks up the new .env)

    # Default financial assumptions for India
    DEFAULT_INFLATION_RATE: float = 0.06        # 6% average Indian inflation
    DEFAULT_EQUITY_RETURN: float = 0.12          # 12% long-term Indian equity return
    DEFAULT_DEBT_RETURN: float = 0.07            # 7% debt fund return
    DEFAULT_FD_RETURN: float = 0.065             # 6.5% fixed deposit return
    DEFAULT_WITHDRAWAL_RATE: float = 0.04        # 4% safe withdrawal rate (FIRE)
    DEFAULT_STEP_UP_RATE: float = 0.10           # 10% annual SIP step-up


settings = Settings()
