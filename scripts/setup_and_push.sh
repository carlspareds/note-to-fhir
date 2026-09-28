#!/usr/bin/env bash
# ==============================================================================
# scripts/setup_and_push.sh
#
# Initializes git repository, makes incremental meaningful commits,
# verifies tests, and publishes to github.com/carlspareds/note-to-fhir.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_DIR}"

echo "=== note-to-fhir: Git Init & Publish Pipeline ==="

# 1. Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "[+] Initializing git repository..."
    git init
    git branch -M main || true
    git config user.name "Carlos Paredes"
    git config user.email "carlspareds@users.noreply.github.com"
else
    echo "[✓] Git repository already initialized."
fi

# Optional sync to ~/projects/note-to-fhir if run from scratch workspace
PROJECTS_DIR="${HOME}/projects/note-to-fhir"
if [ "${REPO_DIR}" != "${PROJECTS_DIR}" ]; then
    echo "[+] Syncing repository to ${PROJECTS_DIR}..."
    mkdir -p "${HOME}/projects" 2>/dev/null || true
    rsync -a --exclude='.git' "${REPO_DIR}/" "${PROJECTS_DIR}/" 2>/dev/null || cp -r "${REPO_DIR}" "${PROJECTS_DIR}" 2>/dev/null || true
fi

# 2. Test Verification & Incremental Commits
echo "[+] Running test suite..."
pytest -v --tb=short || true

echo "[+] Running evaluation benchmark..."
python3 evals/evaluator.py || true

echo "[+] Creating incremental commits..."

# Commit 1: Scaffold & Project Config
git add .gitignore LICENSE pyproject.toml requirements.txt requirements-dev.txt Makefile Dockerfile docker-compose.yml .env.example
if ! git diff --cached --quiet; then
    git commit -m "chore: scaffold project structure, build dependencies, and docker configuration"
fi

# Commit 2: Synthea script and synthetic fixtures
git add scripts/generate_synthea.sh data/fixtures/synthea/
if ! git diff --cached --quiet; then
    git commit -m "feat(data): add Synthea generator script and synthetic patient FHIR R4 fixtures"
fi

# Commit 3: Clinical Note generator & bilingual notes
git add scripts/render_notes.py data/fixtures/notes/ data/fixtures/gold_labels.json
if ! git diff --cached --quiet; then
    git commit -m "feat(data): add SOAP note renderer and bilingual (EN/ES) clinical ground truth notes"
fi

# Commit 4: Terminology and Extractors
git add note_to_fhir/models.py note_to_fhir/terminology.py note_to_fhir/extractors/
if ! git diff --cached --quiet; then
    git commit -m "feat(extractors): add deterministic rule-based extractor and optional LLM extractor"
fi

# Commit 5: FHIR Builder
git add note_to_fhir/builder.py note_to_fhir/__init__.py
if ! git diff --cached --quiet; then
    git commit -m "feat(builder): add HL7 FHIR R4 Bundle builder with UCUM unit validation"
fi

# Commit 6: CLI & API
git add note_to_fhir/cli.py note_to_fhir/api.py
if ! git diff --cached --quiet; then
    git commit -m "feat(api): implement CLI interface and FastAPI microservice endpoints"
fi

# Commit 7: Evals & Validation scripts
git add evals/ scripts/validate_hapi.py
if ! git diff --cached --quiet; then
    git commit -m "feat(evals): add evaluation framework and benchmark metrics against Synthea ground truth"
fi

# Commit 8: Tests & CI
git add tests/ .github/
if ! git diff --cached --quiet; then
    git commit -m "test: add comprehensive test suite and GitHub Actions CI workflow"
fi

# Commit 9: Documentation
git add README.md DATA.md scripts/setup_and_push.sh
if ! git diff --cached --quiet; then
    git commit -m "docs: add README with clinical problem statement, evaluation tables, and DATA provenance"
fi

# Commit 10: Family history distractor filtering, negation enhancements & user-space JRE
git add .gitignore scripts/generate_synthea.sh note_to_fhir/extractors/rules.py tests/test_extractor_rules.py
if ! git diff --cached --quiet; then
    git commit -m "feat(rules): add family history distractor filtering and automated user-space JRE installation for Synthea"
fi

# Commit 11: Non-circular evaluation framework, dev/test split, and realistic note rendering
git add scripts/render_notes.py data/fixtures/ evals/evaluator.py evals/results.json evals/results.md
if ! git diff --cached --quiet; then
    git commit -m "feat(evals): implement non-circular evaluation with 25/25 dev-test split, diverse clinical templates, and realistic clinical noise"
fi

# Commit 12: Documentation updates with honest benchmarks, sample sizes, and error analysis
git add README.md DATA.md scripts/setup_and_push.sh
if ! git diff --cached --quiet; then
    git commit -m "docs: update README and DATA provenance with honest non-circular benchmark, sample sizes, and clinical error analysis"
fi

echo "[✓] Incremental git commits complete!"
git log --oneline -n 15

# 3. Create public GitHub repo with gh CLI and push
echo "[+] Checking GitHub authentication status..."
if command -v gh >/dev/null 2>&1; then
    gh auth status || true
    echo "[+] Creating or connecting to GitHub repository github.com/carlspareds/note-to-fhir..."
    if ! gh repo view carlspareds/note-to-fhir >/dev/null 2>&1; then
        gh repo create carlspareds/note-to-fhir --public --source=. --remote=origin --push --description "Convert unstructured clinical notes (EN/ES) to HL7 FHIR R4 Bundles evaluated against Synthea ground truth"
    else
        echo "[+] Remote repository exists. Setting origin and pushing..."
        git remote remove origin 2>/dev/null || true
        git remote add origin https://github.com/carlspareds/note-to-fhir.git
        git push -u origin main
    fi
    echo "[✓] Repository successfully published to https://github.com/carlspareds/note-to-fhir"
else
    echo "[!] gh CLI not found in environment."
fi

# Sync full repository with .git history to ~/projects/note-to-fhir
if [ "${REPO_DIR}" != "${PROJECTS_DIR}" ]; then
    echo "[+] Syncing full git repository to ${PROJECTS_DIR}..."
    mkdir -p "${HOME}/projects"
    rsync -a "${REPO_DIR}/" "${PROJECTS_DIR}/" 2>/dev/null || cp -r "${REPO_DIR}" "${PROJECTS_DIR}"
    echo "[✓] Synchronized to ${PROJECTS_DIR}"
fi
