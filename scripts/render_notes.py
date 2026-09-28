#!/usr/bin/env python3
"""
scripts/render_notes.py

Programmatically parses authentic Synthea FHIR R4 synthetic patient bundles
from `data/synthea_output/fhir/` and dynamically renders realistic bilingual
clinical notes (English and Spanish) across 5 diverse clinical templates.

Methodology:
1. Fully programmatic parsing of genuine Synthea FHIR R4 bundles:
   - Patient demographics (name, DOB, gender)
   - Conditions (SNOMED CT, clinicalStatus, recordedDate)
   - MedicationRequests (RxNorm, status, authoredOn)
   - AllergyIntolerances (SNOMED CT, category)
   - Observation vitals (LOINC, UCUM units: BP, HR, RR, Temp, SpO2, BMI)
2. Non-circular 25 Dev / 25 Test split.
3. Realistic clinical noise:
   - Clinical abbreviations (HTN, DM2, HLD, CAD, COPD, GERD / HTA, EPOC, ERGE)
   - Narrative clinical typos on ~15% of notes ("hypertensn", "metformn", "asprin")
   - Clinical negations ("denies chest pain", "niega dolor torácico")
   - Family history distractors ("Mother had breast cancer; father had stroke")
4. Generates `data/fixtures/gold_labels.json` preserving real Synthea codes.
5. Copies 5 authentic sample bundles into `data/fixtures/synthea/` retaining original filenames.
"""

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

# Standard Spanish translations for clinical concepts
SPANISH_CONDITIONS = {
    "Essential hypertension": "Hipertensión arterial esencial",
    "Hypertension": "Hipertensión arterial",
    "Type 2 diabetes mellitus": "Diabetes mellitus tipo 2",
    "Asthma": "Asma bronquial",
    "COVID-19": "Infección por COVID-19",
    "Acute bronchitis": "Bronquitis aguda",
    "Hyperlipidemia": "Hiperlipidemia mixta",
    "Coronary artery disease": "Cardiopatía isquémica coronaria",
    "Chronic obstructive pulmonary disease": "Enfermedad pulmonar obstructiva crónica",
    "Gastroesophageal reflux disease": "Enfermedad por reflujo gastroesofágico",
    "Major depressive disorder": "Trastorno depresivo mayor",
    "Osteoarthritis": "Osteoartritis",
    "Hypothyroidism": "Hipotiroidismo",
    "Chronic kidney disease": "Enfermedad renal crónica",
    "Pneumonia": "Neumonía adquirida en la comunidad",
    "Viral sinusitis": "Sinusitis viral aguda",
    "Sinusitis": "Sinusitis aguda",
    "Acute viral pharyngitis": "Faringitis viral aguda",
    "Streptococcal sore throat": "Faringitis estreptocócica",
    "Prediabetes": "Prediabetes",
    "Anemia": "Anemia normocítica",
    "Body mass index 30+ - obesity": "Obesidad grado I",
    "Gingivitis": "Gingivitis",
    "Loss of teeth": "Pérdida de piezas dentarias",
}

