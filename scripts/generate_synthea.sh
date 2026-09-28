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

# 1. Verify or install Java runtime in user space
JAVA_CMD="java"
if ! command -v java >/dev/null 2>&1; then
    ARCH=$(uname -m)
    case "${ARCH}" in
        x86_64) JRE_ARCH="x64" ;;
        aarch64|arm64) JRE_ARCH="aarch64" ;;
        *) JRE_ARCH="x64" ;;
    esac

    JRE_DIR="${PROJECT_ROOT}/bin/jre"
    # Verify existing JRE actually works natively on this architecture
    if [ -x "${JRE_DIR}/bin/java" ] && file -b -L "${JRE_DIR}/bin/java" | grep -qiE "${ARCH}|${JRE_ARCH}" && "${JRE_DIR}/bin/java" -version >/dev/null 2>&1; then
        JAVA_CMD="${JRE_DIR}/bin/java"
        echo "[✓] Using user-space JRE at ${JAVA_CMD}"
    else
        echo "[+] Installing native user-space Eclipse Temurin 17 JRE (${JRE_ARCH})..."
        rm -rf "${JRE_DIR}"
        mkdir -p "${JRE_DIR}"
        TARBALL="${PROJECT_ROOT}/bin/temurin_jre.tar.gz"
        TEMURIN_URL="https://api.adoptium.net/v3/binary/latest/17/ga/linux/${JRE_ARCH}/jre/hotspot/normal/eclipse"
        FALLBACK_URL="https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.10%2B7/OpenJDK17U-jre_${JRE_ARCH}_linux_hotspot_17.0.10_7.tar.gz"

        if curl -L --retry 3 --fail -o "${TARBALL}" "${TEMURIN_URL}"; then
            echo "[✓] Downloaded Eclipse Temurin JRE from Adoptium API (${JRE_ARCH})"
        else
            echo "[+] Retrying with direct GitHub release URL (${JRE_ARCH})..."
            curl -L --retry 3 --fail -o "${TARBALL}" "${FALLBACK_URL}"
        fi

        echo "[+] Extracting JRE to ${JRE_DIR}..."
        tar -xzf "${TARBALL}" -C "${JRE_DIR}" --strip-components=1
        rm -f "${TARBALL}"
        JAVA_CMD="${JRE_DIR}/bin/java"
        chmod +x "${JAVA_CMD}" || true
        echo "[✓] Installed native user-space JRE to ${JAVA_CMD}"
    fi
fi

JAVA_VER=$("${JAVA_CMD}" -version 2>&1 | head -n 1)
echo "[✓] Detected Java: ${JAVA_VER}"

# 2. Ensure bin/ directory and download Synthea JAR if absent
mkdir -p "${PROJECT_ROOT}/bin"
if [ ! -f "${SYNTHEA_JAR}" ]; then
    echo "[+] Downloading official Synthea standalone JAR (${SYNTHEA_VERSION})..."
    SYNTHEA_FALLBACK_URL="https://github.com/synthetichealth/synthea/releases/download/v3.2.0/synthea-with-dependencies.jar"
    if ! curl -L --retry 3 --fail -o "${SYNTHEA_JAR}" "${SYNTHEA_URL}"; then
        echo "[+] Retrying with Synthea v3.2.0 release..."
        curl -L --retry 3 --fail -o "${SYNTHEA_JAR}" "${SYNTHEA_FALLBACK_URL}"
    fi
    echo "[✓] Downloaded Synthea JAR to ${SYNTHEA_JAR}"
else
    echo "[✓] Using existing Synthea JAR at ${SYNTHEA_JAR}"
fi

# 3. Prepare output directory
mkdir -p "${OUTPUT_DIR}"

# 4. Run Synthea generation with FHIR R4 export enabled
echo "[+] Generating ${POPULATION_SIZE} synthetic patients (Seed: ${SEED}) in Massachusetts..."
"${JAVA_CMD}" -jar "${SYNTHEA_JAR}" \
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
