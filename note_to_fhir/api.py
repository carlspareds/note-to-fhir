"""
FastAPI HTTP microservice exposing POST /convert and health check endpoints.
"""

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from note_to_fhir import __version__
from note_to_fhir.builder import FHIRBundleBuilder
from note_to_fhir.extractors.llm import LLMExtractor
from note_to_fhir.extractors.rules import RuleBasedExtractor
from note_to_fhir.models import ClinicalNote

app = FastAPI(
    title="note-to-fhir API",
    description="Convert unstructured clinical notes to HL7 FHIR R4 Bundles evaluated against Synthea ground truth.",
    version=__version__,
)


class ConvertRequest(BaseModel):
    """Payload for clinical note conversion."""
    model_config = ConfigDict(populate_by_name=True)

    text: str = Field(..., description="Unstructured free-text clinical note (English or Spanish).")
    language: str = Field(default="auto", description="'en', 'es', or 'auto'.")
    extractor: str = Field(default="rules", description="'rules' (offline deterministic) or 'llm'.")
    do_validate: bool = Field(default=True, alias="validate", description="Validate output bundle structure.")
    encounter_date: Optional[str] = Field(default=None, description="Optional ISO encounter date (YYYY-MM-DD).")


class ConvertResponse(BaseModel):
    """Response containing generated FHIR R4 Bundle and extraction metadata."""
    is_valid: bool
    validation_messages: List[str]
    entities_count: Dict[str, int]
    bundle: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check status response."""
    status: str
    version: str
    llm_available: bool


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Service health and capability probe."""
    llm = LLMExtractor()
    return HealthResponse(
        status="ok",
        version=__version__,
        llm_available=llm.is_available,
    )


@app.post("/convert", response_model=ConvertResponse)
def convert_note(request: ConvertRequest):
    """
    Convert a clinical note (English or Spanish) into a validated HL7 FHIR R4 Bundle.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Clinical note text cannot be empty.")

    # Select extractor
    if request.extractor.lower() == "llm":
        extractor = LLMExtractor()
    else:
        extractor = RuleBasedExtractor()

    note = ClinicalNote(
        text=request.text,
        language=request.language,
        encounter_date=request.encounter_date,
    )

    try:
        entities = extractor.extract(note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")

    builder = FHIRBundleBuilder()
    bundle = builder.build_bundle(entities)

    is_valid = True
    messages: List[str] = []
    if request.do_validate:
        is_valid, messages = builder.validate_bundle(bundle)

    counts = {
        "conditions": len(entities.conditions),
        "medications": len(entities.medications),
        "allergies": len(entities.allergies),
        "observations": len(entities.observations),
    }

    return ConvertResponse(
        is_valid=is_valid,
        validation_messages=messages,
        entities_count=counts,
        bundle=bundle,
    )


@app.post("/validate")
def validate_bundle_endpoint(bundle: Dict[str, Any]):
    """
    Directly validate an arbitrary FHIR R4 bundle JSON.
    """
    builder = FHIRBundleBuilder()
    is_valid, messages = builder.validate_bundle(bundle)
    return {
        "is_valid": is_valid,
        "validation_messages": messages,
    }