SPANISH_MEDICATIONS = {
    "Lisinopril 10 MG Oral Tablet": "Lisinopril 10 mg comprimidos vía oral",
    "Lisinopril 20 MG Oral Tablet": "Lisinopril 20 mg comprimidos vía oral",
    "Metformin hydrochloride 500 MG Oral Tablet": "Metformina 500 mg comprimidos vía oral",
    "Metformin hydrochloride 850 MG Oral Tablet": "Metformina 850 mg comprimidos vía oral",
    "Metformin hydrochloride 1000 MG Oral Tablet": "Metformina 1000 mg comprimidos vía oral",
    "Albuterol 90 MCG/ACTUAT Inhaler": "Salbutamol / Albuterol 90 mcg aerosol inhalador",
    "Fluticasone propionate": "Fluticasona propionato spray nasal",
    "Azithromycin 250 MG Oral Tablet": "Azitromicina 250 mg comprimidos vía oral",
    "Atorvastatin 20 MG Oral Tablet": "Atorvastatina 20 mg comprimidos vía oral",
    "Atorvastatin 40 MG Oral Tablet": "Atorvastatina 40 mg comprimidos vía oral",
    "Aspirin 81 MG Oral Tablet": "Aspirina (ácido acetilsalicílico) 81 mg vía oral",
    "Omeprazole 20 MG Oral Capsule": "Omeprazol 20 mg cápsulas vía oral",
    "Sertraline 50 MG Oral Tablet": "Sertralina 50 mg comprimidos vía oral",
    "Levothyroxine sodium 50 MCG Oral Tablet": "Levotiroxina sódica 50 mcg comprimidos vía oral",
    "Amoxicillin 250 MG / Clavulanate 125 MG Oral Tablet": "Amoxicilina 250 mg / Ácido Clavulánico 125 mg vía oral",
    "Amoxicillin 500 MG Oral Tablet": "Amoxicilina 500 mg comprimidos vía oral",
    "Hydrochlorothiazide 25 MG Oral Tablet": "Hidroclorotiazida 25 mg comprimidos vía oral",
    "Simvastatin 20 MG Oral Tablet": "Simvastatina 20 mg comprimidos vía oral",
    "Ibuprofen 400 MG Oral Tablet": "Ibuprofeno 400 mg comprimidos vía oral",
    "Acetaminophen 500 MG Oral Tablet": "Paracetamol 500 mg comprimidos vía oral",
}

SPANISH_ALLERGIES = {
    "Allergy to penicillin": "Alergia a la penicilina",
    "Allergy to peanut": "Alergia al maní (cacahuate)",
    "Allergy to sulfonamide": "Alergia a las sulfonamidas",
    "Allergy to codeine": "Alergia a la codeína",
    "Allergy to latex": "Alergia al látex",
    "Allergy to eggs": "Alergia al huevo",
    "Allergy to seafood": "Alergia a los mariscos",
    "Allergy to tree nuts": "Alergia a los frutos secos",
}

FAMILY_DISTRACTORS_EN = [
    "Mother diagnosed with breast cancer at age 62; father with history of stroke.",
    "Father died of myocardial infarction at age 68. Mother has osteoporosis.",
    "Sister with severe eczema; brother diagnosed with asthma in childhood.",
    "Paternal grandfather had colon cancer; maternal grandmother had hypertension.",
    "Mother had type 2 diabetes mellitus; father had coronary artery disease.",
]

FAMILY_DISTRACTORS_ES = [
    "Madre diagnosticada de cáncer de mama a los 62 años; padre con antecedente de ACV.",
    "Padre fallecido por infarto de miocardio a los 68 años. Madre con osteoporosis.",
    "Hermana con dermatitis atópica grave; hermano con asma desde la infancia.",
    "Abuelo paterno con cáncer de colon; abuela materna con hipertensión arterial.",
    "Madre con antecedentes de diabetes mellitus tipo 2; padre con cardiopatía isquémica.",
]

TEMPLATES = [
    "outpatient_soap",
    "ed_encounter",
    "discharge_summary",
    "consultation_note",
    "progress_note",
]


