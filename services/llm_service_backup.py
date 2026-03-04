from __future__ import annotations

import logging
from functools import lru_cache

from openai import AzureOpenAI

from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a healthcare revenue cycle expert."


@lru_cache(maxsize=1)
def _get_client() -> AzureOpenAI:
    """Create and cache an Azure OpenAI client instance."""
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )


def call_llm(prompt: str) -> str:
    """Call Azure OpenAI chat completions API and return only response text."""
    if not prompt or not prompt.strip():
        logger.warning("call_llm received an empty prompt.")
        return ""

    if not settings.AZURE_OPENAI_DEPLOYMENT:
        logger.error("AZURE_OPENAI_DEPLOYMENT is not configured.")
        return ""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content if response.choices else ""
        return content.strip() if content else ""
    except Exception as exc:
        logger.exception("Azure OpenAI request failed: %s", exc)
        return ""
