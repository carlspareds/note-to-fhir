"""
Curated local terminology database mapping clinical terms in English and Spanish
to standard medical coding systems:
- SNOMED CT for Conditions & Allergies
- ICD-10-CM for Conditions
- RxNorm for Medications
- LOINC & UCUM for Vital Signs and Observations
Derived from official HL7 FHIR R4 and Synthea terminology concepts.
"""

import re
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# LOINC Vital Signs & UCUM Units
# ---------------------------------------------------------------------------
VITAL_SIGNS_TERMINOLOGY: Dict[str, Dict[str, Any]] = {
    "blood_pressure": {
        "loinc": "85354-9",
        "display": "Blood pressure panel with all children optional",
        "systolic": {
            "loinc": "8480-6",
            "display": "Systolic blood pressure",
            "unit": "mmHg",
            "ucum": "mm[Hg]",
        },
        "diastolic": {
            "loinc": "8462-4",
            "display": "Diastolic blood pressure",
            "unit": "mmHg",
            "ucum": "mm[Hg]",
        },
    },
    "heart_rate": {
        "loinc": "8867-4",
        "display": "Heart rate",
        "unit": "/min",
        "ucum": "/min",
    },
    "respiratory_rate": {
        "loinc": "9279-1",
        "display": "Respiratory rate",
        "unit": "/min",
        "ucum": "/min",
    },
    "body_temperature": {
        "loinc": "8310-5",
        "display": "Body temperature",
        "unit_fahrenheit": "[degF]",
        "unit_celsius": "Cel",
        "ucum_fahrenheit": "[degF]",
        "ucum_celsius": "Cel",
    },
    "oxygen_saturation": {
        "loinc": "59408-5",
        "display": "Oxygen saturation in Arterial blood by Pulse oximetry",
        "unit": "%",
        "ucum": "%",
    },
    "bmi": {
        "loinc": "39156-5",
        "display": "Body mass index (BMI) [Ratio]",
        "unit": "kg/m2",
        "ucum": "kg/m2",
    },
    "body_weight": {
        "loinc": "29463-7",
        "display": "Body weight",
        "unit": "kg",
        "ucum": "kg",
    },
    "body_height": {
        "loinc": "8302-2",
        "display": "Body height",
        "unit": "cm",
        "ucum": "cm",
    },
}

