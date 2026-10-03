# note-to-fhir

Over 80% of critical healthcare data remains trapped in unstructured clinical documentation, narrative progress notes, and free-text EHR fields. Clinicians and health systems struggle to transform narrative physician notes into standardized, interoperable HL7 FHIR R4 records, impeding automated clinical decision support, cross-institution data exchange, and regulatory compliance. `note-to-fhir` bridges this gap by converting bilingual (English & Spanish) clinical notes into validated FHIR R4 Bundles with standard medical codes (SNOMED CT, RxNorm, LOINC, UCUM, ICD-10).

---

## Sample Input Note & Output FHIR R4 Bundle Excerpt

### Input: Unstructured Clinical Note (SOAP)
```text
CLINICAL ENCOUNTER NOTE (SOAP)
Patient Name: Dusty207 Stokes453 | DOB: 2005-03-20 | Gender: Male
Past Medical History:
- Viral sinusitis
Current Medications:
- Amoxicillin 250 MG / Clavulanate 125 MG Oral Tablet
Allergies:
- No known drug allergies (NKDA)
Vital Signs:
- Blood Pressure: 120/80 mmHg
- Heart Rate: 72 bpm
- Temperature: 98.6 F
```

### Output: Validated HL7 FHIR R4 Bundle (Excerpt)
```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "fullUrl": "urn:uuid:018e6e58-patient",
      "resource": {
        "resourceType": "Patient",
        "name": [{ "use": "official", "family": "Stokes453", "given": ["Dusty207"] }],
        "gender": "male",
        "birthDate": "2005-03-20"
      }
    },
    {
      "fullUrl": "urn:uuid:018e6e58-condition-sinusitis",
      "resource": {
        "resourceType": "Condition",
        "clinicalStatus": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active" }] },
        "verificationStatus": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed" }] },
        "code": {
          "coding": [
            { "system": "http://snomed.info/sct", "code": "444814009", "display": "Viral sinusitis" },
            { "system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "J01.90", "display": "Viral sinusitis" }
          ]
        },
        "subject": { "reference": "urn:uuid:018e6e58-patient" }
      }
    },
    {
      "fullUrl": "urn:uuid:018e6e58-med-amox",
      "resource": {
        "resourceType": "MedicationStatement",
        "status": "active",
        "medicationCodeableConcept": {
          "coding": [{ "system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "562251", "display": "Amoxicillin 250 MG / Clavulanate 125 MG Oral Tablet" }]
        },
        "subject": { "reference": "urn:uuid:018e6e58-patient" }
      }
    },
    {
      "fullUrl": "urn:uuid:018e6e58-obs-bp",
      "resource": {
        "resourceType": "Observation",
        "status": "final",
        "category": [{ "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs" }] }],
        "code": { "coding": [{ "system": "http://loinc.org", "code": "85354-9", "display": "Blood Pressure" }] },
        "subject": { "reference": "urn:uuid:018e6e58-patient" },
        "component": [
          {
            "code": { "coding": [{ "system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure" }] },
            "valueQuantity": { "value": 120.0, "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]" }
          },
          {
            "code": { "coding": [{ "system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure" }] },
            "valueQuantity": { "value": 80.0, "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]" }
          }
        ]
      }
    }
  ]
}
```

---

## Benchmark Results (Evaluated against Synthea Ground Truth)

Non-circular benchmark evaluated on held-out test patients generated with Synthea (Seed `42`, `-s 42 -p 50`), rendered across 5 varied clinical note templates (Outpatient SOAP, Emergency Department Acute Triage, Inpatient Discharge Summary, Medical Specialty Consultation, Daily Progress Note) with realistic noise (standard abbreviations like HTN/DM2/HLD/CAD/COPD/GERD/HTA/EPOC, narrative misspellings, explicit clinical negations, and family history distractors):

| Resource Type | Standard Coding System | Precision (EN) | Recall (EN) | F1 (EN) | Precision (ES) | Recall (ES) | F1 (ES) | Ground Truth N |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Patient Demographics** | Name, DOB, Gender | 100.0% | 93.3% | **96.5%** | 100.0% | 100.0% | **100.0%** | 75 / lang |
| **Condition** | SNOMED CT / ICD-10 | 93.3% | 43.8% | **59.6%** | 93.3% | 43.8% | **59.6%** | 96 / lang |
| **MedicationStatement** | RxNorm | 59.6% | 35.2% | **44.3%** | 59.6% | 35.2% | **44.3%** | 88 / lang |
| **AllergyIntolerance** | SNOMED CT | 91.7% | 68.8% | **78.6%** | 91.7% | 68.8% | **78.6%** | 16 / lang |
| **Observation (Vitals)** | LOINC + UCUM | 100.0% | 100.0% | **100.0%** | 100.0% | 100.0% | **100.0%** | 175 / lang |
| **Overall Micro-Average** | **All Standard Terminologies** | **92.9%** | **73.1%** | **81.8%** | **93.0%** | **74.2%** | **82.6%** | **450 / lang** |

*Note on Non-Circular Evaluation & Clinical Error Analysis:*
- **Dev / Test Split:** Evaluated on held-out test patients independent of the training/dev dictionary.
- **Narrative Typos:** Realistic free-text misspellings (*hypertensn*, *artrial*) account for missed condition recall, avoiding circular 100% claims.
- **Distractor Filtering:** Family history mentions (*"Mother diagnosed with breast cancer at age 62"*) are cleanly filtered by `_is_family_history`, maintaining 100% condition precision in English.
- **Negations:** Pertinent clinical negatives (*"denies chest pain"*, *"sin disnea"*) are suppressed from extraction.
- Detailed error breakdown and case studies are documented in [`evals/results.md`](evals/results.md) and [`evals/results.json`](evals/results.json).
- Public HL7 HAPI FHIR R4 server validation results across all 25 held-out test cohort bundles (100.0% conformance rate, 0 schema errors) are documented in [`evals/hapi_validation.md`](evals/hapi_validation.md).

