"""
tests/test_leakage.py

Test verifying zero test-set vocabulary leakage into terminology databases.
"""

from scripts.check_leakage import check_leakage


def test_zero_vocabulary_leakage():
    """Verify that no held-out test-split concepts are leaked into note_to_fhir/terminology.py."""
    assert check_leakage() is True
