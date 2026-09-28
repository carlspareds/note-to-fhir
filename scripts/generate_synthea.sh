#!/usr/bin/env bash
# ==============================================================================
# scripts/generate_synthea.sh
#
# Generates ~50 synthetic patient FHIR R4 JSON bundles using the official
# Synthea patient generator with a fixed seed for exact reproducibility.
#
# Provenance:
#   Official Synthea releases: https://github.com/synthetichealth/synthea/releases
#   All generated records are 100% synthetic. No real patient data is ever used.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SYNTHEA_VERSION="master-branch-latest"
SYNTHEA_JAR="${PROJECT_ROOT}/bin/synthea-with-dependencies.jar"
SYNTHEA_URL="https://github.com/synthetichealth/synthea/releases/download/${SYNTHEA_VERSION}/synthea-with-dependencies.jar"
OUTPUT_DIR="${PROJECT_ROOT}/data/synthea_output"
POPULATION_SIZE=50
SEED=424242

echo "=== note-to-fhir: Synthea Generation Pipeline ==="

# 1. Verify Java requirement
if ! command -v java >/dev/null 2>&1; then
    echo "ERROR: Java runtime environment (JRE/JDK 11+) is required to run Synthea."
    echo "Please install Java (e.g., 'sudo apt-get install -y default-jre') and retry."
    exit 1
fi

JAVA_VER=$(java -version 2>&1 | head -n 1)
echo "[✓] Detected Java: ${JAVA_VER}"

# 2. Ensure bin/ directory and download Synthea JAR if absent
mkdir -p "${PROJECT_ROOT}/bin"
if [ ! -f "${SYNTHEA_JAR}" ]; then
    echo "[+] Downloading official Synthea standalone JAR (${SYNTHEA_VERSION})..."
    curl -L --retry 3 -o "${SYNTHEA_JAR}" "${SYNTHEA_URL}"
    echo "[✓] Downloaded Synthea JAR to ${SYNTHEA_JAR}"
else
    echo "[✓] Using existing Synthea JAR at ${SYNTHEA_JAR}"
fi

# 3. Prepare output directory
mkdir -p "${OUTPUT_DIR}"

# 4. Run Synthea generation with FHIR R4 export enabled
echo "[+] Generating ${POPULATION_SIZE} synthetic patients (Seed: ${SEED}) in Massachusetts..."
java -jar "${SYNTHEA_JAR}" \
    -p "${POPULATION_SIZE}" \
    -s "${SEED}" \
    --exporter.fhir.export=true \
    --exporter.fhir.use_us_core_ig=false \
    --exporter.hospital.fhir.export=false \
    --exporter.practitioner.fhir.export=false \
    --exporter.submodules.require_all_submodules=false \
    --exporter.baseDirectory="${OUTPUT_DIR}" \
    Massachusetts

FHIR_DIR="${OUTPUT_DIR}/fhir"
if [ -d "${FHIR_DIR}" ]; then
    COUNT=$(find "${FHIR_DIR}" -name "*.json" | wc -l)
    echo "[✓] Synthea generation complete! Successfully generated ${COUNT} FHIR R4 patient bundles in ${FHIR_DIR}"
else
    echo "[-] Note: Synthea exported to ${OUTPUT_DIR}"
fi

echo "=============================================================================="
echo "REMINDER: Generated bundles are gitignored in accordance with repo policy."
echo "Only small sample fixtures in data/fixtures/ are tracked in version control."
echo "=============================================================================="
