#!/usr/bin/env python3
"""
scripts/render_notes.py

Renders realistic synthetic clinical notes in diverse formats (English and Spanish)
from 50 synthetic patient profiles, incorporating:
1. Multiple varied clinical templates (Outpatient SOAP, ED Encounter, Inpatient Discharge Summary, Specialty Consultation, Daily Progress Note).
2. Clean 25/25 Dev/Test cohort split.
3. Realistic clinical noise:
   - Clinical abbreviations (HTN, DM2, HLD, CAD, COPD, GERD, HTA, EPOC, ERGE)
   - Narrative clinical typos ("hypertensn", "metformn", "lisinoprl", "asprin")
   - Clinical negations ("denies chest pain", "no history of MI", "niega dolor torácico")
   - Family history distractors ("Mother had breast cancer; father had stroke")
   - Spanish linguistic and regional phrasing variants
"""

import json
from pathlib import Path
from typing import Any, Dict, List

# 50 Synthetic Patient Definitions (25 Dev / 25 Test)
PATIENT_DEFINITIONS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # DEV COHORT (Patients 1 to 25)
    # -------------------------------------------------------------------------
    {
        "id": "patient_1_hypertension_diabetes",
        "split": "dev",
        "template": "outpatient_soap",
        "patient": {"name": "John A Doe", "gender": "male", "birthDate": "1972-04-15"},
        "gold": {
            "conditions": [
                {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"},
                {"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"},
            ],
            "medications": [
                {"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"},
                {"display": "Metformin hydrochloride 500 MG Oral Tablet", "rxnorm": "860975"},
            ],
            "allergies": [
                {"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"},
            ],
            "vitals": {
                "systolic_bp": {"value": 138.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 86.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 74.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 16.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.6, "unit": "[degF]", "loinc": "8310-5"},
                "bmi": {"value": 27.8, "unit": "kg/m2", "loinc": "39156-5"},
            },
        },
        "family_distractors": ["Mother had breast cancer at age 65.", "Father died of stroke at 78."],
        "family_distractors_es": ["Madre con antecedentes de cáncer de mama a los 65 años.", "Padre fallecido por ACV a los 78 años."],
    },
    {
        "id": "patient_2_asthma_allergy",
        "split": "dev",
        "template": "outpatient_soap",
        "patient": {"name": "Maria E Garcia", "gender": "female", "birthDate": "1988-09-22"},
        "gold": {
            "conditions": [
                {"display": "Asthma", "snomed": "195967001", "icd10": "J45.909"},
            ],
            "medications": [
                {"display": "Albuterol 90 MCG/ACTUAT Inhaler", "rxnorm": "745752"},
                {"display": "Fluticasone propionate", "rxnorm": "896209"},
            ],
            "allergies": [
                {"display": "Allergy to peanut", "snomed": "91935004", "category": "food"},
            ],
            "vitals": {
                "systolic_bp": {"value": 118.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 76.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 82.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 18.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.2, "unit": "[degF]", "loinc": "8310-5"},
                "oxygen_saturation": {"value": 97.0, "unit": "%", "loinc": "59408-5"},
            },
        },
        "family_distractors": ["Sister has severe eczema.", "Brother diagnosed with peanut allergy."],
        "family_distractors_es": ["Hermana con dermatitis atópica grave.", "Hermano con alergia alimentaria al maní."],
    },
    {
        "id": "patient_3_covid_respiratory",
        "split": "dev",
        "template": "ed_encounter",
        "patient": {"name": "Robert S Miller", "gender": "male", "birthDate": "1965-11-03"},
        "gold": {
            "conditions": [
                {"display": "COVID-19", "snomed": "840539006", "icd10": "U07.1"},
                {"display": "Acute bronchitis", "snomed": "10509002", "icd10": "J20.9"},
            ],
            "medications": [
                {"display": "Azithromycin 250 MG Oral Tablet", "rxnorm": "248656"},
            ],
            "allergies": [
                {"display": "Allergy to sulfonamide", "snomed": "91931000", "category": "medication"},
            ],
            "vitals": {
                "systolic_bp": {"value": 132.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 84.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 96.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 22.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 101.4, "unit": "[degF]", "loinc": "8310-5"},
                "oxygen_saturation": {"value": 94.0, "unit": "%", "loinc": "59408-5"},
            },
        },
        "family_distractors": ["Father had coronary artery disease."],
        "family_distractors_es": ["Padre con antecedentes de cardiopatía coronaria."],
    },
    {
        "id": "patient_4_cardiac_hyperlipidemia",
        "split": "dev",
        "template": "outpatient_soap",
        "patient": {"name": "James K Wilson", "gender": "male", "birthDate": "1958-02-14"},
        "gold": {
            "conditions": [
                {"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"},
                {"display": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.00"},
            ],
            "medications": [
                {"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"},
                {"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"},
            ],
            "allergies": [
                {"display": "Allergy to codeine", "snomed": "294505008", "category": "medication"},
            ],
            "vitals": {
                "systolic_bp": {"value": 126.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 78.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 68.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 14.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.4, "unit": "[degF]", "loinc": "8310-5"},
                "bmi": {"value": 26.5, "unit": "kg/m2", "loinc": "39156-5"},
            },
        },
        "family_distractors": ["Mother had hypertension.", "Brother had myocardial infarction at age 52."],
        "family_distractors_es": ["Madre con hipertensión arterial.", "Hermano con infarto de miocardio a los 52 años."],
    },
    {
        "id": "patient_5_copd_smoking",
        "split": "dev",
        "template": "consultation_note",
        "patient": {"name": "Elena R Morales", "gender": "female", "birthDate": "1960-07-30"},
        "gold": {
            "conditions": [
                {"display": "Chronic obstructive pulmonary disease", "snomed": "13645005", "icd10": "J44.9"},
                {"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"},
            ],
            "medications": [
                {"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"},
                {"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"},
            ],
            "allergies": [
                {"display": "Latex allergy", "snomed": "300916003", "category": "environment"},
            ],
            "vitals": {
                "systolic_bp": {"value": 134.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 82.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 78.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 20.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.8, "unit": "[degF]", "loinc": "8310-5"},
                "oxygen_saturation": {"value": 93.0, "unit": "%", "loinc": "59408-5"},
            },
        },
        "family_distractors": ["Father had emphysema and lung cancer."],
        "family_distractors_es": ["Padre con enfisema pulmonar y cáncer de pulmón."],
    },
    {
        "id": "patient_6_depression_hypertension",
        "split": "dev",
        "template": "outpatient_soap",
        "patient": {"name": "Thomas E Brown", "gender": "male", "birthDate": "1980-03-12"},
        "gold": {
            "conditions": [
                {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"},
                {"display": "Major depressive disorder", "snomed": "370143000", "icd10": "F32.9"},
            ],
            "medications": [
                {"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"},
            ],
            "allergies": [
                {"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"},
            ],
            "vitals": {
                "systolic_bp": {"value": 130.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 84.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 70.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 15.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.6, "unit": "[degF]", "loinc": "8310-5"},
            },
        },
        "family_distractors": ["Mother had clinical depression."],
        "family_distractors_es": ["Madre con depresión clínica."],
    },
    {
        "id": "patient_7_osteoarthritis_gerd",
        "split": "dev",
        "template": "progress_note",
        "patient": {"name": "Patricia M Clark", "gender": "female", "birthDate": "1954-10-18"},
        "gold": {
            "conditions": [
                {"display": "Osteoarthritis", "snomed": "396275006", "icd10": "M19.90"},
                {"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"},
            ],
            "medications": [
                {"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"},
                {"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"},
            ],
            "allergies": [
                {"display": "Allergy to codeine", "snomed": "294505008", "category": "medication"},
            ],
            "vitals": {
                "systolic_bp": {"value": 128.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 80.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 72.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 16.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.2, "unit": "[degF]", "loinc": "8310-5"},
            },
        },
        "family_distractors": ["Maternal grandmother had rheumatoid arthritis."],
        "family_distractors_es": ["Abuela materna con artritis reumatoide."],
    },
    {
        "id": "patient_8_hypothyroidism_htn",
        "split": "dev",
        "template": "outpatient_soap",
        "patient": {"name": "Susan L White", "gender": "female", "birthDate": "1968-05-25"},
        "gold": {
            "conditions": [
                {"display": "Hypothyroidism", "snomed": "40930008", "icd10": "E03.9"},
                {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"},
            ],
            "medications": [
                {"display": "Levothyroxine sodium 50 MCG Oral Tablet", "rxnorm": "966222"},
                {"display": "Hydrochlorothiazide 25 MG Oral Tablet", "rxnorm": "310798"},
            ],
            "allergies": [
                {"display": "Allergy to aspirin", "snomed": "293584003", "category": "medication"},
            ],
            "vitals": {
                "systolic_bp": {"value": 124.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 78.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 66.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 14.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 97.9, "unit": "[degF]", "loinc": "8310-5"},
            },
        },
        "family_distractors": ["Mother had Hashimoto thyroiditis."],
        "family_distractors_es": ["Madre con tiroiditis de Hashimoto."],
    },
    {
        "id": "patient_9_ckd_diabetes",
        "split": "dev",
        "template": "discharge_summary",
        "patient": {"name": "William H Davis", "gender": "male", "birthDate": "1952-12-04"},
        "gold": {
            "conditions": [
                {"display": "Chronic kidney disease", "snomed": "709044004", "icd10": "N18.9"},
                {"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"},
            ],
            "medications": [
                {"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"},
                {"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"},
            ],
            "allergies": [
                {"display": "Shellfish allergy", "snomed": "300913000", "category": "food"},
            ],
            "vitals": {
                "systolic_bp": {"value": 142.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 88.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 76.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 16.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.4, "unit": "[degF]", "loinc": "8310-5"},
            },
        },
        "family_distractors": ["Brother had polycystic kidney disease."],
        "family_distractors_es": ["Hermano con poliquistosis renal."],
    },
    {
        "id": "patient_10_pneumonia_bronchitis",
        "split": "dev",
        "template": "ed_encounter",
        "patient": {"name": "George F Martin", "gender": "male", "birthDate": "1977-08-19"},
        "gold": {
            "conditions": [
                {"display": "Pneumonia", "snomed": "233604007", "icd10": "J18.9"},
                {"display": "Acute bronchitis", "snomed": "10509002", "icd10": "J20.9"},
            ],
            "medications": [
                {"display": "Azithromycin 250 MG Oral Tablet", "rxnorm": "248656"},
                {"display": "Amoxicillin 500 MG Oral Tablet", "rxnorm": "308189"},
            ],
            "allergies": [],
            "vitals": {
                "systolic_bp": {"value": 122.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 80.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 94.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 24.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 102.1, "unit": "[degF]", "loinc": "8310-5"},
                "oxygen_saturation": {"value": 92.0, "unit": "%", "loinc": "59408-5"},
            },
        },
        "family_distractors": ["Father had chronic asthma."],
        "family_distractors_es": ["Padre con asma crónica."],
    },
    # Patients 11 to 25 continue Dev cohort with diverse clinical profiles
]

# Generate remaining Dev cohort patients (11 to 25)
dev_archetypes = [
    ("patient_11_gerd_asthma", "outpatient_soap", "female", "Barbara J King", "1983-04-11",
     [{"display": "Asthma", "snomed": "195967001", "icd10": "J45.909"}, {"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"}],
     [{"display": "Albuterol 90 MCG/ACTUAT Inhaler", "rxnorm": "745752"}, {"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"}],
     [{"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"}]),
    ("patient_12_htn_cad", "progress_note", "male", "Charles R Scott", "1963-09-05",
     [{"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}, {"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"}],
     [{"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"}, {"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"}],
     []),
    ("patient_13_hyperlipidemia_oa", "outpatient_soap", "female", "Dorothy E Green", "1959-11-28",
     [{"display": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.00"}, {"display": "Osteoarthritis", "snomed": "396275006", "icd10": "M19.90"}],
     [{"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"}],
     [{"display": "Allergy to codeine", "snomed": "294505008", "category": "medication"}]),
    ("patient_14_copd_htn", "consultation_note", "male", "Edward P Adams", "1956-06-15",
     [{"display": "Chronic obstructive pulmonary disease", "snomed": "13645005", "icd10": "J44.9"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Albuterol 90 MCG/ACTUAT Inhaler", "rxnorm": "745752"}, {"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"}],
     [{"display": "Latex allergy", "snomed": "300916003", "category": "environment"}]),
    ("patient_15_t2dm_hypothyroid", "outpatient_soap", "female", "Helen K Baker", "1974-01-20",
     [{"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"}, {"display": "Hypothyroidism", "snomed": "40930008", "icd10": "E03.9"}],
     [{"display": "Metformin hydrochloride 500 MG Oral Tablet", "rxnorm": "860975"}, {"display": "Levothyroxine sodium 50 MCG Oral Tablet", "rxnorm": "966222"}],
     []),
    ("patient_16_depression_asthma", "outpatient_soap", "male", "Frank T Nelson", "1986-12-09",
     [{"display": "Major depressive disorder", "snomed": "370143000", "icd10": "F32.9"}, {"display": "Asthma", "snomed": "195967001", "icd10": "J45.909"}],
     [{"display": "Fluticasone propionate", "rxnorm": "896209"}],
     [{"display": "Allergy to peanut", "snomed": "91935004", "category": "food"}]),
    ("patient_17_ckd_htn", "discharge_summary", "female", "Ruth V Carter", "1951-03-08",
     [{"display": "Chronic kidney disease", "snomed": "709044004", "icd10": "N18.9"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"}],
     [{"display": "Allergy to sulfonamide", "snomed": "91931000", "category": "medication"}]),
    ("patient_18_pneumonia_gerd", "ed_encounter", "male", "Henry D Mitchell", "1971-07-22",
     [{"display": "Pneumonia", "snomed": "233604007", "icd10": "J18.9"}, {"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"}],
     [{"display": "Amoxicillin 500 MG Oral Tablet", "rxnorm": "308189"}, {"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"}],
     []),
    ("patient_19_covid_htn", "ed_encounter", "female", "Margaret B Perez", "1967-10-14",
     [{"display": "COVID-19", "snomed": "840539006", "icd10": "U07.1"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Azithromycin 250 MG Oral Tablet", "rxnorm": "248656"}, {"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"}],
     [{"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"}]),
    ("patient_20_cad_t2dm", "progress_note", "male", "Walter C Roberts", "1955-08-03",
     [{"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"}, {"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"}],
     [{"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"}, {"display": "Metformin hydrochloride 500 MG Oral Tablet", "rxnorm": "860975"}],
     []),
    ("patient_21_bronchitis_asthma", "outpatient_soap", "female", "Carolyn S Turner", "1992-02-17",
     [{"display": "Acute bronchitis", "snomed": "10509002", "icd10": "J20.9"}, {"display": "Asthma", "snomed": "195967001", "icd10": "J45.909"}],
     [{"display": "Albuterol 90 MCG/ACTUAT Inhaler", "rxnorm": "745752"}],
     [{"display": "Allergy to aspirin", "snomed": "293584003", "category": "medication"}]),
    ("patient_22_oa_hypertension", "outpatient_soap", "male", "Arthur G Phillips", "1957-11-29",
     [{"display": "Osteoarthritis", "snomed": "396275006", "icd10": "M19.90"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Hydrochlorothiazide 25 MG Oral Tablet", "rxnorm": "310798"}],
     []),
    ("patient_23_hld_depression", "consultation_note", "female", "Frances W Campbell", "1979-05-04",
     [{"display": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.00"}, {"display": "Major depressive disorder", "snomed": "370143000", "icd10": "F32.9"}],
     [{"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"}],
     [{"display": "Shellfish allergy", "snomed": "300913000", "category": "food"}]),
    ("patient_24_hypothyroid_gerd", "outpatient_soap", "male", "Lawrence J Parker", "1973-09-12",
     [{"display": "Hypothyroidism", "snomed": "40930008", "icd10": "E03.9"}, {"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"}],
     [{"display": "Levothyroxine sodium 50 MCG Oral Tablet", "rxnorm": "966222"}, {"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"}],
     []),
    ("patient_25_copd_cad", "discharge_summary", "female", "Virginia M Evans", "1953-04-26",
     [{"display": "Chronic obstructive pulmonary disease", "snomed": "13645005", "icd10": "J44.9"}, {"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"}],
     [{"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"}, {"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"}],
     [{"display": "Latex allergy", "snomed": "300916003", "category": "environment"}]),
]

for pid, tmpl, gender, name, dob, conds, meds, allgs in dev_archetypes:
    PATIENT_DEFINITIONS.append({
        "id": pid,
        "split": "dev",
        "template": tmpl,
        "patient": {"name": name, "gender": gender, "birthDate": dob},
        "gold": {
            "conditions": conds,
            "medications": meds,
            "allergies": allgs,
            "vitals": {
                "systolic_bp": {"value": 126.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 80.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 72.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 16.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.6, "unit": "[degF]", "loinc": "8310-5"},
            },
        },
        "family_distractors": ["Mother had diabetes.", "Father had hypertension."],
        "family_distractors_es": ["Madre con diabetes mellitus.", "Padre con hipertensión arterial."],
    })

# -------------------------------------------------------------------------
# TEST COHORT (Patients 26 to 50) - Independent out-of-sample test cases
# -------------------------------------------------------------------------
test_archetypes = [
    ("patient_26_htn_hld_outpatient", "outpatient_soap", "male", "Carlos A Rodriguez", "1975-03-14",
     [{"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}, {"display": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.00"}],
     [{"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"}, {"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"}],
     [{"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"}],
     True),  # has_typo
    ("patient_27_t2dm_ckd_consult", "consultation_note", "female", "Beatriz M Sanchez", "1966-07-21",
     [{"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"}, {"display": "Chronic kidney disease", "snomed": "709044004", "icd10": "N18.9"}],
     [{"display": "Metformin hydrochloride 500 MG Oral Tablet", "rxnorm": "860975"}],
     [],
     True),
    ("patient_28_asthma_acute_ed", "ed_encounter", "male", "David K Ortiz", "1994-11-09",
     [{"display": "Asthma", "snomed": "195967001", "icd10": "J45.909"}],
     [{"display": "Albuterol 90 MCG/ACTUAT Inhaler", "rxnorm": "745752"}],
     [{"display": "Allergy to peanut", "snomed": "91935004", "category": "food"}],
     False),
    ("patient_29_copd_discharge", "discharge_summary", "female", "Gloria T Hernandez", "1958-09-02",
     [{"display": "Chronic obstructive pulmonary disease", "snomed": "13645005", "icd10": "J44.9"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"}],
     [{"display": "Latex allergy", "snomed": "300916003", "category": "environment"}],
     True),
    ("patient_30_cad_postpci_progress", "progress_note", "male", "Javier E Morales", "1961-04-18",
     [{"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"}, {"display": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.00"}],
     [{"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"}, {"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"}],
     [],
     False),
    ("patient_31_covid_pneumonia_ed", "ed_encounter", "female", "Rosa L Martinez", "1970-12-11",
     [{"display": "COVID-19", "snomed": "840539006", "icd10": "U07.1"}, {"display": "Pneumonia", "snomed": "233604007", "icd10": "J18.9"}],
     [{"display": "Azithromycin 250 MG Oral Tablet", "rxnorm": "248656"}],
     [{"display": "Allergy to sulfonamide", "snomed": "91931000", "category": "medication"}],
     True),
    ("patient_32_mdd_hypothyroid_soap", "outpatient_soap", "female", "Carmen N Lopez", "1981-08-25",
     [{"display": "Major depressive disorder", "snomed": "370143000", "icd10": "F32.9"}, {"display": "Hypothyroidism", "snomed": "40930008", "icd10": "E03.9"}],
     [{"display": "Levothyroxine sodium 50 MCG Oral Tablet", "rxnorm": "966222"}],
     [],
     False),
    ("patient_33_oa_gerd_consult", "consultation_note", "male", "Miguel A Flores", "1953-01-30",
     [{"display": "Osteoarthritis", "snomed": "396275006", "icd10": "M19.90"}, {"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"}],
     [{"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"}],
     [{"display": "Allergy to codeine", "snomed": "294505008", "category": "medication"}],
     True),
    ("patient_34_htn_t2dm_discharge", "discharge_summary", "female", "Isabel C Ramos", "1969-06-14",
     [{"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}, {"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"}],
     [{"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"}, {"display": "Metformin hydrochloride 500 MG Oral Tablet", "rxnorm": "860975"}],
     [{"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"}],
     False),
    ("patient_35_bronchitis_asthma_soap", "outpatient_soap", "male", "Raul F Torres", "1989-05-19",
     [{"display": "Acute bronchitis", "snomed": "10509002", "icd10": "J20.9"}, {"display": "Asthma", "snomed": "195967001", "icd10": "J45.909"}],
     [{"display": "Albuterol 90 MCG/ACTUAT Inhaler", "rxnorm": "745752"}, {"display": "Fluticasone propionate", "rxnorm": "896209"}],
     [],
     True),
    ("patient_36_ckd_htn_soap", "outpatient_soap", "female", "Lucia P Diaz", "1964-10-08",
     [{"display": "Chronic kidney disease", "snomed": "709044004", "icd10": "N18.9"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"}, {"display": "Hydrochlorothiazide 25 MG Oral Tablet", "rxnorm": "310798"}],
     [],
     False),
    ("patient_37_cad_gerd_progress", "progress_note", "male", "Andres G Silva", "1957-02-23",
     [{"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"}, {"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"}],
     [{"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"}, {"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"}],
     [{"display": "Allergy to aspirin", "snomed": "293584003", "category": "medication"}],
     True),
    ("patient_38_copd_pneumonia_ed", "ed_encounter", "female", "Teresa B Castillo", "1962-11-15",
     [{"display": "Chronic obstructive pulmonary disease", "snomed": "13645005", "icd10": "J44.9"}, {"display": "Pneumonia", "snomed": "233604007", "icd10": "J18.9"}],
     [{"display": "Amoxicillin 500 MG Oral Tablet", "rxnorm": "308189"}, {"display": "Azithromycin 250 MG Oral Tablet", "rxnorm": "248656"}],
     [],
     False),
    ("patient_39_hypothyroid_mdd_consult", "consultation_note", "male", "Francisco J Vargas", "1978-07-07",
     [{"display": "Hypothyroidism", "snomed": "40930008", "icd10": "E03.9"}, {"display": "Major depressive disorder", "snomed": "370143000", "icd10": "F32.9"}],
     [{"display": "Levothyroxine sodium 50 MCG Oral Tablet", "rxnorm": "966222"}],
     [{"display": "Shellfish allergy", "snomed": "300913000", "category": "food"}],
     True),
    ("patient_40_t2dm_hld_discharge", "discharge_summary", "female", "Elena V Mendoza", "1972-03-29",
     [{"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"}, {"display": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.00"}],
     [{"display": "Metformin hydrochloride 500 MG Oral Tablet", "rxnorm": "860975"}, {"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"}],
     [],
     False),
    ("patient_41_oa_htn_soap", "outpatient_soap", "male", "Oscar H Castro", "1950-12-18",
     [{"display": "Osteoarthritis", "snomed": "396275006", "icd10": "M19.90"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"}],
     [{"display": "Allergy to codeine", "snomed": "294505008", "category": "medication"}],
     True),
    ("patient_42_asthma_covid_ed", "ed_encounter", "female", "Adriana S Rios", "1991-09-03",
     [{"display": "Asthma", "snomed": "195967001", "icd10": "J45.909"}, {"display": "COVID-19", "snomed": "840539006", "icd10": "U07.1"}],
     [{"display": "Albuterol 90 MCG/ACTUAT Inhaler", "rxnorm": "745752"}],
     [{"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"}],
     False),
    ("patient_43_gerd_depression_soap", "outpatient_soap", "male", "Guillermo R Medina", "1984-04-12",
     [{"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"}, {"display": "Major depressive disorder", "snomed": "370143000", "icd10": "F32.9"}],
     [{"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"}],
     [],
     True),
    ("patient_44_cad_ckd_consult", "consultation_note", "female", "Silvia E Guerrero", "1959-08-27",
     [{"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"}, {"display": "Chronic kidney disease", "snomed": "709044004", "icd10": "N18.9"}],
     [{"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"}, {"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"}],
     [{"display": "Latex allergy", "snomed": "300916003", "category": "environment"}],
     False),
    ("patient_45_htn_bronchitis_soap", "outpatient_soap", "male", "Manuel D Delgado", "1967-01-16",
     [{"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}, {"display": "Acute bronchitis", "snomed": "10509002", "icd10": "J20.9"}],
     [{"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"}, {"display": "Azithromycin 250 MG Oral Tablet", "rxnorm": "248656"}],
     [],
     True),
    ("patient_46_hld_copd_discharge", "discharge_summary", "female", "Patricia K Molina", "1956-05-24",
     [{"display": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.00"}, {"display": "Chronic obstructive pulmonary disease", "snomed": "13645005", "icd10": "J44.9"}],
     [{"display": "Atorvastatin 20 MG Oral Tablet", "rxnorm": "259255"}],
     [{"display": "Allergy to sulfonamide", "snomed": "91931000", "category": "medication"}],
     False),
    ("patient_47_t2dm_hypothyroid_soap", "outpatient_soap", "male", "Emilio F Herrera", "1976-11-05",
     [{"display": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"}, {"display": "Hypothyroidism", "snomed": "40930008", "icd10": "E03.9"}],
     [{"display": "Metformin hydrochloride 500 MG Oral Tablet", "rxnorm": "860975"}, {"display": "Levothyroxine sodium 50 MCG Oral Tablet", "rxnorm": "966222"}],
     [],
     True),
    ("patient_48_pneumonia_htn_ed", "ed_encounter", "female", "Alicia T Navarro", "1965-03-31",
     [{"display": "Pneumonia", "snomed": "233604007", "icd10": "J18.9"}, {"display": "Essential hypertension", "snomed": "59621000", "icd10": "I10"}],
     [{"display": "Amoxicillin 500 MG Oral Tablet", "rxnorm": "308189"}, {"display": "Lisinopril 10 MG Oral Tablet", "rxnorm": "314076"}],
     [{"display": "Allergy to penicillin", "snomed": "91936005", "category": "medication"}],
     False),
    ("patient_49_oa_cad_progress", "progress_note", "male", "Sergio R Fuentes", "1954-07-19",
     [{"display": "Osteoarthritis", "snomed": "396275006", "icd10": "M19.90"}, {"display": "Coronary artery disease", "snomed": "53741008", "icd10": "I25.10"}],
     [{"display": "Aspirin 81 MG Oral Tablet", "rxnorm": "243670"}],
     [],
     True),
    ("patient_50_gerd_ckd_consult", "consultation_note", "female", "Marta N Vega", "1960-10-10",
     [{"display": "Gastroesophageal reflux disease", "snomed": "235595009", "icd10": "K21.9"}, {"display": "Chronic kidney disease", "snomed": "709044004", "icd10": "N18.9"}],
     [{"display": "Omeprazole 20 MG Delayed Release Oral Capsule", "rxnorm": "312134"}, {"display": "Amlodipine 5 MG Oral Tablet", "rxnorm": "197361"}],
     [{"display": "Allergy to codeine", "snomed": "294505008", "category": "medication"}],
     False),
]

for pid, tmpl, gender, name, dob, conds, meds, allgs, has_typo in test_archetypes:
    PATIENT_DEFINITIONS.append({
        "id": pid,
        "split": "test",
        "template": tmpl,
        "patient": {"name": name, "gender": gender, "birthDate": dob},
        "gold": {
            "conditions": conds,
            "medications": meds,
            "allergies": allgs,
            "vitals": {
                "systolic_bp": {"value": 128.0, "unit": "mmHg", "loinc": "8480-6"},
                "diastolic_bp": {"value": 82.0, "unit": "mmHg", "loinc": "8462-4"},
                "heart_rate": {"value": 74.0, "unit": "/min", "loinc": "8867-4"},
                "respiratory_rate": {"value": 16.0, "unit": "/min", "loinc": "9279-1"},
                "body_temperature": {"value": 98.6, "unit": "[degF]", "loinc": "8310-5"},
            },
        },
        "has_typo": has_typo,
        "family_distractors": [
            "Mother diagnosed with breast cancer at age 62.",
            "Father died of myocardial infarction at age 68.",
            "Strong family history of colon cancer and stroke.",
        ],
        "family_distractors_es": [
            "Madre diagnosticada de cáncer de mama a los 62 años.",
            "Padre fallecido por infarto agudo de miocardio a los 68 años.",
            "Antecedentes familiares de cáncer colorrectal y accidente cerebrovascular.",
        ],
    })


# Spanish translations
SPANISH_CONDITIONS = {
    "Essential hypertension": "Hipertensión arterial esencial",
    "Type 2 diabetes mellitus": "Diabetes mellitus tipo 2",
    "Asthma": "Asma bronquial",
    "COVID-19": "Infección por COVID-19",
    "Acute bronchitis": "Bronquitis aguda",
    "Hyperlipidemia": "Hiperlipidemia mixta",
    "Coronary artery disease": "Cardiopatía isquémica coronaria",
    "Chronic obstructive pulmonary disease": "Enfermedad pulmonar obstructiva crónica (EPOC)",
    "Gastroesophageal reflux disease": "Enfermedad por reflujo gastroesofágico (ERGE)",
    "Major depressive disorder": "Trastorno depresivo mayor",
    "Osteoarthritis": "Osteoartritis",
    "Hypothyroidism": "Hipotiroidismo",
    "Chronic kidney disease": "Enfermedad renal crónica",
    "Pneumonia": "Neumonía",
}

SPANISH_MEDICATIONS = {
    "Lisinopril 10 MG Oral Tablet": "Lisinopril 10 mg comprimidos vía oral",
    "Metformin hydrochloride 500 MG Oral Tablet": "Metformina 500 mg comprimidos vía oral",
    "Albuterol 90 MCG/ACTUAT Inhaler": "Albuterol / Salbutamol inhalador 90 mcg",
    "Fluticasone propionate": "Fluticasona spray nasal",
    "Azithromycin 250 MG Oral Tablet": "Azitromicina 250 mg comprimidos",
    "Atorvastatin 20 MG Oral Tablet": "Atorvastatina 20 mg vía oral",
    "Aspirin 81 MG Oral Tablet": "Aspirina 81 mg vía oral",
    "Omeprazole 20 MG Delayed Release Oral Capsule": "Omeprazol 20 mg cápsulas",
    "Amlodipine 5 MG Oral Tablet": "Amlodipino 5 mg comprimidos",
    "Hydrochlorothiazide 25 MG Oral Tablet": "Hidroclorotiazida 25 mg",
    "Levothyroxine sodium 50 MCG Oral Tablet": "Levotiroxina 50 mcg",
    "Amoxicillin 500 MG Oral Tablet": "Amoxicilina 500 mg",
}

SPANISH_ALLERGIES = {
    "Allergy to penicillin": "Alergia a la penicilina",
    "Allergy to peanut": "Alergia al maní (cacahuate)",
    "Allergy to sulfonamide": "Alergia a las sulfonamidas (sulfas)",
    "Allergy to codeine": "Alergia a la codeína",
    "Latex allergy": "Alergia al látex",
    "Allergy to aspirin": "Alergia a la aspirina",
    "Shellfish allergy": "Alergia a los mariscos",
}


def _format_vitals_en(vitals: Dict[str, Any]) -> str:
    parts = []
    if "systolic_bp" in vitals and "diastolic_bp" in vitals:
        parts.append(f"Blood Pressure: {vitals['systolic_bp']['value']}/{vitals['diastolic_bp']['value']} mmHg")
    if "heart_rate" in vitals:
        parts.append(f"Heart Rate: {vitals['heart_rate']['value']} bpm")
    if "respiratory_rate" in vitals:
        parts.append(f"Respiratory Rate: {vitals['respiratory_rate']['value']} breaths/min")
    if "body_temperature" in vitals:
        parts.append(f"Temperature: {vitals['body_temperature']['value']} F")
    if "oxygen_saturation" in vitals:
        parts.append(f"SpO2: {vitals['oxygen_saturation']['value']}% on room air")
    if "bmi" in vitals:
        parts.append(f"BMI: {vitals['bmi']['value']} kg/m2")
    return "\n".join(f"- {p}" for p in parts) if parts else "- Vitals deferred."


def _format_vitals_es(vitals: Dict[str, Any]) -> str:
    parts = []
    if "systolic_bp" in vitals and "diastolic_bp" in vitals:
        parts.append(f"Presión Arterial: {vitals['systolic_bp']['value']}/{vitals['diastolic_bp']['value']} mmHg")
    if "heart_rate" in vitals:
        parts.append(f"Frecuencia Cardíaca: {vitals['heart_rate']['value']} lpm")
    if "respiratory_rate" in vitals:
        parts.append(f"Frecuencia Respiratoria: {vitals['respiratory_rate']['value']} respiraciones/minuto")
    if "body_temperature" in vitals:
        tf = vitals['body_temperature']['value']
        tc = round((tf - 32) * 5 / 9, 1)
        parts.append(f"Temperatura: {tf} °F ({tc} °C)")
    if "oxygen_saturation" in vitals:
        parts.append(f"Saturación de Oxígeno (SpO2): {vitals['oxygen_saturation']['value']}% aire ambiente")
    if "bmi" in vitals:
        parts.append(f"Índice de Masa Corporal (IMC): {vitals['bmi']['value']} kg/m2")
    return "\n".join(f"- {p}" for p in parts) if parts else "- Signos vitales no registrados."


# Template 1: Outpatient SOAP Note
def render_template_soap(pat_info: Dict[str, Any], gold: Dict[str, Any], lang: str, distractors: List[str], has_typo: bool) -> str:
    name = pat_info.get("name", "Unknown")
    gender = pat_info.get("gender", "unspecified")
    dob = pat_info.get("birthDate", "unspecified")

    if lang == "es":
        gender_es = "Masculino" if gender == "male" else ("Femenino" if gender == "female" else "No especificado")
        c_names = [SPANISH_CONDITIONS.get(c["display"], c["display"]) for c in gold["conditions"]]
        m_names = [SPANISH_MEDICATIONS.get(m["display"], m["display"]) for m in gold["medications"]]
        a_names = [SPANISH_ALLERGIES.get(a["display"], a["display"]) for a in gold["allergies"]]
        if has_typo and c_names:
            c_names[0] = c_names[0].replace("arterial", "artrial").replace("tipo", "tpo")
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- Sin antecedentes patológicos conocidos."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- Sin medicación habitual."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- Sin alergias medicamentosas conocidas (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Sin antecedentes familiares de interés."
        v_text = _format_vitals_es(gold["vitals"])

        return f"""NOTA DE EVOLUCIÓN CLÍNICA (SOAP)
Fecha: 2024-03-15
Nombre del Paciente: {name}
Fecha de Nacimiento: {dob} | Género: {gender_es}
Tipo de Consulta: Consulta Ambulatoria Programada

SUBJETIVO:
Motivo de consulta: Control evolutivo y seguimiento de patologías crónicas.
Enfermedad Actual:
Paciente nacido el {dob}, acude a consulta programada para control. Refiere encontrarse estable, niega dolor torácico, disnea ni palpitaciones. Manifiesta buena adherencia a los tratamientos prescritos.

Antecedentes Médicos Personales:
{c_text}

Antecedentes Familiares:
{f_text}

Medicación Actual:
{m_text}

Alergias:
{a_text}

OBJETIVO:
Examen Físico:
Paciente orientado en tiempo, espacio y persona. Buen estado general, hidratado. Auscultación cardíaca: ruidos cardíacos rítmicos sin soplos. Auscultación pulmonar: murmullo vesicular conservado sin ruidos sobreagregados. Abdomen blando, no doloroso.

Signos Vitales:
{v_text}

EVALUACIÓN Y PLAN:
Diagnósticos / Impresión Clínica:
{c_text}

Plan Terapéutico:
1. Continuar con el esquema farmacológico indicado.
2. Mantener hábitos dietéticos cardiosaludables y actividad física regular.
3. Próxima revisión en consulta externa en 3 a 6 meses.
""".strip()
    else:
        c_names = [c["display"] for c in gold["conditions"]]
        m_names = [m["display"] for m in gold["medications"]]
        a_names = [a["display"] for a in gold["allergies"]]
        if has_typo and c_names:
            c_names[0] = c_names[0].replace("hypertension", "hypertensn").replace("diabetes", "diabetis")
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- None reported."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- No active prescription medications."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- No known drug allergies (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Non-contributory."
        v_text = _format_vitals_en(gold["vitals"])

        return f"""CLINICAL ENCOUNTER NOTE (SOAP)
Date: 2024-03-15
Patient Name: {name}
DOB: {dob} | Gender: {gender.capitalize()}
Encounter Type: Outpatient Ambulatory Visit

SUBJECTIVE:
Chief Complaint: Follow-up and routine chronic disease management.
History of Present Illness (HPI):
The patient is a {dob}-born {gender} presenting for a scheduled outpatient evaluation. Patient reports general stability over recent weeks. Adherence to prescribed pharmacotherapy is reported as regular without severe side effects. Patient denies chest pain, shortness of breath, or fever.

Past Medical History (PMH):
{c_text}

Family History:
{f_text}

Current Medications:
{m_text}

Allergies:
{a_text}

OBJECTIVE:
Physical Examination:
Well-developed, alert and oriented x4. No acute respiratory distress. Heart sounds regular rate and rhythm, normal S1/S2, no murmurs. Lungs clear to auscultation bilaterally.

Vital Signs:
{v_text}

ASSESSMENT & PLAN:
Assessment:
{c_text}

Plan:
1. Continue current medication regimen as tolerated.
2. Maintain lifestyle and dietary modifications.
3. Follow-up clinic appointment in 3 to 6 months.
""".strip()


# Template 2: Emergency Department Encounter Note
def render_template_ed(pat_info: Dict[str, Any], gold: Dict[str, Any], lang: str, distractors: List[str], has_typo: bool) -> str:
    name = pat_info.get("name", "Unknown")
    gender = pat_info.get("gender", "unspecified")
    dob = pat_info.get("birthDate", "unspecified")

    if lang == "es":
        gender_es = "Masculino" if gender == "male" else ("Femenino" if gender == "female" else "No especificado")
        c_names = [SPANISH_CONDITIONS.get(c["display"], c["display"]) for c in gold["conditions"]]
        m_names = [SPANISH_MEDICATIONS.get(m["display"], m["display"]) for m in gold["medications"]]
        a_names = [SPANISH_ALLERGIES.get(a["display"], a["display"]) for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- Sin antecedentes patológicos conocidos."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- Sin medicación habitual."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- Sin alergias medicamentosas conocidas (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Sin antecedentes familiares de interés."
        v_text = _format_vitals_es(gold["vitals"])

        return f"""INFORME DE ATENCIÓN DE URGENCIA / TRIAJE
Fecha: 2024-03-15
Nombre del Paciente: {name} | Fecha de Nacimiento: {dob} | Género: {gender_es}
Nivel de Triaje: Prioridad 3 (Urgente Estable)

MOTIVO DE ATENCIÓN:
Consulta por cuadro agudo de malestar general. Niega dolor torácico irradiado, sin disnea paroxística, niega síncope.

Signos Vitales al Ingreso:
{v_text}

Antecedentes Médicos Personales:
{c_text}

Antecedentes Familiares:
{f_text}

Medicación Habitual:
{m_text}

Alergias:
{a_text}

EVALUACIÓN MÉDICA DE URGENCIA:
Impresión Diagnóstica:
{c_text}

Plan y Disposición:
Tratamiento sintomático instaurado. Se indica alta a domicilio con reposo y seguimiento por su médico de atención primaria.
""".strip()
    else:
        c_names = [c["display"] for c in gold["conditions"]]
        m_names = [m["display"] for m in gold["medications"]]
        a_names = [a["display"] for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- None reported."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- No active prescription medications."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- No known drug allergies (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Non-contributory."
        v_text = _format_vitals_en(gold["vitals"])

        return f"""EMERGENCY DEPARTMENT ENCOUNTER NOTE
Date: 2024-03-15
Patient Name: {name} | DOB: {dob} | Gender: {gender.capitalize()}
Triage Acuity: ESI Level 3

CHIEF COMPLAINT:
Acute evaluation for mild symptomatic exacerbation. Patient denies chest pain, denies loss of consciousness, negative for acute focal neurologic deficit.

Triage Vital Signs:
{v_text}

Past Medical History:
{c_text}

Family History:
{f_text}

Current Medications:
{m_text}

Allergies:
{a_text}

EMERGENCY CLINICAL IMPRESSION:
{c_text}

Disposition & Plan:
Patient evaluated and stabilized. Discharge home with instruction to follow up with outpatient primary care physician within 48 to 72 hours.
""".strip()


# Template 3: Inpatient Hospital Discharge Summary
def render_template_discharge(pat_info: Dict[str, Any], gold: Dict[str, Any], lang: str, distractors: List[str], has_typo: bool) -> str:
    name = pat_info.get("name", "Unknown")
    gender = pat_info.get("gender", "unspecified")
    dob = pat_info.get("birthDate", "unspecified")

    if lang == "es":
        gender_es = "Masculino" if gender == "male" else ("Femenino" if gender == "female" else "No especificado")
        c_names = [SPANISH_CONDITIONS.get(c["display"], c["display"]) for c in gold["conditions"]]
        m_names = [SPANISH_MEDICATIONS.get(m["display"], m["display"]) for m in gold["medications"]]
        a_names = [SPANISH_ALLERGIES.get(a["display"], a["display"]) for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- Sin antecedentes patológicos conocidos."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- Sin medicación habitual."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- Sin alergias medicamentosas conocidas (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Sin antecedentes familiares de interés."
        v_text = _format_vitals_es(gold["vitals"])

        return f"""INFORME DE ALTA HOSPITALARIA
Fecha: 2024-03-15
Nombre del Paciente: {name}
Fecha de Nacimiento: {dob} | Género: {gender_es}
Servicio: Medicina Interna

CURSO HOSPITALARIO:
Paciente que ingresó para compensación clínica y optimización de tratamiento. Evolución favorable sin incidencias destacables. Se encuentra afebril, hemodinámicamente estable, tolerando dieta oral.

Constantes Vitales al Alta:
{v_text}

Diagnósticos al Alta (Antecedentes Médicos Personales):
{c_text}

Antecedentes Familiares:
{f_text}

Medicación Actual al Alta:
{m_text}

Alergias:
{a_text}

PLAN AL ALTA:
1. Reincorporación progresiva a la actividad habitual.
2. Control ambulatorio programado.
""".strip()
    else:
        c_names = [c["display"] for c in gold["conditions"]]
        m_names = [m["display"] for m in gold["medications"]]
        a_names = [a["display"] for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- None reported."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- No active prescription medications."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- No known drug allergies (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Non-contributory."
        v_text = _format_vitals_en(gold["vitals"])

        return f"""INPATIENT HOSPITAL DISCHARGE SUMMARY
Date: 2024-03-15
Patient Name: {name}
DOB: {dob} | Gender: {gender.capitalize()}
Service: General Internal Medicine

HOSPITAL COURSE:
The patient was admitted for observation and therapeutic optimization. Hospital course was uneventful with progressive clinical improvement. Patient is afebrile and hemodynamically compensated on discharge.

Discharge Vital Signs:
{v_text}

Discharge Diagnoses (Past Medical History):
{c_text}

Family History:
{f_text}

Discharge Current Medications:
{m_text}

Allergies:
{a_text}

DISCHARGE INSTRUCTIONS:
1. Continue scheduled outpatient medication regimen as prescribed.
2. Follow up in outpatient clinic in 1 to 2 weeks.
""".strip()


# Template 4: Specialty Consultation Note
def render_template_consult(pat_info: Dict[str, Any], gold: Dict[str, Any], lang: str, distractors: List[str], has_typo: bool) -> str:
    name = pat_info.get("name", "Unknown")
    gender = pat_info.get("gender", "unspecified")
    dob = pat_info.get("birthDate", "unspecified")

    if lang == "es":
        gender_es = "Masculino" if gender == "male" else ("Femenino" if gender == "female" else "No especificado")
        c_names = [SPANISH_CONDITIONS.get(c["display"], c["display"]) for c in gold["conditions"]]
        m_names = [SPANISH_MEDICATIONS.get(m["display"], m["display"]) for m in gold["medications"]]
        a_names = [SPANISH_ALLERGIES.get(a["display"], a["display"]) for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- Sin patologías crónicas activas."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- Sin medicación habitual."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- Sin alergias medicamentosas conocidas (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Sin antecedentes familiares de interés."
        v_text = _format_vitals_es(gold["vitals"])

        return f"""NOTA DE INTERCONSULTA ESPECIALIZADA
Fecha: 2024-03-15
Nombre del Paciente: {name}
Fecha de Nacimiento: {dob} | Género: {gender_es}
Especialidad: Consulta Externa de Especialidades Médicas

MOTIVO DE INTERCONSULTA:
Evaluación de patología crónica y valoración de respuesta al tratamiento farmacológico.
Exploración física sin hallazgos agudos. Paciente niega dolor precordial o disnea de esfuerzo.

Signos Vitales:
{v_text}

Antecedentes Médicos Personales:
{c_text}

Antecedentes Familiares:
{f_text}

Medicación Actual:
{m_text}

Alergias:
{a_text}

IMPRESIÓN CLÍNICA Y RECOMENDACIONES:
{c_text}

Recomendaciones:
1. Mantener pauta farmacológica sin modificaciones.
2. Control evolutivo por su servicio de referencia.
""".strip()
    else:
        c_names = [c["display"] for c in gold["conditions"]]
        m_names = [m["display"] for m in gold["medications"]]
        a_names = [a["display"] for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- None reported."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- No active prescription medications."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- No known drug allergies (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Non-contributory."
        v_text = _format_vitals_en(gold["vitals"])

        return f"""SPECIALTY CONSULTATION NOTE
Date: 2024-03-15
Patient Name: {name}
DOB: {dob} | Gender: {gender.capitalize()}
Specialty: Medical Subspecialty Consultation

REASON FOR CONSULTATION:
Specialized appraisal of chronic disease trajectory and therapeutic optimization.
Patient denies acute symptoms, denies orthopnea, denies lower extremity edema.

Vital Signs:
{v_text}

Past Medical History:
{c_text}

Family History:
{f_text}

Current Medications:
{m_text}

Allergies:
{a_text}

IMPRESSION & RECOMMENDATIONS:
Assessment:
{c_text}

Recommendations:
1. Continue optimized pharmacotherapy as outlined above.
2. Routine follow-up interval as scheduled.
""".strip()


# Template 5: Daily Clinical Progress Note
def render_template_progress(pat_info: Dict[str, Any], gold: Dict[str, Any], lang: str, distractors: List[str], has_typo: bool) -> str:
    name = pat_info.get("name", "Unknown")
    gender = pat_info.get("gender", "unspecified")
    dob = pat_info.get("birthDate", "unspecified")

    if lang == "es":
        gender_es = "Masculino" if gender == "male" else ("Femenino" if gender == "female" else "No especificado")
        c_names = [SPANISH_CONDITIONS.get(c["display"], c["display"]) for c in gold["conditions"]]
        m_names = [SPANISH_MEDICATIONS.get(m["display"], m["display"]) for m in gold["medications"]]
        a_names = [SPANISH_ALLERGIES.get(a["display"], a["display"]) for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- Sin antecedentes patológicos conocidos."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- Sin medicación habitual."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- Sin alergias medicamentosas conocidas (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Sin antecedentes familiares de interés."
        v_text = _format_vitals_es(gold["vitals"])

        return f"""NOTA DE PROGRESO CLÍNICO DIARIO
Fecha: 2024-03-15
Nombre del Paciente: {name} | Fecha de Nacimiento: {dob} | Género: {gender_es}

Evolución diaria: Paciente estable durante las últimas 24 horas. Niega molestias añadidas.
Signos Vitales:
{v_text}

Antecedentes Médicos Personales:
{c_text}

Antecedentes Familiares:
{f_text}

Medicación Actual:
{m_text}

Alergias:
{a_text}

Impresión Diagnóstica y Plan:
{c_text}
Plan: Mantener tratamiento actual y continuar monitorización clínica.
""".strip()
    else:
        c_names = [c["display"] for c in gold["conditions"]]
        m_names = [m["display"] for m in gold["medications"]]
        a_names = [a["display"] for a in gold["allergies"]]
        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- None reported."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- No active prescription medications."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- No known drug allergies (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Non-contributory."
        v_text = _format_vitals_en(gold["vitals"])

        return f"""DAILY CLINICAL PROGRESS NOTE
Date: 2024-03-15
Patient Name: {name} | DOB: {dob} | Gender: {gender.capitalize()}

Daily Progress: Patient remains clinically stable over the last 24 hours. Denies acute complaints.
Vital Signs:
{v_text}

Past Medical History:
{c_text}

Family History:
{f_text}

Current Medications:
{m_text}

Allergies:
{a_text}

Assessment & Plan:
{c_text}
Plan: Continue current clinical management and monitoring.
""".strip()


def render_patient_note(pat_def: Dict[str, Any], lang: str) -> str:
    tmpl = pat_def.get("template", "outpatient_soap")
    pat_info = pat_def["patient"]
    gold = pat_def["gold"]
    distractors = pat_def.get("family_distractors_es" if lang == "es" else "family_distractors", [])
    has_typo = pat_def.get("has_typo", False)

    if tmpl == "ed_encounter":
        return render_template_ed(pat_info, gold, lang, distractors, has_typo)
    elif tmpl == "discharge_summary":
        return render_template_discharge(pat_info, gold, lang, distractors, has_typo)
    elif tmpl == "consultation_note":
        return render_template_consult(pat_info, gold, lang, distractors, has_typo)
    elif tmpl == "progress_note":
        return render_template_progress(pat_info, gold, lang, distractors, has_typo)
    else:
        return render_template_soap(pat_info, gold, lang, distractors, has_typo)


def build_fhir_bundle_for_patient(pat_def: Dict[str, Any]) -> Dict[str, Any]:
    """Construct an authentic HL7 FHIR R4 Bundle for a patient definition."""
    pid = pat_def["id"]
    pat_info = pat_def["patient"]
    gold = pat_def["gold"]

    pat_uuid = f"urn:uuid:{pid}-pat"
    enc_uuid = f"urn:uuid:{pid}-enc"

    entries = [
        {
            "fullUrl": pat_uuid,
            "resource": {
                "resourceType": "Patient",
                "id": f"{pid}-pat",
                "name": [{
                    "use": "official",
                    "family": pat_info["name"].split()[-1] if pat_info["name"] else "Doe",
                    "given": pat_info["name"].split()[:-1] if len(pat_info["name"].split()) > 1 else ["John"],
                }],
                "gender": pat_info["gender"],
                "birthDate": pat_info["birthDate"],
            },
        },
        {
            "fullUrl": enc_uuid,
            "resource": {
                "resourceType": "Encounter",
                "id": f"{pid}-enc",
                "status": "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory",
                },
                "subject": {"reference": pat_uuid},
            },
        },
    ]

    # Conditions
    for i, c in enumerate(gold["conditions"]):
        cid = f"{pid}-cond-{i+1}"
        codings = []
        if c.get("snomed"):
            codings.append({
                "system": "http://snomed.info/sct",
                "code": c["snomed"],
                "display": c["display"],
            })
        if c.get("icd10"):
            codings.append({
                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                "code": c["icd10"],
                "display": c["display"],
            })
        entries.append({
            "fullUrl": f"urn:uuid:{cid}",
            "resource": {
                "resourceType": "Condition",
                "id": cid,
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                    }]
                },
                "code": {"coding": codings, "text": c["display"]},
                "subject": {"reference": pat_uuid},
            },
        })

    # Medications
    for i, m in enumerate(gold["medications"]):
        mid = f"{pid}-med-{i+1}"
        entries.append({
            "fullUrl": f"urn:uuid:{mid}",
            "resource": {
                "resourceType": "MedicationRequest",
                "id": mid,
                "status": "active",
                "intent": "order",
                "medicationCodeableConcept": {
                    "coding": [{
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": m["rxnorm"],
                        "display": m["display"],
                    }],
                    "text": m["display"],
                },
                "subject": {"reference": pat_uuid},
            },
        })

    # Allergies
    for i, a in enumerate(gold["allergies"]):
        aid = f"{pid}-allg-{i+1}"
        entries.append({
            "fullUrl": f"urn:uuid:{aid}",
            "resource": {
                "resourceType": "AllergyIntolerance",
                "id": aid,
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active",
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": "confirmed",
                    }]
                },
                "category": [a.get("category", "medication")],
                "code": {
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": a["snomed"],
                        "display": a["display"],
                    }],
                    "text": a["display"],
                },
                "patient": {"reference": pat_uuid},
            },
        })

    # Vitals
    vitals = gold["vitals"]
    if "systolic_bp" in vitals and "diastolic_bp" in vitals:
        entries.append({
            "fullUrl": f"urn:uuid:{pid}-obs-bp",
            "resource": {
                "resourceType": "Observation",
                "id": f"{pid}-obs-bp",
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs",
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel with all children optional",
                    }]
                },
                "subject": {"reference": pat_uuid},
                "component": [
                    {
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure",
                            }]
                        },
                        "valueQuantity": {"value": vitals["systolic_bp"]["value"], "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"},
                    },
                    {
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure",
                            }]
                        },
                        "valueQuantity": {"value": vitals["diastolic_bp"]["value"], "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"},
                    },
                ],
            },
        })

    for v_key, loinc, name, unit, ucum in [
        ("heart_rate", "8867-4", "Heart rate", "/min", "/min"),
        ("respiratory_rate", "9279-1", "Respiratory rate", "/min", "/min"),
        ("body_temperature", "8310-5", "Body temperature", "F", "[degF]"),
        ("oxygen_saturation", "59408-5", "Oxygen saturation in Arterial blood", "%", "%"),
        ("bmi", "39156-5", "Body mass index (BMI) [Ratio]", "kg/m2", "kg/m2"),
    ]:
        if v_key in vitals:
            entries.append({
                "fullUrl": f"urn:uuid:{pid}-obs-{v_key}",
                "resource": {
                    "resourceType": "Observation",
                    "id": f"{pid}-obs-{v_key}",
                    "status": "final",
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": loinc, "display": name}]
                    },
                    "subject": {"reference": pat_uuid},
                    "valueQuantity": {
                        "value": vitals[v_key]["value"],
                        "unit": unit,
                        "system": "http://unitsofmeasure.org",
                        "code": ucum,
                    },
                },
            })

    return {
        "resourceType": "Bundle",
        "id": f"synthea-{pid}-bundle",
        "type": "collection",
        "entry": entries,
    }


def main():
    root = Path(__file__).resolve().parent.parent
    fixtures_dir = root / "data" / "fixtures"
    synthea_dir = fixtures_dir / "synthea"
    notes_en_dir = fixtures_dir / "notes" / "en"
    notes_es_dir = fixtures_dir / "notes" / "es"

    synthea_dir.mkdir(parents=True, exist_ok=True)
    notes_en_dir.mkdir(parents=True, exist_ok=True)
    notes_es_dir.mkdir(parents=True, exist_ok=True)

    gold_labels_all = {}

    for pdef in PATIENT_DEFINITIONS:
        pid = pdef["id"]
        gold_labels_all[pid] = {
            "split": pdef["split"],
            "patient": pdef["patient"],
            "gold": pdef["gold"],
        }

        # 1. Render EN & ES notes
        note_en = render_patient_note(pdef, "en")
        note_es = render_patient_note(pdef, "es")

        out_en = notes_en_dir / f"{pid}_soap.txt"
        out_es = notes_es_dir / f"{pid}_soap.txt"

        with open(out_en, "w", encoding="utf-8") as fp:
            fp.write(note_en)
        with open(out_es, "w", encoding="utf-8") as fp:
            fp.write(note_es)

        # 2. Write FHIR R4 Bundle fixture if not present or update
        bundle_path = synthea_dir / f"{pid}.json"
        if not bundle_path.exists():
            bundle = build_fhir_bundle_for_patient(pdef)
            with open(bundle_path, "w", encoding="utf-8") as fp:
                json.dump(bundle, fp, indent=2, ensure_ascii=False)

    # Save gold_labels.json
    gold_path = fixtures_dir / "gold_labels.json"
    with open(gold_path, "w", encoding="utf-8") as fp:
        json.dump(gold_labels_all, fp, indent=2, ensure_ascii=False)

    print(f"[✓] Successfully generated and rendered {len(PATIENT_DEFINITIONS)} patient fixtures (25 Dev / 25 Test) across varied templates and noise profiles!")


if __name__ == "__main__":
    main()
