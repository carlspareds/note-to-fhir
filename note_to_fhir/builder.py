"""
FHIR R4 Bundle Builder.
Constructs valid HL7 FHIR R4 Bundles containing Patient, Encounter, Condition,
MedicationStatement, AllergyIntolerance, and Observation (with UCUM units).
Validates every output using the fhir.resources library and strict structural schema checks.
"""

import datetime
import uuid
from typing import Any, Dict, List, Optional, Tuple

from note_to_fhir.models import (
    AllergyEntity,
    ConditionEntity,
    ExtractedEntities,
    MedicationEntity,
    VitalSignObservation,
)

# Attempt to import official fhir.resources models (R4B specification for FHIR R4)
try:
    from fhir.resources.R4B.bundle import Bundle as FhirBundle
    FHIR_RESOURCES_AVAILABLE = True
except ImportError:
    try:
        from fhir.resources.bundle import Bundle as FhirBundle
        FHIR_RESOURCES_AVAILABLE = True
    except ImportError:
        FHIR_RESOURCES_AVAILABLE = False


class FHIRBundleBuilder:
    """
    Constructs and validates HL7 FHIR R4 Bundles from extracted clinical entities.
    """

    def __init__(self, bundle_type: str = "collection"):
        self.bundle_type = bundle_type

    def build_bundle(self, entities: ExtractedEntities) -> Dict[str, Any]:
        """
        Build a FHIR R4 Bundle containing all extracted resources.
        """
        bundle_id = str(uuid.uuid4())
        entries: List[Dict[str, Any]] = []

        patient_uuid = f"urn:uuid:{uuid.uuid4()}"
        encounter_uuid = f"urn:uuid:{uuid.uuid4()}"

        # 1. Patient Resource
        patient_res = self._build_patient_resource(entities.patient, patient_uuid)
        entries.append({
            "fullUrl": patient_uuid,
            "resource": patient_res,
        })

        # 2. Encounter Resource
        encounter_res = self._build_encounter_resource(entities.encounter, encounter_uuid, patient_uuid)
        entries.append({
            "fullUrl": encounter_uuid,
            "resource": encounter_res,
        })

        # 3. Condition Resources
        for cond in entities.conditions:
            cond_uuid = f"urn:uuid:{uuid.uuid4()}"
            cond_res = self._build_condition_resource(cond, cond_uuid, patient_uuid, encounter_uuid)
            entries.append({
                "fullUrl": cond_uuid,
                "resource": cond_res,
            })

        # 4. MedicationStatement Resources
        for med in entities.medications:
            med_uuid = f"urn:uuid:{uuid.uuid4()}"
            med_res = self._build_medication_statement_resource(med, med_uuid, patient_uuid, encounter_uuid)
            entries.append({
                "fullUrl": med_uuid,
                "resource": med_res,
            })

        # 5. AllergyIntolerance Resources
        for allg in entities.allergies:
            allg_uuid = f"urn:uuid:{uuid.uuid4()}"
            allg_res = self._build_allergy_intolerance_resource(allg, allg_uuid, patient_uuid, encounter_uuid)
            entries.append({
                "fullUrl": allg_uuid,
                "resource": allg_res,
            })

        # 6. Observation (Vital Signs) Resources
        for obs in entities.observations:
            obs_uuid = f"urn:uuid:{uuid.uuid4()}"
            obs_res = self._build_observation_resource(obs, obs_uuid, patient_uuid, encounter_uuid)
            entries.append({
                "fullUrl": obs_uuid,
                "resource": obs_res,
            })

        bundle_dict: Dict[str, Any] = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": self.bundle_type,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "entry": entries,
        }
        if self.bundle_type in ("searchset", "history"):
            bundle_dict["total"] = len(entries)

        return bundle_dict

    def validate_bundle(self, bundle_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate the FHIR Bundle using fhir.resources and structural rule checks.
        Returns (is_valid, list_of_errors_or_warnings).
        """
        messages: List[str] = []
        is_valid = True

        # 1. Structural Checks
        if bundle_dict.get("resourceType") != "Bundle":
            messages.append("Missing or invalid resourceType; expected 'Bundle'")
            return False, messages

        if "type" not in bundle_dict:
            messages.append("Bundle missing required field 'type'")
            is_valid = False

        entries = bundle_dict.get("entry", [])
        if not isinstance(entries, list):
            messages.append("Bundle 'entry' must be a list")
            return False, messages

        for idx, entry in enumerate(entries):
            res = entry.get("resource", {})
            rtype = res.get("resourceType")
            if not rtype:
                messages.append(f"Entry {idx} missing 'resourceType'")
                is_valid = False
                continue

            # Check UCUM in observations
            if rtype == "Observation":
                components = res.get("component", [])
                if components:
                    for comp in components:
                        vq = comp.get("valueQuantity", {})
                        if vq.get("system") != "http://unitsofmeasure.org":
                            messages.append(f"Observation component missing UCUM system in entry {idx}")
                            is_valid = False
                else:
                    vq = res.get("valueQuantity", {})
                    if vq and vq.get("system") != "http://unitsofmeasure.org":
                        messages.append(f"Observation missing UCUM system in entry {idx}")
                        is_valid = False

        # 2. Validation with fhir.resources library if present
        if FHIR_RESOURCES_AVAILABLE:
            try:
                # Support both Pydantic v1 (parse_obj) and v2 (model_validate)
                if hasattr(FhirBundle, "model_validate"):
                    FhirBundle.model_validate(bundle_dict)
                else:
                    FhirBundle.parse_obj(bundle_dict)
                messages.append("fhir.resources validation succeeded.")
            except Exception as e:
                is_valid = False
                messages.append(f"fhir.resources validation error: {str(e)}")
        else:
            messages.append("fhir.resources package not installed; passed structural validation.")

        return is_valid, messages

    def _build_patient_resource(self, patient_info, patient_uuid: str) -> Dict[str, Any]:
        """Construct FHIR R4 Patient resource."""
        res: Dict[str, Any] = {
            "resourceType": "Patient",
            "id": patient_uuid.replace("urn:uuid:", ""),
        }

        if patient_info.name:
            parts = patient_info.name.split()
            family = parts[-1] if len(parts) > 1 else parts[0]
            given = parts[:-1] if len(parts) > 1 else [parts[0]]
            res["name"] = [{
                "use": "official",
                "family": family,
                "given": given,
                "text": patient_info.name,
            }]

        if patient_info.gender in ["male", "female", "other", "unknown"]:
            res["gender"] = patient_info.gender
        else:
            res["gender"] = "unknown"

        if patient_info.birth_date:
            res["birthDate"] = patient_info.birth_date

        return res

    def _build_encounter_resource(self, encounter_info, encounter_uuid: str, patient_uuid: str) -> Dict[str, Any]:
        """Construct FHIR R4 Encounter resource."""
        date_str = encounter_info.date or "2024-03-15"
        res: Dict[str, Any] = {
            "resourceType": "Encounter",
            "id": encounter_uuid.replace("urn:uuid:", ""),
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {"reference": patient_uuid},
            "period": {
                "start": f"{date_str}T09:00:00Z",
                "end": f"{date_str}T09:45:00Z",
            },
        }
        return res

    def _build_condition_resource(
        self, cond: ConditionEntity, cond_uuid: str, patient_uuid: str, encounter_uuid: str
    ) -> Dict[str, Any]:
        """Construct FHIR R4 Condition resource."""
        codings = []
        if cond.snomed_code:
            codings.append({
                "system": "http://snomed.info/sct",
                "code": cond.snomed_code,
                "display": cond.display or cond.text,
            })
        if cond.icd10_code:
            codings.append({
                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                "code": cond.icd10_code,
                "display": cond.display or cond.text,
            })

        res: Dict[str, Any] = {
            "resourceType": "Condition",
            "id": cond_uuid.replace("urn:uuid:", ""),
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": cond.status or "active",
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed",
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                    "code": "problem-list-item",
                    "display": "Problem List Item",
                }]
            }],
            "code": {
                "coding": codings,
                "text": cond.display or cond.text,
            },
            "subject": {"reference": patient_uuid},
            "encounter": {"reference": encounter_uuid},
        }
        return res

    def _build_medication_statement_resource(
        self, med: MedicationEntity, med_uuid: str, patient_uuid: str, encounter_uuid: str
    ) -> Dict[str, Any]:
        """Construct FHIR R4 MedicationStatement resource."""
        codings = []
        if med.rxnorm_code:
            codings.append({
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": med.rxnorm_code,
                "display": med.display or med.text,
            })

        res: Dict[str, Any] = {
            "resourceType": "MedicationStatement",
            "id": med_uuid.replace("urn:uuid:", ""),
            "status": med.status or "active",
            "medicationCodeableConcept": {
                "coding": codings,
                "text": med.display or med.text,
            },
            "subject": {"reference": patient_uuid},
            "context": {"reference": encounter_uuid},
            "effectiveDateTime": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        }
        if med.dosage:
            res["dosage"] = [{"text": med.dosage}]
        return res

    def _build_allergy_intolerance_resource(
        self, allg: AllergyEntity, allg_uuid: str, patient_uuid: str, encounter_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Construct FHIR R4 AllergyIntolerance resource."""
        codings = []
        if allg.snomed_code:
            codings.append({
                "system": "http://snomed.info/sct",
                "code": allg.snomed_code,
                "display": allg.display or allg.text,
            })

        res: Dict[str, Any] = {
            "resourceType": "AllergyIntolerance",
            "id": allg_uuid.replace("urn:uuid:", ""),
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    "code": allg.status or "active",
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                    "code": "confirmed",
                }]
            },
            "type": "allergy",
            "category": [allg.category if allg.category in ["medication", "food", "environment", "biologic"] else "medication"],
            "code": {
                "coding": codings,
                "text": allg.display or allg.text,
            },
            "patient": {"reference": patient_uuid},
        }
        if encounter_uuid:
            res["encounter"] = {"reference": encounter_uuid}
        return res

    def _build_observation_resource(
        self, obs: VitalSignObservation, obs_uuid: str, patient_uuid: str, encounter_uuid: str
    ) -> Dict[str, Any]:
        """Construct FHIR R4 Observation resource with UCUM units."""
        res: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": obs_uuid.replace("urn:uuid:", ""),
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
                    "code": obs.loinc_code,
                    "display": obs.name.replace("_", " ").title(),
                }],
                "text": obs.name.replace("_", " ").title(),
            },
            "subject": {"reference": patient_uuid},
            "encounter": {"reference": encounter_uuid},
            "effectiveDateTime": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        }

        # Multi-component Observation (e.g. Blood Pressure panel)
        if obs.name == "blood_pressure" and obs.systolic is not None and obs.diastolic is not None:
            res["component"] = [
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure",
                        }]
                    },
                    "valueQuantity": {
                        "value": obs.systolic,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8462-4",
                            "display": "Diastolic blood pressure",
                        }]
                    },
                    "valueQuantity": {
                        "value": obs.diastolic,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
            ]
        elif obs.value is not None:
            res["valueQuantity"] = {
                "value": obs.value,
                "unit": obs.unit,
                "system": "http://unitsofmeasure.org",
                "code": obs.ucum_code or obs.unit,
            }

        return res