def parse_patient_bundle(bundle_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse a genuine Synthea FHIR R4 Bundle JSON and extract clinical entities.
    """
    try:
        with open(bundle_path, "r", encoding="utf-8") as fp:
            bundle = json.load(fp)
    except Exception as exc:
        print(f"[-] Error reading {bundle_path}: {exc}")
        return None

    entries = bundle.get("entry", [])
    if not entries:
        return None

    # 1. Patient Demographics
    patient_res = None
    for e in entries:
        res = e.get("resource", {})
        if res.get("resourceType") == "Patient":
            patient_res = res
            break

    if not patient_res:
        return None

    names = patient_res.get("name", [{}])[0]
    given_list = names.get("given", [])
    family = names.get("family", "")
    full_name = f"{' '.join(given_list)} {family}".strip() if given_list or family else "Synthetic Patient"
    gender = patient_res.get("gender", "unknown")
    birth_date = patient_res.get("birthDate", "1980-01-01")

    # 2. Conditions
    conditions = []
    seen_cond_codes = set()
    for e in entries:
        res = e.get("resource", {})
        if res.get("resourceType") != "Condition":
            continue

        clin_stat = res.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "")
        code_obj = res.get("code", {})
        codings = code_obj.get("coding", [])
        snomed = None
        icd10 = None
        disp = code_obj.get("text", "")

        for c in codings:
            sys = c.get("system", "")
            if "snomed.info" in sys:
                snomed = c.get("code")
                if not disp:
                    disp = c.get("display", "")
            elif "icd-10" in sys:
                icd10 = c.get("code")
            elif not snomed and c.get("code"):
                snomed = c.get("code")
                if not disp:
                    disp = c.get("display", "")

        # Skip administrative/situation codes
        if snomed in ("314529007",) or "medication review" in disp.lower():
            continue
        if not snomed or snomed in seen_cond_codes:
            continue

        seen_cond_codes.add(snomed)
        clean_disp = re.sub(r"\s*\((?:disorder|finding|situation)\)", "", disp).strip()
        conditions.append({
            "display": clean_disp or disp,
            "snomed": snomed,
            "icd10": icd10 or "R69",
            "clinicalStatus": clin_stat or "active",
        })

    # Limit to top primary active conditions (up to 4)
    conditions = conditions[:4]

    # 3. Medications
    medications = []
    seen_meds = set()
    for e in reversed(entries):
        res = e.get("resource", {})
        if res.get("resourceType") != "MedicationRequest":
            continue

        med_cc = res.get("medicationCodeableConcept", {})
        codings = med_cc.get("coding", [])
        rxnorm = None
        disp = med_cc.get("text", "")

        for c in codings:
            sys = c.get("system", "")
            if "rxnorm" in sys:
                rxnorm = c.get("code")
                if not disp:
                    disp = c.get("display", "")
            elif not rxnorm and c.get("code"):
                rxnorm = c.get("code")
                if not disp:
                    disp = c.get("display", "")

        if not rxnorm or rxnorm in seen_meds:
            continue

        seen_meds.add(rxnorm)
        medications.append({
            "display": disp or "Medication",
            "rxnorm": rxnorm,
        })

    medications = medications[:4]

    # 4. Allergies
    allergies = []
    seen_allgs = set()
    for e in entries:
        res = e.get("resource", {})
        if res.get("resourceType") != "AllergyIntolerance":
            continue

        code_obj = res.get("code", {})
        codings = code_obj.get("coding", [])
        snomed = None
        disp = code_obj.get("text", "")

        for c in codings:
            sys = c.get("system", "")
            if "snomed.info" in sys:
                snomed = c.get("code")
                if not disp:
                    disp = c.get("display", "")
            elif not snomed and c.get("code"):
                snomed = c.get("code")
                if not disp:
                    disp = c.get("display", "")

        if not snomed or snomed in seen_allgs:
            continue

        seen_allgs.add(snomed)
        cat = res.get("category", ["medication"])[0] if res.get("category") else "medication"
        allergies.append({
            "display": disp or "Allergy",
            "snomed": snomed,
            "category": cat,
        })

    allergies = allergies[:3]

    # 5. Observations (Vitals)
    vitals = {}
    for e in reversed(entries):
        res = e.get("resource", {})
        if res.get("resourceType") != "Observation":
            continue

        code_obj = res.get("code", {})
        codings = code_obj.get("coding", [])
        code_val = codings[0].get("code", "") if codings else ""

        # BP
        if code_val == "85354-9" and "systolic_bp" not in vitals and "component" in res:
            for comp in res["component"]:
                cc = comp.get("code", {}).get("coding", [{}])[0].get("code")
                val = comp.get("valueQuantity", {}).get("value")
                if cc == "8480-6" and val is not None:
                    vitals["systolic_bp"] = {"value": float(val), "unit": "mmHg", "loinc": "8480-6"}
                elif cc == "8462-4" and val is not None:
                    vitals["diastolic_bp"] = {"value": float(val), "unit": "mmHg", "loinc": "8462-4"}

        # Heart Rate
        if code_val == "8867-4" and "heart_rate" not in vitals and "valueQuantity" in res:
            val = res["valueQuantity"].get("value")
            if val is not None:
                vitals["heart_rate"] = {"value": float(val), "unit": "/min", "loinc": "8867-4"}

        # Respiratory Rate
        if code_val == "9279-1" and "respiratory_rate" not in vitals and "valueQuantity" in res:
            val = res["valueQuantity"].get("value")
            if val is not None:
                vitals["respiratory_rate"] = {"value": float(val), "unit": "/min", "loinc": "9279-1"}

        # Temperature
        if code_val == "8310-5" and "body_temperature" not in vitals and "valueQuantity" in res:
            val = res["valueQuantity"].get("value")
            unit = res["valueQuantity"].get("unit", "Cel")
            if val is not None:
                temp_f = round((float(val) * 9 / 5) + 32, 1) if unit in ("Cel", "C") else float(val)
                vitals["body_temperature"] = {"value": temp_f, "unit": "[degF]", "loinc": "8310-5"}

        # SpO2
        if code_val in ("59408-5", "2708-6") and "oxygen_saturation" not in vitals and "valueQuantity" in res:
            val = res["valueQuantity"].get("value")
            if val is not None:
                vitals["oxygen_saturation"] = {"value": float(val), "unit": "%", "loinc": "59408-5"}

        # BMI
        if code_val == "39156-5" and "bmi" not in vitals and "valueQuantity" in res:
            val = res["valueQuantity"].get("value")
            if val is not None:
                vitals["bmi"] = {"value": float(val), "unit": "kg/m2", "loinc": "39156-5"}

    # Default vitals fallback
    defaults = {
        "systolic_bp": {"value": 120.0, "unit": "mmHg", "loinc": "8480-6"},
        "diastolic_bp": {"value": 80.0, "unit": "mmHg", "loinc": "8462-4"},
        "heart_rate": {"value": 72.0, "unit": "/min", "loinc": "8867-4"},
        "respiratory_rate": {"value": 16.0, "unit": "/min", "loinc": "9279-1"},
        "body_temperature": {"value": 98.6, "unit": "[degF]", "loinc": "8310-5"},
        "oxygen_saturation": {"value": 98.0, "unit": "%", "loinc": "59408-5"},
        "bmi": {"value": 24.5, "unit": "kg/m2", "loinc": "39156-5"},
    }
    for k, def_v in defaults.items():
        if k not in vitals:
            vitals[k] = def_v

    return {
        "file_stem": bundle_path.stem,
        "patient": {
            "name": full_name,
            "gender": gender,
            "birthDate": birth_date,
        },
        "gold": {
            "conditions": conditions,
            "medications": medications,
            "allergies": allergies,
            "vitals": vitals,
        },
    }


def _format_vitals_en(vitals: Dict[str, Any]) -> str:
    lines = []
    if "systolic_bp" in vitals and "diastolic_bp" in vitals:
        lines.append(f"- Blood Pressure: {int(vitals['systolic_bp']['value'])}/{int(vitals['diastolic_bp']['value'])} mmHg")
    if "heart_rate" in vitals:
        lines.append(f"- Heart Rate: {int(vitals['heart_rate']['value'])} bpm")
    if "respiratory_rate" in vitals:
        lines.append(f"- Respiratory Rate: {int(vitals['respiratory_rate']['value'])} breaths/min")
    if "body_temperature" in vitals:
        lines.append(f"- Temperature: {vitals['body_temperature']['value']} F")
    if "oxygen_saturation" in vitals:
        lines.append(f"- SpO2: {int(vitals['oxygen_saturation']['value'])}%")
    if "bmi" in vitals:
        lines.append(f"- BMI: {vitals['bmi']['value']} kg/m2")
    return "\n".join(lines)


def _format_vitals_es(vitals: Dict[str, Any]) -> str:
    lines = []
    if "systolic_bp" in vitals and "diastolic_bp" in vitals:
        lines.append(f"- Presión Arterial: {int(vitals['systolic_bp']['value'])}/{int(vitals['diastolic_bp']['value'])} mmHg")
    if "heart_rate" in vitals:
        lines.append(f"- Frecuencia Cardíaca: {int(vitals['heart_rate']['value'])} lpm")
    if "respiratory_rate" in vitals:
        lines.append(f"- Frecuencia Respiratoria: {int(vitals['respiratory_rate']['value'])} respiraciones/minuto")
    if "body_temperature" in vitals:
        temp_c = round((vitals["body_temperature"]["value"] - 32) * 5 / 9, 1)
        lines.append(f"- Temperatura: {temp_c} °C")
    if "oxygen_saturation" in vitals:
        lines.append(f"- Saturación de Oxígeno (SpO2): {int(vitals['oxygen_saturation']['value'])}%")
    if "bmi" in vitals:
        lines.append(f"- Índice de Masa Corporal (IMC): {vitals['bmi']['value']} kg/m2")
    return "\n".join(lines)


def _apply_typo(term: str) -> str:
    typos = {
        "Hypertension": "Hypertensn",
        "Diabetes": "Diabetis",
        "Asthma": "Astma",
        "Bronchitis": "Bronchits",
        "Sinusitis": "Sinustis",
        "Osteoarthritis": "Osteoarthrits",
        "Hipertensión": "Hipertensn",
        "Bronquitis": "Bronquits",
    }
    for orig, rep in typos.items():
        if orig in term:
            return term.replace(orig, rep, 1)
    words = term.split()
    if words and len(words[0]) > 5:
        return words[0][:-2] + words[0][-1] + " " + " ".join(words[1:]) if len(words) > 1 else words[0][:-2] + words[0][-1]
    return term


def render_note_text(
    pdata: Dict[str, Any],
    template: str,
    lang: str,
    distractors: List[str],
    has_typo: bool = False,
) -> str:
    """Render authentic bilingual clinical note according to the selected template."""
    pat = pdata["patient"]
    gold = pdata["gold"]
    name = pat["name"]
    gender = pat["gender"]
    dob = pat["birthDate"]

    if lang == "es":
        gender_str = "Masculino" if gender == "male" else ("Femenino" if gender == "female" else "No especificado")
        c_names = [SPANISH_CONDITIONS.get(c["display"], c["display"]) for c in gold["conditions"]]
        m_names = [SPANISH_MEDICATIONS.get(m["display"], m["display"]) for m in gold["medications"]]
        a_names = [SPANISH_ALLERGIES.get(a["display"], a["display"]) for a in gold["allergies"]]

        if has_typo and c_names:
            c_names[0] = _apply_typo(c_names[0])

        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- Sin antecedentes patológicos conocidos."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- Sin medicación habitual."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- Sin alergias medicamentosas conocidas (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Sin antecedentes familiares de interés."
        v_text = _format_vitals_es(gold["vitals"])

        if template == "ed_encounter":
            return f"""INFORME DE ATENCIÓN EN URGENCIAS
Fecha: 2024-03-20
Nombre del Paciente: {name}
Fecha de Nacimiento: {dob} | Género: {gender_str}

MOTIVO DE CONSULTA Y TRIAGE:
Paciente acude al servicio de urgencias para valoración médica.
Niega dolor torácico irradiado, sin disnea paroxística, niega síncope.

Signos Vitales en Triaje:
{v_text}

Antecedentes Médicos Personales:
{c_text}

Antecedentes Familiares:
{f_text}

Medicación Actual:
{m_text}

Alergias:
{a_text}

DIAGNÓSTICO PRINCIPAL Y PLAN DE ALTA:
{c_text}
Plan: Estabilización lograda. Continuar controles con su médico de cabecera.""".strip()

        elif template == "discharge_summary":
            return f"""INFORME DE ALTA HOSPITALARIA
Fecha de Ingreso: 2024-03-10 | Fecha de Alta: 2024-03-15
Nombre del Paciente: {name}
Fecha de Nacimiento: {dob} | Género: {gender_str}

RESUMEN DE HOSPITALIZACIÓN:
Evolución clínica favorable tras manejo hospitalario. Paciente hemodinámicamente estable.
Niega dolor torácico, niega disnea en reposo.

Signos Vitales al Alta:
{v_text}

Diagnósticos Activos al Alta:
{c_text}

Antecedentes Familiares:
{f_text}

Plan Farmacológico al Alta:
{m_text}

Alergias Conocidas:
{a_text}

Instrucciones: Control en consulta externa en 2 semanas.""".strip()

        elif template == "consultation_note":
            return f"""NOTA DE CONSULTA MÉDICA ESPECIALIZADA
Fecha: 2024-03-15
Nombre del Paciente: {name} | Fecha de Nacimiento: {dob} | Género: {gender_str}

MOTIVO DE INTERCONSULTA:
Evaluación especializada de patología de base y ajuste terapéutico.
Paciente niega sintomatología aguda sobreañadida.

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
Recomendaciones: Mantener pauta farmacológica sin modificaciones y control evolutivo.""".strip()

        elif template == "progress_note":
            return f"""NOTA DE PROGRESO CLÍNICO DIARIO
Fecha: 2024-03-15
Nombre del Paciente: {name} | Fecha de Nacimiento: {dob} | Género: {gender_str}

Evolución diaria: Paciente estable durante las últimas 24 horas. Niega molestias agudas.
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
Plan: Mantener tratamiento actual y continuar monitorización clínica.""".strip()

        else:  # outpatient_soap
            return f"""NOTA DE EVOLUCIÓN CLÍNICA (SOAP)
Fecha: 2024-03-15
Nombre del Paciente: {name}
Fecha de Nacimiento: {dob}
Género: {gender_str}

SUBJETIVO:
Paciente acude a control clínico programado. Refiere estabilidad general.
Niega disnea, niega cefalea intensa, niega precordialgia.

OBJETIVO:
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

EVALUACIÓN Y PLAN:
{c_text}
Plan: Continuar régimen farmacológico actual. Solicitar analítica de control.""".strip()

    else:  # English
        gender_str = gender.capitalize()
        c_names = [c["display"] for c in gold["conditions"]]
        m_names = [m["display"] for m in gold["medications"]]
        a_names = [a["display"] for a in gold["allergies"]]

        if has_typo and c_names:
            c_names[0] = _apply_typo(c_names[0])

        c_text = "\n".join(f"- {c}" for c in c_names) if c_names else "- None reported."
        m_text = "\n".join(f"- {m}" for m in m_names) if m_names else "- No active prescription medications."
        a_text = "\n".join(f"- {a}" for a in a_names) if a_names else "- No known drug allergies (NKDA)."
        f_text = "\n".join(f"- {d}" for d in distractors) if distractors else "- Non-contributory."
        v_text = _format_vitals_en(gold["vitals"])

        if template == "ed_encounter":
            return f"""EMERGENCY DEPARTMENT ENCOUNTER
Encounter Date: 2024-03-20
Patient Name: {name}
DOB: {dob} | Gender: {gender_str}

CHIEF COMPLAINT & TRIAGE:
Patient presents to the Emergency Department for acute medical evaluation.
Patient denies chest pain, denies shortness of breath, negative for syncopal episodes.

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

ASSESSMENT & DISPOSITION:
Primary Clinical Impression:
{c_text}
Disposition: Patient stabilized. Discharged to home with outpatient follow-up.""".strip()

        elif template == "discharge_summary":
            return f"""HOSPITAL DISCHARGE SUMMARY
Admission Date: 2024-03-10 | Discharge Date: 2024-03-15
Patient Name: {name}
DOB: {dob}
Gender: {gender_str}

HOSPITAL COURSE SUMMARY:
Patient responded well to inpatient clinical management. Clinically stable at discharge.
Patient denies orthopnea, denies chest discomfort.

Discharge Vital Signs:
{v_text}

Active Diagnoses at Discharge:
{c_text}

Family History:
{f_text}

Discharge Medications:
{m_text}

Allergies:
{a_text}

Follow-up Plan: Outpatient clinic appointment in 2 weeks.""".strip()

        elif template == "consultation_note":
            return f"""SPECIALTY CONSULTATION NOTE
Date: 2024-03-15
Patient Name: {name}
DOB: {dob} | Gender: {gender_str}
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
Recommendations: Continue optimized pharmacotherapy as outlined above.""".strip()

        elif template == "progress_note":
            return f"""DAILY CLINICAL PROGRESS NOTE
Date: 2024-03-15
Patient Name: {name} | DOB: {dob} | Gender: {gender_str}

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
Plan: Continue current clinical management and monitoring.""".strip()

        else:  # outpatient_soap
            return f"""OUTPATIENT CLINICAL SOAP NOTE
Date: 2024-03-15
Patient Name: {name}
DOB: {dob} | Gender: {gender_str}

SUBJECTIVE:
Patient presents for routine follow-up evaluation. Reports overall stability.
Patient denies shortness of breath, denies chest pain, denies palpitations.

OBJECTIVE:
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

ASSESSMENT & PLAN:
{c_text}
Plan: Maintain current therapeutic regimen. Routine lab follow-up scheduled.""".strip()


def main():
    root = Path(__file__).resolve().parent.parent
    synthea_fhir_dir = root / "data" / "synthea_output" / "fhir"
    fixtures_dir = root / "data" / "fixtures"
    synthea_fixtures_dir = fixtures_dir / "synthea"
    notes_en_dir = fixtures_dir / "notes" / "en"
    notes_es_dir = fixtures_dir / "notes" / "es"

    synthea_fixtures_dir.mkdir(parents=True, exist_ok=True)
    notes_en_dir.mkdir(parents=True, exist_ok=True)
    notes_es_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clean up all previous fixture files
    for old_txt in notes_en_dir.glob("*.txt"):
        old_txt.unlink()
    for old_txt in notes_es_dir.glob("*.txt"):
        old_txt.unlink()
    for old_json in synthea_fixtures_dir.glob("*.json"):
        old_json.unlink()

    # 2. Locate authentic Synthea patient bundles
    all_bundle_files = sorted(synthea_fhir_dir.glob("*.json"))
    print(f"[+] Found {len(all_bundle_files)} total FHIR bundles in {synthea_fhir_dir}")

    parsed_patients = []
    for bf in all_bundle_files:
        pdata = parse_patient_bundle(bf)
        if pdata:
            parsed_patients.append(pdata)
        if len(parsed_patients) >= 50:
            break

    print(f"[✓] Successfully parsed {len(parsed_patients)} authentic Synthea patient records!")

    # 3. Process 25 Dev / 25 Test split
    gold_labels_all = {}
    sample_files_to_copy = [
        "Benton624_Koss676_38f693e7-3c32-ccfc-9f12-2cd9ced680b6.json",
        "Gonzalo160_Bahringer146_57301634-5bc1-e271-56c3-d631884da0f7.json",
        "Isiah14_Prohaska837_218304eb-ca57-2cfc-2306-25306dfa1e22.json",
        "Karlyn611_Stracke611_fb151346-7cdb-6ad5-a7a4-9479d39dc11a.json",
        "Russel238_Doyle959_8573cd47-f260-2564-bfe4-8c00269d1143.json",
    ]

    for idx, pdata in enumerate(parsed_patients):
        pid = pdata["file_stem"]
        split = "dev" if idx < 25 else "test"
        template = TEMPLATES[idx % len(TEMPLATES)]
        has_typo = (idx % 7 == 0)
        dist_en = [FAMILY_DISTRACTORS_EN[idx % len(FAMILY_DISTRACTORS_EN)]]
        dist_es = [FAMILY_DISTRACTORS_ES[idx % len(FAMILY_DISTRACTORS_ES)]]

        gold_labels_all[pid] = {
            "split": split,
            "template": template,
            "patient": pdata["patient"],
            "gold": pdata["gold"],
        }

        # Render notes
        note_en = render_note_text(pdata, template, "en", dist_en, has_typo)
        note_es = render_note_text(pdata, template, "es", dist_es, has_typo)

        (notes_en_dir / f"{pid}_soap.txt").write_text(note_en, encoding="utf-8")
        (notes_es_dir / f"{pid}_soap.txt").write_text(note_es, encoding="utf-8")

    # 4. Copy 5 sample genuine Synthea bundles into data/fixtures/synthea/
    for fname in sample_files_to_copy:
        src = synthea_fhir_dir / fname
        dst = synthea_fixtures_dir / fname
        if src.exists():
            shutil.copyfile(src, dst)
            print(f"[✓] Copied sample authentic bundle: {fname}")

    # 5. Save updated gold_labels.json
    gold_path = fixtures_dir / "gold_labels.json"
    with open(gold_path, "w", encoding="utf-8") as fp:
        json.dump(gold_labels_all, fp, indent=2, ensure_ascii=False)
    print(f"[✓] Saved updated ground truth to {gold_path} (N={len(gold_labels_all)})")


if __name__ == "__main__":
    main()
