from typing import Literal
from pydantic import Field
from src.models.schemas.base import ApiModel

DocumentStatus = Literal["uploaded", "processing", "completed", "error"]


class DocumentItem(ApiModel):
    document_id: str = Field(alias="documentId")
    filename: str
    blob_name: str = Field(alias="blobName")
    status: DocumentStatus


class DocumentUploadResult(DocumentItem):
    success: bool = True
