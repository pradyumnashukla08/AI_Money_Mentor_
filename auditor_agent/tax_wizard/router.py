"""
router.py — FastAPI router for the Tax Wizard module.

Endpoints:
  POST /api/tax-wizard/upload       → Upload Form 16 PDF, get full tax comparison
  POST /api/tax-wizard/manual       → Submit income/deduction data manually (no PDF)
  GET  /api/tax-wizard/health       → Health check
"""

import os
import tempfile
import logging
from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from auditor_agent.tax_wizard.pdf_extractor import extract_form16_text
from auditor_agent.tax_wizard.form16_agent import parse_form16_with_llm, Form16Data
from auditor_agent.tax_wizard.tax_calculator import compare_regimes, TaxComparison

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tax-wizard", tags=["Tax Wizard"])


# ── Helper: convert dataclass to JSON-safe dict ────────────────────────────

def _comparison_to_dict(comparison: TaxComparison) -> dict:
    """Recursively convert TaxComparison dataclass to a JSON-serializable dict."""
    def _result_to_dict(r) -> dict:
        return {
            "regime": r.regime,
            "gross_income": r.gross_income,
            "total_exemptions": r.total_exemptions,
            "total_deductions": r.total_deductions,
            "taxable_income": r.taxable_income,
            "slab_breakdown": [
                {
                    "slab_label": s.slab_label,
                    "taxable_in_slab": s.taxable_in_slab,
                    "rate": s.rate,
                    "tax": s.tax,
                }
                for s in r.slab_breakdown
            ],
            "base_tax": r.base_tax,
            "rebate_87a": r.rebate_87a,
            "tax_after_rebate": r.tax_after_rebate,
            "surcharge": r.surcharge,
            "cess": r.cess,
            "total_tax_payable": r.total_tax_payable,
            "tds_already_paid": r.tds_already_paid,
            "tax_due_or_refund": r.tax_due_or_refund,
            "effective_tax_rate": r.effective_tax_rate,
        }

    return {
        "old_regime": _result_to_dict(comparison.old_regime),
        "new_regime": _result_to_dict(comparison.new_regime),
        "recommended_regime": comparison.recommended_regime,
        "savings_with_recommended": comparison.savings_with_recommended,
        "recommendation_reason": comparison.recommendation_reason,
    }


# ── POST /api/tax-wizard/upload ─────────────────────────────────────────────

@router.post("/upload", summary="Upload Form 16 PDF and get tax comparison")
async def upload_form16(file: UploadFile = File(...)):
    """
    Upload a Form 16 PDF (Part A or Part B) and receive a complete
    Old vs. New tax regime comparison with a personalized recommendation.

    - Accepts: PDF file (multipart/form-data)
    - Returns: JSON with both regime breakdowns and recommendation
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload your Form 16 as a PDF."
        )

    # Save to temp file for extraction
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        logger.info("Processing uploaded PDF: %s (%d bytes)", file.filename, len(content))

        # Step 1: Extract text from PDF
        raw_text = extract_form16_text(tmp_path)

        # Step 2: LLM-powered structured data extraction
        form16_data = parse_form16_with_llm(raw_text)

        # Step 3: Compute tax comparison
        comparison = compare_regimes(form16_data)

        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "extracted_data": form16_data.model_dump(),
            "tax_comparison": _comparison_to_dict(comparison),
        })

    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error during Form 16 processing: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(exc)}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ── POST /api/tax-wizard/manual ─────────────────────────────────────────────

class ManualTaxInput(BaseModel):
    """Manual income and deduction input for users without Form 16."""
    employer_name: str = Field(default="Self-provided")
    employee_name: str = Field(default="You")
    assessment_year: str = Field(default="2025-26")
    gross_salary: float = Field(..., gt=0, description="Annual gross salary (₹)")
    hra_received: float = Field(default=0.0)
    basic_salary: float = Field(default=0.0)
    hra_exempt: float = Field(default=0.0)
    lta_exempt: float = Field(default=0.0)
    professional_tax: float = Field(default=0.0)
    deduction_80c: float = Field(default=0.0, le=150_000)
    deduction_80d: float = Field(default=0.0)
    deduction_80ccd1b: float = Field(default=0.0, le=50_000)
    deduction_80ccd2: float = Field(default=0.0)
    deduction_80tta: float = Field(default=0.0, le=10_000)
    deduction_80e: float = Field(default=0.0)
    deduction_home_loan_interest: float = Field(default=0.0)
    other_deductions: float = Field(default=0.0)
    tds_deducted: float = Field(default=0.0)
    advance_tax_paid: float = Field(default=0.0)


@router.post("/manual", summary="Submit income data manually and get tax comparison")
async def manual_tax_calculation(payload: ManualTaxInput):
    """
    Calculate tax without uploading a PDF.
    Accepts manual income and deduction inputs and returns the full comparison.
    """
    try:
        form16_data = Form16Data(**payload.model_dump())
        comparison = compare_regimes(form16_data)
        return JSONResponse(content={
            "status": "success",
            "input_data": form16_data.model_dump(),
            "tax_comparison": _comparison_to_dict(comparison),
        })
    except Exception as exc:
        logger.error("Manual tax calculation error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(exc)}")


# ── GET /api/tax-wizard/health ──────────────────────────────────────────────

@router.get("/health", summary="Health check for Tax Wizard module")
async def health_check():
    return {"status": "ok", "module": "Tax Wizard", "version": "1.0.0"}
