# pyre-ignore-all-errors
"""
Google Gemma API client wrapper for The Strategist Agent.

Provides a clean interface to Google's insanely fast cloud inference
running the Open-Source Gemma 3 (12B) model for Hackathon compliance.
"""

import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

def generate_response(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
) -> str:
    """Generate a text response from the Gemma 3 API."""
    
    if not settings.GEMINI_API_KEY:
        msg = "GEMINI_API_KEY is missing. Please add it to your .env file."
        logger.warning(msg)
        return msg
        
    full_text = prompt
    if system_prompt:
        full_text = f"SYSTEM INSTRUCTION: {system_prompt}\n\nUSER REQUEST: {prompt}"
        
    payload = {
        "contents": [{
            "parts": [{"text": full_text}]
        }],
        "generationConfig": {
            "temperature": temperature
        }
    }

    import time

    for attempt in range(3):
        try:
            # httpx timeout set to 60s
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-12b-it:generateContent?key={settings.GEMINI_API_KEY}",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [429, 503] and attempt < 2:
                time.sleep(3.5)  # Pause for 3.5 seconds to cool down the free API tier
                continue
            logger.error(f"Gemma API error: {e}")
            return f"Error communicating with Open-Source Gemma AI service: {e}"
        except Exception as e:
            logger.error(f"Gemma API error: {e}")
            return f"Error communicating with Open-Source Gemma AI service: {e}"

    return "Error: Maximum retries exceeded for Open-Source Gemma AI service due to rate limiting."

def generate_structured_response(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.3,
) -> str:
    """Generate a response optimised for structured / JSON output using lower temperature."""
    return generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
    )
