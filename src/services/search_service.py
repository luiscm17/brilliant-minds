"""Azure AI Search service for classic vector RAG and layout-based rag-v2."""

import asyncio
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from openai import AsyncAzureOpenAI

from src.config.settings import (
    AgenticRagSettings,
    AzureSearchSettings,
    LayoutRagSettings,
    OpenAISettings,
)
from src.services.search.rag_pipeline import run_pipeline


def _search_client(index_name: str | None = None) -> SearchClient:
    AzureSearchSettings.validate()
    return SearchClient(
        endpoint=AzureSearchSettings.ENDPOINT,
        index_name=index_name or AzureSearchSettings.INDEX,
        credential=AzureKeyCredential(AzureSearchSettings.KEY),
    )


def _index_client() -> SearchIndexClient:
    AzureSearchSettings.validate()
    return SearchIndexClient(
        endpoint=AzureSearchSettings.ENDPOINT,
        credential=AzureKeyCredential(AzureSearchSettings.KEY),
    )


def _indexer_client() -> SearchIndexerClient:
    AzureSearchSettings.validate()
    return SearchIndexerClient(
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
        model=OpenAISettings.EMBEDDING_DEPLOYMENT,
        input=text,
    )
    return response.data[0].embedding


def agentic_rag_enabled() -> bool:
    """Return whether Azure AI Search knowledge assets should be managed."""
    return AgenticRagSettings.ENABLED


def layout_rag_enabled() -> bool:
    """Return whether the app should use the Azure Search layout index."""
    return LayoutRagSettings.ENABLED


async def ensure_agentic_assets() -> None:
    """Create or update agentic retrieval assets when explicitly enabled."""
    if not agentic_rag_enabled():
        return
    await asyncio.to_thread(run_pipeline)


async def ensure_index_exists() -> None:
    """Create the vector index used by the current retrieval flow if needed."""
    async with _index_client() as client:
        index = SearchIndex(
            name=AzureSearchSettings.INDEX,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SimpleField(
                    name="document_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="user_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
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
                profiles=[
                    VectorSearchProfile(
                        name="default-profile",
                        algorithm_configuration_name="default-algo",
                    )
                ],
            ),
        )
        try:
            await client.create_index(index)
        except Exception:
            pass


async def index_document(
    document_id: str,
    user_id: str,
    filename: str,
    chunks: list[str],
) -> None:
    """Generate embeddings, upload chunks, and optionally refresh agentic assets."""
    await ensure_index_exists()
    documents = []
    for index, chunk in enumerate(chunks):
        embedding = await _get_embedding(chunk)
        documents.append(
            {
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "user_id": user_id,
                "chunk_index": index,
                "filename": filename,
                "content": chunk,
                "content_vector": embedding,
            }
        )

    async with _search_client() as client:
        await client.upload_documents(documents=documents)

    if agentic_rag_enabled():
        await ensure_agentic_assets()


async def run_layout_indexer() -> None:
    """Run the configured layout indexer after uploading a document to Blob."""
    if not layout_rag_enabled():
        return
    async with _indexer_client() as client:
        await client.run_indexer(LayoutRagSettings.INDEXER_NAME)


def _normalize_layout_path(value: str | None) -> str:
    return (value or "").strip().lower()


def _matches_layout_result(
    path: str,
    user_id: str | None = None,
    document_ids: list[str] | None = None,
) -> bool:
    normalized_path = _normalize_layout_path(path)
    if not normalized_path:
        return False

    if user_id:
        user_marker = f"/{user_id.lower()}/"
        if user_marker not in normalized_path:
            return False

    if document_ids:
        allowed = [f"{document_id.lower()}_" for document_id in document_ids]
        if not any(marker in normalized_path for marker in allowed):
            return False

    return True


def _format_layout_result(result: dict) -> str:
    content = str(result.get(LayoutRagSettings.CONTENT_FIELD, "") or "").strip()
    if not content:
        return ""

    title = str(result.get(LayoutRagSettings.TITLE_FIELD, "") or "").strip()
    page = result.get(LayoutRagSettings.PAGE_FIELD)
    prefix_parts = []
    if title:
        prefix_parts.append(title)
    if page not in (None, ""):
        prefix_parts.append(f"pagina {page}")

    if prefix_parts:
        return f"[{' | '.join(prefix_parts)}]\n{content}"
    return content


