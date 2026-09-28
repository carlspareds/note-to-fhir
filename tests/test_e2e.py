"""
End-to-end integration tests on sample Synthea fixtures.
Converts realistic English and Spanish clinical notes, verifies FHIR R4 Bundle schema
conformance, resource linkages, and terminology precision.
"""

from pathlib import Path

import pytest

from note_to_fhir.builder import FHIRBundleBuilder
from note_to_fhir.extractors.rules import RuleBasedExtractor
from note_to_fhir.models import ClinicalNote


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parent.parent / "data" / "fixtures"


def test_e2e_conversion_patient_english(fixtures_dir):
    notes_en = sorted((fixtures_dir / "notes" / "en").glob("*_soap.txt"))
    assert len(notes_en) > 0, "No English notes found in fixtures"
    note_path = notes_en[0]
    assert note_path.exists()
    text = note_path.read_text(encoding="utf-8")

    extractor = RuleBasedExtractor()
    note = ClinicalNote(text=text, language="en")
    entities = extractor.extract(note)

    assert entities.patient.name is not None and len(entities.patient.name) > 0
    assert entities.patient.gender in ["male", "female", "other", "unknown"]
    assert entities.patient.birth_date is not None

    # Vitals
    obs_loincs = {o.loinc_code for o in entities.observations}
    assert "85354-9" in obs_loincs or "8867-4" in obs_loincs

    # Build and validate FHIR bundle
    builder = FHIRBundleBuilder()
    bundle = builder.build_bundle(entities)
    is_valid, messages = builder.validate_bundle(bundle)

    assert is_valid, f"Bundle validation failed: {messages}"
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"

    # Verify Patient reference in Conditions and Observations
    patient_entries = [e for e in bundle["entry"] if e["resource"]["resourceType"] == "Patient"]
    assert len(patient_entries) == 1
    patient_ref = patient_entries[0]["fullUrl"]

    for entry in bundle["entry"]:
        res = entry["resource"]
        if res["resourceType"] in ["Condition", "MedicationStatement", "Observation", "Encounter"]:
            subj = res.get("subject", {}).get("reference")
            assert subj == patient_ref


def test_e2e_conversion_patient_spanish(fixtures_dir):
    notes_es = sorted((fixtures_dir / "notes" / "es").glob("*_soap.txt"))
    assert len(notes_es) > 0, "No Spanish notes found in fixtures"
    note_path = notes_es[0]
    assert note_path.exists()
    text = note_path.read_text(encoding="utf-8")

    extractor = RuleBasedExtractor()
    note = ClinicalNote(text=text, language="es")
    entities = extractor.extract(note)

    assert entities.patient.name is not None and len(entities.patient.name) > 0
    assert entities.patient.gender in ["male", "female", "other", "unknown"]
    assert entities.patient.birth_date is not None

    builder = FHIRBundleBuilder()
    bundle = builder.build_bundle(entities)
    is_valid, messages = builder.validate_bundle(bundle)

    assert is_valid
