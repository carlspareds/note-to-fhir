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
    {
        "snomed": "195662009",
        "icd10": "J02.9",
        "display": "Acute viral pharyngitis",
        "terms_en": ["acute viral pharyngitis", "viral pharyngitis", "pharyngitis", "sore throat"],
        "terms_es": ["faringitis viral aguda", "faringitis viral", "faringitis aguda", "faringitis", "dolor de garganta"],
    },
    {
        "snomed": "43878008",
        "icd10": "J02.0",
        "display": "Streptococcal sore throat",
        "terms_en": ["streptococcal sore throat", "strep throat", "streptococcal pharyngitis"],
        "terms_es": ["faringitis estreptocócica", "amigdalitis estreptocócica"],
    },
    {
        "snomed": "444814009",
        "icd10": "J01.90",
        "display": "Viral sinusitis",
        "terms_en": ["viral sinusitis", "acute viral sinusitis", "sinusitis"],
        "terms_es": ["sinusitis viral aguda", "sinusitis viral", "sinusitis aguda", "sinusitis"],
    },
    {
        "snomed": "65363002",
        "icd10": "H66.90",
        "display": "Otitis media",
        "terms_en": ["otitis media", "acute otitis media", "middle ear infection"],
        "terms_es": ["otitis media", "otitis media aguda", "infección de oído"],
    },
    {
        "snomed": "233678006",
        "icd10": "J45.909",
        "display": "Childhood asthma",
        "terms_en": ["childhood asthma", "pediatric asthma"],
        "terms_es": ["asma infantil", "asma del niño"],
    },
    {
        "snomed": "162864005",
        "icd10": "E66.9",
        "display": "Body mass index 30+ - obesity",
        "terms_en": ["body mass index 30+ - obesity", "obesity", "obese", "bmi 30+"],
        "terms_es": ["obesidad grado i", "obesidad", "obeso", "imc 30+"],
    },
    {
        "snomed": "714628002",
        "icd10": "R73.03",
        "display": "Prediabetes",
        "terms_en": ["prediabetes", "pre-diabetes", "impaired fasting glucose"],
        "terms_es": ["prediabetes", "intolerancia a la glucosa"],
    },
    {
        "snomed": "109570002",
        "icd10": "K02.9",
        "display": "Primary dental caries",
        "terms_en": ["primary dental caries", "dental caries", "tooth decay", "cavities"],
        "terms_es": ["caries dental primaria", "caries dental", "caries"],
    },
    {
        "snomed": "37320007",
        "icd10": "K08.109",
        "display": "Loss of teeth",
        "terms_en": ["loss of teeth", "tooth loss", "missing teeth"],
        "terms_es": ["pérdida de piezas dentarias", "pérdida de dientes"],
    },
    {
        "snomed": "66383009",
        "icd10": "K05.10",
        "display": "Gingivitis",
        "terms_en": ["gingivitis", "gum inflammation"],
        "terms_es": ["gingivitis", "inflamación gingival"],
    },
    {
        "snomed": "18718003",
        "icd10": "K06.9",
        "display": "Gingival disease",
        "terms_en": ["gingival disease", "gum disease"],
        "terms_es": ["enfermedad gingival", "enfermedad periodontal"],
    },
    {
        "snomed": "196416002",
        "icd10": "K01.1",
        "display": "Impacted molars",
        "terms_en": ["impacted molars", "impacted wisdom teeth"],
        "terms_es": ["molares impactados", "muelas del juicio impactadas"],
    },
    {
        "snomed": "82423001",
        "icd10": "G89.29",
        "display": "Chronic pain",
        "terms_en": ["chronic pain", "persistent pain"],
        "terms_es": ["dolor crónico", "dolor persistente"],
    },
    {
        "snomed": "125605004",
        "icd10": "T14.8",
        "display": "Fracture of bone",
        "terms_en": ["fracture of bone", "bone fracture", "fracture"],
        "terms_es": ["fractura de hueso", "fractura ósea", "fractura"],
    },
    {
        "snomed": "16114001",
        "icd10": "S82.899A",
        "display": "Fracture of ankle",
        "terms_en": ["fracture of ankle", "ankle fracture"],
        "terms_es": ["fractura de tobillo"],
    },
    {
        "snomed": "263102004",
        "icd10": "S62.90XA",
        "display": "Fracture subluxation of wrist",
        "terms_en": ["fracture subluxation of wrist", "wrist fracture"],
        "terms_es": ["fractura de muñeca", "subluxación de muñeca"],
    },
    {
        "snomed": "384709000",
        "icd10": "S93.409A",
        "display": "Sprain (morphologic abnormality)",
        "terms_en": ["sprain", "joint sprain", "ligament sprain"],
        "terms_es": ["esguince", "torcedura", "distensión"],
    },
    {
        "snomed": "312608009",
        "icd10": "T14.1",
        "display": "Laceration - injury",
        "terms_en": ["laceration - injury", "laceration", "cut wound", "wound"],
        "terms_es": ["laceración", "herida cortante", "herida"],
    },
    {
        "snomed": "283385000",
        "icd10": "S71.119A",
        "display": "Laceration of thigh",
        "terms_en": ["laceration of thigh", "thigh laceration"],
        "terms_es": ["laceración de muslo", "herida en muslo"],
    },
    {
        "snomed": "283371005",
        "icd10": "S51.819A",
        "display": "Laceration of forearm",
        "terms_en": ["laceration of forearm", "forearm laceration"],
        "terms_es": ["laceración de antebrazo", "herida en antebrazo"],
    },
    {
        "snomed": "271737000",
        "icd10": "D64.9",
        "display": "Anemia",
        "terms_en": ["anemia", "anaemia", "normocytic anemia"],
        "terms_es": ["anemia", "anemia normocítica"],
    },
    {
        "snomed": "110030002",
        "icd10": "S06.0X0A",
        "display": "Concussion injury of brain",
        "terms_en": ["concussion injury of brain", "concussion", "brain concussion"],
        "terms_es": ["conmoción cerebral", "traumatismo craneoencefálico"],
    },
    {
        "snomed": "62564004",
        "icd10": "S06.0X1A",
        "display": "Concussion with loss of consciousness",
        "terms_en": ["concussion with loss of consciousness"],
        "terms_es": ["conmoción con pérdida de conciencia"],
    },
    {
        "snomed": "124171000119105",
        "icd10": "G43.019",
        "display": "Chronic intractable migraine without aura",
        "terms_en": ["chronic intractable migraine without aura", "chronic migraine", "migraine"],
        "terms_es": ["migraña crónica", "migraña sin aura", "migraña", "jaqueca"],
    },
    {
        "snomed": "91434003",
        "icd10": "I37.1",
        "display": "Pulmonic valve regurgitation",
        "terms_en": ["pulmonic valve regurgitation", "pulmonary regurgitation"],
        "terms_es": ["insuficiencia valvular pulmonar", "regurgitación pulmonar"],
    },
    {
        "snomed": "73595000",
        "icd10": "F43.0",
        "display": "Stress",
        "terms_en": ["stress", "emotional stress"],
        "terms_es": ["estrés", "estrés emocional"],
    },
    {
        "snomed": "422650009",
        "icd10": "Z60.2",
        "display": "Social isolation",
        "terms_en": ["social isolation", "isolated socially"],
        "terms_es": ["aislamiento social"],
    },
    {
        "snomed": "105531004",
        "icd10": "Z59.1",
        "display": "Housing unsatisfactory",
        "terms_en": ["housing unsatisfactory", "substandard housing"],
        "terms_es": ["vivienda insatisfactoria"],
    },
    {
        "snomed": "73438004",
        "icd10": "Z56.0",
        "display": "Unemployed",
        "terms_en": ["unemployed", "unemployment"],
        "terms_es": ["desempleado", "desempleo"],
    },
    {
        "snomed": "266948004",
        "icd10": "Z65.0",
        "display": "Has a criminal record",
        "terms_en": ["has a criminal record", "criminal record"],
        "terms_es": ["antecedentes penales"],
    },
    {
        "snomed": "1187604002",
        "icd10": "Z56.82",
        "display": "Serving in military service",
        "terms_en": ["serving in military service", "military service"],
        "terms_es": ["servicio militar"],
    },
    {
        "snomed": "6525002",
        "icd10": "F19.20",
        "display": "Dependent drug abuse",
        "terms_en": ["dependent drug abuse", "substance dependence", "drug abuse"],
        "terms_es": ["dependencia de drogas", "abuso de sustancias"],
    },
    {
        "snomed": "446654005",
        "icd10": "Z59.7",
        "display": "Refugee (person)",
        "terms_en": ["refugee", "refugee (person)"],
        "terms_es": ["refugiado", "persona refugiada"],
    },
    {
        "snomed": "266934004",
        "icd10": "Z59.82",
        "display": "Transport problem",
        "terms_en": ["transport problem", "lack of transportation"],
        "terms_es": ["problema de transporte"],
    },
    {
        "snomed": "161744009",
        "icd10": "Z87.59",
        "display": "Past pregnancy history of miscarriage",
        "terms_en": ["past pregnancy history of miscarriage", "history of miscarriage", "miscarriage"],
        "terms_es": ["antecedente de aborto espontáneo", "aborto espontáneo previo"],
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
    {
        "rxnorm": "308192",
        "display": "Amoxicillin 500 MG Oral Tablet",
        "terms_en": ["amoxicillin 500 mg oral tablet", "amoxicillin 500 mg", "amoxicillin 500mg", "amoxicillin", "amoxil"],
        "terms_es": ["amoxicilina 500 mg comprimidos vía oral", "amoxicilina 500 mg", "amoxicilina 500mg", "amoxicilina"],
    },
    {
        "rxnorm": "562251",
        "display": "Amoxicillin 250 MG / Clavulanate 125 MG Oral Tablet",
        "terms_en": ["amoxicillin 250 mg / clavulanate 125 mg", "amoxicillin / clavulanate", "augmentin"],
        "terms_es": ["amoxicilina 250 mg / ácido clavulánico 125 mg", "amoxicilina / clavulánico", "clavulánico"],
    },
    {
        "rxnorm": "198405",
        "display": "Ibuprofen 100 MG Oral Tablet",
        "terms_en": ["ibuprofen 100 mg oral tablet", "ibuprofen 100 mg", "ibuprofen 100mg", "ibuprofen", "advil", "motrin"],
        "terms_es": ["ibuprofeno 100 mg comprimidos vía oral", "ibuprofeno 100 mg", "ibuprofeno 100mg", "ibuprofeno"],
    },
    {
        "rxnorm": "313782",
        "display": "Acetaminophen 325 MG Oral Tablet",
        "terms_en": ["acetaminophen 325 mg oral tablet", "acetaminophen 325 mg", "acetaminophen 325mg", "acetaminophen", "tylenol", "paracetamol"],
        "terms_es": ["paracetamol 325 mg comprimidos vía oral", "paracetamol 325 mg", "paracetamol", "acetaminofén"],
    },
    {
        "rxnorm": "313820",
        "display": "Acetaminophen 160 MG Chewable Tablet",
        "terms_en": ["acetaminophen 160 mg chewable tablet", "acetaminophen 160 mg", "chewable tylenol"],
        "terms_es": ["paracetamol 160 mg comprimidos masticables", "paracetamol 160 mg"],
    },
    {
        "rxnorm": "857005",
        "display": "Acetaminophen 325 MG / HYDROcodone Bitartrate 7.5 MG Oral Tablet",
        "terms_en": ["acetaminophen 325 mg / hydrocodone bitartrate 7.5 mg", "hydrocodone / acetaminophen", "hydrocodone"],
        "terms_es": ["paracetamol / hidrocodona", "hidrocodona"],
    },
    {
        "rxnorm": "856987",
        "display": "Acetaminophen 300 MG / HYDROcodone Bitartrate 5 MG Oral Tablet",
        "terms_en": ["acetaminophen 300 mg / hydrocodone bitartrate 5 mg", "hydrocodone 5 mg"],
        "terms_es": ["paracetamol 300 mg / hidrocodona 5 mg"],
    },
    {
        "rxnorm": "1049221",
        "display": "Acetaminophen 325 MG / Oxycodone Hydrochloride 5 MG Oral Tablet",
        "terms_en": ["acetaminophen 325 mg / oxycodone hydrochloride 5 mg", "oxycodone / acetaminophen", "percocet"],
        "terms_es": ["paracetamol / oxicodona", "oxicodona / paracetamol"],
    },
    {
        "rxnorm": "849574",
        "display": "Naproxen sodium 220 MG Oral Tablet",
        "terms_en": ["naproxen sodium 220 mg oral tablet", "naproxen sodium 220 mg", "naproxen", "aleve"],
        "terms_es": ["naproxeno sódico 220 mg", "naproxeno sódico", "naproxeno"],
    },
    {
        "rxnorm": "834061",
        "display": "Penicillin V Potassium 250 MG Oral Tablet",
        "terms_en": ["penicillin v potassium 250 mg oral tablet", "penicillin v potassium", "penicillin v", "penicillin vk"],
        "terms_es": ["penicilina v potásica 250 mg", "penicilina v potásica", "penicilina v"],
    },
    {
        "rxnorm": "665078",
        "display": "Loratadine 5 MG Chewable Tablet",
        "terms_en": ["loratadine 5 mg chewable tablet", "loratadine 5 mg", "loratadine", "claritin"],
        "terms_es": ["loratadina 5 mg comprimidos masticables", "loratadina 5 mg", "loratadina"],
    },
    {
        "rxnorm": "855332",
        "display": "Warfarin Sodium 5 MG Oral Tablet",
        "terms_en": ["warfarin sodium 5 mg oral tablet", "warfarin sodium 5 mg", "warfarin", "coumadin"],
        "terms_es": ["warfarina sódica 5 mg", "warfarina sódica", "warfarina"],
    },
    {
        "rxnorm": "309309",
        "display": "ciprofloxacin 500 MG Oral Tablet",
        "terms_en": ["ciprofloxacin 500 mg oral tablet", "ciprofloxacin 500 mg", "ciprofloxacin", "cipro"],
        "terms_es": ["ciprofloxacino 500 mg", "ciprofloxacino"],
    },
    {
        "rxnorm": "197454",
        "display": "cephalexin 500 MG Oral Tablet",
        "terms_en": ["cephalexin 500 mg oral tablet", "cephalexin 500 mg", "cephalexin", "keflex"],
        "terms_es": ["cefalexina 500 mg", "cefalexina"],
    },
    {
        "rxnorm": "284215",
        "display": "clindamycin 300 MG Oral Capsule",
        "terms_en": ["clindamycin 300 mg oral capsule", "clindamycin 300 mg", "clindamycin", "cleocin"],
        "terms_es": ["clindamicina 300 mg", "clindamicina"],
    },
    {
        "rxnorm": "310325",
        "display": "ferrous sulfate 325 MG Oral Tablet",
        "terms_en": ["ferrous sulfate 325 mg oral tablet", "ferrous sulfate 325 mg", "ferrous sulfate", "iron sulfate"],
        "terms_es": ["sulfato ferroso 325 mg", "sulfato ferroso"],
    },
    {
        "rxnorm": "308136",
        "display": "amLODIPine 2.5 MG Oral Tablet",
        "terms_en": ["amlodipine 2.5 mg oral tablet", "amlodipine 2.5 mg", "amlodipine", "norvasc"],
        "terms_es": ["amlodipino 2.5 mg", "amlodipino"],
    },
    {
        "rxnorm": "314231",
        "display": "Simvastatin 10 MG Oral Tablet",
        "terms_en": ["simvastatin 10 mg oral tablet", "simvastatin 10 mg", "simvastatin", "zocor"],
        "terms_es": ["simvastatina 10 mg", "simvastatina"],
    },
    {
        "rxnorm": "630208",
        "display": "albuterol 0.83 MG/ML Inhalation Solution",
        "terms_en": ["albuterol 0.83 mg/ml inhalation solution", "albuterol solution", "albuterol inhalation"],
        "terms_es": ["salbutamol 0.83 mg/ml solución para inhalación", "salbutamol solución"],
    },
    {
        "rxnorm": "351109",
        "display": "budesonide 0.25 MG/ML Inhalation Suspension",
        "terms_en": ["budesonide 0.25 mg/ml inhalation suspension", "budesonide suspension", "pulmicort"],
        "terms_es": ["budesonida 0.25 mg/ml suspensión para inhalación", "budesonida suspensión"],
    },
    {
        "rxnorm": "204892",
        "display": "clonazePAM 0.25 MG Oral Tablet",
        "terms_en": ["clonazepam 0.25 mg oral tablet", "clonazepam 0.25 mg", "clonazepam", "klonopin"],
        "terms_es": ["clonazepam 0.25 mg", "clonazepam"],
    },
    {
        "rxnorm": "904419",
        "display": "Alendronic acid 10 MG Oral Tablet",
        "terms_en": ["alendronic acid 10 mg oral tablet", "alendronic acid 10 mg", "alendronate", "fosamax"],
        "terms_es": ["ácido alendrónico 10 mg", "alendronato"],
    },
    {
        "rxnorm": "1736854",
        "display": "Cisplatin 50 MG Injection",
        "terms_en": ["cisplatin 50 mg injection", "cisplatin 50 mg", "cisplatin"],
        "terms_es": ["cisplatino 50 mg inyección", "cisplatino 50 mg", "cisplatino"],
    },
    {
        "rxnorm": "226719",
        "display": "etoposide 100 MG Injection [Etopophos]",
        "terms_en": ["etoposide 100 mg injection", "etoposide 100 mg", "etoposide", "etopophos"],
        "terms_es": ["etopósido 100 mg inyección", "etopósido"],
    },
    {
        "rxnorm": "1860154",
        "display": "Abuse-Deterrent 12 HR Oxycodone Hydrochloride 15 MG Extended Release Oral Tablet",
        "terms_en": ["oxycodone hydrochloride 15 mg extended release", "oxycodone 15 mg", "oxycontin"],
        "terms_es": ["oxicodona hidrocloruro 15 mg", "oxicodona"],
    },
    {
        "rxnorm": "757594",
        "display": "{28 (norethindrone 0.35 MG Oral Tablet) } Pack [Jolivette 28 Day]",
        "terms_en": ["norethindrone 0.35 mg oral tablet", "norethindrone 0.35 mg", "jolivette", "norethindrone"],
        "terms_es": ["noretindrona 0.35 mg", "noretindrona"],
    },
    {
        "rxnorm": "831533",
        "display": "{28 (norethindrone 0.35 MG Oral Tablet) } Pack [Errin 28 Day]",
        "terms_en": ["errin 28 day", "errin"],
        "terms_es": ["errin 28 días"],
    },
    {
        "rxnorm": "807283",
        "display": "levonorgestrel 0.000833 MG/HR Intrauterine System [Mirena]",
        "terms_en": ["levonorgestrel intrauterine system", "mirena"],
        "terms_es": ["sistema intrauterino de levonorgestrel", "mirena"],
    },
    {
        "rxnorm": "1605257",
        "display": "levonorgestrel 0.000813 MG/HR Intrauterine System [Liletta]",
        "terms_en": ["liletta intrauterine system", "liletta"],
        "terms_es": ["liletta"],
    },
    {
        "rxnorm": "1000126",
        "display": "1 ML medroxyprogesterone acetate 150 MG/ML Injection",
        "terms_en": ["medroxyprogesterone acetate 150 mg/ml injection", "medroxyprogesterone", "depo-provera"],
        "terms_es": ["acetato de medroxiprogesterona 150 mg/ml", "depo-provera"],
    },
    {
        "rxnorm": "1664463",
        "display": "24 HR tacrolimus 1 MG Extended Release Oral Tablet [Envarsus]",
        "terms_en": ["tacrolimus 1 mg extended release", "tacrolimus", "envarsus"],
        "terms_es": ["tacrolimus 1 mg", "tacrolimus"],
    },
    {
        "rxnorm": "308971",
        "display": "carbamazepine 20 MG/ML Oral Suspension [Tegretol]",
        "terms_en": ["carbamazepine 20 mg/ml oral suspension", "carbamazepine", "tegretol"],
        "terms_es": ["carbamazepina 20 mg/ml", "tegretol"],
    },
    {
        "rxnorm": "1870230",
        "display": "NDA020800 0.3 ML Epinephrine 1 MG/ML Auto-Injector",
        "terms_en": ["epinephrine 1 mg/ml auto-injector", "epinephrine", "epipen"],
        "terms_es": ["adrenalina 1 mg/ml", "epinefrina", "autoinyector de adrenalina"],
    },
    {
        "rxnorm": "861467",
        "display": "Meperidine Hydrochloride 50 MG Oral Tablet",
        "terms_en": ["meperidine hydrochloride 50 mg oral tablet", "meperidine 50 mg", "demerol"],
        "terms_es": ["meperidina hidrocloruro 50 mg", "meperidina"],
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
    {
        "snomed": "260147004",
        "display": "House dust mite (organism)",
        "category": "environment",
        "terms_en": ["house dust mite", "dust mite allergy", "dust mite", "dust allergy"],
        "terms_es": ["ácaros del polvo", "alergia a los ácaros del polvo", "ácaros"],
    },
    {
        "snomed": "3718001",
        "display": "Cow's milk (substance)",
        "category": "food",
        "terms_en": ["cow's milk", "milk allergy", "cow milk allergy", "dairy allergy"],
        "terms_es": ["leche de vaca", "alergia a la leche de vaca", "alergia a los lácteos", "leche"],
    },
    {
        "snomed": "735029006",
        "display": "Shellfish (substance)",
        "category": "food",
        "terms_en": ["shellfish (substance)", "shellfish", "shellfish allergy"],
        "terms_es": ["mariscos", "alergia a los mariscos"],
    },
    {
        "snomed": "84489001",
        "display": "Mold (organism)",
        "category": "environment",
        "terms_en": ["mold (organism)", "mold allergy", "mold", "fungus allergy"],
        "terms_es": ["moho", "alergia al moho", "hongos"],
    },
    {
        "snomed": "29046",
        "display": "Lisinopril",
        "category": "medication",
        "terms_en": ["lisinopril allergy", "allergy to lisinopril"],
        "terms_es": ["alergia al lisinopril", "alergia a lisinopril"],
    },
    {
        "snomed": "609328004",
        "display": "Allergic disposition (finding)",
        "category": "environment",
        "terms_en": ["allergic disposition", "atopic disposition", "atopy"],
        "terms_es": ["predisposición alérgica", "atopia"],
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
