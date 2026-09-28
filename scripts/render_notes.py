#!/usr/bin/env python3
"""
scripts/render_notes.py

Renders realistic synthetic clinical notes in SOAP format (English and Spanish)
from Synthea FHIR R4 JSON patient bundles, preserving the source Conditions,
MedicationRequests, AllergyIntolerances, and Observations as gold labels.
"""

import json
from pathlib import Path
from typing import Any, Dict


def extract_patient_info(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Extract patient demographics from FHIR bundle."""
    patient = None
    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        if res.get("resourceType") == "Patient":
            patient = res
            break
    if not patient:
        return {"name": "Unknown Patient", "gender": "unknown", "birthDate": "unknown"}

    names = patient.get("name", [{}])
    given = " ".join(names[0].get("given", [""]))
    family = names[0].get("family", "")
    full_name = f"{given} {family}".strip()
    return {
        "name": full_name or "Anonymous",
        "gender": patient.get("gender", "unknown"),
        "birthDate": patient.get("birthDate", "unknown"),
    }


def extract_gold_labels(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured gold labels from Synthea FHIR R4 bundle."""
    conditions = []
    medications = []
    allergies = []
    vitals = {}

    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        rtype = res.get("resourceType")

        if rtype == "Condition":
            codings = res.get("code", {}).get("coding", [])
            snomed_code = None
            icd_code = None
            display = res.get("code", {}).get("text", "")
            for c in codings:
                sys = c.get("system", "")
                if "snomed" in sys:
                    snomed_code = c.get("code")
                    display = display or c.get("display")
                elif "icd-10" in sys:
                    icd_code = c.get("code")
            conditions.append({
                "display": display,
                "snomed": snomed_code,
                "icd10": icd_code,
            })

        elif rtype in ("MedicationRequest", "MedicationStatement"):
            codings = res.get("medicationCodeableConcept", {}).get("coding", [])
            rxnorm_code = None
            display = res.get("medicationCodeableConcept", {}).get("text", "")
            for c in codings:
                if "rxnorm" in c.get("system", ""):
                    rxnorm_code = c.get("code")
                    display = display or c.get("display")
            medications.append({
                "display": display,
                "rxnorm": rxnorm_code,
            })

        elif rtype == "AllergyIntolerance":
            codings = res.get("code", {}).get("coding", [])
            snomed_code = None
            display = res.get("code", {}).get("text", "")
            for c in codings:
                if "snomed" in c.get("system", ""):
                    snomed_code = c.get("code")
                    display = display or c.get("display")
            category = res.get("category", ["medication"])
            allergies.append({
                "display": display,
                "snomed": snomed_code,
                "category": category[0] if category else "other",
            })

        elif rtype == "Observation":
            code_obj = res.get("code", {})
            codings = code_obj.get("coding", [])
            loinc_code = codings[0].get("code") if codings else ""

            # Check for BP components
            components = res.get("component", [])
            if components:
                for comp in components:
                    comp_loinc = comp.get("code", {}).get("coding", [{}])[0].get("code")
                    val = comp.get("valueQuantity", {}).get("value")
                    unit = comp.get("valueQuantity", {}).get("unit", "mmHg")
                    if comp_loinc == "8480-6":
                        vitals["systolic_bp"] = {"value": val, "unit": unit, "loinc": "8480-6"}
                    elif comp_loinc == "8462-4":
                        vitals["diastolic_bp"] = {"value": val, "unit": unit, "loinc": "8462-4"}
            else:
                val_q = res.get("valueQuantity", {})
                val = val_q.get("value")
                unit = val_q.get("unit", "")
                if loinc_code == "8867-4":
                    vitals["heart_rate"] = {"value": val, "unit": unit or "/min", "loinc": "8867-4"}
                elif loinc_code == "9279-1":
                    vitals["respiratory_rate"] = {"value": val, "unit": unit or "/min", "loinc": "9279-1"}
                elif loinc_code == "8310-5":
                    vitals["body_temperature"] = {"value": val, "unit": unit or "[degF]", "loinc": "8310-5"}
                elif loinc_code in ("59408-5", "2708-6"):
                    vitals["oxygen_saturation"] = {"value": val, "unit": unit or "%", "loinc": "59408-5"}
                elif loinc_code == "39156-5":
                    vitals["bmi"] = {"value": val, "unit": unit or "kg/m2", "loinc": "39156-5"}

    return {
        "conditions": conditions,
        "medications": medications,
        "allergies": allergies,
        "vitals": vitals,
    }


def render_soap_note_en(patient: Dict[str, Any], gold: Dict[str, Any]) -> str:
    """Render a realistic English SOAP clinical note."""
    name = patient.get("name", "Unknown")
    gender = patient.get("gender", "unspecified")
    dob = patient.get("birthDate", "unspecified")

    cond_names = [c["display"] for c in gold["conditions"]]
    med_names = [m["display"] for m in gold["medications"]]
    allergy_names = [a["display"] for a in gold["allergies"]]

    vitals = gold["vitals"]
    v_parts = []
    if "systolic_bp" in vitals and "diastolic_bp" in vitals:
        v_parts.append(f"Blood Pressure: {vitals['systolic_bp']['value']}/{vitals['diastolic_bp']['value']} mmHg")
    if "heart_rate" in vitals:
        v_parts.append(f"Heart Rate: {vitals['heart_rate']['value']} bpm")
    if "respiratory_rate" in vitals:
        v_parts.append(f"Respiratory Rate: {vitals['respiratory_rate']['value']} breaths/min")
    if "body_temperature" in vitals:
        v_parts.append(f"Temperature: {vitals['body_temperature']['value']} F")
    if "oxygen_saturation" in vitals:
        v_parts.append(f"SpO2: {vitals['oxygen_saturation']['value']}% on room air")
    if "bmi" in vitals:
        v_parts.append(f"BMI: {vitals['bmi']['value']} kg/m2")

    vitals_text = "\n".join(f"- {p}" for p in v_parts) if v_parts else "- Vitals deferred."

    cond_text = "\n".join(f"- {c}" for c in cond_names) if cond_names else "- None reported."
    med_text = "\n".join(f"- {m}" for m in med_names) if med_names else "- No active prescription medications."
    all_text = "\n".join(f"- {a}" for a in allergy_names) if allergy_names else "- No known drug allergies (NKDA)."

    note = f"""CLINICAL ENCOUNTER NOTE (SOAP)
Date: 2024-03-15
Patient Name: {name}
DOB: {dob} | Gender: {gender.capitalize()}
Encounter Type: Outpatient Ambulatory Visit

SUBJECTIVE:
Chief Complaint: Follow-up and routine chronic disease management.
History of Present Illness (HPI):
The patient is a {dob}-born {gender} presenting for a scheduled outpatient evaluation. Patient reports general stability over recent weeks. Adherence to prescribed pharmacotherapy is reported as regular without severe side effects.

Past Medical History (PMH):
{cond_text}

Current Medications:
{med_text}

Allergies:
{all_text}

OBJECTIVE:
Physical Examination:
Well-developed, well-nourished, alert and oriented x4. No acute respiratory distress. Heart sounds regular rate and rhythm, normal S1/S2, no murmurs. Lungs clear to auscultation bilaterally. Abdomen soft, non-tender.

Vital Signs:
{vitals_text}

ASSESSMENT & PLAN:
Assessment:
{cond_text}

Plan:
1. Continue current medication regimen as tolerated.
2. Maintain lifestyle and dietary modifications.
3. Routine laboratory tests ordered.
4. Follow-up clinic appointment in 3 to 6 months or sooner if acute symptoms develop.
"""
    return note.strip()


def render_soap_note_es(patient: Dict[str, Any], gold: Dict[str, Any]) -> str:
    """Render a realistic Spanish SOAP clinical note."""
    name = patient.get("name", "Desconocido")
    gender = "Masculino" if patient.get("gender") == "male" else ("Femenino" if patient.get("gender") == "female" else "No especificado")
    dob = patient.get("birthDate", "desconocida")

    # Spanish translation dictionaries for realistic rendering
    es_cond = {
        "Essential hypertension": "Hipertensión arterial esencial",
        "Type 2 diabetes mellitus": "Diabetes mellitus tipo 2",
        "Asthma": "Asma bronquial",
        "COVID-19": "Infección por COVID-19",
        "Acute bronchitis": "Bronquitis aguda",
        "Hyperlipidemia": "Hiperlipidemia mixta",
        "Coronary artery disease": "Cardiopatía isquémica coronaria",
        "Chronic obstructive pulmonary disease": "Enfermedad pulmonar obstructiva crónica (EPOC)",
        "Gastroesophageal reflux disease": "Enfermedad por reflujo gastroesofágico (ERGE)",
    }
    es_med = {
        "Lisinopril 10 MG Oral Tablet": "Lisinopril 10 mg comprimidos vía oral",
        "Metformin hydrochloride 500 MG Oral Tablet": "Metformina 500 mg comprimidos vía oral",
        "Albuterol 90 MCG/ACTUAT Inhaler": "Albuterol / Salbutamol inhalador 90 mcg",
        "Fluticasone propionate": "Fluticasona spray nasal",
        "Azithromycin 250 MG Oral Tablet": "Azitromicina 250 mg comprimidos",
        "Atorvastatin 20 MG Oral Tablet": "Atorvastatina 20 mg vía oral",
        "Aspirin 81 MG Oral Tablet": "Aspirina 81 mg vía oral",
        "Omeprazole 20 MG Delayed Release Oral Capsule": "Omeprazol 20 mg cápsulas",
        "Amlodipine 5 MG Oral Tablet": "Amlodipino 5 mg comprimidos",
    }
    es_all = {
        "Allergy to penicillin": "Alergia a la penicilina",
        "Allergy to peanut": "Alergia al maní (cacahuate)",
        "Allergy to sulfonamide": "Alergia a las sulfonamidas (sulfas)",
        "Allergy to codeine": "Alergia a la codeína",
        "Latex allergy": "Alergia al látex",
    }

    cond_names = [es_cond.get(c["display"], c["display"]) for c in gold["conditions"]]
    med_names = [es_med.get(m["display"], m["display"]) for m in gold["medications"]]
    allergy_names = [es_all.get(a["display"], a["display"]) for a in gold["allergies"]]

    vitals = gold["vitals"]
    v_parts = []
    if "systolic_bp" in vitals and "diastolic_bp" in vitals:
        v_parts.append(f"Presión Arterial: {vitals['systolic_bp']['value']}/{vitals['diastolic_bp']['value']} mmHg")
    if "heart_rate" in vitals:
        v_parts.append(f"Frecuencia Cardíaca: {vitals['heart_rate']['value']} lpm")
    if "respiratory_rate" in vitals:
        v_parts.append(f"Frecuencia Respiratoria: {vitals['respiratory_rate']['value']} respiraciones/minuto")
    if "body_temperature" in vitals:
        temp_f = vitals['body_temperature']['value']
        # Also provide Celsius equivalent or keep F
        temp_c = round((temp_f - 32) * 5 / 9, 1)
        v_parts.append(f"Temperatura: {temp_f} °F ({temp_c} °C)")
    if "oxygen_saturation" in vitals:
        v_parts.append(f"Saturación de Oxígeno (SpO2): {vitals['oxygen_saturation']['value']}% aire ambiente")
    if "bmi" in vitals:
        v_parts.append(f"Índice de Masa Corporal (IMC): {vitals['bmi']['value']} kg/m2")

    vitals_text = "\n".join(f"- {p}" for p in v_parts) if v_parts else "- Signos vitales no registrados."
    cond_text = "\n".join(f"- {c}" for c in cond_names) if cond_names else "- Sin antecedentes patológicos conocidos."
    med_text = "\n".join(f"- {m}" for m in med_names) if med_names else "- Sin medicación habitual."
    all_text = "\n".join(f"- {a}" for a in allergy_names) if allergy_names else "- Sin alergias medicamentosas conocidas (NKDA)."

    note = f"""NOTA DE EVOLUCIÓN CLÍNICA (SOAP)
Fecha: 2024-03-15
Nombre del Paciente: {name}
Fecha de Nacimiento: {dob} | Género: {gender}
Tipo de Consulta: Consulta Ambulatoria Programada

SUBJETIVO:
Motivo de consulta: Control evolutivo y seguimiento de patologías crónicas.
Enfermedad Actual:
Paciente nacido el {dob}, acude a consulta programada para control. Refiere encontrarse estable, sin dolor torácico, disnea paroxística ni cambios en su sintomatología basal. Manifiesta buena adherencia a los tratamientos prescritos.

Antecedentes Médicos Personales:
{cond_text}

Medicación Actual:
{med_text}

Alergias:
{all_text}

OBJETIVO:
Examen Físico:
Paciente orientado en tiempo, espacio y persona. Buen estado general, hidratado, normocoloreado. Auscultación cardíaca: ruidos cardíacos rítmicos sin soplos. Auscultación pulmonar: murmullo vesicular conservado sin ruidos sobreagregados. Abdomen blando, depresible, no doloroso a la palpación.

Signos Vitales:
{vitals_text}

EVALUACIÓN Y PLAN:
Diagnósticos / Impresión Clínica:
{cond_text}

Plan Terapéutico:
1. Continuar con el esquema farmacológico indicado.
2. Mantener hábitos dietéticos cardiosaludables y actividad física regular.
3. Solicitud de analítica de control.
4. Próxima revisión en consulta externa en 3 a 6 meses.
"""
    return note.strip()


def main():
    root = Path(__file__).resolve().parent.parent
    synthea_dir = root / "data" / "fixtures" / "synthea"
    notes_en_dir = root / "data" / "fixtures" / "notes" / "en"
    notes_es_dir = root / "data" / "fixtures" / "notes" / "es"
    notes_en_dir.mkdir(parents=True, exist_ok=True)
    notes_es_dir.mkdir(parents=True, exist_ok=True)

    gold_labels_all = {}

    fixture_files = sorted(synthea_dir.glob("*.json"))
    for f in fixture_files:
        with open(f, "r", encoding="utf-8") as fp:
            bundle = json.load(fp)

        pid = f.stem
        pat = extract_patient_info(bundle)
        gold = extract_gold_labels(bundle)
        gold_labels_all[pid] = {
            "patient": pat,
            "gold": gold,
        }

        note_en = render_soap_note_en(pat, gold)
        note_es = render_soap_note_es(pat, gold)

        out_en = notes_en_dir / f"{pid}_soap.txt"
        out_es = notes_es_dir / f"{pid}_soap.txt"

        with open(out_en, "w", encoding="utf-8") as fp:
            fp.write(note_en)
        with open(out_es, "w", encoding="utf-8") as fp:
            fp.write(note_es)

        print(f"Rendered EN & ES notes for {pid}")

    gold_path = root / "data" / "fixtures" / "gold_labels.json"
    with open(gold_path, "w", encoding="utf-8") as fp:
        json.dump(gold_labels_all, fp, indent=2, ensure_ascii=False)
    print(f"Saved gold labels to {gold_path}")


if __name__ == "__main__":
    main()
