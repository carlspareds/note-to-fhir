"""
Unit tests for note_to_fhir.terminology.
"""

from note_to_fhir.terminology import (
    ALLERGIES_DATABASE,
    CONDITIONS_DATABASE,
    MEDICATIONS_DATABASE,
    VITAL_SIGNS_TERMINOLOGY,
    match_allergy,
    match_condition,
    match_medication,
)


def test_databases_loaded():
    """Verify terminology databases are non-empty and have valid schemas."""
    assert len(CONDITIONS_DATABASE) >= 10
    assert len(MEDICATIONS_DATABASE) >= 10
    assert len(ALLERGIES_DATABASE) >= 5
    for c in CONDITIONS_DATABASE:
        assert "snomed" in c and "display" in c
    for m in MEDICATIONS_DATABASE:
        assert "rxnorm" in m and "display" in m
    for a in ALLERGIES_DATABASE:
        assert "snomed" in a and "display" in a


def test_vital_signs_definitions():
    """Verify standard LOINC and UCUM codes for all vitals."""
    bp = VITAL_SIGNS_TERMINOLOGY["blood_pressure"]
    assert bp["loinc"] == "85354-9"
    assert bp["systolic"]["loinc"] == "8480-6"
    assert bp["systolic"]["ucum"] == "mm[Hg]"
    assert bp["diastolic"]["loinc"] == "8462-4"
    assert bp["diastolic"]["ucum"] == "mm[Hg]"

    hr = VITAL_SIGNS_TERMINOLOGY["heart_rate"]
    assert hr["loinc"] == "8867-4"
    assert hr["ucum"] == "/min"

    rr = VITAL_SIGNS_TERMINOLOGY["respiratory_rate"]
    assert rr["loinc"] == "9279-1"
    assert rr["ucum"] == "/min"

    temp = VITAL_SIGNS_TERMINOLOGY["body_temperature"]
    assert temp["loinc"] == "8310-5"
    assert temp["ucum_fahrenheit"] == "[degF]"
    assert temp["ucum_celsius"] == "Cel"

    spo2 = VITAL_SIGNS_TERMINOLOGY["oxygen_saturation"]
    assert spo2["loinc"] == "59408-5"
    assert spo2["ucum"] == "%"


def test_match_condition_en_and_es():
    """Verify condition lookup in English and Spanish."""
    # English
    c_en = match_condition("Hyperlipidemia")
    assert c_en is not None
    assert c_en["snomed"] == "55822004"
    assert c_en["icd10"] == "E78.00"

    # Spanish
    c_es = match_condition("hiperlipidemia mixta")
    assert c_es is not None
    assert c_es["snomed"] == "55822004"

    # Acronym / synonym
    c_dm = match_condition("t2dm")
    assert c_dm is not None
    assert c_dm["snomed"] == "44054006"

    c_dm_es = match_condition("diabetes mellitus tipo 2")
    assert c_dm_es is not None
    assert c_dm_es["snomed"] == "44054006"


def test_match_medication_en_and_es():
    """Verify medication lookup in English and Spanish."""
    m_en = match_medication("Lisinopril 10 mg")
    assert m_en is not None
    assert m_en["rxnorm"] == "314076"

    m_es = match_medication("metformina 500 mg")
    assert m_es is not None
    assert m_es["rxnorm"] == "860975"

    m_inhaler = match_medication("salbutamol")
    assert m_inhaler is not None
    assert m_inhaler["rxnorm"] == "745752"


def test_match_allergy_en_and_es():
    """Verify allergy lookup and categories."""
    a_pen = match_allergy("penicillin allergy")
    assert a_pen is not None
    assert a_pen["snomed"] == "91936005"
    assert a_pen["category"] == "medication"

    a_peanut_es = match_allergy("alergia al maní")
    assert a_peanut_es is not None
    assert a_peanut_es["snomed"] == "91935004"
    assert a_peanut_es["category"] == "food"

    a_latex = match_allergy("latex allergy")
    assert a_latex is not None
    assert a_latex["snomed"] == "300916003"
    assert a_latex["category"] == "environment"


def test_clinical_acronyms_word_boundary():
    """Verify that short medical acronyms match accurately with word boundaries."""
    # Condition acronyms
    assert match_condition("t2dm")["snomed"] == "44054006"
    assert match_condition("history of t2dm")["snomed"] == "44054006"
    assert match_condition("patient has cad")["snomed"] == "53741008"
    assert match_condition("copd exacerbation")["snomed"] == "13645005"
    assert match_condition("ckd stage 3")["snomed"] == "709044004"
    assert match_condition("gerd symptoms")["snomed"] == "235595009"
    assert match_condition("erge")["snomed"] == "235595009"
    assert match_condition("dm2")["snomed"] == "44054006"

    # Medication acronyms
    assert match_medication("hctz 25 mg")["rxnorm"] == "310798"
    assert match_medication("aas 81")["rxnorm"] == "243670"

    # Word boundary safety: substrings inside non-medical words should not falsely match
    assert match_condition("broadway") is None  # Does not match 'oa'
    assert match_condition("arcade") is None    # Does not match 'cad'
