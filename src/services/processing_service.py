"""Trigger document processing either inline or via Azure Function."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from urllib import error, request

from src.config.settings import ProcessingTriggerSettings
from src.services import search_service


@dataclass(slots=True)
class ProcessingTriggerPayload:
    """Serializable payload describing an uploaded document."""

    document_id: str
    user_id: str
    filename: str
    blob_name: str
    content_type: str | None = None


def _build_headers() -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "docsimplify-processing-trigger/1.0",
    }
    if ProcessingTriggerSettings.SHARED_SECRET:
        headers["x-docsimplify-processing-secret"] = (
            ProcessingTriggerSettings.SHARED_SECRET
        )
    return headers


def _post_processing_request(payload: ProcessingTriggerPayload) -> None:
    """Send the processing payload to the configured Azure Function."""
    ProcessingTriggerSettings.validate_function_mode()
    assert ProcessingTriggerSettings.FUNCTION_URL is not None

    body = json.dumps(asdict(payload)).encode("utf-8")
    http_request = request.Request(
        ProcessingTriggerSettings.FUNCTION_URL,
        data=body,
        headers=_build_headers(),
        method="POST",
    )
    timeout = max(1, ProcessingTriggerSettings.TIMEOUT_SECONDS)

    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            status_code = getattr(response, "status", 200)
            if status_code >= 400:
                raise RuntimeError(
                    f"Azure Function returned unexpected status {status_code}"
                )
    except error.HTTPError as exc:
        raise RuntimeError(
            f"Azure Function rejected the processing trigger with status {exc.code}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(
            "Azure Function trigger is unreachable. Check PROCESSING_FUNCTION_URL."
        ) from exc


async def trigger_document_processing(payload: ProcessingTriggerPayload) -> str:
    """Trigger processing using the configured delivery mode."""
    if ProcessingTriggerSettings.use_azure_function():
        await asyncio.to_thread(_post_processing_request, payload)
        return "queued"

    await search_service.run_layout_indexer()
    return "processing"
