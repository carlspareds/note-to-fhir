# Data Provenance and Synthetic Data Policy

## 1. Overview & Data Provenance

All patient data and clinical records utilized, generated, or referenced by **`note-to-fhir`** are **100% synthetic**. Under no circumstances is real Protected Health Information (PHI) or Personally Identifiable Information (PII) processed, stored, or committed to this repository.

Ground truth patient histories and FHIR R4 bundles are generated using **Synthea™**, an open-source, agent-based synthetic patient generator developed and maintained by the Synthetic Health initiative ([synthetichealth/synthea](https://github.com/synthetichealth/synthea)).

### Why Synthea?
- **Clinically Realistic Disease Trajectories**: Synthea models standard-of-care disease progressions from birth to death, incorporating clinical practice guidelines, census demographic distributions, and epidemiologic incidence rates.
- **Native HL7 FHIR R4 Export**: Synthea outputs validated HL7 FHIR R4 resource bundles containing standard clinical terminologies:
  - **SNOMED CT** for Clinical Conditions and Diagnoses
  - **RxNorm** for Medication Orders and Prescriptions
  - **LOINC** for Laboratory Tests and Vital Signs
  - **UCUM** for Standardized Units of Measure
  - **ICD-10-CM** for Secondary Diagnostic Classifications

---

## 2. Synthea Generation Pipeline & User-Space JRE Automation

Running Synthea for longitudinal populations generates hundreds of megabytes of raw JSON across thousands of resource entries. In accordance with clinical software engineering best practices:

1. **Deterministic Reproducibility**: The generation script [`scripts/generate_synthea.sh`](scripts/generate_synthea.sh) executes Synthea with an explicit random seed (`SEED=42`, `-s 42 -p 50`) generating 50 synthetic patient bundles. Anyone can reproduce the exact synthetic population on demand:
   ```bash
   bash scripts/generate_synthea.sh
   ```
2. **Automated User-Space JRE**: If Java is missing on the system, `scripts/generate_synthea.sh` automatically downloads a portable **Eclipse Temurin 17 JRE** (Linux x64 / aarch64) tarball into user space (`bin/jre`), sets `PATH`, and executes `synthea-with-dependencies.jar` without requiring root or system package manager privileges.
3. **Git Hygiene & Sample Fixture Policy**: All bulk outputs under `data/synthea_output/`, `output/`, and `*.jar` are strictly gitignored via [`.gitignore`](.gitignore). A representative sample of 5 genuine Synthea bundles (`Benton624_Koss676_...`, `Gonzalo160_Bahringer146_...`, `Isiah14_Prohaska837_...`, `Karlyn611_Stracke611_...`, `Russel238_Doyle959_...`) is retained in `data/fixtures/synthea/`, with the remaining notes and gold labels dynamically derived from the full 50-patient cohort via [`scripts/render_notes.py`](scripts/render_notes.py).

---

## 3. Non-Circular Evaluation Fixtures & Dev/Test Split

To eliminate circularity (where dictionaries and note templates are derived from the same 5 samples), `note-to-fhir` establishes a rigorous non-circular evaluation methodology:

1. **Dev / Test Split**: 50 synthetic patients are partitioned into:
   - **Dev Cohort (25 patients)**: For rule development, regex tuning, and dictionary curation.
   - **Held-Out Test Cohort (25 patients)**: Strictly unseen during rule design for unbiased generalization appraisal.
2. **5 Varied Clinical Note Templates**:
   - Outpatient SOAP Follow-up Note
   - Emergency Department Acute Triage Note
   - Inpatient Hospital Discharge Summary
   - Medical Specialty Consultation Note
   - Daily Inpatient Clinical Progress Note
3. **Realistic Clinical Noise**:
   - **Standard Clinical Abbreviations**: *HTN*, *DM2*, *HLD*, *CAD*, *COPD*, *GERD*, *HTA*, *EPOC*, *ERGE*.
   - **Narrative Typos**: Realistic free-text misspellings (*hypertensn*, *artrial*) that challenge dictionary tokenization and avoid artificial 100% precision/recall claims.
   - **Clinical Negations**: Pertinent negative declarations (*"denies chest pain"*, *"sin disnea ni dolor precordial"*) verifying negation suppression.
   - **Family History Distractors**: Family diagnoses (*"Mother diagnosed with breast cancer at age 62; father died of myocardial infarction"*) verifying distractor suppression via `_is_family_history`.
   - **Spanish Linguistic Variants**: Regional terminology (*presión alta*, *pastillas del colesterol*).

Each fixture includes:
- Source Synthea FHIR R4 Bundle (`data/fixtures/synthea/*.json`)
- Rendered realistic English clinical note (`data/fixtures/notes/en/*.txt`)
- Rendered realistic Spanish clinical note (`data/fixtures/notes/es/*.txt`)
- Extracted gold labels with dev/test partition tags (`data/fixtures/gold_labels.json`)

---

## 4. Compliance & Privacy Statement

This repository complies with the Health Insurance Portability and Accountability Act (HIPAA) Safe Harbor method (45 CFR § 164.514(b)(2)). All personal identifiers, dates, and locations represent purely fictitious synthetic entities.
