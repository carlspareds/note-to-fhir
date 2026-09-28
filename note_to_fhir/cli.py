"""
Command-line interface (CLI) for note-to-fhir.
Usage:
    note-to-fhir convert note.txt -o bundle.json [--lang es] [--extractor rules] [--validate]
    note-to-fhir eval
    note-to-fhir serve --port 8000
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from note_to_fhir import __version__
from note_to_fhir.builder import FHIRBundleBuilder
from note_to_fhir.extractors.llm import LLMExtractor
from note_to_fhir.extractors.rules import RuleBasedExtractor
from note_to_fhir.models import ClinicalNote


@click.group()
@click.version_option(version=__version__, prog_name="note-to-fhir")
def main():
    """note-to-fhir: Convert unstructured clinical notes to HL7 FHIR R4 Bundles."""
    pass


@main.command("convert")
@click.argument("note_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output JSON file for generated FHIR R4 bundle. Defaults to stdout if not specified.",
)
@click.option(
    "-l",
    "--lang",
    type=click.Choice(["en", "es", "auto"], case_sensitive=False),
    default="auto",
    help="Clinical note language (default: auto).",
)
@click.option(
    "-e",
    "--extractor",
    type=click.Choice(["rules", "llm"], case_sensitive=False),
    default="rules",
    help="Extractor engine to use (default: rules).",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate generated bundle against FHIR R4 schema and UCUM rules.",
)
def convert_cmd(
    note_path: Path,
    output_path: Optional[Path],
    lang: str,
    extractor: str,
    validate: bool,
):
    """Convert a clinical text note to an HL7 FHIR R4 Bundle JSON."""
    # Direct diagnostic messages to stderr if writing JSON to stdout
    log_err = output_path is None

    click.echo(f"[*] Reading clinical note from: {note_path}", err=log_err)
    note_text = note_path.read_text(encoding="utf-8")

    # Select extractor
    if extractor == "llm":
        ext = LLMExtractor()
        if not ext.is_available:
            click.echo("[!] No LLM API key detected. Falling back to offline RuleBasedExtractor.", err=log_err)
    else:
        ext = RuleBasedExtractor()

    clinical_note = ClinicalNote(text=note_text, language=lang)
    click.echo(f"[*] Extracting clinical entities using engine: {extractor}...", err=log_err)
    entities = ext.extract(clinical_note)

    click.echo(
        f"[✓] Extracted: {len(entities.conditions)} conditions, "
        f"{len(entities.medications)} medications, "
        f"{len(entities.allergies)} allergies, "
        f"{len(entities.observations)} vital signs.",
        err=log_err,
    )

    builder = FHIRBundleBuilder()
    bundle = builder.build_bundle(entities)

    if validate:
        click.echo("[*] Validating FHIR R4 Bundle conformance...", err=log_err)
        is_valid, messages = builder.validate_bundle(bundle)
        if is_valid:
            click.echo("[✓] Bundle passed FHIR R4 validation.", err=log_err)
        else:
            click.echo(f"[!] Validation warnings/errors: {messages}", err=log_err)

    bundle_json = json.dumps(bundle, indent=2, ensure_ascii=False)

    if output_path:
        output_path.write_text(bundle_json, encoding="utf-8")
        click.echo(f"[✓] Successfully wrote FHIR R4 Bundle to: {output_path}")
    else:
        click.echo(bundle_json)


@main.command("serve")
@click.option("--host", default="0.0.0.0", help="Host address to bind.")
@click.option("--port", default=8000, type=int, help="Port to listen on.")
@click.option("--reload/--no-reload", default=False, help="Enable auto-reload.")
def serve_cmd(host: str, port: int, reload: bool):
    """Start the FastAPI HTTP microservice."""
    try:
        import uvicorn
        click.echo(f"[*] Starting note-to-fhir API server at http://{host}:{port}")
        uvicorn.run("note_to_fhir.api:app", host=host, port=port, reload=reload)
    except ImportError:
        click.echo("[ERROR] Uvicorn is required to run the API server. Install with `pip install uvicorn`.", err=True)
        sys.exit(1)


@main.command("eval")
@click.option(
    "--fixtures-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory containing ground truth fixtures.",
)
def eval_cmd(fixtures_dir: Optional[Path]):
    """Run full evaluation suite against Synthea ground truth."""
    from evals.evaluator import run_evaluation

    if fixtures_dir is None:
        cwd_fixtures = Path.cwd() / "data" / "fixtures"
        pkg_fixtures = Path(__file__).resolve().parent.parent / "data" / "fixtures"
        if cwd_fixtures.exists():
            fixtures_dir = cwd_fixtures
        elif pkg_fixtures.exists():
            fixtures_dir = pkg_fixtures
        else:
            fixtures_dir = cwd_fixtures

    click.echo(f"[*] Running note-to-fhir evaluation on fixtures in: {fixtures_dir}")
    metrics = run_evaluation(fixtures_dir)
    click.echo("\n=== Evaluation Results ===")
    click.echo(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
