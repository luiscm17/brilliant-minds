"""Azure Blob Storage service for document management."""

from azure.storage.blob.aio import BlobServiceClient

from src.config.settings import BlobStorageSettings


def _client() -> BlobServiceClient:
    """Create and return an authenticated BlobServiceClient."""
    BlobStorageSettings.validate()
    return BlobServiceClient.from_connection_string(BlobStorageSettings.CONNECTION_STRING)


async def ensure_container():
    """Ensure the blob container exists."""
    async with _client() as client:
        container = client.get_container_client(BlobStorageSettings.AZURE_STORAGE_CONTAINER)
        try:
            await container.create_container()
        except Exception:
            # Already exists or other non-critical error
            pass


async def upload_document(file_bytes: bytes, filename: str, user_id: str) -> str:
    """Upload a document to Blob Storage. Returns the blob URL."""
    await ensure_container()
    blob_name = f"{user_id}/{filename}"
    async with _client() as client:
        container = client.get_container_client(BlobStorageSettings.AZURE_STORAGE_CONTAINER)
        await container.upload_blob(blob_name, file_bytes, overwrite=True)
        return f"{client.url}/{BlobStorageSettings.AZURE_STORAGE_CONTAINER}/{blob_name}"


async def download_document(blob_name: str) -> bytes:
    """Download a document from Blob Storage."""
    await ensure_container()
    async with _client() as client:
        blob = client.get_blob_client(BlobStorageSettings.AZURE_STORAGE_CONTAINER, blob_name)
        stream = await blob.download_blob()
        return await stream.readall()


async def delete_document(blob_name: str) -> None:
    """Delete a document from Blob Storage."""
    await ensure_container()
    async with _client() as client:
        blob = client.get_blob_client(BlobStorageSettings.AZURE_STORAGE_CONTAINER, blob_name)
        await blob.delete_blob()


async def list_documents(user_id: str) -> list[dict]:
    """List documents in Blob Storage for a specific user."""
    await ensure_container()
    prefix = f"{user_id}/"
    documents = []
    async with _client() as client:
        container = client.get_container_client(BlobStorageSettings.AZURE_STORAGE_CONTAINER)
        async for blob in container.list_blobs(name_starts_with=prefix):
            documents.append({
                "name": blob.name,
                "blob_name": blob.name,
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                "document_id": blob.name.split("/")[-1].split("_")[0] if "_" in blob.name else None,
                "filename": "_".join(blob.name.split("/")[-1].split("_")[1:]) if "_" in blob.name else blob.name.split("/")[-1]
            })
    return documents
