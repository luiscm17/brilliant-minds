import secrets
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from src.core.dependencies import get_current_user_id
from src.models.schemas.documents import DocumentItem, DocumentUploadResult
from src.services import blob_service

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


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
    """Upload a document exclusively to Blob Storage."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )

    file_bytes = await file.read()
    document_id = secrets.token_hex(6)
    filename = file.filename or f"document-{document_id}"

    # Store with a unique prefix to avoid collisions
    unique_filename = f"{document_id}_{filename}"

    try:
        blob_url = await blob_service.upload_document(
            file_bytes, unique_filename, user_id
        )
        return DocumentUploadResult(
            success=True,
            documentId=document_id,
            filename=filename,
            blobName=f"{user_id}/{unique_filename}",
            status="uploaded",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload to storage: {str(e)}",
        )


@router.get("", response_model=list[DocumentItem], response_model_by_alias=True)
async def list_documents(user_id: str = Depends(get_current_user_id)):
    """List documents directly from Blob Storage."""
    items = await blob_service.list_documents(user_id)
    return [
        DocumentItem(
            documentId=item["document_id"] or "unknown",
            filename=item["filename"],
            blobName=item["blob_name"],
            status="uploaded",
        )
        for item in items
    ]


@router.get("/{blob_name:path}")
async def download_document(
    blob_name: str, user_id: str = Depends(get_current_user_id)
):
    """Download a document from Blob Storage."""
    # Security: Ensure user only downloads their own blobs
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )


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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
