"""End-to-end smoke test for the RAG-V3 text and image indexes.

Uploads a PDF to Blob Storage, triggers the Azure Search indexer, and scans the
text/image indexes until the document appears or the timeout is reached.
"""

from __future__ import annotations

import argparse
import asyncio
import uuid
from pathlib import Path

from azure.core.exceptions import ResourceExistsError
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes import SearchIndexerClient
from dotenv import load_dotenv

from src.config.settings import AISearchSettings, RagV3Settings
from src.services import blob_service, search_service


def _safe_text(value: object, limit: int = 180) -> str:
    text = str(value or "")[:limit]
    return text.encode("ascii", errors="replace").decode("ascii")


def _indexer_status_client() -> SearchIndexerClient:
    return SearchIndexerClient(
        endpoint=AISearchSettings.get_endpoint(),
        credential=AzureKeyCredential(AISearchSettings.get_api_key()),
    )


async def _get_indexer_last_result_signature() -> str:
    client = _indexer_status_client()
    status = await asyncio.to_thread(client.get_indexer_status, RagV3Settings.INDEXER_NAME)
    last_result = getattr(status, "last_result", None)
    if not last_result:
        return "none"
    return "|".join(
        [
            str(getattr(last_result, "status", "") or ""),
            str(getattr(last_result, "start_time", "") or ""),
            str(getattr(last_result, "end_time", "") or ""),
        ]
    )


async def _wait_for_indexer_idle(
    delay_seconds: int,
    max_checks: int,
) -> None:
    client = _indexer_status_client()
    for check in range(1, max_checks + 1):
        status = await asyncio.to_thread(client.get_indexer_status, RagV3Settings.INDEXER_NAME)
        state = str(getattr(status, "status", "") or "").lower()
        print(f"indexer_state_check={check} state={state}")
        if state != "running":
            return
        await asyncio.sleep(delay_seconds)


async def _wait_for_indexer_cycle(
    before_signature: str,
    delay_seconds: int,
    max_checks: int,
) -> None:
    client = _indexer_status_client()
    for check in range(1, max_checks + 1):
        status = await asyncio.to_thread(client.get_indexer_status, RagV3Settings.INDEXER_NAME)
        state = str(getattr(status, "status", "") or "").lower()
        last_result = getattr(status, "last_result", None)
        current_signature = (
            "none"
            if not last_result
            else "|".join(
                [
                    str(getattr(last_result, "status", "") or ""),
                    str(getattr(last_result, "start_time", "") or ""),
                    str(getattr(last_result, "end_time", "") or ""),
                ]
            )
        )
        print(
            "indexer_cycle_check="
            f"{check} state={state} signature_changed={current_signature != before_signature}"
        )
        if state != "running" and current_signature != before_signature:
            return
        await asyncio.sleep(delay_seconds)


async def _collect_hits(
    client: SearchClient,
    marker: str,
    select: list[str],
    limit: int,
) -> list[dict]:
    hits: list[dict] = []
    results = await client.search(search_text="*", top=limit, select=select)
    async for item in results:
        title = str(item.get("document_title", "")).lower()
        path = str(item.get("metadata_storage_path", "")).lower()
        if marker in title or marker in path:
            hits.append(item)
    return hits


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run a RAG-V3 smoke test.")
    parser.add_argument(
        "--file",
        default="test-visual-ragv3.pdf",
        help="PDF file to upload and validate.",
    )
    parser.add_argument(
        "--user-id",
        default="ragv3-smoke",
        help="Synthetic user id prefix for the blob path.",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=12,
        help="How many polling attempts to run.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=int,
        default=20,
        help="Delay between polling attempts.",
    )
    parser.add_argument(
        "--scan-limit",
        type=int,
        default=300,
        help="How many docs to scan per index on each attempt.",
    )
    parser.add_argument(
        "--indexer-wait-checks",
        type=int,
        default=12,
        help="How many checks to wait for an already-running indexer to finish.",
    )
    args = parser.parse_args()

    load_dotenv(".env")

    file_path = Path(args.file)
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")

    document_id = str(uuid.uuid4())
    stored_name = f"{document_id}_{file_path.name}"
    marker = stored_name.lower()

    blob_url = await blob_service.upload_document(
        file_path.read_bytes(),
        stored_name,
        args.user_id,
    )
    print(f"uploaded_blob={blob_url}")
    before_signature = await _get_indexer_last_result_signature()

    try:
        await search_service.run_layout_indexer()
        print("indexer_triggered=true")
    except ResourceExistsError:
        print("indexer_triggered=already-running")
        await _wait_for_indexer_idle(
            delay_seconds=args.delay_seconds,
            max_checks=args.indexer_wait_checks,
        )
        await search_service.run_layout_indexer()
        print("indexer_triggered=after-wait")

    await _wait_for_indexer_cycle(
        before_signature=before_signature,
        delay_seconds=args.delay_seconds,
        max_checks=args.indexer_wait_checks,
    )

    text_client = SearchClient(
        endpoint=AISearchSettings.get_endpoint(),
        index_name=RagV3Settings.INDEX_NAME,
        credential=AzureKeyCredential(AISearchSettings.get_api_key()),
    )
    image_client = SearchClient(
        endpoint=AISearchSettings.get_endpoint(),
        index_name=RagV3Settings.IMAGE_INDEX_NAME,
        credential=AzureKeyCredential(AISearchSettings.get_api_key()),
    )

    try:
        text_hits: list[dict] = []
        image_hits: list[dict] = []

        for attempt in range(1, args.attempts + 1):
            text_hits = await _collect_hits(
                text_client,
                marker,
                ["document_title", "metadata_storage_path", "page_number", "content"],
                args.scan_limit,
            )
            image_hits = await _collect_hits(
                image_client,
                marker,
                [
                    "document_title",
                    "metadata_storage_path",
                    "page_number",
                    "image_path",
                    "image_caption",
                ],
                args.scan_limit,
            )

            print(
                f"attempt={attempt} text_hits={len(text_hits)} image_hits={len(image_hits)}"
            )
            if text_hits or image_hits:
                break
            await asyncio.sleep(args.delay_seconds)

        print(f"final_text_hits={len(text_hits)}")
        print(f"final_image_hits={len(image_hits)}")

        if text_hits:
            sample = text_hits[0]
            print(f"text_title={_safe_text(sample.get('document_title'))}")
            print(f"text_page={_safe_text(sample.get('page_number'))}")
            print(f"text_content={_safe_text(sample.get('content'))}")

        if image_hits:
            sample = image_hits[0]
            print(f"image_path={_safe_text(sample.get('image_path'))}")
            print(f"image_page={_safe_text(sample.get('page_number'))}")
            print(f"image_caption={_safe_text(sample.get('image_caption'))}")

        return 0 if text_hits or image_hits else 1
    finally:
        await text_client.close()
        await image_client.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
