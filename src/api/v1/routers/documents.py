"""Documents router — upload, list, delete with automatic RAG pipeline."""

import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.core.dependencies import get_current_user_id
from src.models.schemas import DocumentList, DocumentResponse
from src.services import blob_service, cosmos_service, search_service
from src.agents.parser_agent import extract_text, chunk_text

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF, DOCX, and plain text files are supported",
        )

    file_bytes = await file.read()
    document_id = str(uuid.uuid4())
    filename = f"{document_id}_{file.filename}"

    # 1. Upload to Blob Storage
    blob_url = await blob_service.upload_document(file_bytes, filename, user_id)

    # 2. Extract text via Document Intelligence
    text = await extract_text(file_bytes, file.filename)

    # 3. Chunk and index in Azure AI Search (RAG pipeline)
    if text.strip():
        chunks = chunk_text(text)
        await search_service.index_document(document_id, user_id, file.filename, chunks)

    # 4. Save metadata in Cosmos DB
    metadata = await cosmos_service.save_document_metadata(document_id, user_id, file.filename, blob_url)

    return DocumentResponse(
        document_id=metadata["document_id"],
        filename=metadata["filename"],
        status=metadata["status"],
        user_id=metadata["user_id"],
        blob_url=metadata["blob_url"],
        uploaded_at=metadata["uploaded_at"],
    )


@router.get("", response_model=DocumentList)
async def list_documents(user_id: str = Depends(get_current_user_id)):
    items = await cosmos_service.list_user_documents(user_id)
    docs = [
        DocumentResponse(
            document_id=item["document_id"],
            filename=item["filename"],
            status=item["status"],
            user_id=item["user_id"],
            blob_url=item.get("blob_url"),
            uploaded_at=item["uploaded_at"],
        )
        for item in items
    ]
    return DocumentList(documents=docs, total=len(docs))


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    # Delete from Blob Storage
    blob_name = f"{user_id}/{document_id}"
    try:
        await blob_service.delete_document(blob_name)
    except Exception:
        pass  # Already deleted or not found

    # Delete indexed chunks from Azure AI Search
    await search_service.delete_document_chunks(document_id)

    # Delete metadata from Cosmos DB
    await cosmos_service.delete_document_metadata(document_id, user_id)

    return {"status": "deleted", "document_id": document_id}
