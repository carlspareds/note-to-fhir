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

## 2. Why Bulk Generated Data Is Not Committed

Running Synthea for longitudinal populations generates hundreds of megabytes of raw JSON across thousands of resource entries. In accordance with clinical software engineering best practices:

1. **Git Repository Hygiene**: Bulk generated datasets cause severe git repository bloat, slow down clones, and degrade CI/CD pipelines.
2. **Deterministic Reproducibility**: The generation script [`scripts/generate_synthea.sh`](scripts/generate_synthea.sh) executes Synthea with an explicit random seed (`SEED=424242`). Anyone can reproduce the exact same synthetic population on demand by executing:
   ```bash
   bash scripts/generate_synthea.sh
   ```
3. **Repository Policy**: All bulk outputs under `data/synthea_output/`, `output/`, and `*.jar` are strictly gitignored via [`.gitignore`](.gitignore).

---

## 3. Sample Evaluation Fixtures

To ensure immediate testability and verifiable evaluation out of the box without requiring users to download the 150 MB Synthea JAR or install Java, the repository includes 5 curated, representative synthetic patient fixtures in [`data/fixtures/`](data/fixtures/):

| Fixture ID | Archetype / Primary Diagnoses | Standard Terminologies Included |
| :--- | :--- | :--- |
| `patient_1_hypertension_diabetes` | Essential Hypertension, Type 2 Diabetes | SNOMED `59621000`, `44054006`; RxNorm `314076`, `860975`; SNOMED `91936005` (Penicillin allergy) |
| `patient_2_asthma_allergy` | Moderate Persistent Asthma | SNOMED `195967001`; RxNorm `745752`, `896209`; SNOMED `91935004` (Peanut allergy) |
| `patient_3_covid_respiratory` | COVID-19, Acute Bronchitis | SNOMED `840539006`, `10509002`; RxNorm `248656`; SNOMED `91931000` (Sulfa allergy) |
| `patient_4_cardiac_hyperlipidemia` | Hyperlipidemia, Coronary Artery Disease | SNOMED `55822004`, `53741008`; RxNorm `259255`, `243670`; SNOMED `294505008` (Codeine allergy) |
| `patient_5_copd_smoking` | COPD, Gastroesophageal Reflux (GERD) | SNOMED `13645005`, `235595009`; RxNorm `312134`, `197361`; SNOMED `300916003` (Latex allergy) |

Each fixture includes:
- Source Synthea FHIR R4 Bundle (`data/fixtures/synthea/*.json`)
- Rendered realistic English SOAP note (`data/fixtures/notes/en/*.txt`)
- Rendered realistic Spanish SOAP note (`data/fixtures/notes/es/*.txt`)
- Extracted gold labels (`data/fixtures/gold_labels.json`)

---

## 4. Compliance & Privacy Statement

This repository complies with the Health Insurance Portability and Accountability Act (HIPAA) Safe Harbor method (45 CFR § 164.514(b)(2)). All personal identifiers, dates, and locations represent purely fictitious synthetic entities.
