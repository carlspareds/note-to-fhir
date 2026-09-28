"""
Unit tests for CLI interface.
"""

from click.testing import CliRunner

from note_to_fhir.cli import main


def test_cli_convert_help():
    runner = CliRunner()
    result = runner.invoke(main, ["convert", "--help"])
    assert result.exit_code == 0
    assert "Convert a clinical text note to an HL7 FHIR R4 Bundle JSON." in result.output


def test_cli_convert_note_file(tmp_path):
    runner = CliRunner()
    note_file = tmp_path / "test_note.txt"
    note_file.write_text(
        "Patient Name: John Doe\n"
        "DOB: 1980-01-01\n"
        "Past Medical History:\n- Essential hypertension\n"
        "Current Medications:\n- Lisinopril 10 MG\n"
        "Allergies:\n- Penicillin\n"
        "Vital Signs:\n- Blood Pressure: 120/80 mmHg\n",
        encoding="utf-8",
    )
    out_file = tmp_path / "out_bundle.json"

    result = runner.invoke(
        main,
        ["convert", str(note_file), "-o", str(out_file), "--lang", "en", "--extractor", "rules"],
    )
    assert result.exit_code == 0
    assert out_file.exists()
    assert "Successfully wrote FHIR R4 Bundle" in result.output
