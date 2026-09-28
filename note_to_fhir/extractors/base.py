"""
Base Extractor interface for clinical entity extraction.
"""

from abc import ABC, abstractmethod

from note_to_fhir.models import ClinicalNote, ExtractedEntities


class BaseExtractor(ABC):
    """Abstract base class for clinical entity extractors."""

    @abstractmethod
    def extract(self, note: ClinicalNote) -> ExtractedEntities:
        """
        Extract clinical entities (Patient, Encounter, Conditions,
        Medications, Allergies, Observations) from an unstructured clinical note.

        Args:
            note: Input ClinicalNote object containing text, language, and metadata.

        Returns:
            ExtractedEntities instance containing standard-coded clinical entities.
        """
        pass
