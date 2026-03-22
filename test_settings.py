import os
import sys

# Ensure backend folder is in path
sys.path.insert(0, os.path.abspath("backend"))

try:
    from auditor_agent.config import settings
    print(f"GROQ_API_KEY found: {bool(settings.GROQ_API_KEY)}")
    print(f"GROQ_MODEL: {settings.GROQ_MODEL}")
    settings.validate()
    print("Settings validated successfully!")
except Exception as e:
    print(f"Validation failed: {type(e).__name__}: {e}")
