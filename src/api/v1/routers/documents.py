"""Documents router for upload/list/delete with a frontend-friendly contract."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.agents.parser_agent import chunk_text, extract_text
from src.core.dependencies import get_current_user_id
from src.models.schemas import DocumentItem, DocumentUploadResult
from src.services import blob_service, cosmos_service, search_service

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


def _normalize_document_status(status: str | None) -> str:
    if not status:
        return "completed"

    normalized = status.strip().lower()
    legacy_map = {
        "indexed": "completed",
        "done": "completed",
        "queued": "processing",
        "uploading": "processing",
        "failed": "error",
    }
    return legacy_map.get(normalized, normalized)


def _to_document_item(item: dict) -> DocumentItem:
    return DocumentItem(
        documentId=item["document_id"],
        filename=item["filename"],
        status=_normalize_document_status(item.get("status")),
    )


@router.post("", response_model=DocumentUploadResult, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF, DOC, DOCX, and plain text files are supported",
        )

    file_bytes = await file.read()
    document_id = str(uuid.uuid4())
    filename = file.filename or f"document-{document_id}"
    blob_name = f"{user_id}/{document_id}_{filename}"
    blob_url = None
    document_status = "completed"

    try:
        blob_url = await blob_service.upload_document(file_bytes, f"{document_id}_{filename}", user_id)
    except Exception:
        document_status = "processing"

    if search_service.layout_rag_enabled() and blob_url:
        try:
            await search_service.run_layout_indexer()
            document_status = "processing"
        except Exception:
            if document_status == "completed":
                document_status = "processing"
    else:
        try:
            text = await extract_text(file_bytes, filename)
            if text.strip():
                chunks = chunk_text(text)
                await search_service.index_document(document_id, user_id, filename, chunks)
        except Exception:
            if document_status == "completed":
                document_status = "processing"

    metadata = await cosmos_service.save_document_metadata(
        document_id=document_id,
        user_id=user_id,
        filename=filename,
        blob_url=blob_url,
        blob_name=blob_name,
        status=document_status,
    )

    return DocumentUploadResult(
        success=True,
        documentId=metadata["document_id"],
        filename=metadata["filename"],
        status=metadata["status"],
    )


@router.get("", response_model=list[DocumentItem])
async def list_documents(user_id: str = Depends(get_current_user_id)):
    items = await cosmos_service.list_user_documents(user_id)
    if search_service.layout_rag_enabled():
        for item in items:
            if _normalize_document_status(item.get("status")) != "processing":
                continue

            ready = await search_service.layout_document_ready(
                blob_url=item.get("blob_url"),
                blob_name=item.get("blob_name"),
                user_id=user_id,
                document_id=item["document_id"],
            )
            if ready:
                updated = await cosmos_service.update_document_status(
                    item["document_id"],
                    user_id,
                    "completed",
                )
                if updated:
                    item.update(updated)
    return [_to_document_item(item) for item in items]


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    metadata = await cosmos_service.get_document_metadata(document_id, user_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    blob_name = metadata.get("blob_name")
    if blob_name:
        try:
            await blob_service.delete_document(blob_name)
        except Exception:
            pass

    try:
        await search_service.delete_document_chunks(document_id)
    except Exception:
        pass

    await cosmos_service.delete_document_metadata(document_id, user_id)
    return {"status": "deleted"}
