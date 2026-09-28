"""
Unit tests for FHIRBundleBuilder.
"""

from note_to_fhir.builder import FHIRBundleBuilder
from note_to_fhir.models import (
    AllergyEntity,
    ConditionEntity,
    EncounterInfo,
    ExtractedEntities,
    MedicationEntity,
    PatientInfo,
    VitalSignObservation,
)


def test_fhir_bundle_builder_structure():
    builder = FHIRBundleBuilder()
    entities = ExtractedEntities(
        patient=PatientInfo(name="Test Patient", gender="female", birth_date="1990-05-10"),
        encounter=EncounterInfo(date="2024-03-15", encounter_type="ambulatory"),
        conditions=[
            ConditionEntity(text="Asthma", display="Asthma", snomed_code="195967001", icd10_code="J45.909")
        ],
        medications=[
            MedicationEntity(text="Albuterol", display="Albuterol 90 MCG", rxnorm_code="745752")
        ],
        allergies=[
            AllergyEntity(text="Penicillin", display="Allergy to penicillin", snomed_code="91936005", category="medication")
        ],
        observations=[
            VitalSignObservation(
                name="blood_pressure",
                loinc_code="85354-9",
                unit="mmHg",
                ucum_code="mm[Hg]",
                systolic=120.0,
                diastolic=80.0,
            ),
            VitalSignObservation(
                name="heart_rate",
                loinc_code="8867-4",
                value=72.0,
                unit="/min",
                ucum_code="/min",
            ),
        ],
    )

    bundle = builder.build_bundle(entities)

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"
    assert len(bundle["entry"]) == 7  # Patient, Encounter, Condition, Med, Allergy, 2 Obs (BP + HR)

    # Check resource types
    resource_types = [e["resource"]["resourceType"] for e in bundle["entry"]]
    assert "Patient" in resource_types
    assert "Encounter" in resource_types
    assert "Condition" in resource_types
    assert "MedicationStatement" in resource_types
    assert "AllergyIntolerance" in resource_types
    assert "Observation" in resource_types

    # Validate bundle
    is_valid, messages = builder.validate_bundle(bundle)
    assert is_valid, f"Bundle validation failed: {messages}"


def test_fhir_builder_ucum_compliance():
    builder = FHIRBundleBuilder()
    entities = ExtractedEntities(
        patient=PatientInfo(name="UCUM Test"),
        encounter=EncounterInfo(date="2024-03-15"),
        observations=[
            VitalSignObservation(
                name="body_temperature",
                loinc_code="8310-5",
                value=37.0,
                unit="Cel",
                ucum_code="Cel",
            )
        ],
    )
    bundle = builder.build_bundle(entities)
    obs_res = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Observation"][0]
    vq = obs_res["valueQuantity"]
    assert vq["system"] == "http://unitsofmeasure.org"
    assert vq["code"] == "Cel"
    assert vq["value"] == 37.0


def test_fhir_builder_uuid_and_id_alignment():
    """Verify that resource.id matches the UUID suffix in fullUrl."""
    builder = FHIRBundleBuilder()
    entities = ExtractedEntities(
        patient=PatientInfo(name="Jane Doe"),
        conditions=[ConditionEntity(text="Asthma", snomed_code="195967001")],
        medications=[MedicationEntity(text="Albuterol", rxnorm_code="745752")],
        allergies=[AllergyEntity(text="Penicillin", snomed_code="91936005")],
        observations=[
            VitalSignObservation(
                name="heart_rate", loinc_code="8867-4", value=70.0, unit="/min", ucum_code="/min"
            )
        ],
    )
    bundle = builder.build_bundle(entities)

    for entry in bundle["entry"]:
        full_url = entry["fullUrl"]
        res_id = entry["resource"]["id"]
        assert full_url.startswith("urn:uuid:")
        assert full_url.replace("urn:uuid:", "") == res_id


def test_fhir_builder_ucum_validation_failure():
    """Verify that observations with non-UCUM systems fail validation."""
    builder = FHIRBundleBuilder()
    entities = ExtractedEntities(
        patient=PatientInfo(name="Invalid UCUM"),
        observations=[
            VitalSignObservation(
                name="heart_rate", loinc_code="8867-4", value=70.0, unit="bpm", ucum_code="bpm"
            )
        ],
    )
    bundle = builder.build_bundle(entities)
    # Corrupt the unit system
    for entry in bundle["entry"]:
        if entry["resource"]["resourceType"] == "Observation":
            entry["resource"]["valueQuantity"]["system"] = "http://custom-system.org"

    is_valid, messages = builder.validate_bundle(bundle)
    assert not is_valid
    assert any("missing UCUM system" in m for m in messages)


def test_fhir_builder_context_references():
    """Verify that Condition, MedicationStatement, Observation, and Allergy link to encounter."""
    builder = FHIRBundleBuilder()
    entities = ExtractedEntities(
        patient=PatientInfo(name="Context Test"),
        encounter=EncounterInfo(date="2024-03-15"),
        conditions=[ConditionEntity(text="Asthma", snomed_code="195967001")],
        medications=[MedicationEntity(text="Albuterol", rxnorm_code="745752")],
        allergies=[AllergyEntity(text="Penicillin", snomed_code="91936005")],
        observations=[
            VitalSignObservation(
                name="heart_rate", loinc_code="8867-4", value=70.0, unit="/min", ucum_code="/min"
            )
        ],
    )
    bundle = builder.build_bundle(entities)
    enc_entry = [e for e in bundle["entry"] if e["resource"]["resourceType"] == "Encounter"][0]
    enc_ref = enc_entry["fullUrl"]

    for entry in bundle["entry"]:
        res = entry["resource"]
        if res["resourceType"] == "Condition":
            assert res.get("encounter", {}).get("reference") == enc_ref
        elif res["resourceType"] == "MedicationStatement":
            assert res.get("context", {}).get("reference") == enc_ref
        elif res["resourceType"] == "Observation":
            assert res.get("encounter", {}).get("reference") == enc_ref
        elif res["resourceType"] == "AllergyIntolerance":
            assert res.get("encounter", {}).get("reference") == enc_ref
