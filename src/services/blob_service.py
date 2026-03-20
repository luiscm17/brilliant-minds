"""Azure Blob Storage service for document management."""

from azure.storage.blob.aio import BlobServiceClient

from src.config.settings import BlobStorageSettings


def _client() -> BlobServiceClient:
    BlobStorageSettings.validate()
    return BlobServiceClient.from_connection_string(BlobStorageSettings.CONNECTION_STRING)


async def upload_document(file_bytes: bytes, filename: str, user_id: str) -> str:
    """Upload a document to Blob Storage. Returns the blob URL."""
    blob_name = f"{user_id}/{filename}"
    async with _client() as client:
        container = client.get_container_client(BlobStorageSettings.CONTAINER)
        await container.upload_blob(blob_name, file_bytes, overwrite=True)
        return f"{client.url}/{BlobStorageSettings.CONTAINER}/{blob_name}"


async def download_document(blob_name: str) -> bytes:
    """Download a document from Blob Storage."""
    async with _client() as client:
        blob = client.get_blob_client(BlobStorageSettings.CONTAINER, blob_name)
        stream = await blob.download_blob()
        return await stream.readall()


async def delete_document(blob_name: str) -> None:
    """Delete a document from Blob Storage."""
    async with _client() as client:
        blob = client.get_blob_client(BlobStorageSettings.CONTAINER, blob_name)
        await blob.delete_blob()
