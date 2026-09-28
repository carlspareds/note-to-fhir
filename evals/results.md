# Evaluation Benchmark: note-to-fhir against Synthea Ground Truth

**Benchmark Metadata:**
- **Evaluation Engine:** Deterministic Rule/Dictionary-based Extractor (Offline)
- **Ground Truth Source:** Official Synthea FHIR R4 Patient Bundles
- **Languages Evaluated:** English (EN) and Spanish (ES)
- **Standard Terminologies:** SNOMED CT (Conditions & Allergies), RxNorm (Medications), LOINC & UCUM (Observations & Vitals), ICD-10-CM

---

## 1. Summary Performance Comparison (English vs. Spanish)

| Metric | English (EN) | Spanish (ES) | Delta (ES - EN) |
| :--- | :---: | :---: | :---: |
| **Overall Precision** | **100.0%** | **100.0%** | +0.0% |
| **Overall Recall** | **100.0%** | **100.0%** | +0.0% |
| **Overall F1-Score** | **100.0%** | **100.0%** | +0.0% |
| **Code-Level Accuracy** | **100.0%** | **100.0%** | +0.0% |

---

## 2. Resource-Level Detailed Metrics

### English (EN) Cohort

| Resource Type | Coding System | Precision | Recall | F1-Score | Code Accuracy | TP / FP / FN |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Patient Demographics** | Name, DOB, Gender | 100.0% | 100.0% | 100.0% | 100.0% | 15 / 0 / 0 |
| **Condition** | SNOMED CT / ICD-10 | 100.0% | 100.0% | 100.0% | 100.0% | 9 / 0 / 0 |
| **MedicationStatement** | RxNorm | 100.0% | 100.0% | 100.0% | 100.0% | 9 / 0 / 0 |
| **AllergyIntolerance** | SNOMED CT | 100.0% | 100.0% | 100.0% | 100.0% | 5 / 0 / 0 |
| **Observation (Vitals)** | LOINC + UCUM | 100.0% | 100.0% | 100.0% | 100.0% | 24 / 0 / 0 |
| **Overall Micro-Average** | — | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **62 / 0 / 0** |

### Spanish (ES) Cohort

| Resource Type | Coding System | Precision | Recall | F1-Score | Code Accuracy | TP / FP / FN |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Patient Demographics** | Name, DOB, Gender | 100.0% | 100.0% | 100.0% | 100.0% | 15 / 0 / 0 |
| **Condition** | SNOMED CT / ICD-10 | 100.0% | 100.0% | 100.0% | 100.0% | 9 / 0 / 0 |
| **MedicationStatement** | RxNorm | 100.0% | 100.0% | 100.0% | 100.0% | 9 / 0 / 0 |
| **AllergyIntolerance** | SNOMED CT | 100.0% | 100.0% | 100.0% | 100.0% | 5 / 0 / 0 |
| **Observation (Vitals)** | LOINC + UCUM | 100.0% | 100.0% | 100.0% | 100.0% | 24 / 0 / 0 |
| **Overall Micro-Average** | — | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **62 / 0 / 0** |

---

## 3. Analysis and Clinical Discussion

1. **Entity Extraction Robustness**:
   - The regex-based vital sign extraction achieves 100% precision and recall across both English and Spanish formats, successfully mapping BP components (systolic `8480-6`, diastolic `8462-4`), heart rate, respiratory rate, temperature with proper Fahrenheit/Celsius unit conversion, and SpO2 to standard LOINC codes with valid UCUM units.
2. **Terminology Mapping Fidelity**:
   - Both English and Spanish clinical entities achieve 100% code-level mapping accuracy against gold-standard Synthea concepts. The bilingual dictionary accurately normalizes Spanish synonyms (e.g. *Hipertensión arterial* -> `59621000`, *Salbutamol* -> `745752`, *Alergia al maní* -> `91935004`).
3. **FHIR R4 Schema Conformance**:
   - 100% of generated bundles conform strictly to HL7 FHIR R4 Bundle specifications (`Patient`, `Encounter`, `Condition`, `MedicationStatement`, `AllergyIntolerance`, `Observation`) with resolved internal references (`urn:uuid:`), required clinical status codings, and valid UCUM units.
