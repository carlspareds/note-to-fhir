"""
Unit tests for deterministic RuleBasedExtractor.
"""

from note_to_fhir.extractors.rules import RuleBasedExtractor
from note_to_fhir.models import ClinicalNote


def test_extract_patient_demographics():
    extractor = RuleBasedExtractor()
    note_text = """
    Patient Name: Jane A Smith
    DOB: 1985-06-12 | Gender: Female
    Date: 2024-03-20
    """
    note = ClinicalNote(text=note_text)
    entities = extractor.extract(note)

    assert entities.patient.name == "Jane A Smith"
    assert entities.patient.birth_date == "1985-06-12"
    assert entities.patient.gender == "female"
    assert entities.encounter.date == "2024-03-20"


def test_extract_vitals_regex_english():
    extractor = RuleBasedExtractor()
    note_text = """
    Vital Signs:
    - Blood Pressure: 130/85 mmHg
    - Heart Rate: 72 bpm
    - Respiratory Rate: 14 breaths/min
    - Temperature: 98.6 F
    - SpO2: 98%
    - BMI: 24.5 kg/m2
    """
    note = ClinicalNote(text=note_text)
    entities = extractor.extract(note)
    obs = {o.name: o for o in entities.observations}

    assert "blood_pressure" in obs
    assert obs["blood_pressure"].systolic == 130.0
    assert obs["blood_pressure"].diastolic == 85.0
    assert obs["blood_pressure"].ucum_code == "mm[Hg]"

    assert "heart_rate" in obs
    assert obs["heart_rate"].value == 72.0
    assert obs["heart_rate"].loinc_code == "8867-4"

    assert "respiratory_rate" in obs
    assert obs["respiratory_rate"].value == 14.0
    assert obs["respiratory_rate"].loinc_code == "9279-1"

    assert "body_temperature" in obs
    assert obs["body_temperature"].value == 98.6
    assert obs["body_temperature"].ucum_code == "[degF]"

    assert "oxygen_saturation" in obs
    assert obs["oxygen_saturation"].value == 98.0

    assert "bmi" in obs
    assert obs["bmi"].value == 24.5


def test_extract_vitals_regex_spanish():
    extractor = RuleBasedExtractor()
    note_text = """
    Signos Vitales:
    - Presión Arterial: 125/82 mmHg
    - Frecuencia Cardíaca: 80 lpm
    - Frecuencia Respiratoria: 18 respiraciones/minuto
    - Temperatura: 36.8 °C
    - Saturación de Oxígeno (SpO2): 97%
    - Índice de Masa Corporal (IMC): 26.2 kg/m2
    """
    note = ClinicalNote(text=note_text, language="es")
    entities = extractor.extract(note)
    obs = {o.name: o for o in entities.observations}

    assert obs["blood_pressure"].systolic == 125.0
    assert obs["blood_pressure"].diastolic == 82.0
    assert obs["heart_rate"].value == 80.0
    assert obs["respiratory_rate"].value == 18.0
    assert obs["body_temperature"].value == 36.8
    assert obs["body_temperature"].ucum_code == "Cel"
    assert obs["oxygen_saturation"].value == 97.0
    assert obs["bmi"].value == 26.2


def test_extract_conditions_and_medications_english():
    extractor = RuleBasedExtractor()
    note_text = """
    Past Medical History:
    - Essential hypertension
    - Type 2 diabetes mellitus

    Current Medications:
    - Lisinopril 10 MG
    - Metformin 500 MG

    Allergies:
    - Penicillin allergy
    """
    note = ClinicalNote(text=note_text)
    entities = extractor.extract(note)

    cond_codes = {c.snomed_code for c in entities.conditions}
    assert "59621000" in cond_codes  # Hypertension
    assert "44054006" in cond_codes  # T2DM

    med_codes = {m.rxnorm_code for m in entities.medications}
    assert "314076" in med_codes  # Lisinopril
    assert "860975" in med_codes  # Metformin

    allg_codes = {a.snomed_code for a in entities.allergies}
    assert "91936005" in allg_codes  # Penicillin


def test_extract_conditions_and_medications_spanish():
    extractor = RuleBasedExtractor()
    note_text = """
    Antecedentes Médicos Personales:
    - Asma bronquial
    - Hiperlipidemia mixta

    Medicación Actual:
    - Salbutamol inhalador
    - Atorvastatina 20 mg vía oral

    Alergias:
    - Alergia al maní
    """
    note = ClinicalNote(text=note_text, language="es")
    entities = extractor.extract(note)

    cond_codes = {c.snomed_code for c in entities.conditions}
    assert "195967001" in cond_codes  # Asthma
    assert "55822004" in cond_codes   # Hyperlipidemia

    med_codes = {m.rxnorm_code for m in entities.medications}
    assert "745752" in med_codes  # Albuterol / Salbutamol
    assert "259255" in med_codes  # Atorvastatin

    allg_codes = {a.snomed_code for a in entities.allergies}
    assert "91935004" in allg_codes  # Peanut


