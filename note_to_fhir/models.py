"""
Data models for clinical note extraction and FHIR conversion.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    """Patient demographic details extracted from note."""
    name: Optional[str] = None
    gender: Optional[str] = "unknown"  # male | female | other | unknown
    birth_date: Optional[str] = None   # YYYY-MM-DD


class EncounterInfo(BaseModel):
    """Encounter metadata extracted from note."""
    date: Optional[str] = None
    encounter_type: str = "ambulatory"


class ConditionEntity(BaseModel):
    """Extracted medical condition or problem."""
    text: str
    display: Optional[str] = None
    snomed_code: Optional[str] = None
    icd10_code: Optional[str] = None
    status: str = "active"  # active | recurrence | relapse | inactive | remission | resolved


class MedicationEntity(BaseModel):
    """Extracted medication or prescription."""
    text: str
    display: Optional[str] = None
    rxnorm_code: Optional[str] = None
    dosage: Optional[str] = None
    status: str = "active"


class AllergyEntity(BaseModel):
    """Extracted allergy or intolerance."""
    text: str
    display: Optional[str] = None
    snomed_code: Optional[str] = None
    category: str = "medication"  # medication | food | environment | biologic
    status: str = "active"


class VitalSignObservation(BaseModel):
    """Extracted vital sign measurement."""
    name: str  # systolic_bp, diastolic_bp, blood_pressure, heart_rate, respiratory_rate, body_temperature, oxygen_saturation, bmi, etc.
    loinc_code: str
    value: Optional[float] = None
    unit: str
    ucum_code: str
    # If panel (e.g. BP) with systolic & diastolic:
    systolic: Optional[float] = None
    diastolic: Optional[float] = None


class ExtractedEntities(BaseModel):
    """Unified container for all extracted clinical entities."""
    patient: PatientInfo = Field(default_factory=PatientInfo)
    encounter: EncounterInfo = Field(default_factory=EncounterInfo)
    conditions: List[ConditionEntity] = Field(default_factory=list)
    medications: List[MedicationEntity] = Field(default_factory=list)
    allergies: List[AllergyEntity] = Field(default_factory=list)
    observations: List[VitalSignObservation] = Field(default_factory=list)


class ClinicalNote(BaseModel):
    """Input clinical note container."""
    text: str
    language: str = "en"  # "en", "es", or "auto"
    encounter_date: Optional[str] = None


class ConversionResult(BaseModel):
    """Result of clinical note conversion to FHIR R4 Bundle."""
    bundle: Dict[str, Any]
    is_valid: bool
    validation_messages: List[str] = Field(default_factory=list)
    extracted_entities: ExtractedEntities
