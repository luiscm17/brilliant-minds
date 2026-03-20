"""Azure AI Search service for RAG — indexing and retrieval of document chunks."""

import json
import uuid
from typing import Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchField as VectorField,
)
from openai import AsyncAzureOpenAI

from src.config.settings import AzureSearchSettings, OpenAISettings


def _search_client() -> SearchClient:
    AzureSearchSettings.validate()
    return SearchClient(
        endpoint=AzureSearchSettings.ENDPOINT,
        index_name=AzureSearchSettings.INDEX,
        credential=AzureKeyCredential(AzureSearchSettings.KEY),
    )


def _index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=AzureSearchSettings.ENDPOINT,
        credential=AzureKeyCredential(AzureSearchSettings.KEY),
    )


async def _get_embedding(text: str) -> list[float]:
    client = AsyncAzureOpenAI(
        azure_endpoint=OpenAISettings.ENDPOINT,
        api_key=OpenAISettings.API_KEY,
        api_version="2024-02-01",
    )
    response = await client.embeddings.create(
        model=OpenAISettings.EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def ensure_index_exists() -> None:
    """Create the search index if it does not exist."""
    async with _index_client() as client:
        index = SearchIndex(
            name=AzureSearchSettings.INDEX,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="user_id", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="chunk_index", type=SearchFieldDataType.Int32),
                SimpleField(name="filename", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="default-profile",
                ),
            ],
            vector_search=VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="default-algo")],
                profiles=[VectorSearchProfile(name="default-profile", algorithm_configuration_name="default-algo")],
            ),
        )
        try:
            await client.create_index(index)
        except Exception:
            pass  # Index already exists


async def index_document(document_id: str, user_id: str, filename: str, chunks: list[str]) -> None:
    """Generate embeddings for each chunk and index them in Azure AI Search."""
    await ensure_index_exists()
    docs = []
    for i, chunk in enumerate(chunks):
        embedding = await _get_embedding(chunk)
        docs.append({
            "id": str(uuid.uuid4()),
            "document_id": document_id,
            "user_id": user_id,
            "chunk_index": i,
            "filename": filename,
            "content": chunk,
            "content_vector": embedding,
        })
    async with _search_client() as client:
        await client.upload_documents(documents=docs)


async def search_context(query: str, user_id: str, top_k: int = 5) -> list[str]:
    """Search for the most relevant chunks for a given query and user."""
    query_vector = await _get_embedding(query)
    async with _search_client() as client:
        from azure.search.documents.models import VectorizedQuery
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top_k,
            fields="content_vector",
        )
        results = await client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=f"user_id eq '{user_id}'",
            top=top_k,
        )
        chunks = []
        async for result in results:
            chunks.append(result["content"])
        return chunks


async def delete_document_chunks(document_id: str) -> None:
    """Delete all indexed chunks for a document."""
    async with _search_client() as client:
        results = await client.search(
            search_text="*",
            filter=f"document_id eq '{document_id}'",
            select=["id"],
        )
        ids = [{"id": r["id"]} async for r in results]
        if ids:
            await client.delete_documents(documents=ids)
