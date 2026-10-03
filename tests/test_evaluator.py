"""
tests/test_evaluator.py

Unit tests verifying that evaluation metrics for English and Spanish cohorts
are computed independently from their respective note directories, maintain
distinct object identities, and produce distinct benchmark metrics.
"""

import json
from pathlib import Path

from evals.evaluator import run_evaluation


def test_evaluator_en_and_es_test_cohorts_independent():
    """Verify that English and Spanish test-cohort counts in evals/results.json are distinct."""
    root = Path(__file__).resolve().parent.parent
    results_json = root / "evals" / "results.json"

    assert results_json.exists(), "evals/results.json does not exist"
    with open(results_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_en = data["test_cohort"]["english"]
    test_es = data["test_cohort"]["spanish"]

    # Assert they are distinct objects and not identical copies
    assert test_en is not test_es
    assert test_en["categories"] is not test_es["categories"]
    assert test_en["overall"] is not test_es["overall"]

    # Assert overall counts are distinct between English and Spanish
    assert test_en["overall"]["tp"] != test_es["overall"]["tp"]
    assert test_en["overall"]["fn"] != test_es["overall"]["fn"]
    assert test_en["overall"]["f1"] != test_es["overall"]["f1"]

    # Verify exact benchmark numbers
    assert test_en["overall"]["tp"] == 329
    assert test_es["overall"]["tp"] == 334
    assert test_en["overall"]["fn"] == 121
    assert test_es["overall"]["fn"] == 116
    assert test_en["overall"]["f1"] == 0.8184
    assert test_es["overall"]["f1"] == 0.8257

    # Verify demographic extraction accounts for English vs Spanish formatting
    assert test_en["categories"]["demographics"]["tp"] == 70
    assert test_es["categories"]["demographics"]["tp"] == 75
    assert test_en["categories"]["demographics"]["fn"] == 5
    assert test_es["categories"]["demographics"]["fn"] == 0


def test_evaluator_computes_from_separate_directories(tmp_path):
    """
    Verify that run_evaluation reads from separate language directories and
    produces distinct result objects without reusing internal dictionaries.
    """
    en_dir = tmp_path / "notes" / "en"
    es_dir = tmp_path / "notes" / "es"
    en_dir.mkdir(parents=True)
    es_dir.mkdir(parents=True)

    # 1 patient in test split
    pid = "Patient_Test_001"
    gold_labels = {
        pid: {
            "split": "test",
            "patient": {"name": "Alice Smith", "gender": "female", "birthDate": "1980-01-01"},
            "gold": {
                "conditions": [{"snomed": "44054006", "display": "Type 2 diabetes mellitus"}],
                "medications": [{"rxnorm": "314076", "display": "Lisinopril"}],
                "allergies": [],
                "vitals": {},
            },
        }
    }
    with open(tmp_path / "gold_labels.json", "w", encoding="utf-8") as f:
        json.dump(gold_labels, f)

    # English note has diabetes and lisinopril
    en_note = (
        "Patient: Alice Smith\n"
        "DOB: 1980-01-01 | Gender: Female\n"
        "Past Medical History: Type 2 diabetes mellitus\n"
        "Medications: Lisinopril 10 mg"
    )
    (en_dir / f"{pid}_soap.txt").write_text(en_note, encoding="utf-8")

    # Spanish note has diabetes only (no medication)
    es_note = (
        "Paciente: Alice Smith\n"
        "Fecha de Nacimiento: 1980-01-01 | Género: Femenino\n"
        "Antecedentes: Diabetes mellitus tipo 2"
    )
    (es_dir / f"{pid}_soap.txt").write_text(es_note, encoding="utf-8")

    res = run_evaluation(tmp_path, extractor_name="rules")
    assert res is not None

    test_en = res["test_cohort"]["english"]
    test_es = res["test_cohort"]["spanish"]

    # Verify distinct object identities
    assert test_en is not test_es
    assert test_en["categories"] is not test_es["categories"]
    assert test_en["overall"] is not test_es["overall"]

    # Verify separate counts from different directory contents
    assert test_en["categories"]["medications"]["tp"] == 1
    assert test_es["categories"]["medications"]["tp"] == 0
    assert test_en["overall"]["tp"] != test_es["overall"]["tp"]
