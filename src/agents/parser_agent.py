"""Parser Agent — extracts clean text from PDF/Word using Azure Document Intelligence."""

import io
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from src.config.settings import DocumentIntelligenceSettings

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


async def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from a PDF or Word document."""
    settings = DocumentIntelligenceSettings
    if not settings.ENDPOINT or not settings.KEY:
        # Fallback: return raw bytes decoded as utf-8 (for plain text files in dev)
        try:
            return file_bytes.decode("utf-8")
        except Exception:
            return ""

    async with DocumentIntelligenceClient(
        endpoint=settings.ENDPOINT,
        credential=AzureKeyCredential(settings.KEY),
    ) as client:
        poller = await client.begin_analyze_document(
            "prebuilt-read",
            analyze_request=file_bytes,
            content_type="application/octet-stream",
        )
        result = await poller.result()
        return result.content or ""


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks of ~CHUNK_SIZE words."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + CHUNK_SIZE
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks or [text]
