"""
Deterministic rule-based and dictionary extractor for clinical notes (English & Spanish).
Runs completely offline with zero external API dependencies.
"""

import re
from typing import Dict, List, Optional, Set

from note_to_fhir.extractors.base import BaseExtractor
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
from note_to_fhir.terminology import (
    ALLERGIES_DATABASE,
    CONDITIONS_DATABASE,
    MEDICATIONS_DATABASE,
    VITAL_SIGNS_TERMINOLOGY,
)


class RuleBasedExtractor(BaseExtractor):
    """
    Offline deterministic clinical entity extractor using regex and curated terminology tables.
    Supports bilingual English & Spanish notes.
    """

    def __init__(self):
        self._init_regexes()

    def _init_regexes(self):
        """Compile regex patterns for demographic details and vital signs."""
        # Patient Name: captures name and stops at |, newline, or subsequent demographic tags
        self.re_name = re.compile(
            r"(?:Patient Name|Nombre del Paciente|Paciente|Patient)\s*[:=-]?\s*([^|\n\r]+?)(?=\s*(?:\||\b(?:DOB|Fecha|Gender|Género|Sexo|Date)\b|\r|\n|$))",
            re.IGNORECASE,
        )
        # DOB: YYYY-MM-DD or MM/DD/YYYY or DD/MM/YYYY
        self.re_dob = re.compile(
            r"(?:DOB|Fecha de Nacimiento|Date of Birth|nacido(?: el)?|born)\s*[:=-]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}/[0-9]{1,2}/[0-9]{4})|"
            r"(?:born\s+|nacido el\s+)([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}/[0-9]{1,2}/[0-9]{4})",
            re.IGNORECASE,
        )
        # Gender
        self.re_gender = re.compile(
            r"(?:Gender|Género|Sexo)\s*[:=-]?\s*([^\n\r,|]+)",
            re.IGNORECASE,
        )
        # Encounter Date
        self.re_date = re.compile(
            r"(?:Date|Fecha|Encounter Date|Fecha de Consulta)\s*[:=-]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
            re.IGNORECASE,
        )

        # Blood Pressure: 120/80, 138.0/86.0 mmHg
        self.re_bp = re.compile(
            r"(?:Blood Pressure|Presión Arterial|BP|PA)(?:\s*\([^)]*\))?\s*[:=-]?\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*[/x]\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*(?:mm\s*Hg|mmHg)?",
            re.IGNORECASE,
        )
        # Heart Rate: 74 bpm, 74.0 lpm
        self.re_hr = re.compile(
            r"(?:Heart Rate|Frecuencia Cardíaca|Pulse|Pulso|HR|FC)(?:\s*\([^)]*\))?\s*[:=-]?\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*(?:bpm|lpm|/min)?",
            re.IGNORECASE,
        )
        # Respiratory Rate: 16 breaths/min, 16.0 respiraciones/minuto
        self.re_rr = re.compile(
            r"(?:Respiratory Rate|Frecuencia Respiratoria|RR|FR)(?:\s*\([^)]*\))?\s*[:=-]?\s*([0-9]{1,2}(?:\.[0-9]+)?)\s*(?:breaths/min|respiraciones/minuto|rpm|/min)?",
            re.IGNORECASE,
        )
        # Body Temperature: 98.6 F, 37.0 °C, 101.4 F
        self.re_temp = re.compile(
            r"(?:Temperature|Temperatura|Temp)(?:\s*\([^)]*\))?\s*[:=-]?\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*(?:(?:°|deg(?:rees)?|grados)?\s*([FCfc]))?",
            re.IGNORECASE,
        )
        # SpO2: 96%, 93.0%
        self.re_spo2 = re.compile(
            r"(?:SpO2|Oxygen Saturation|Saturación de Oxígeno|SatO2)(?:\s*\([^)]*\))?\s*[:=-]?\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*%?",
            re.IGNORECASE,
        )
        # BMI: 27.8 kg/m2
        self.re_bmi = re.compile(
            r"(?:BMI|Body Mass Index|IMC|Índice de Masa Corporal)(?:\s*\([^)]*\))?\s*[:=-]?\s*([0-9]{1,2}(?:\.[0-9]+)?)\s*(?:kg/m2)?",
            re.IGNORECASE,
        )
        # Weight
        self.re_weight = re.compile(
            r"(?:Weight|Peso)\s*[:=-]?\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*(kg|lbs?|libras|kilos)?",
            re.IGNORECASE,
        )
        # Height
        self.re_height = re.compile(
            r"(?:Height|Talla|Estatura)\s*[:=-]?\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*(cm|m|pulgadas|in)?",
            re.IGNORECASE,
        )

    def extract(self, note: ClinicalNote) -> ExtractedEntities:
        """Extract structured clinical entities from the clinical note."""
        text = note.text
        patient = self._extract_patient(text)
        encounter = self._extract_encounter(text, note.encounter_date)
        observations = self._extract_vitals(text)
        sections = self._split_sections(text)

        conditions = self._extract_conditions(text, sections)
        medications = self._extract_medications(text, sections)
        allergies = self._extract_allergies(text, sections)

        return ExtractedEntities(
            patient=patient,
            encounter=encounter,
            conditions=conditions,
            medications=medications,
            allergies=allergies,
            observations=observations,
        )

    def _extract_patient(self, text: str) -> PatientInfo:
        """Extract patient demographic info."""
        name = None
        m_name = self.re_name.search(text)
        if m_name:
            raw_name = m_name.group(1).strip().strip("-:| ")
            # If Last, First format (e.g. Doe, John), keep clean or flip
            if "," in raw_name and len(raw_name.split(",")) == 2:
                last, first = raw_name.split(",", 1)
                name = f"{first.strip()} {last.strip()}".strip()
            else:
                name = raw_name

        birth_date = None
        m_dob = self.re_dob.search(text)
        if m_dob:
            raw_dob = m_dob.group(1) or m_dob.group(2)
            if raw_dob:
                # Normalize MM/DD/YYYY to YYYY-MM-DD
                if "/" in raw_dob:
                    parts = raw_dob.split("/")
                    if len(parts) == 3 and len(parts[2]) == 4:
                        birth_date = f"{parts[2]}-{int(parts[0]):02d}-{int(parts[1]):02d}"
                    else:
                        birth_date = raw_dob
                else:
                    birth_date = raw_dob

        gender = "unknown"
        m_gen = self.re_gender.search(text)
        female_tokens = {"female", "femenino", "mujer", "f", "woman"}
        male_tokens = {"male", "masculino", "hombre", "m", "man", "varón", "varon"}

        if m_gen:
            raw_gen = m_gen.group(1).strip().lower()
            words = set(re.findall(r"\b\w+\b", raw_gen))
            # CRITICAL: Test female FIRST to avoid 'female' matching 'male' or 'm'
            if words & female_tokens or raw_gen in female_tokens:
                gender = "female"
            elif words & male_tokens or raw_gen in male_tokens:
                gender = "male"
            else:
                gender = "other"
        else:
            # Fallback search in text with strict word boundaries
            t_low = text.lower()
            if re.search(r"\b(?:female|femenino|mujer)\b", t_low):
                gender = "female"
            elif re.search(r"\b(?:male|masculino|hombre|varón|varon)\b", t_low):
                gender = "male"

        return PatientInfo(name=name, gender=gender, birth_date=birth_date)

    def _extract_encounter(self, text: str, default_date: Optional[str]) -> EncounterInfo:
        """Extract encounter metadata."""
        date = default_date
        m_date = self.re_date.search(text)
        if m_date:
            date = m_date.group(1)
        return EncounterInfo(date=date or "2024-03-15", encounter_type="ambulatory")

    def _extract_vitals(self, text: str) -> List[VitalSignObservation]:
        """Extract all vital signs from text using regex and map to LOINC & UCUM."""
        obs_list: List[VitalSignObservation] = []

        # 1. Blood pressure
        m_bp = self.re_bp.search(text)
        if m_bp:
            systolic = float(m_bp.group(1))
            diastolic = float(m_bp.group(2))
            bp_def = VITAL_SIGNS_TERMINOLOGY["blood_pressure"]
            obs_list.append(
                VitalSignObservation(
                    name="blood_pressure",
                    loinc_code=bp_def["loinc"],
                    unit="mmHg",
                    ucum_code="mm[Hg]",
                    systolic=systolic,
                    diastolic=diastolic,
                )
            )

        # 2. Heart rate
        m_hr = self.re_hr.search(text)
        if m_hr:
            val = float(m_hr.group(1))
            hr_def = VITAL_SIGNS_TERMINOLOGY["heart_rate"]
            obs_list.append(
                VitalSignObservation(
                    name="heart_rate",
                    loinc_code=hr_def["loinc"],
                    value=val,
                    unit=hr_def["unit"],
                    ucum_code=hr_def["ucum"],
                )
            )

        # 3. Respiratory rate
        m_rr = self.re_rr.search(text)
        if m_rr:
            val = float(m_rr.group(1))
            rr_def = VITAL_SIGNS_TERMINOLOGY["respiratory_rate"]
            obs_list.append(
                VitalSignObservation(
                    name="respiratory_rate",
                    loinc_code=rr_def["loinc"],
                    value=val,
                    unit=rr_def["unit"],
                    ucum_code=rr_def["ucum"],
                )
            )

        # 4. Temperature
        m_temp = self.re_temp.search(text)
        if m_temp:
            val = float(m_temp.group(1))
            unit_hint = (m_temp.group(2) or "").upper()
            if unit_hint == "C" or (not unit_hint and val < 45.0):
                unit = "Cel"
                ucum = "Cel"
            else:
                unit = "[degF]"
                ucum = "[degF]"

            temp_def = VITAL_SIGNS_TERMINOLOGY["body_temperature"]
            obs_list.append(
                VitalSignObservation(
                    name="body_temperature",
                    loinc_code=temp_def["loinc"],
                    value=val,
                    unit=unit,
                    ucum_code=ucum,
                )
            )

        # 5. SpO2
        m_spo2 = self.re_spo2.search(text)
        if m_spo2:
            val = float(m_spo2.group(1))
            spo2_def = VITAL_SIGNS_TERMINOLOGY["oxygen_saturation"]
            obs_list.append(
                VitalSignObservation(
                    name="oxygen_saturation",
                    loinc_code=spo2_def["loinc"],
                    value=val,
                    unit=spo2_def["unit"],
                    ucum_code=spo2_def["ucum"],
                )
            )

        # 6. BMI
        m_bmi = self.re_bmi.search(text)
        if m_bmi:
            val = float(m_bmi.group(1))
            bmi_def = VITAL_SIGNS_TERMINOLOGY["bmi"]
            obs_list.append(
                VitalSignObservation(
                    name="bmi",
                    loinc_code=bmi_def["loinc"],
                    value=val,
                    unit=bmi_def["unit"],
                    ucum_code=bmi_def["ucum"],
                )
            )

        # 7. Body Weight
        m_wt = self.re_weight.search(text)
        if m_wt:
            val = float(m_wt.group(1))
            unit_hint = (m_wt.group(2) or "").lower()
            if "lb" in unit_hint or "libra" in unit_hint:
                val = round(val * 0.453592, 1)
            wt_def = VITAL_SIGNS_TERMINOLOGY["body_weight"]
            obs_list.append(
                VitalSignObservation(
                    name="body_weight",
                    loinc_code=wt_def["loinc"],
                    value=val,
                    unit=wt_def["unit"],
                    ucum_code=wt_def["ucum"],
                )
            )

        # 8. Body Height
        m_ht = self.re_height.search(text)
        if m_ht:
            val = float(m_ht.group(1))
            unit_hint = (m_ht.group(2) or "").lower()
            if unit_hint == "m" or (val < 2.5 and not unit_hint):
                val = round(val * 100, 1)
            elif "in" in unit_hint or "pulgada" in unit_hint:
                val = round(val * 2.54, 1)
            ht_def = VITAL_SIGNS_TERMINOLOGY["body_height"]
            obs_list.append(
                VitalSignObservation(
                    name="body_height",
                    loinc_code=ht_def["loinc"],
                    value=val,
                    unit=ht_def["unit"],
                    ucum_code=ht_def["ucum"],
                )
            )

        return obs_list

    def _split_sections(self, text: str) -> Dict[str, str]:
        """Split SOAP clinical note into sections."""
        sections: Dict[str, str] = {
            "pmh": "",
            "medications": "",
            "allergies": "",
            "vitals": "",
            "assessment": "",
            "plan": "",
            "other": "",
        }

        # Identify section boundaries by common headers
        lines = text.splitlines()
        current_section = None

        for line in lines:
            line_str = line.strip()
            l_low = line_str.lower()

            if any(h in l_low for h in ["past medical history", "antecedentes médicos", "pmh:"]):
                current_section = "pmh"
                continue
            elif any(h in l_low for h in ["current medications", "medicación actual", "medications:", "fármacos"]):
                current_section = "medications"
                continue
            elif any(h in l_low for h in ["allergies:", "alergias:", "known allergies"]):
                current_section = "allergies"
                continue
            elif any(h in l_low for h in ["vital signs:", "signos vitales:", "constantes vitales"]):
                current_section = "vitals"
                continue
            elif any(h in l_low for h in ["assessment:", "impresión clínica:", "diagnósticos:"]):
                current_section = "assessment"
                continue
            elif any(h in l_low for h in ["plan:", "plan terapéutico:"]):
                current_section = "plan"
                continue
            elif any(h in l_low for h in [
                "subjective:", "subjetivo:", "objective:", "objetivo:",
                "history of present illness", "enfermedad actual", "hpi:",
                "physical examination:", "examen físico:", "exploración física:",
                "chief complaint:", "motivo de consulta:"
            ]):
                current_section = "other"
                continue

            if current_section and current_section in sections:
                sections[current_section] += line_str + "\n"

        return sections

    def _is_negated(self, text_segment: str, match_start: int) -> bool:
        """Check if a clinical mention is preceded by a negation expression on the same line."""
        line_start = text_segment.rfind("\n", 0, match_start)
        if line_start == -1:
            line_start = 0
        window = text_segment[line_start:match_start].lower()

        neg_patterns = [
            r"\bno\s+history\s+of\b",
            r"\bno\s+evidence\s+of\b",
            r"\bdenies\b",
            r"\bdenied\b",
            r"\bnegative\s+for\b",
            r"\bruled\s+out\b",
            r"\bwithout\b",
            r"\bno\b",
            r"\bsin\s+antecedentes\s+de\b",
            r"\bsin\s+historia\s+de\b",
            r"\bniega\b",
            r"\bnegativo\s+para\b",
            r"\bdescartado\b",
            r"\bsin\b",
        ]
        for np in neg_patterns:
            if re.search(np, window):
                return True
        return False

    def _extract_conditions(self, text: str, sections: Dict[str, str]) -> List[ConditionEntity]:
        """Match conditions against PMH/Assessment sections and full text with negation filtering."""
        candidates = sections.get("pmh", "") + "\n" + sections.get("assessment", "")
        if not candidates.strip():
            candidates = text

        found: List[ConditionEntity] = []
        seen_snomed: Set[str] = set()

        for cond in CONDITIONS_DATABASE:
            matched = False
            terms = cond["terms_en"] + cond["terms_es"]
            for term in terms:
                pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
                for m in re.finditer(pattern, candidates, re.IGNORECASE):
                    if not self._is_negated(candidates, m.start()):
                        matched = True
                        break
                if matched:
                    break

            if matched and cond["snomed"] not in seen_snomed:
                seen_snomed.add(cond["snomed"])
                found.append(
                    ConditionEntity(
                        text=cond["display"],
                        display=cond["display"],
                        snomed_code=cond["snomed"],
                        icd10_code=cond.get("icd10"),
                        status="active",
                    )
                )

        return found

    def _extract_medications(self, text: str, sections: Dict[str, str]) -> List[MedicationEntity]:
        """Match medications against the Medications section, filtering out allergies and negations."""
        candidates = sections.get("medications", "")
        if not candidates.strip():
            # Exclude allergies section from fallback to avoid extracting allergens as medications
            allergies_text = sections.get("allergies", "")
            candidates = text
            if allergies_text:
                candidates = candidates.replace(allergies_text, "")

        # Check for general negative medication declarations
        neg_med_patterns = [
            r"no active (?:prescription )?medications",
            r"no medications",
            r"sin medicación habitual",
            r"sin medicación",
            r"niega medicación",
        ]
        for nmp in neg_med_patterns:
            if re.search(nmp, candidates, re.IGNORECASE):
                return []

        found: List[MedicationEntity] = []
        seen_rxnorm: Set[str] = set()

        for med in MEDICATIONS_DATABASE:
            matched = False
            terms = med["terms_en"] + med["terms_es"]
            for term in terms:
                pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
                for m in re.finditer(pattern, candidates, re.IGNORECASE):
                    if not self._is_negated(candidates, m.start()):
                        matched = True
                        break
                if matched:
                    break

            if matched and med["rxnorm"] not in seen_rxnorm:
                seen_rxnorm.add(med["rxnorm"])
                found.append(
                    MedicationEntity(
                        text=med["display"],
                        display=med["display"],
                        rxnorm_code=med["rxnorm"],
                        status="active",
                    )
                )

        return found

    def _extract_allergies(self, text: str, sections: Dict[str, str]) -> List[AllergyEntity]:
        """Match allergies against Allergies section."""
        candidates = sections.get("allergies", "")
        if not candidates.strip():
            candidates = text

        # Check for negative allergy declarations
        neg_patterns = [
            r"no known (?:drug )?allergies",
            r"nkda",
            r"no allergies",
            r"sin alergias conocidas",
            r"sin alergias",
            r"niega alergias",
        ]
        for np in neg_patterns:
            if re.search(np, candidates, re.IGNORECASE):
                # No positive allergies to extract
                return []

        found: List[AllergyEntity] = []
        seen_snomed: Set[str] = set()

        for allg in ALLERGIES_DATABASE:
            matched = False
            terms = allg["terms_en"] + allg["terms_es"]
            for term in terms:
                pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
                for m in re.finditer(pattern, candidates, re.IGNORECASE):
                    if not self._is_negated(candidates, m.start()):
                        matched = True
                        break
                if matched:
                    break

            if matched and allg["snomed"] not in seen_snomed:
                seen_snomed.add(allg["snomed"])
                found.append(
                    AllergyEntity(
                        text=allg["display"],
                        display=allg["display"],
                        snomed_code=allg["snomed"],
                        category=allg.get("category", "medication"),
                        status="active",
                    )
                )

        return found
