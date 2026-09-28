.PHONY: help install test eval run lint format clean synthea

PYTHON ?= python3
PIP ?= pip

help:
	@echo "note-to-fhir development targets:"
	@echo "  make install    Install note-to-fhir package and dev dependencies"
	@echo "  make test       Run test suite with pytest"
	@echo "  make eval       Run clinical evaluation pipeline against Synthea ground truth"
	@echo "  make run        Start FastAPI HTTP microservice on port 8000"
	@echo "  make synthea    Run official Synthea patient generator (scripts/generate_synthea.sh)"
	@echo "  make lint       Check code quality with ruff"
	@echo "  make format     Autoformat code with ruff"
	@echo "  make clean      Remove build and test artifacts"

install:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/

eval:
	$(PYTHON) evals/evaluator.py

run:
	uvicorn note_to_fhir.api:app --reload --host 0.0.0.0 --port 8000

synthea:
	bash scripts/generate_synthea.sh

lint:
	ruff check .

format:
	ruff check --fix .
	ruff format .

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .ruff_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
