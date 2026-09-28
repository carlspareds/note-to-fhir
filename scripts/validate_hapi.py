#!/usr/bin/env python3
"""
scripts/validate_hapi.py

Optionally POSTs a generated FHIR R4 Bundle to the public HAPI FHIR test server
endpoint ($validate) to verify strict server-side HL7 FHIR conformance.
"""

import json
import sys
from pathlib import Path

import requests

HAPI_VALIDATE_URL = "https://hapi.fhir.org/baseR4/Bundle/$validate"


def validate_with_hapi(bundle_path: Path) -> bool:
    """Send bundle to public HAPI FHIR $validate endpoint."""
    print(f"[*] Reading bundle from: {bundle_path}")
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle_data = json.load(f)

    headers = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json",
    }

    print(f"[*] Posting bundle to public HAPI test server: {HAPI_VALIDATE_URL}...")
    try:
        resp = requests.post(
            HAPI_VALIDATE_URL,
            json=bundle_data,
            headers=headers,
            timeout=15,
        )
        print(f"[+] HTTP Status: {resp.status_code}")
        outcome = resp.json()
        print("\n--- HAPI Server OperationOutcome ---")
        print(json.dumps(outcome, indent=2))

        # Check for errors in OperationOutcome
        has_error = False
        for issue in outcome.get("issue", []):
            severity = issue.get("severity", "")
            if severity in ("error", "fatal"):
                has_error = True
                print(f"[!] HAPI Validation Error: {issue.get('diagnostics')}")

        if not has_error and resp.status_code == 200:
            print("\n[✓] Public HAPI FHIR Server validated bundle successfully!")
            return True
        else:
            print("\n[!] Public HAPI FHIR Server returned validation warnings/errors.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[!] Network error reaching public HAPI FHIR server: {e}")
        print("Note: The public HAPI test server may occasionally experience downtime or rate limiting.")
        return False


def main():
    root = Path(__file__).resolve().parent.parent
    sample_note = root / "data" / "fixtures" / "notes" / "en" / "patient_1_hypertension_diabetes_soap.txt"

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if not target.exists():
            print(f"File not found: {target}")
            sys.exit(1)
        if target.suffix == ".json":
            validate_with_hapi(target)
            return
        sample_note = target

    print(f"[*] Generating FHIR R4 Bundle from clinical note: {sample_note}")
    from note_to_fhir import convert
    text = sample_note.read_text(encoding="utf-8")
    result = convert(text=text, language="auto", extractor_engine="rules", validate=True)

    tmp_bundle_path = root / "data" / "fixtures" / "generated_sample_bundle.json"
    with open(tmp_bundle_path, "w", encoding="utf-8") as f:
        json.dump(result.bundle, f, indent=2, ensure_ascii=False)

    print(f"[✓] Saved generated bundle to temporary file: {tmp_bundle_path}")
    success = validate_with_hapi(tmp_bundle_path)
    if tmp_bundle_path.exists():
        tmp_bundle_path.unlink()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
