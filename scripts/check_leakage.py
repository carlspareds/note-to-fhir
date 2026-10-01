#!/usr/bin/env python3
"""
scripts/check_leakage.py

Automated check for test-set vocabulary leakage.
Ensures that no clinical coding concepts (SNOMED CT for conditions/allergies,
RxNorm for medications) present ONLY in held-out test patients are hardcoded
into note_to_fhir/terminology.py.
"""

import json
import sys
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
GOLD_LABELS_PATH = ROOT / "data" / "fixtures" / "gold_labels.json"


def check_leakage() -> bool:
    if not GOLD_LABELS_PATH.exists():
        print(f"[!] Error: Gold labels file not found at {GOLD_LABELS_PATH}", file=sys.stderr)
        return False

    with open(GOLD_LABELS_PATH, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    # 1. Partition codes by split
    dev_conditions = set()
    test_conditions = set()
    dev_medications = set()
    test_medications = set()
    dev_allergies = set()
    test_allergies = set()

    for pid, pinfo in gold_data.items():
        split = pinfo.get("split", "dev")
        gold = pinfo.get("gold", {})

        for c in gold.get("conditions", []):
            code = str(c.get("snomed"))
            if split == "dev":
                dev_conditions.add(code)
            else:
                test_conditions.add(code)

        for m in gold.get("medications", []):
            code = str(m.get("rxnorm"))
            if split == "dev":
                dev_medications.add(code)
            else:
                test_medications.add(code)

        for a in gold.get("allergies", []):
            code = str(a.get("snomed"))
            if split == "dev":
                dev_allergies.add(code)
            else:
                test_allergies.add(code)

    # 2. Compute test-only codes
    test_only_conditions = test_conditions - dev_conditions
    test_only_medications = test_medications - dev_medications
    test_only_allergies = test_allergies - dev_allergies

    # 3. Check against note_to_fhir/terminology.py
    sys.path.insert(0, str(ROOT))
    try:
        from note_to_fhir.terminology import (
            ALLERGIES_DATABASE,
            CONDITIONS_DATABASE,
            MEDICATIONS_DATABASE,
        )
    except ImportError as e:
        print(f"[!] Failed to import note_to_fhir.terminology: {e}", file=sys.stderr)
        return False

    term_conditions = {str(c["snomed"]): c.get("display") for c in CONDITIONS_DATABASE}
    term_medications = {str(m["rxnorm"]): m.get("display") for m in MEDICATIONS_DATABASE}
    term_allergies = {str(a["snomed"]): a.get("display") for a in ALLERGIES_DATABASE}

    leaked_conditions = {c: term_conditions[c] for c in test_only_conditions if c in term_conditions}
    leaked_medications = {m: term_medications[m] for m in test_only_medications if m in term_medications}
    leaked_allergies = {a: term_allergies[a] for a in test_only_allergies if a in term_allergies}

    has_leakage = False
    if leaked_conditions:
        print("[!] TEST LEAKAGE DETECTED in Conditions (SNOMED):", file=sys.stderr)
        for code, disp in leaked_conditions.items():
            print(f"    - {code}: {disp}", file=sys.stderr)
        has_leakage = True

    if leaked_medications:
        print("[!] TEST LEAKAGE DETECTED in Medications (RxNorm):", file=sys.stderr)
        for code, disp in leaked_medications.items():
            print(f"    - {code}: {disp}", file=sys.stderr)
        has_leakage = True

    if leaked_allergies:
        print("[!] TEST LEAKAGE DETECTED in Allergies (SNOMED):", file=sys.stderr)
        for code, disp in leaked_allergies.items():
            print(f"    - {code}: {disp}", file=sys.stderr)
        has_leakage = True

    if not has_leakage:
        print(f"[✓] Zero test-set vocabulary leakage detected across {len(test_only_conditions)} test conditions, {len(test_only_medications)} test medications, and {len(test_only_allergies)} test allergies.")
        return True
    else:
        return False


def main():
    passed = check_leakage()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
