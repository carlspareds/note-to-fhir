"""
Unit tests for note_to_fhir.convert high-level API.
"""

from note_to_fhir import convert
from note_to_fhir.models import ConversionResult


def test_top_level_convert_function_english():
    note_text = (
        "Patient Name: Sarah Connor\n"
        "DOB: 1985-05-12 | Gender: Female\n"
        "Date: 2024-03-15\n"
        "Past Medical History:\n- Essential hypertension\n"
        "Current Medications:\n- Lisinopril 10 MG\n"
        "Allergies:\n- Penicillin allergy\n"
        "Vital Signs:\n- Blood Pressure: 125/80 mmHg\n- Heart Rate: 72 bpm\n"
    )
    res = convert(note_text)
    assert isinstance(res, ConversionResult)
    assert res.is_valid
    assert res.bundle["resourceType"] == "Bundle"
    assert res.extracted_entities.patient.name == "Sarah Connor"
    assert res.extracted_entities.patient.gender == "female"
    assert len(res.extracted_entities.conditions) >= 1
    assert len(res.extracted_entities.medications) >= 1
    assert len(res.extracted_entities.allergies) >= 1
    assert len(res.extracted_entities.observations) >= 2


def test_top_level_convert_function_spanish():
    note_text = (
        "Nombre del Paciente: Mateo Gomez\n"
        "Fecha de Nacimiento: 1975-08-10 | Género: Masculino\n"
        "Fecha: 2024-03-15\n"
        "Antecedentes Médicos Personales:\n- Diabetes mellitus tipo 2\n"
        "Medicación Actual:\n- Metformina 500 mg\n"
        "Alergias:\n- Alergia al maní\n"
        "Signos Vitales:\n- Presión Arterial: 120/75 mmHg\n"
    )
    res = convert(note_text, language="es")
    assert isinstance(res, ConversionResult)
    assert res.is_valid
    assert res.extracted_entities.patient.gender == "male"
    assert res.extracted_entities.conditions[0].snomed_code == "44054006"
