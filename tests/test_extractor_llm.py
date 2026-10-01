"""
Unit tests for LLMExtractor fallback and JSON handling.
"""

import os
from unittest.mock import patch

from note_to_fhir.extractors.llm import LLMExtractor
from note_to_fhir.models import ClinicalNote


def test_llm_extractor_fallback_when_no_keys():
    """Verify fallback to RuleBasedExtractor when no API keys are set."""
    with patch.dict(os.environ, {}, clear=True):
        extractor = LLMExtractor()
        assert not extractor.is_available

        note = ClinicalNote(
            text="Patient Name: Alex Brown\nPast Medical History: Type 2 diabetes mellitus\nCurrent Medications: Lisinopril 10 mg\nVital Signs:\n- Heart Rate: 72 bpm"
        )
        entities = extractor.extract(note)

        assert entities.patient.name == "Alex Brown"
        assert len(entities.conditions) >= 1
        assert entities.conditions[0].snomed_code == "44054006"


def test_llm_json_parsing_clean_markdown():
    """Verify markdown code fence stripping and JSON mapping."""
    extractor = LLMExtractor()
    raw_response = """```json
    {
      "patient": {"name": "Carlos Gomez", "gender": "male", "birth_date": "1980-01-01"},
      "encounter": {"date": "2024-03-15", "encounter_type": "ambulatory"},
      "conditions": [{"text": "Asthma", "display": "Asthma", "snomed_code": "195967001", "status": "active"}],
      "medications": [{"text": "Albuterol", "display": "Albuterol", "rxnorm_code": "745752", "status": "active"}],
      "allergies": [],
      "observations": [{"name": "heart_rate", "loinc_code": "8867-4", "value": 75.0, "unit": "/min", "ucum_code": "/min"}]
    }
    ```"""
    parsed = extractor._parse_json(raw_response)
    entities = extractor._build_entities_from_dict(parsed)

    assert entities.patient.name == "Carlos Gomez"
    assert entities.conditions[0].snomed_code == "195967001"
    assert entities.medications[0].rxnorm_code == "745752"
    assert entities.observations[0].value == 75.0