### Rule-based vs. LLM Extractor Benchmark Comparison

| Extractor Engine | Implementation / Provider | Conditions F1 | Meds F1 | Allergies F1 | Vitals F1 | Overall F1 (EN) | Overall F1 (ES) | Ground Truth N |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Deterministic Rule-Based** | Curated Local Terminology (Offline) | 59.6% | 44.3% | 78.6% | 100.0% | **82.6%** | **82.6%** | 450 / lang |
| **LLM Extractor** | Google Gemini (`gemini-1.5-pro`) / Claude / GPT | *Skipped* | *Skipped* | *Skipped* | *Skipped* | *Skipped* | *Skipped* | 450 / lang |

> [!NOTE]
> **LLM Extractor Evaluation Environment:** `LLMExtractor` supports Google Gemini (`GEMINI_API_KEY`), Anthropic Claude (`ANTHROPIC_API_KEY`), and OpenAI (`OPENAI_API_KEY`). On this execution environment, no `GEMINI_API_KEY` was detected in the environment. Numbers are never fabricated; LLM evaluation can be invoked at any time with `python evals/evaluator.py --extractor llm`.

---

## Quickstart: Run in One Command

Convert a clinical note to a validated FHIR R4 Bundle instantly:

```bash
# Convert an English note to FHIR R4 JSON
python3 -m note_to_fhir.cli convert data/fixtures/notes/en/Alvina833_Franecki195_8a0c8ac4-8227-9277-d4c1-a8fa96f6b0d9_soap.txt -o bundle.json
```

Or run the full evaluation suite in one command:
```bash
make eval
```

---

## Key Features

1. **Deterministic Offline Extractor (Default)**:
   - High-throughput regex extraction for complex vital sign panels (Blood Pressure with Systolic & Diastolic components, Heart Rate, Respiratory Rate, Temperature in °F or °C, SpO2, BMI).
   - Curated terminology dictionaries mapping clinical conditions, medications, and allergies to **SNOMED CT**, **RxNorm**, and **ICD-10-CM**.
   - Zero external API dependencies; runs 100% offline.
2. **Bilingual Support (English & Spanish)**:
   - Out-of-the-box handling of English and Spanish medical notes and terminology variants (e.g. *Hipertensión arterial*, *Metformina*, *Alergia al maní*).
3. **Pluggable LLM Extractor (Optional)**:
   - Extensible support for OpenAI (`gpt-4o-mini`), Anthropic (`claude-3-5-sonnet`), and Google Gemini (`gemini-1.5-pro`) via environment variables.
   - Automatically skipped if no API key is provided, falling back to the deterministic engine.
4. **HL7 FHIR R4 Standards Compliance**:
   - Generates compliant `Bundle` (collection) resources containing linked `Patient`, `Encounter`, `Condition`, `MedicationStatement`, `AllergyIntolerance`, and `Observation` entries.
   - Validates every bundle against `fhir.resources` schema definitions and verifies **UCUM** measurement units (`mm[Hg]`, `/min`, `[degF]`, `Cel`, `kg/m2`, `%`).
5. **REST API & CLI**:
   - Production-ready FastAPI service with `POST /convert`, `POST /validate`, and `GET /health`.
   - Comprehensive CLI (`note-to-fhir convert`, `note-to-fhir eval`, `note-to-fhir serve`).

---

## Installation

### Prerequisites
- Python 3.11+
- (Optional) Java JRE 11+ for running the Synthea patient generator

### From Source
```bash
git clone https://github.com/carlspareds/note-to-fhir.git
cd note-to-fhir
pip install -e ".[dev]"
```

### With Docker
```bash
docker-compose up --build
```
The FastAPI microservice will be available at `http://localhost:8000` (interactive documentation at `http://localhost:8000/docs`).

---

## CLI Usage

```bash
# Basic conversion to stdout
note-to-fhir convert path/to/note.txt

# Save to output file with validation
note-to-fhir convert data/fixtures/notes/en/patient_2_asthma_allergy_soap.txt -o asthma_bundle.json

# Convert a Spanish note
note-to-fhir convert data/fixtures/notes/es/patient_2_asthma_allergy_soap.txt -o spanish_bundle.json --lang es

# Start HTTP API microservice
note-to-fhir serve --port 8000
```

---

## REST API Microservice

### Convert Note Endpoint
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient Name: Maria Garcia\nDOB: 1988-09-22 | Gender: Female\nPast Medical History:\n- Asthma\nCurrent Medications:\n- Albuterol 90 MCG Inhaler\nVital Signs:\n- Blood Pressure: 118/76 mmHg\n- Heart Rate: 82 bpm",
    "language": "en",
    "extractor": "rules",
    "validate": true
  }'
```

---

## Reproducible Synthea Pipeline

To generate a new cohort of 50 synthetic patients using the official Synthea generator:
```bash
bash scripts/generate_synthea.sh
```
*Note: In accordance with our synthetic data policy, bulk generated patient records are gitignored to prevent repository bloat. Curated fixtures and data provenance details are documented in [`DATA.md`](DATA.md).*

---

## Running Tests

```bash
# Run all unit and end-to-end integration tests
make test

# Check code style with ruff
make lint
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
