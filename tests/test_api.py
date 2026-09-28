"""
Unit tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient

from note_to_fhir.api import app

client = TestClient(app)


def test_api_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_api_convert_endpoint_english():
    payload = {
        "text": (
            "Patient Name: Alice Smith\n"
            "DOB: 1975-08-20\n"
            "Past Medical History:\n- Essential hypertension\n"
            "Current Medications:\n- Lisinopril 10 MG\n"
            "Allergies:\n- Allergy to penicillin\n"
            "Vital Signs:\n- Blood Pressure: 130/80 mmHg\n"
        ),
        "language": "en",
        "extractor": "rules",
        "validate": True,
    }
    resp = client.post("/convert", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["entities_count"]["conditions"] >= 1
    assert data["entities_count"]["medications"] >= 1
    assert data["entities_count"]["allergies"] >= 1
    assert data["bundle"]["resourceType"] == "Bundle"


def test_api_convert_endpoint_spanish():
    payload = {
        "text": (
            "Nombre del Paciente: Juan Perez\n"
            "Fecha de Nacimiento: 1982-04-10\n"
            "Antecedentes Médicos Personales:\n- Diabetes mellitus tipo 2\n"
            "Medicación Actual:\n- Metformina 500 mg\n"
            "Alergias:\n- Alergia al maní\n"
            "Signos Vitales:\n- Presión Arterial: 120/75 mmHg\n"
        ),
        "language": "es",
        "extractor": "rules",
        "validate": True,
    }
    resp = client.post("/convert", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["entities_count"]["conditions"] >= 1
    assert data["entities_count"]["medications"] >= 1


def test_api_convert_empty_error():
    payload = {"text": "   "}
    resp = client.post("/convert", json=payload)
    assert resp.status_code == 400
