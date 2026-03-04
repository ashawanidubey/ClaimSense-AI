from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from agents.claim_agent import process_claim

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ClaimSense AI API",
    version="1.0.0",
    description="Backend service for claim document analysis.",
)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def _validate_file(file: UploadFile) -> None:
    """Validate uploaded file metadata before reading content."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must include a filename.",
        )


def _read_upload_content(content: bytes) -> str:
    """Decode uploaded content safely as UTF-8 text."""
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max supported size is {MAX_FILE_SIZE_BYTES} bytes.",
        )

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode file as UTF-8 text.",
        ) from exc


@app.post("/analyze-claim", status_code=status.HTTP_200_OK)
async def analyze_claim(file: UploadFile = File(...)) -> dict[str, Any]:
    """Analyze an uploaded claim document and return structured results."""
    _validate_file(file)

    try:
        raw_content: bytes = await file.read()
        claim_text: str = _read_upload_content(raw_content)

        analysis: Any = process_claim(claim_text)

        return {
            "status": "success",
            "filename": file.filename,
            "analysis": analysis,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error while analyzing claim: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during claim analysis.",
        ) from exc
    finally:
        await file.close()
