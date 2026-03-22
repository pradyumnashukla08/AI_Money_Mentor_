"""
Centralised configuration for The Strategist Agent.
Loads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

# Force load the root Next.js .env.local file so all Agents have the Groq API Key
root_env_local = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env.local"))
root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

if os.path.exists(root_env_local):
    load_dotenv(dotenv_path=root_env_local)
elif os.path.exists(root_env):
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    # Global configurations

    # (Hot-Reload trigger so that uvicorn automatically picks up the new .env)

    # Default financial assumptions for India
    DEFAULT_INFLATION_RATE: float = 0.06        # 6% average Indian inflation
    DEFAULT_EQUITY_RETURN: float = 0.12          # 12% long-term Indian equity return
    DEFAULT_DEBT_RETURN: float = 0.07            # 7% debt fund return
    DEFAULT_FD_RETURN: float = 0.065             # 6.5% fixed deposit return
    DEFAULT_WITHDRAWAL_RATE: float = 0.04        # 4% safe withdrawal rate (FIRE)
    DEFAULT_STEP_UP_RATE: float = 0.10           # 10% annual SIP step-up


settings = Settings()
