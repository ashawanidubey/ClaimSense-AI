from __future__ import annotations

from typing import Any

from services.claim_parser import parse_claim
from services.llm_service import call_llm


def _build_denial_explanation_prompt(parsed_data: dict[str, Any]) -> str:
    """Create a focused prompt asking the LLM to explain claim denial reasons."""
    return (
        "Review the following healthcare claim details and provide a concise denial explanation. "
        "Include likely root causes and what documentation may be missing.\n\n"
        f"Claim Data: {parsed_data}"
    )


def _build_appeal_letter_prompt(parsed_data: dict[str, Any], explanation: str) -> str:
    """Create a prompt asking the LLM to draft an appeal letter."""
    return (
        "Draft a professional healthcare claim appeal letter using the claim details and denial explanation below. "
        "Use clear sections: subject, summary of claim, rationale for reconsideration, and requested action.\n\n"
        f"Claim Data: {parsed_data}\n\n"
        f"Denial Explanation: {explanation}"
    )


def process_claim(file_text: str) -> dict[str, Any]:
    """Run the claim agent workflow and return parsed data plus LLM outputs."""
    # Step 1: Parse raw claim/EDI text into structured fields for downstream reasoning.
    parsed_data = parse_claim(file_text)

    # Step 2: Generate denial explanation via configured LLM backend (mock or Azure).
    explanation_prompt = _build_denial_explanation_prompt(parsed_data)
    explanation = call_llm(explanation_prompt)

    # Step 3: Generate appeal letter draft from parsed data and explanation context.
    appeal_prompt = _build_appeal_letter_prompt(parsed_data, explanation)
    appeal_letter = call_llm(appeal_prompt)

    # Step 4: Return structured payload consumed by FastAPI response and Streamlit UI.
    return {
        "parsed_data": parsed_data,
        "explanation": explanation,
        "appeal_letter": appeal_letter,
    }