# ---------------------------------------------------------------------------
# Conditions (SNOMED CT & ICD-10)
# ---------------------------------------------------------------------------
CONDITIONS_DATABASE: List[Dict[str, Any]] = [
    {
        "snomed": "59621000",
        "icd10": "I10",
        "display": "Essential hypertension",
        "terms_en": [
            "essential hypertension",
            "hypertension",
            "high blood pressure",
            "htn",
            "primary hypertension",
        ],
        "terms_es": [
            "hipertensión arterial esencial",
            "hipertensión arterial",
            "hipertensión esencial",
            "hipertensión",
            "presión alta",
            "hta",
        ],
    },
    {
        "snomed": "44054006",
        "icd10": "E11.9",
        "display": "Type 2 diabetes mellitus",
        "terms_en": [
            "type 2 diabetes mellitus",
            "type 2 diabetes",
            "type ii diabetes",
            "diabetes mellitus type 2",
            "t2dm",
            "t2d",
            "non-insulin-dependent diabetes",
        ],
        "terms_es": [
            "diabetes mellitus tipo 2",
            "diabetes tipo 2",
            "diabetes mellitus tipo ii",
            "dm2",
            "t2dm",
            "diabetes del adulto",
        ],
    },
    {
        "snomed": "195967001",
        "icd10": "J45.909",
        "display": "Asthma",
        "terms_en": [
            "asthma",
            "bronchial asthma",
            "moderate persistent asthma",
            "mild intermittent asthma",
            "reactive airway disease",
        ],
        "terms_es": [
            "asma bronquial",
            "asma",
            "asma moderada persistente",
            "asma leve",
        ],
    },
    {
        "snomed": "840539006",
        "icd10": "U07.1",
        "display": "COVID-19",
        "terms_en": [
            "covid-19",
            "covid 19",
            "sars-cov-2",
            "novel coronavirus infection",
            "coronavirus disease 2019",
        ],
        "terms_es": [
            "infección por covid-19",
            "covid-19",
            "covid 19",
            "coronavirus",
            "sars-cov-2",
        ],
    },
    {
        "snomed": "10509002",
        "icd10": "J20.9",
        "display": "Acute bronchitis",
        "terms_en": [
            "acute bronchitis",
            "bronchitis",
            "tracheobronchitis",
        ],
        "terms_es": [
            "bronquitis aguda",
            "bronquitis",
            "traqueobronquitis",
        ],
    },
    {
        "snomed": "55822004",
        "icd10": "E78.00",
        "display": "Hyperlipidemia",
        "terms_en": [
            "hyperlipidemia",
            "hypercholesterolemia",
            "dyslipidemia",
            "high cholesterol",
            "elevated cholesterol",
        ],
        "terms_es": [
            "hiperlipidemia mixta",
            "hiperlipidemia",
            "hipercolesterolemia",
            "dislipidemia",
            "colesterol alto",
        ],
    },
    {
        "snomed": "53741008",
        "icd10": "I25.10",
        "display": "Coronary artery disease",
        "terms_en": [
            "coronary artery disease",
            "coronary arteriosclerosis",
            "cad",
            "ischemic heart disease",
            "coronary heart disease",
        ],
        "terms_es": [
            "cardiopatía isquémica coronaria",
            "enfermedad arterial coronaria",
            "cardiopatía isquémica",
            "eac",
            "esclerosis coronaria",
        ],
    },
    {
        "snomed": "13645005",
        "icd10": "J44.9",
        "display": "Chronic obstructive pulmonary disease",
        "terms_en": [
            "chronic obstructive pulmonary disease",
            "copd",
            "chronic bronchitis",
            "emphysema",
        ],
        "terms_es": [
            "enfermedad pulmonar obstructiva crónica",
            "epoc",
            "bronquitis crónica",
            "enfisema pulmonar",
        ],
    },
    {
        "snomed": "235595009",
        "icd10": "K21.9",
        "display": "Gastroesophageal reflux disease",
        "terms_en": [
            "gastroesophageal reflux disease",
            "gerd",
            "acid reflux",
            "reflux esophagitis",
        ],
        "terms_es": [
            "enfermedad por reflujo gastroesofágico",
            "erge",
            "reflujo gastroesofágico",
            "reflujo ácido",
            "pirosis",
        ],
    },
    {
        "snomed": "370143000",
        "icd10": "F32.9",
        "display": "Major depressive disorder",
        "terms_en": [
            "major depressive disorder",
            "depression",
            "major depression",
            "depressive disorder",
        ],
        "terms_es": [
            "depresión mayor",
            "trastorno depresivo mayor",
            "depresión",
        ],
    },
    {
        "snomed": "396275006",
        "icd10": "M19.90",
        "display": "Osteoarthritis",
        "terms_en": [
            "osteoarthritis",
            "degenerative joint disease",
            "oa",
            "arthrosis",
        ],
        "terms_es": [
            "osteoartritis",
            "artrosis",
            "enfermedad degenerativa articular",
        ],
    },
    {
        "snomed": "40930008",
        "icd10": "E03.9",
        "display": "Hypothyroidism",
        "terms_en": [
            "hypothyroidism",
            "underactive thyroid",
            "myxedema",
        ],
        "terms_es": [
            "hipotiroidismo",
            "tiroides hipoactiva",
        ],
    },
    {
        "snomed": "709044004",
        "icd10": "N18.9",
        "display": "Chronic kidney disease",
        "terms_en": [
            "chronic kidney disease",
            "ckd",
            "chronic renal failure",
            "chronic renal insufficiency",
        ],
        "terms_es": [
            "enfermedad renal crónica",
            "erc",
            "insuficiencia renal crónica",
        ],
    },
    {
        "snomed": "233604007",
        "icd10": "J18.9",
        "display": "Pneumonia",
        "terms_en": [
            "pneumonia",
            "bacterial pneumonia",
            "community acquired pneumonia",
        ],
        "terms_es": [
            "neumonía",
            "neumonía adquirida en la comunidad",
            "pulmonía",
        ],
    },
]

