FROM python:3.11-slim

LABEL maintainer="Carlos Paredes <carlspareds@users.noreply.github.com>"
LABEL description="note-to-fhir: Unstructured clinical note to HL7 FHIR R4 Bundle converter"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies (curl for downloads, default-jre for Synthea)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "note_to_fhir.api:app", "--host", "0.0.0.0", "--port", "8000"]
