"""
form16_agent.py — LLM-powered Form 16 data extraction agent.

Uses Groq (llama3-8b-8192, free & open-source) to parse raw PDF text
and return a clean, structured JSON representing all key Form 16 fields.
"""

import json
import logging
import re
from typing import Optional

from groq import Groq
from pydantic import BaseModel, Field, validator

# Import settings lazily to avoid circular imports at module level
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from auditor_agent.config import settings

logger = logging.getLogger(__name__)


# ── Pydantic model for structured Form 16 data ─────────────────────────────

class Form16Data(BaseModel):
    """Structured representation of data extracted from Form 16."""

    # Identity
    employer_name: str = Field(default="Unknown", description="Name of the employer / company")
    employee_name: str = Field(default="Unknown", description="Employee's full name")
    pan: str = Field(default="UNKNOWN", description="Employee's PAN number")
    assessment_year: str = Field(default="2025-26", description="Assessment Year e.g. 2025-26")
    financial_year: str = Field(default="2024-25", description="Financial Year e.g. 2024-25")

    # Income components (₹)
    gross_salary: float = Field(default=0.0, description="Gross salary before deductions")
    hra_received: float = Field(default=0.0, description="HRA component of salary")
    basic_salary: float = Field(default=0.0, description="Basic salary component")
    special_allowance: float = Field(default=0.0, description="Special / other allowances")
    bonus_and_incentives: float = Field(default=0.0, description="Bonus, incentives, performance pay")

    # Exempt allowances
    hra_exempt: float = Field(default=0.0, description="HRA exemption computed u/s 10(13A)")
    lta_exempt: float = Field(default=0.0, description="LTA exemption u/s 10(5)")

    # Standard deduction
    standard_deduction: float = Field(default=50_000.0, description="Standard deduction (₹50k old / ₹75k new)")
    professional_tax: float = Field(default=0.0, description="Professional tax paid")

    # Chapter VI-A deductions (old regime)
    deduction_80c: float = Field(default=0.0, description="PPF, ELSS, LIC, EPF etc. u/s 80C (max ₹1.5L)")
    deduction_80d: float = Field(default=0.0, description="Health insurance premium u/s 80D")
    deduction_80ccd1b: float = Field(default=0.0, description="NPS additional contribution u/s 80CCD(1B)")
    deduction_80ccd2: float = Field(default=0.0, description="Employer NPS contribution u/s 80CCD(2)")
    deduction_80tta: float = Field(default=0.0, description="Savings account interest u/s 80TTA")
    deduction_80e: float = Field(default=0.0, description="Education loan interest u/s 80E")
    deduction_80g: float = Field(default=0.0, description="Donations to charitable institutions u/s 80G")
    deduction_80eea: float = Field(default=0.0, description="Interest on affordable housing loan u/s 80EEA")
    deduction_home_loan_interest: float = Field(default=0.0, description="Home loan interest u/s 24(b)")
    other_deductions: float = Field(default=0.0, description="Any other declared deductions")

    # Tax paid
    tds_deducted: float = Field(default=0.0, description="Total TDS deducted by employer")
    advance_tax_paid: float = Field(default=0.0, description="Advance tax / self-assessment tax paid")

    # Metadata
    extraction_confidence: str = Field(
        default="medium",
        description="LLM confidence: high / medium / low"
    )
    notes: str = Field(default="", description="Any caveats or assumptions made during extraction")


# ── System prompt for Form 16 extraction ───────────────────────────────────