# ---------------------------------------------------------------------------
# Medications (RxNorm)
# ---------------------------------------------------------------------------
MEDICATIONS_DATABASE: List[Dict[str, Any]] = [
    {
        "rxnorm": "314076",
        "display": "Lisinopril 10 MG Oral Tablet",
        "terms_en": [
            "lisinopril 10 mg oral tablet",
            "lisinopril 10 mg",
            "lisinopril 10mg",
            "lisinopril",
            "prinivil",
            "zestril",
        ],
        "terms_es": [
            "lisinopril 10 mg comprimidos vía oral",
            "lisinopril 10 mg",
            "lisinopril 10mg",
            "lisinopril",
        ],
    },
    {
        "rxnorm": "860975",
        "display": "Metformin hydrochloride 500 MG Oral Tablet",
        "terms_en": [
            "metformin hydrochloride 500 mg oral tablet",
            "metformin 500 mg",
            "metformin 500mg",
            "metformin",
            "glucophage",
        ],
        "terms_es": [
            "metformina 500 mg comprimidos vía oral",
            "metformina 500 mg",
            "metformina 500mg",
            "metformina",
        ],
    },
    {
        "rxnorm": "745752",
        "display": "Albuterol 90 MCG/ACTUAT Inhaler",
        "terms_en": [
            "albuterol 90 mcg/actuat inhaler",
            "albuterol 90 mcg",
            "albuterol inhaler",
            "albuterol",
            "proair",
            "ventolin",
            "salbutamol",
        ],
        "terms_es": [
            "albuterol / salbutamol inhalador 90 mcg",
            "salbutamol inhalador",
            "salbutamol",
            "albuterol inhalador",
            "albuterol",
        ],
    },
    {
        "rxnorm": "896209",
        "display": "Fluticasone propionate",
        "terms_en": [
            "fluticasone propionate",
            "fluticasone nasal spray",
            "fluticasone",
            "flonase",
        ],
        "terms_es": [
            "fluticasona spray nasal",
            "fluticasona",
            "propionato de fluticasona",
        ],
    },
    {
        "rxnorm": "248656",
        "display": "Azithromycin 250 MG Oral Tablet",
        "terms_en": [
            "azithromycin 250 mg oral tablet",
            "azithromycin 250 mg",
            "azithromycin",
            "zithromax",
            "z-pak",
        ],
        "terms_es": [
            "azitromicina 250 mg comprimidos",
            "azitromicina 250 mg",
            "azitromicina",
        ],
    },
    {
        "rxnorm": "259255",
        "display": "Atorvastatin 20 MG Oral Tablet",
        "terms_en": [
            "atorvastatin 20 mg oral tablet",
            "atorvastatin 20 mg",
            "atorvastatin 20mg",
            "atorvastatin",
            "lipitor",
        ],
        "terms_es": [
            "atorvastatina 20 mg vía oral",
            "atorvastatina 20 mg",
            "atorvastatina 20mg",
            "atorvastatina",
        ],
    },
    {
        "rxnorm": "243670",
        "display": "Aspirin 81 MG Oral Tablet",
        "terms_en": [
            "aspirin 81 mg oral tablet",
            "aspirin 81 mg",
            "baby aspirin",
            "low dose aspirin",
            "aspirin",
            "acetylsalicylic acid",
        ],
        "terms_es": [
            "aspirina 81 mg vía oral",
            "aspirina 81 mg",
            "aspirina",
            "ácido acetilsalicílico",
            "aas 100",
            "aas 81",
        ],
    },
    {
        "rxnorm": "312134",
        "display": "Omeprazole 20 MG Delayed Release Oral Capsule",
        "terms_en": [
            "omeprazole 20 mg delayed release oral capsule",
            "omeprazole 20 mg",
            "omeprazole",
            "prilosec",
        ],
        "terms_es": [
            "omeprazol 20 mg cápsulas",
            "omeprazol 20 mg",
            "omeprazol",
        ],
    },
    {
        "rxnorm": "197361",
        "display": "Amlodipine 5 MG Oral Tablet",
        "terms_en": [
            "amlodipine 5 mg oral tablet",
            "amlodipine 5 mg",
            "amlodipine",
            "norvasc",
        ],
        "terms_es": [
            "amlodipino 5 mg comprimidos",
            "amlodipino 5 mg",
            "amlodipino",
        ],
    },
    {
        "rxnorm": "310798",
        "display": "Hydrochlorothiazide 25 MG Oral Tablet",
        "terms_en": [
            "hydrochlorothiazide 25 mg",
            "hydrochlorothiazide",
            "hctz",
        ],
        "terms_es": [
            "hidroclorotiazida 25 mg",
            "hidroclorotiazida",
            "hctz",
        ],
    },
    {
        "rxnorm": "966222",
        "display": "Levothyroxine sodium 50 MCG Oral Tablet",
        "terms_en": [
            "levothyroxine 50 mcg",
            "levothyroxine",
            "synthroid",
        ],
        "terms_es": [
            "levotiroxina 50 mcg",
            "levotiroxina",
            "eutirox",
        ],
    },
    {
        "rxnorm": "308189",
        "display": "Amoxicillin 500 MG Oral Tablet",
        "terms_en": [
            "amoxicillin 500 mg",
            "amoxicillin",
            "amoxil",
        ],
        "terms_es": [
            "amoxicilina 500 mg",
            "amoxicilina",
        ],
    },
]

