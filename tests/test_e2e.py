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


def test_e2e_conversion_patient_1_english(fixtures_dir):
    note_path = fixtures_dir / "notes" / "en" / "patient_1_hypertension_diabetes_soap.txt"
    assert note_path.exists()
    text = note_path.read_text(encoding="utf-8")

    extractor = RuleBasedExtractor()
    note = ClinicalNote(text=text, language="en")
    entities = extractor.extract(note)

    assert entities.patient.name == "John A Doe"
    assert entities.patient.birth_date == "1972-04-15"
    assert entities.patient.gender == "male"

    # Conditions
    cond_codes = {c.snomed_code for c in entities.conditions}
    assert "59621000" in cond_codes  # Hypertension
    assert "44054006" in cond_codes  # T2DM

    # Meds
    med_codes = {m.rxnorm_code for m in entities.medications}
    assert "314076" in med_codes  # Lisinopril
    assert "860975" in med_codes  # Metformin

    # Allergies
    allg_codes = {a.snomed_code for a in entities.allergies}
    assert "91936005" in allg_codes  # Penicillin

    # Vitals
    obs_loincs = {o.loinc_code for o in entities.observations}
    assert "85354-9" in obs_loincs  # Blood pressure
    assert "8867-4" in obs_loincs   # Heart rate

    # Build and validate FHIR bundle
    builder = FHIRBundleBuilder()
    bundle = builder.build_bundle(entities)
    is_valid, messages = builder.validate_bundle(bundle)

    assert is_valid, f"Bundle validation failed: {messages}"
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"

    # Verify Patient reference in Conditions and Observations
    patient_entry = [e for e in bundle["entry"] if e["resource"]["resourceType"] == "Patient"][0]
    patient_ref = patient_entry["fullUrl"]

    for entry in bundle["entry"]:
        res = entry["resource"]
        if res["resourceType"] in ["Condition", "MedicationStatement", "Observation", "Encounter"]:
            subj = res.get("subject", {}).get("reference")
            assert subj == patient_ref


def test_e2e_conversion_patient_2_spanish(fixtures_dir):
    note_path = fixtures_dir / "notes" / "es" / "patient_2_asthma_allergy_soap.txt"
    assert note_path.exists()
    text = note_path.read_text(encoding="utf-8")

    extractor = RuleBasedExtractor()
    note = ClinicalNote(text=text, language="es")
    entities = extractor.extract(note)

    assert entities.patient.name == "Maria E Garcia"
    assert entities.patient.gender == "female"
    assert entities.patient.birth_date == "1988-09-22"

    cond_codes = {c.snomed_code for c in entities.conditions}
    assert "195967001" in cond_codes  # Asthma

    med_codes = {m.rxnorm_code for m in entities.medications}
    assert "745752" in med_codes  # Albuterol / Salbutamol

    allg_codes = {a.snomed_code for a in entities.allergies}
    assert "91935004" in allg_codes  # Peanut

    builder = FHIRBundleBuilder()
    bundle = builder.build_bundle(entities)
    is_valid, messages = builder.validate_bundle(bundle)

    assert is_valid