async def _search_layout_context(query: str, top_k: int = 5) -> list[str]:
    """Search the Azure Search layout index created for rag-v2."""
    query_vector = await _get_embedding(query)
    candidate_top = max(top_k * 6, 20)
    async with _search_client(LayoutRagSettings.INDEX_NAME) as client:
        from azure.search.documents.models import VectorizedQuery

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top_k,
            fields=LayoutRagSettings.VECTOR_FIELD,
        )
        try:
            results = await client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=candidate_top,
                select=[
                    LayoutRagSettings.CONTENT_FIELD,
                    LayoutRagSettings.TITLE_FIELD,
                    LayoutRagSettings.PAGE_FIELD,
                    LayoutRagSettings.PATH_FIELD,
                ],
            )
        except Exception:
            # Some portal-created indexes do not expose the vector field name we expect.
            results = await client.search(
                search_text=query,
                top=candidate_top,
                select=[
                    LayoutRagSettings.CONTENT_FIELD,
                    LayoutRagSettings.TITLE_FIELD,
                    LayoutRagSettings.PAGE_FIELD,
                    LayoutRagSettings.PATH_FIELD,
                ],
            )

        chunks = []
        async for result in results:
            formatted = _format_layout_result(result)
            if formatted:
                chunks.append(formatted)
            if len(chunks) >= top_k:
                break
        return chunks


async def _search_filtered_layout_context(
    query: str,
    top_k: int = 5,
    user_id: str | None = None,
    document_ids: list[str] | None = None,
) -> list[str]:
    query_vector = await _get_embedding(query)
    candidate_top = max(top_k * 8, 30)
    async with _search_client(LayoutRagSettings.INDEX_NAME) as client:
        from azure.search.documents.models import VectorizedQuery

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=max(top_k, 10),
            fields=LayoutRagSettings.VECTOR_FIELD,
        )
        try:
            results = await client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=candidate_top,
                select=[
                    LayoutRagSettings.CONTENT_FIELD,
                    LayoutRagSettings.TITLE_FIELD,
                    LayoutRagSettings.PAGE_FIELD,
                    LayoutRagSettings.PATH_FIELD,
                ],
            )
        except Exception:
            results = await client.search(
                search_text=query,
                top=candidate_top,
                select=[
                    LayoutRagSettings.CONTENT_FIELD,
                    LayoutRagSettings.TITLE_FIELD,
                    LayoutRagSettings.PAGE_FIELD,
                    LayoutRagSettings.PATH_FIELD,
                ],
            )

        chunks = []
        async for result in results:
            result_path = str(result.get(LayoutRagSettings.PATH_FIELD, "") or "")
            if not _matches_layout_result(
                result_path,
                user_id=user_id,
                document_ids=document_ids,
            ):
                continue
            formatted = _format_layout_result(result)
            if formatted:
                chunks.append(formatted)
            if len(chunks) >= top_k:
                break
        return chunks


async def layout_document_ready(
    blob_url: str | None,
    blob_name: str | None,
    user_id: str,
    document_id: str,
) -> bool:
    if not layout_rag_enabled():
        return False

    identifiers = [identifier for identifier in [blob_url, blob_name, document_id] if identifier]
    async with _search_client(LayoutRagSettings.INDEX_NAME) as client:
        for identifier in identifiers:
            try:
                results = await client.search(
                    search_text=str(identifier),
                    top=10,
                    select=[LayoutRagSettings.PATH_FIELD],
                )
            except Exception:
                continue

            async for result in results:
                result_path = str(result.get(LayoutRagSettings.PATH_FIELD, "") or "")
                if (
                    _matches_layout_result(
                        result_path,
                        user_id=user_id,
                        document_ids=[document_id],
                    )
                    or _normalize_layout_path(str(identifier))
                    in _normalize_layout_path(result_path)
                ):
                    return True

    return False


async def search_context(
    query: str,
    user_id: str,
    top_k: int = 5,
    document_ids: list[str] | None = None,
) -> list[str]:
    """Search for the most relevant chunks for a given query."""
    if layout_rag_enabled():
        return await _search_filtered_layout_context(
            query,
            top_k=top_k,
            user_id=user_id,
            document_ids=document_ids,
        )

    query_vector = await _get_embedding(query)
    filters = [f"user_id eq '{user_id}'"]
    if document_ids:
        doc_filter = " or ".join(f"document_id eq '{doc_id}'" for doc_id in document_ids)
        filters.append(f"({doc_filter})")

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
            filter=" and ".join(filters),
            top=top_k,
        )
        chunks = []
        async for result in results:
            chunks.append(result["content"])
        return chunks


async def delete_document_chunks(document_id: str) -> None:
    """Delete all indexed chunks for a document."""
    if layout_rag_enabled():
        return

    async with _search_client() as client:
        results = await client.search(
            search_text="*",
            filter=f"document_id eq '{document_id}'",
            select=["id"],
        )
        ids = [{"id": result["id"]} async for result in results]
        if ids:
            await client.delete_documents(documents=ids)