# ---------------------------------------------------------------------------
# Allergies (SNOMED CT)
# ---------------------------------------------------------------------------
ALLERGIES_DATABASE: List[Dict[str, Any]] = [
    {
        "snomed": "91936005",
        "display": "Allergy to penicillin",
        "category": "medication",
        "terms_en": [
            "allergy to penicillin",
            "penicillin allergy",
            "penicillin",
            "pcn allergy",
        ],
        "terms_es": [
            "alergia a la penicilina",
            "alergia a penicilina",
            "penicilina",
        ],
    },
    {
        "snomed": "91931000",
        "display": "Allergy to sulfonamide",
        "category": "medication",
        "terms_en": [
            "allergy to sulfonamide",
            "sulfonamide allergy",
            "sulfa allergy",
            "sulfas",
            "sulfa drugs",
        ],
        "terms_es": [
            "alergia a las sulfonamidas",
            "alergia a las sulfas",
            "sulfas",
            "sulfonamidas",
        ],
    },
    {
        "snomed": "91935004",
        "display": "Allergy to peanut",
        "category": "food",
        "terms_en": [
            "allergy to peanut",
            "peanut allergy",
            "peanuts",
        ],
        "terms_es": [
            "alergia al maní",
            "alergia a los cacahuates",
            "maní",
            "cacahuates",
        ],
    },
    {
        "snomed": "294505008",
        "display": "Allergy to codeine",
        "category": "medication",
        "terms_en": [
            "allergy to codeine",
            "codeine allergy",
            "codeine",
        ],
        "terms_es": [
            "alergia a la codeína",
            "codeína",
        ],
    },
    {
        "snomed": "300916003",
        "display": "Latex allergy",
        "category": "environment",
        "terms_en": [
            "latex allergy",
            "allergy to latex",
            "latex",
        ],
        "terms_es": [
            "alergia al látex",
            "látex",
        ],
    },
    {
        "snomed": "293584003",
        "display": "Allergy to aspirin",
        "category": "medication",
        "terms_en": [
            "allergy to aspirin",
            "aspirin allergy",
            "asa allergy",
        ],
        "terms_es": [
            "alergia a la aspirina",
            "alergia a aspirina",
        ],
    },
    {
        "snomed": "300913000",
        "display": "Shellfish allergy",
        "category": "food",
        "terms_en": [
            "shellfish allergy",
            "allergy to shellfish",
            "seafood allergy",
        ],
        "terms_es": [
            "alergia a los mariscos",
            "mariscos",
        ],
    },
]


# ---------------------------------------------------------------------------
# Lookup Helpers
# ---------------------------------------------------------------------------
def match_condition(query: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """Match a condition name or phrase against the database."""
    q = query.lower().strip()
    if not q:
        return None
    for entry in CONDITIONS_DATABASE:
        terms = entry["terms_en"] + entry["terms_es"]
        for term in terms:
            if term == q or re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", q):
                return {
                    "snomed": entry["snomed"],
                    "icd10": entry["icd10"],
                    "display": entry["display"],
                }
    return None


def match_medication(query: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """Match a medication name or phrase against the database."""
    q = query.lower().strip()
    if not q:
        return None
    for entry in MEDICATIONS_DATABASE:
        terms = entry["terms_en"] + entry["terms_es"]
        for term in terms:
            if term == q or re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", q):
                return {
                    "rxnorm": entry["rxnorm"],
                    "display": entry["display"],
                }
    return None


def match_allergy(query: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """Match an allergy name or phrase against the database."""
    q = query.lower().strip()
    if not q:
        return None
    for entry in ALLERGIES_DATABASE:
        terms = entry["terms_en"] + entry["terms_es"]
        for term in terms:
            if term == q or re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", q):
                return {
                    "snomed": entry["snomed"],
                    "display": entry["display"],
                    "category": entry["category"],
                }
    return None
