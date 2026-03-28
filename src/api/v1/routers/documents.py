import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from src.core.dependencies import get_current_user_id
from src.models.schemas.documents import DocumentItem, DocumentUploadResult
from src.services import blob_service, processing_service, search_service

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

LAYOUT_RAG_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _is_layout_candidate(filename: str) -> bool:
    extension = Path(filename).suffix.lower()
    return extension in {".pdf", ".doc", ".docx"}


def _normalize_document_status(status: str | None) -> str:
    if not status:
        return "uploaded"

    normalized = status.strip().lower()
    if normalized in {"queued", "uploading", "uploaded"}:
        return "processing" if search_service.layout_rag_enabled() else "uploaded"
    if normalized in {"indexed", "done"}:
        return "completed"
    if normalized in {"failed"}:
        return "error"
    return normalized


@router.post(
    "",
    response_model=DocumentUploadResult,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=True,
)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    """Upload a document to Blob Storage and trigger the layout RAG flow when enabled."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )

    file_bytes = await file.read()
    document_id = secrets.token_hex(6)
    filename = file.filename or f"document-{document_id}"
    unique_filename = f"{document_id}_{filename}"
    blob_name = f"{user_id}/{unique_filename}"

    try:
        await blob_service.upload_document(file_bytes, unique_filename, user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload to storage: {str(exc)}",
        ) from exc

    should_trigger_layout = (
        search_service.layout_rag_enabled()
        and (
            file.content_type in LAYOUT_RAG_TYPES
            or _is_layout_candidate(filename)
        )
    )

    document_status = "uploaded"
    if should_trigger_layout:
        try:
            document_status = await processing_service.trigger_document_processing(
                processing_service.ProcessingTriggerPayload(
                    document_id=document_id,
                    user_id=user_id,
                    filename=filename,
                    blob_name=blob_name,
                    content_type=file.content_type,
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Document was uploaded but the indexing pipeline is currently unavailable."
                ),
            ) from exc

    return DocumentUploadResult(
        success=True,
        documentId=document_id,
        filename=filename,
        blobName=blob_name,
        status=document_status,
    )


@router.get("", response_model=list[DocumentItem], response_model_by_alias=True)
async def list_documents(user_id: str = Depends(get_current_user_id)):
    """List documents from Blob Storage and derive RAG status when layout indexing is enabled."""
    items = await blob_service.list_documents(user_id)
    documents: list[DocumentItem] = []

    for item in items:
        document_id = item["document_id"] or "unknown"
        filename = item["filename"]
        blob_name = item["blob_name"]
        status_value = "uploaded"

        if search_service.layout_rag_enabled() and _is_layout_candidate(filename):
            ready = await search_service.layout_document_ready(
                blob_url=None,
                blob_name=blob_name,
                user_id=user_id,
                document_id=document_id,
            )
            if ready:
                status_value = "completed"
            else:
                failed = await search_service.layout_document_failed(
                    blob_url=None,
                    blob_name=blob_name,
                    document_id=document_id,
                )
                status_value = "error" if failed else "processing"

        documents.append(
            DocumentItem(
                documentId=document_id,
                filename=filename,
                blobName=blob_name,
                status=_normalize_document_status(status_value),
            )
        )

    return documents


@router.get("/{blob_name:path}")
async def download_document(
    blob_name: str, user_id: str = Depends(get_current_user_id)
):
    """Download a document from Blob Storage."""
    if not blob_name.startswith(f"{user_id}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    try:
        content = await blob_service.download_document(blob_name)
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={blob_name.split('/')[-1]}"
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        ) from exc


@router.delete("/{blob_name:path}", status_code=status.HTTP_200_OK)
async def delete_document(blob_name: str, user_id: str = Depends(get_current_user_id)):
    """Delete a document from Blob Storage."""
    if not blob_name.startswith(f"{user_id}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    try:
        await blob_service.delete_document(blob_name)
        return {"status": "deleted", "blob_name": blob_name}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        ) from exc
