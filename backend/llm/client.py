# pyre-ignore-all-errors
"""
Groq API client wrapper for The Strategist Agent.

Provides a clean interface to Groq's insanely fast cloud inference
running the Open-Source LLaMA 3 model for Hackathon compliance.
"""

from groq import Groq
from auditor_agent.config import settings
import logging

logger = logging.getLogger(__name__)

def generate_response(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
) -> str:
    """Generate a text response from the Groq API."""
    
    if not settings.GROQ_API_KEY:
        msg = "GROQ_API_KEY is missing. Please add it to your .env file."
        logger.warning(msg)
        return msg
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()
                
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return f"Error communicating with Open-Source LLaMA AI service: {e}"

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
