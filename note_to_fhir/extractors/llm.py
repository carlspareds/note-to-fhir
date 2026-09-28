"""
Optional LLM-assisted clinical entity extractor supporting OpenAI, Anthropic, and Gemini.
Gracefully falls back to RuleBasedExtractor when API keys are not provided.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from note_to_fhir.extractors.base import BaseExtractor
from note_to_fhir.extractors.rules import RuleBasedExtractor
from note_to_fhir.models import (
    AllergyEntity,
    ClinicalNote,
    ConditionEntity,
    EncounterInfo,
    ExtractedEntities,
    MedicationEntity,
    PatientInfo,
    VitalSignObservation,
)

logger = logging.getLogger(__name__)


EXTRACTION_SYSTEM_PROMPT = """You are an expert clinical NLP system.
Extract structured clinical entities from the clinical note (in English or Spanish)
and return ONLY a valid JSON object matching the following structure:

{
  "patient": {
    "name": "string or null",
    "gender": "male | female | other | unknown",
    "birth_date": "YYYY-MM-DD or null"
  },
  "encounter": {
    "date": "YYYY-MM-DD or null",
    "encounter_type": "ambulatory"
  },
  "conditions": [
    {
      "text": "verbatim text",
      "display": "standard clinical name",
      "snomed_code": "SNOMED CT ID string",
      "icd10_code": "ICD-10-CM code string",
      "status": "active"
    }
  ],
  "medications": [
    {
      "text": "verbatim text",
      "display": "standard drug name",
      "rxnorm_code": "RxNorm CUI string",
      "dosage": "string or null",
      "status": "active"
    }
  ],
  "allergies": [
    {
      "text": "verbatim allergen",
      "display": "standard allergy name",
      "snomed_code": "SNOMED CT ID string",
      "category": "medication | food | environment | biologic",
      "status": "active"
    }
  ],
  "observations": [
    {
      "name": "vital sign name",
      "loinc_code": "LOINC code",
      "value": float or null,
      "unit": "string",
      "ucum_code": "UCUM code string",
      "systolic": float or null,
      "diastolic": float or null
    }
  ]
}

Return ONLY the JSON. Do not include markdown formatting or commentary.
"""


class LLMExtractor(BaseExtractor):
    """
    LLM Extractor with multi-provider support (OpenAI, Anthropic, Gemini).
    Automatically skips LLM and uses deterministic rule-based extractor if no keys are found.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or self._detect_provider()
        self.fallback = RuleBasedExtractor()

    def _detect_provider(self) -> Optional[str]:
        explicit_provider = os.getenv("LLM_PROVIDER") or os.getenv("EXTRACTOR_PROVIDER")
        if explicit_provider:
            return explicit_provider.lower()
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.getenv("GEMINI_API_KEY"):
            return "gemini"
        return None

    @property
    def is_available(self) -> bool:
        """Returns True if a supported LLM provider API key is present."""
        return self.provider is not None

    def extract(self, note: ClinicalNote) -> ExtractedEntities:
        """
        Extract clinical entities using configured LLM, or fallback to RuleBasedExtractor.
        """
        if not self.is_available:
            logger.info("No LLM API keys configured. Using offline RuleBasedExtractor fallback.")
            return self.fallback.extract(note)

        try:
            raw_json_str = self._call_llm(note.text)
            parsed = self._parse_json(raw_json_str)
            return self._build_entities_from_dict(parsed)
        except Exception as e:
            logger.warning("LLM extraction encountered error: %s. Falling back to RuleBasedExtractor.", e)
            return self.fallback.extract(note)

    def _call_llm(self, note_text: str) -> str:
        """Invoke the configured LLM API provider."""
        if self.provider == "openai":
            import openai
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": note_text},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content or "{}"

        elif self.provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic()
            resp = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                system=EXTRACTION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": note_text}],
                temperature=0.0,
                max_tokens=4000,
            )
            return resp.content[0].text

        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(
                model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
                system_instruction=EXTRACTION_SYSTEM_PROMPT,
            )
            resp = model.generate_content(note_text)
            return resp.text

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _parse_json(self, raw_str: str) -> Dict[str, Any]:
        """Safely parse JSON string, removing markdown codeblocks and surrounding text if present."""
        clean = raw_str.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        first_brace = clean.find("{")
        last_brace = clean.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace >= first_brace:
            clean = clean[first_brace : last_brace + 1]
        return json.loads(clean.strip())

    def _build_entities_from_dict(self, data: Dict[str, Any]) -> ExtractedEntities:
        """Map parsed dictionary into ExtractedEntities domain model."""
        pat_d = data.get("patient", {})
        patient = PatientInfo(
            name=pat_d.get("name"),
            gender=pat_d.get("gender", "unknown"),
            birth_date=pat_d.get("birth_date"),
        )

        enc_d = data.get("encounter", {})
        encounter = EncounterInfo(
            date=enc_d.get("date", "2024-03-15"),
            encounter_type=enc_d.get("encounter_type", "ambulatory"),
        )

        conditions = [
            ConditionEntity(
                text=c.get("text", ""),
                display=c.get("display") or c.get("text", ""),
                snomed_code=c.get("snomed_code"),
                icd10_code=c.get("icd10_code"),
                status=c.get("status", "active"),
            )
            for c in data.get("conditions", [])
        ]

        medications = [
            MedicationEntity(
                text=m.get("text", ""),
                display=m.get("display") or m.get("text", ""),
                rxnorm_code=m.get("rxnorm_code"),
                dosage=m.get("dosage"),
                status=m.get("status", "active"),
            )
            for m in data.get("medications", [])
        ]

        allergies = [
            AllergyEntity(
                text=a.get("text", ""),
                display=a.get("display") or a.get("text", ""),
                snomed_code=a.get("snomed_code"),
                category=a.get("category", "medication"),
                status=a.get("status", "active"),
            )
            for a in data.get("allergies", [])
        ]

        observations = [
            VitalSignObservation(
                name=o.get("name", "vital_sign"),
                loinc_code=o.get("loinc_code", ""),
                value=o.get("value"),
                unit=o.get("unit", ""),
                ucum_code=o.get("ucum_code", ""),
                systolic=o.get("systolic"),
                diastolic=o.get("diastolic"),
            )
            for o in data.get("observations", [])
        ]

        return ExtractedEntities(
            patient=patient,
            encounter=encounter,
            conditions=conditions,
            medications=medications,
            allergies=allergies,
            observations=observations,
        )
