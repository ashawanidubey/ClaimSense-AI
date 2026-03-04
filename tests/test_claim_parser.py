from __future__ import annotations

from services.claim_parser import parse_claim


def test_parse_claim_extracts_expected_fields() -> None:
    sample_text = """
    Claim ID: CLM-12345
    Denial Code: CO-16
    Amount: $1,250.75
    CPT: 99213
    ICD-10: E11.9
    """

    result = parse_claim(sample_text)

    assert set(result.keys()) == {"claim_id", "denial_code", "amount", "cpt", "icd"}
    assert result["claim_id"] == "CLM-12345"
    assert result["denial_code"] == "CO-16"
    assert result["amount"] == 1250.75
    assert result["cpt"] == "99213"
    assert result["icd"] == "E11.9"


def test_parse_claim_uses_defaults_when_missing() -> None:
    sample_text = "Patient note without claim metadata."

    result = parse_claim(sample_text)

    assert set(result.keys()) == {"claim_id", "denial_code", "amount", "cpt", "icd"}
    assert result["claim_id"] == "UNKNOWN"
    assert result["denial_code"] == "UNKNOWN"
    assert result["amount"] == 0.0
    assert result["cpt"] == "UNKNOWN"
    assert result["icd"] == "UNKNOWN"
