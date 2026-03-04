from __future__ import annotations

import logging
from typing import Final

from config import settings

try:
    # Keep optional import safe so mock mode works even without Azure SDK installed.
    from openai import AzureOpenAI
except Exception:  # pragma: no cover - import safety branch
    AzureOpenAI = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

SYSTEM_PROMPT: Final[str] = "You are a healthcare revenue cycle expert."

MOCK_DENIAL_EXPLANATION: Final[str] = (
    "Risk Score: 42/100\n"
    "Fraud Probability: 42%\n"
    "Observations:\n"
    "- CAS denial pattern suggests likely missing or incomplete supporting documentation.\n"
    "- Billed amount and service coding are generally plausible but need coding-policy verification.\n"
    "- Payer edit behavior indicates administrative denial risk rather than confirmed clinical fraud.\n"
    "Recommendation: Approve"
)

MOCK_APPEAL_LETTER: Final[str] = (
    "Risk Score: 68/100\n"
    "Fraud Probability: 68%\n"
    "Observations:\n"
    "- Denial appears linked to insufficient justification for billed service intensity.\n"
    "- Claim context indicates documentation gaps that can be resolved with corrected submission.\n"
    "- Prior authorization or medical-necessity wording likely needs explicit reinforcement.\n"
    "Recommendation: Flag"
)


def _is_appeal_prompt(prompt: str) -> bool:
    """Detect whether prompt is requesting an appeal letter output."""
    prompt_lower = prompt.lower()
    return "appeal" in prompt_lower or "letter" in prompt_lower


def _build_mock_response(prompt: str) -> str:
    """Return stable predefined responses for hackathon/demo reliability."""
    # Mock mode purpose: deterministic outputs so demos are stable without model/network variance.
    if _is_appeal_prompt(prompt):
        return MOCK_APPEAL_LETTER
    return MOCK_DENIAL_EXPLANATION


def _call_azure_llm(prompt: str) -> str:
    """Call Azure OpenAI in production mode and return response text only."""
    # Azure mode purpose: production-ready integration with real model inference.
    if AzureOpenAI is None:
        logger.error("Azure mode enabled but openai package is unavailable.")
        return ""

    try:
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        if not response.choices:
            logger.warning("Azure OpenAI returned no choices.")
            return ""

        content = response.choices[0].message.content
        return content.strip() if content else ""
    except Exception as exc:
        logger.exception("Azure OpenAI request failed: %s", exc)
        return ""


def call_llm(prompt: str) -> str:
    """Generate text from configured LLM backend while preserving response-only output."""
    if not prompt or not prompt.strip():
        logger.warning("call_llm received an empty prompt.")
        return ""

    llm_mode = settings.LLM_MODE
    try:
        if llm_mode == "mock":
            return _build_mock_response(prompt)
        if llm_mode == "azure":
            return _call_azure_llm(prompt)

        logger.error("Unsupported LLM_MODE '%s'. Falling back to mock response.", llm_mode)
        return _build_mock_response(prompt)
    except Exception as exc:
        logger.exception("LLM call failed in mode '%s': %s", llm_mode, exc)
        return ""
