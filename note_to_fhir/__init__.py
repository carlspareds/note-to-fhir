"""
note_to_fhir: Convert unstructured clinical notes (English & Spanish) into valid HL7 FHIR R4 Bundles.
"""

from note_to_fhir.builder import FHIRBundleBuilder
from note_to_fhir.extractors.base import BaseExtractor
from note_to_fhir.extractors.llm import LLMExtractor
from note_to_fhir.extractors.rules import RuleBasedExtractor
from note_to_fhir.models import ClinicalNote, ConversionResult, ExtractedEntities

__version__ = "0.1.0"


def convert(
    text: str,
    language: str = "auto",
    extractor_engine: str = "rules",
    encounter_date: str | None = None,
    validate: bool = True,
) -> ConversionResult:
    """
    High-level convenience function to convert clinical note text to an HL7 FHIR R4 Bundle.
    """
    if extractor_engine.lower() == "llm":
        extractor = LLMExtractor()
    else:
        extractor = RuleBasedExtractor()

    note = ClinicalNote(text=text, language=language, encounter_date=encounter_date)
    entities = extractor.extract(note)
    builder = FHIRBundleBuilder()
    bundle = builder.build_bundle(entities)
    is_valid = True
    messages = []
    if validate:
        is_valid, messages = builder.validate_bundle(bundle)

    return ConversionResult(
        bundle=bundle,
        is_valid=is_valid,
        validation_messages=messages,
        extracted_entities=entities,
    )


__all__ = [
    "BaseExtractor",
    "RuleBasedExtractor",
    "LLMExtractor",
    "FHIRBundleBuilder",
    "ClinicalNote",
    "ExtractedEntities",
    "ConversionResult",
    "convert",
]