FORM16_SYSTEM_PROMPT = """You are a highly accurate Indian tax document analyst.
Your task is to extract structured financial data from raw Form 16 / salary certificate text.

Return ONLY a valid JSON object — no prose, no markdown, no explanation.
Use 0.0 for any field not found in the document.
All monetary values must be in INR (Indian Rupees) as plain numbers (no commas, no ₹ symbols).
If you are unsure about a value, use 0.0 and note it in the 'notes' field.
Set 'extraction_confidence' to 'high' if most fields are clearly present, 'medium' if some guesses were made, 'low' if the document is unclear.

Return a JSON object with exactly these keys:
{
  "employer_name": "",
  "employee_name": "",
  "pan": "",
  "assessment_year": "",
  "financial_year": "",
  "gross_salary": 0.0,
  "hra_received": 0.0,
  "basic_salary": 0.0,
  "special_allowance": 0.0,
  "bonus_and_incentives": 0.0,
  "hra_exempt": 0.0,
  "lta_exempt": 0.0,
  "standard_deduction": 50000.0,
  "professional_tax": 0.0,
  "deduction_80c": 0.0,
  "deduction_80d": 0.0,
  "deduction_80ccd1b": 0.0,
  "deduction_80ccd2": 0.0,
  "deduction_80tta": 0.0,
  "deduction_80e": 0.0,
  "deduction_80g": 0.0,
  "deduction_80eea": 0.0,
  "deduction_home_loan_interest": 0.0,
  "other_deductions": 0.0,
  "tds_deducted": 0.0,
  "advance_tax_paid": 0.0,
  "extraction_confidence": "medium",
  "notes": ""
}"""

FORM16_USER_PROMPT_TEMPLATE = """Below is the raw text extracted from a Form 16 PDF.
Please extract all financial details and return them as a JSON object.

FORM 16 TEXT:
{raw_text}

Return ONLY the JSON object, nothing else."""


# ── LLM agent call ──────────────────────────────────────────────────────────

def parse_form16_with_llm(raw_text: str) -> Form16Data:
    """
    Send extracted PDF text to Groq LLM and parse the response into Form16Data.

    Args:
        raw_text: Raw text extracted from a Form 16 PDF.

    Returns:
        Validated Form16Data Pydantic model.

    Raises:
        ValueError: If LLM returns invalid JSON or critical parsing fails.
    """
    client = Groq(api_key=settings.GROQ_API_KEY)

    # Truncate to 12,000 chars to stay safely within llama3-8b context limits
    truncated_text = raw_text[:12_000] if len(raw_text) > 12_000 else raw_text

    user_prompt = FORM16_USER_PROMPT_TEMPLATE.format(raw_text=truncated_text)

    logger.info("Sending Form 16 text to Groq LLM for extraction...")

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": FORM16_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,   # Deterministic — we want consistent extraction
            max_tokens=1024,
        )
    except Exception as exc:
        raise ValueError(f"Groq API call failed: {exc}") from exc

    raw_response = response.choices[0].message.content.strip()
    logger.debug("LLM raw response: %s", raw_response[:500])

    # Strip markdown code fences if present (```json ... ```)
    json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if not json_match:
        raise ValueError(
            f"LLM did not return a valid JSON object. Response:\n{raw_response[:300]}"
        )

    json_str = json_match.group()

    try:
        data_dict = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse LLM JSON response: {exc}") from exc

    logger.info("Form 16 data extracted successfully. Confidence: %s", data_dict.get("extraction_confidence", "unknown"))
    return Form16Data(**data_dict)


# ── Demo / CLI test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick smoke test with dummy text
    sample_text = """
    FORM 16 - Certificate of Tax Deducted at Source
    Assessment Year: 2025-26
    Employee Name: Arjun Sharma
    PAN: ABCDE1234F
    Employer: TechSoft India Pvt Ltd

    Gross Salary:         12,00,000
    Basic Salary:          6,00,000
    HRA Received:          2,40,000
    Special Allowance:     3,60,000

    HRA Exemption u/s 10(13A): 1,44,000
    Standard Deduction:           50,000
    Professional Tax:              2,400

    Chapter VI-A Deductions:
    80C (EPF + PPF + ELSS):    1,50,000
    80D (Health Insurance):       25,000
    80CCD(1B) NPS:               50,000

    TDS Deducted:               90,000
    """

    result = parse_form16_with_llm(sample_text)
    print("\nExtracted Form 16 Data:")
    print(result.model_dump_json(indent=2))