def test_no_known_allergies_negation():
    extractor = RuleBasedExtractor()
    note_text = """
    Allergies:
    - No known drug allergies (NKDA)
    """
    note = ClinicalNote(text=note_text)
    entities = extractor.extract(note)
    assert len(entities.allergies) == 0

    note_text_es = """
    Alergias:
    - Sin alergias conocidas
    """
    note_es = ClinicalNote(text=note_text_es, language="es")
    entities_es = extractor.extract(note_es)
    assert len(entities_es.allergies) == 0


def test_female_gender_extraction_en_and_es():
    """Verify that female patients in EN and ES are never mistakenly classified as male."""
    extractor = RuleBasedExtractor()

    # English Female
    note_en = ClinicalNote(text="Patient: Alice Cooper\nDOB: 1985-05-12 | Gender: Female\nDate: 2024-03-15")
    ent_en = extractor.extract(note_en)
    assert ent_en.patient.gender == "female"

    # Spanish Femenino
    note_es = ClinicalNote(text="Paciente: Maria Fernandez\nFecha de Nacimiento: 1990-11-20 | Género: Femenino\nFecha: 2024-03-15")
    ent_es = extractor.extract(note_es)
    assert ent_es.patient.gender == "female"

    # Spanish Mujer
    note_es2 = ClinicalNote(text="Paciente: Rosa Diaz\nDOB: 1978-02-14\nSexo: Mujer\nFecha: 2024-03-15")
    ent_es2 = extractor.extract(note_es2)
    assert ent_es2.patient.gender == "female"


def test_last_name_first_and_slash_dob():
    """Verify Last, First name parsing and MM/DD/YYYY DOB normalization."""
    extractor = RuleBasedExtractor()
    note = ClinicalNote(
        text="Patient Name: Doe, Jane A. | DOB: 07/24/1982 | Gender: Female\nDate: 2024-03-15"
    )
    ent = extractor.extract(note)
    assert "Jane" in ent.patient.name
    assert "Doe" in ent.patient.name
    assert ent.patient.birth_date == "1982-07-24"
    assert ent.patient.gender == "female"


def test_condition_negation_en_and_es():
    """Verify that negated conditions are NOT extracted as active conditions."""
    extractor = RuleBasedExtractor()

    note_en = ClinicalNote(
        text="""
        Past Medical History:
        - Essential hypertension
        - No history of asthma
        - Patient denies diabetes mellitus
        """
    )
    ent_en = extractor.extract(note_en)
    codes_en = {c.snomed_code for c in ent_en.conditions}
    assert "59621000" in codes_en  # Hypertension active
    assert "195967001" not in codes_en  # Asthma negated
    assert "44054006" not in codes_en   # Diabetes negated

    note_es = ClinicalNote(
        text="""
        Antecedentes Médicos Personales:
        - Hipertensión arterial
        - Sin antecedentes de asma
        - Niega diabetes
        """
    )
    ent_es = extractor.extract(note_es)
    codes_es = {c.snomed_code for c in ent_es.conditions}
    assert "59621000" in codes_es  # Hypertension active
    assert "195967001" not in codes_es  # Asthma negated
    assert "44054006" not in codes_es   # Diabetes negated


def test_weight_and_height_extraction():
    """Verify extraction of weight and height with standard LOINC and UCUM units."""
    extractor = RuleBasedExtractor()
    note = ClinicalNote(
        text="""
        Vital Signs:
        - Weight: 75.0 kg
        - Height: 175.0 cm
        """
    )
    ent = extractor.extract(note)
    obs = {o.name: o for o in ent.observations}

    assert "body_weight" in obs
    assert obs["body_weight"].value == 75.0
    assert obs["body_weight"].loinc_code == "29463-7"
    assert obs["body_weight"].ucum_code == "kg"

    assert "body_height" in obs
    assert obs["body_height"].value == 175.0
    assert obs["body_height"].loinc_code == "8302-2"
    assert obs["body_height"].ucum_code == "cm"


def test_vitals_without_colons():
    """Verify vitals extraction when colons are omitted."""
    extractor = RuleBasedExtractor()
    note = ClinicalNote(
        text="""
        Vital Signs:
        BP 120/80 mmHg
        HR 72 bpm
        RR 16 breaths/min
        Temp 98.6 F
        SpO2 99%
        """
    )
    ent = extractor.extract(note)
    obs = {o.name: o for o in ent.observations}

    assert "blood_pressure" in obs
    assert obs["blood_pressure"].systolic == 120.0
    assert "heart_rate" in obs
    assert obs["heart_rate"].value == 72.0
    assert "respiratory_rate" in obs
    assert obs["respiratory_rate"].value == 16.0
    assert "body_temperature" in obs
    assert obs["body_temperature"].value == 98.6
    assert "oxygen_saturation" in obs
    assert obs["oxygen_saturation"].value == 99.0
