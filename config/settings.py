from __future__ import annotations

import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


def _get_required_env(var_name: str) -> str:
    """Return a required environment variable or raise a clear configuration error."""
    value = os.getenv(var_name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {var_name}. "
            "Set Azure OpenAI credentials before starting the application."
        )
    return value

def _resolve_llm_mode() -> str:
    """Resolve LLM mode with backward compatibility for USE_MOCK_LLM."""
    llm_mode = os.getenv("LLM_MODE", "").strip().lower()
    if llm_mode in {"mock", "azure"}:
        return llm_mode

    # Backward compatibility: legacy flag takes effect when LLM_MODE is not set.
    legacy_use_mock = os.getenv("USE_MOCK_LLM", "").strip().lower()
    if legacy_use_mock == "true":
        return "mock"
    if legacy_use_mock == "false":
        return "azure"

    # Default mode for hackathon/demo stability.
    return "mock"


LLM_MODE: Final[str] = _resolve_llm_mode()
USE_MOCK_LLM: Final[bool] = LLM_MODE == "mock"

if LLM_MODE == "azure":
    # Production mode: enforce Azure credentials strictly.
    AZURE_OPENAI_API_KEY: Final[str] = _get_required_env("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Final[str] = _get_required_env("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT: Final[str] = _get_required_env("AZURE_OPENAI_DEPLOYMENT")
else:
    # Mock mode: keep optional placeholders so local runs do not require Azure secrets.
    AZURE_OPENAI_API_KEY: Final[str] = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    AZURE_OPENAI_ENDPOINT: Final[str] = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    AZURE_OPENAI_DEPLOYMENT: Final[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

AZURE_OPENAI_API_VERSION: Final[str] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01").strip()
