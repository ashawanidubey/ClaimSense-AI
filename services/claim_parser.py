from __future__ import annotations

import re
from typing import Any, Final

CLAIM_ID_DEFAULT: Final[str] = "DEMO-CLM-1001"
DENIAL_CODE_DEFAULT: Final[str] = "CO-16"
AMOUNT_DEFAULT: Final[float] = 1250.0
CPT_DEFAULT: Final[str] = "99213"
ICD_DEFAULT: Final[str] = "E11.9"


def _extract_first(patterns: list[str], text: str, default: str) -> str:
    """Return the first captured regex match from provided patterns or default."""
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return default


def _extract_amount_from_bpr(text: str) -> float:
    """Extract payment amount from X12-style BPR segment with text fallback."""
    bpr_patterns = [
        r"\bBPR\*[^*\r\n]*\*([0-9]+(?:\.[0-9]{1,2})?)",
        r"\bBPR\|[^|\r\n]*\|([0-9]+(?:\.[0-9]{1,2})?)",
        r"\bamount\b\s*[:=-]?\s*\$?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
        r"\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
    ]
    raw_amount = _extract_first(bpr_patterns, text, "")
    if not raw_amount:
        return AMOUNT_DEFAULT
    try:
        return float(raw_amount.replace(",", ""))
    except ValueError:
        return AMOUNT_DEFAULT


def parse_claim(text: str) -> dict[str, Any]:
    """Parse claim text/EDI segments and return normalized claim fields.

    Priority is given to EDI-style segments:
    - claim_id from `CLP`
    - denial_code from `CAS`
    - amount from `BPR`
    - cpt from `SVC`

    Fallback demo values are returned if fields are missing so demos remain stable.
    """
    claim_id_patterns = [
        r"\bCLP\*([^*\r\n]+)",
        r"\bCLP\|([^|\r\n]+)",
        r"\bclaim\s*id\b\s*[:=-]?\s*([A-Z0-9\-_/]+)",
        r"\bclaim\b\s*#\s*([A-Z0-9\-_/]+)",
    ]
    denial_code_patterns = [
        r"\bCAS\*[^*\r\n]*\*([A-Z0-9\-_.]+)",
        r"\bCAS\|[^|\r\n]*\|([A-Z0-9\-_.]+)",
        r"\bdenial\s*code\b\s*[:=-]?\s*([A-Z0-9\-_.]+)",
    ]
    cpt_patterns = [
        r"\bSVC\*HC:([0-9]{5})",
        r"\bSVC\|HC:([0-9]{5})",
        r"\bcpt\b\s*[:=-]?\s*([0-9]{5})",
    ]
    icd_patterns = [
        r"\bHI\*[^*\r\n]*:([A-TV-Z][0-9][A-Z0-9](?:\.[A-Z0-9]{1,4})?)",
        r"\bicd(?:-10)?\b\s*[:=-]?\s*([A-TV-Z][0-9][A-Z0-9](?:\.[A-Z0-9]{1,4})?)",
    ]

    return {
        "claim_id": _extract_first(claim_id_patterns, text, CLAIM_ID_DEFAULT),
        "denial_code": _extract_first(denial_code_patterns, text, DENIAL_CODE_DEFAULT),
        "amount": _extract_amount_from_bpr(text),
        "cpt": _extract_first(cpt_patterns, text, CPT_DEFAULT),
        "icd": _extract_first(icd_patterns, text, ICD_DEFAULT),
    }
