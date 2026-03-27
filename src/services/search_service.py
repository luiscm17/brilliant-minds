"""Azure AI Search service for classic vector RAG and layout-based rag-v2/rag-v3."""

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
    AISearchSettings,
    BlobStorageSettings,
    LayoutRagSettings,
    OpenAISettings,
    RagV3Settings,
)
from src.services.search.rag_pipeline import run_pipeline


def _search_client(index_name: str | None = None) -> SearchClient:
    """Create and return an authenticated SearchClient for the specified index."""
    AISearchSettings.validate()
    return SearchClient(
        endpoint=AISearchSettings.get_endpoint(),
        index_name=index_name or AISearchSettings.get_index_name(),
        credential=AzureKeyCredential(AISearchSettings.get_api_key()),
    )


def _index_client() -> SearchIndexClient:
    """Create and return an authenticated SearchIndexClient for index management."""
    AISearchSettings.validate()
    return SearchIndexClient(
        endpoint=AISearchSettings.get_endpoint(),
        credential=AzureKeyCredential(AISearchSettings.get_api_key()),
    )


def _indexer_client() -> SearchIndexerClient:
    """Create and return an authenticated SearchIndexerClient for indexer management."""
    AISearchSettings.validate()
    return SearchIndexerClient(
        endpoint=AISearchSettings.get_endpoint(),
        credential=AzureKeyCredential(AISearchSettings.get_api_key()),
    )


def _classic_embedding_dimensions() -> int:
    """Return the embedding dimensions for classic vector search."""
    return 1536


async def _get_embedding(text: str, dimensions: int | None = None) -> list[float]:
    """Generate embedding vector for the given text using Azure OpenAI."""
    async with AsyncAzureOpenAI(
        azure_endpoint=OpenAISettings.ENDPOINT,
        api_key=OpenAISettings.API_KEY,
        api_version="2024-02-01",
    ) as client:
        request_kwargs = {
            "model": OpenAISettings.EMBEDDING_DEPLOYMENT,
            "input": text,
        }
        if dimensions is not None:
            request_kwargs["dimensions"] = dimensions
        response = await client.embeddings.create(**request_kwargs)
        return response.data[0].embedding


def agentic_rag_enabled() -> bool:
    """Return whether Azure AI Search knowledge assets should be managed."""
    return AgenticRagSettings.ENABLED


def layout_rag_enabled() -> bool:
    """Return whether the app should use the Azure Search layout index."""
    return LayoutRagSettings.ENABLED or RagV3Settings.ENABLED


def rag_v3_enabled() -> bool:
    """Return whether the app should use the multimodal-ready rag-v3 index."""
    return RagV3Settings.ENABLED


def _active_layout_settings():
    """Return the active layout settings based on RAG version."""
    return RagV3Settings if rag_v3_enabled() else LayoutRagSettings


def _active_image_index_name() -> str | None:
    """Return the active image index name for RAG v3, or None for other versions."""
    if rag_v3_enabled():
        return RagV3Settings.IMAGE_INDEX_NAME
    return None


async def ensure_agentic_assets() -> None:
    """Create or update agentic retrieval assets when explicitly enabled."""
    if not agentic_rag_enabled():
        return
    await asyncio.to_thread(run_pipeline)


async def ensure_index_exists() -> None:
    """Create the vector index used by the current retrieval flow if needed."""
    async with _index_client() as client:
        index = SearchIndex(
            name=AISearchSettings.get_index_name(),
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
                    vector_search_dimensions=_classic_embedding_dimensions(),
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
        embedding = await _get_embedding(
            chunk,
            dimensions=_classic_embedding_dimensions(),
        )
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
    active_settings = _active_layout_settings()
    async with _indexer_client() as client:
        await client.run_indexer(active_settings.INDEXER_NAME)


async def layout_document_failed(
    blob_url: str | None,
    blob_name: str | None,
    document_id: str,
) -> bool:
    if not layout_rag_enabled():
        return False

    identifiers = [
        _normalize_layout_path(identifier)
        for identifier in [blob_url, blob_name, document_id]
        if identifier
    ]
    if not identifiers:
        return False

    active_settings = _active_layout_settings()
    async with _indexer_client() as client:
        try:
            status = await client.get_indexer_status(active_settings.INDEXER_NAME)
        except Exception:
            return False

    history = []
    if getattr(status, "last_result", None):
        history.append(status.last_result)
    history.extend(getattr(status, "execution_history", []) or [])

    for run in history:
        for issue in list(getattr(run, "errors", []) or []):
            details = " ".join(
                [
                    str(getattr(issue, "key", "") or ""),
                    str(getattr(issue, "details", "") or ""),
                    str(getattr(issue, "error_message", "") or ""),
                ]
            ).lower()
            if any(identifier in details for identifier in identifiers):
                return True

    return False


def _normalize_layout_path(value: str | None) -> str:
    """Normalize layout path by trimming whitespace and converting to lowercase."""
    return (value or "").strip().lower()


def _matches_layout_result(
    path: str,
    user_id: str | None = None,
    document_ids: list[str] | None = None,
) -> bool:
    """Check if a layout result matches the given user and document filters."""
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
    """Format a layout result into a readable string with title and content."""
    active_settings = _active_layout_settings()
    content = str(result.get(active_settings.CONTENT_FIELD, "") or "").strip()
    if rag_v3_enabled() and not content:
        content = str(
            result.get(getattr(active_settings, "IMAGE_CAPTION_FIELD", ""), "") or ""
        ).strip()
    if not content:
        return ""

    title = str(result.get(active_settings.TITLE_FIELD, "") or "").strip()
    page = result.get(active_settings.PAGE_FIELD)
    prefix_parts = []
    if title:
        prefix_parts.append(title)
    if page not in (None, ""):
        prefix_parts.append(f"pagina {page}")

    if prefix_parts:
        return f"[{' | '.join(prefix_parts)}]\n{content}"
    return content


def _build_visual_reference(result: dict) -> dict | None:
    """Build a visual reference object from a layout result with image and metadata."""
    active_settings = _active_layout_settings()
    content = str(result.get(active_settings.CONTENT_FIELD, "") or "").strip()
    path = str(result.get(active_settings.PATH_FIELD, "") or "").strip()
    title = str(result.get(active_settings.TITLE_FIELD, "") or "").strip()
    page = result.get(active_settings.PAGE_FIELD)
    image_path = (
        str(result.get(getattr(active_settings, "IMAGE_PATH_FIELD", ""), "") or "").strip()
        if rag_v3_enabled()
        else ""
    )
    image_caption = (
        str(result.get(getattr(active_settings, "IMAGE_CAPTION_FIELD", ""), "") or "").strip()
        if rag_v3_enabled()
        else ""
    )
    source_kind = (
        str(result.get(getattr(active_settings, "SOURCE_KIND_FIELD", ""), "") or "").strip()
        if rag_v3_enabled()
        else ""
    )
    section_kind = (
        str(result.get(getattr(active_settings, "SECTION_KIND_FIELD", ""), "") or "").strip()
        if rag_v3_enabled()
        else ""
    )

    if not (content or path or title or image_path or image_caption):
        return None

    image_url = None
    if image_path:
        normalized_image_path = image_path.lstrip("/")
        if BlobStorageSettings.AZURE_STORAGE_CONTAINER:
            image_url = (
                f"{BlobStorageSettings.AZURE_BLOB_STORAGE_URL.rstrip('/')}/{BlobStorageSettings.AZURE_STORAGE_CONTAINER}/{normalized_image_path}"
            )
        elif normalized_image_path.startswith(("http://", "https://")):
            image_url = normalized_image_path

    return {
        "title": title or None,
        "pageNumber": page if page not in (None, "") else None,
        "path": path or None,
        "imageUrl": image_url,
        "imageCaption": image_caption or None,
        "previewText": (image_caption or content)[:220] if (image_caption or content) else None,
        "sourceKind": source_kind or None,
        "sectionKind": section_kind or None,
        "kind": "layout_image" if image_path else "layout_chunk",
    }


def _layout_select_fields() -> list[str]:
    """Return the list of fields to select from layout search results."""
    active_settings = _active_layout_settings()
    fields = [
        active_settings.CONTENT_FIELD,
        active_settings.TITLE_FIELD,
        active_settings.PAGE_FIELD,
        active_settings.PATH_FIELD,
    ]
    if rag_v3_enabled():
        fields.extend(
            [
                active_settings.IMAGE_PATH_FIELD,
                active_settings.IMAGE_CAPTION_FIELD,
                active_settings.SOURCE_KIND_FIELD,
                active_settings.SECTION_KIND_FIELD,
            ]
        )
    return fields


async def _search_layout_context(query: str, top_k: int = 5) -> list[str]:
    """Search the Azure Search layout index created for rag-v2."""
    query_vector = await _get_embedding(
        query,
        dimensions=_classic_embedding_dimensions(),
    )
    candidate_top = max(top_k * 6, 20)
    active_settings = _active_layout_settings()
    async with _search_client(active_settings.INDEX_NAME) as client:
        from azure.search.documents.models import VectorizedQuery

        vector_query = VectorizedQuery(
            vector=query_vector,
            k=top_k,
            fields=active_settings.VECTOR_FIELD,
        )
        try:
            results = await client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=candidate_top,
                select=_layout_select_fields(),
            )
        except Exception:
            # Some portal-created indexes do not expose the vector field name we expect.
            results = await client.search(
                search_text=query,
                top=candidate_top,
                select=_layout_select_fields(),
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
    active_settings = _active_layout_settings()
    async with _search_client(active_settings.INDEX_NAME) as client:
        from azure.search.documents.models import VectorizedQuery

        vector_query = VectorizedQuery(
            vector=query_vector,
            k=max(top_k, 10),
            fields=active_settings.VECTOR_FIELD,
        )
        try:
            results = await client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=candidate_top,
                select=_layout_select_fields(),
            )
        except Exception:
            results = await client.search(
                search_text=query,
                top=candidate_top,
                select=_layout_select_fields(),
            )

        chunks = []
        async for result in results:
            result_path = str(result.get(active_settings.PATH_FIELD, "") or "")
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


async def _search_filtered_layout_bundle(
    query: str,
    top_k: int = 5,
    user_id: str | None = None,
    document_ids: list[str] | None = None,
) -> tuple[list[str], list[dict]]:
    query_vector = await _get_embedding(query)
    candidate_top = max(top_k * 8, 30)
    active_settings = _active_layout_settings()
    async with _search_client(active_settings.INDEX_NAME) as client:
        from azure.search.documents.models import VectorizedQuery

        vector_query = VectorizedQuery(
            vector=query_vector,
            k=max(top_k, 10),
            fields=active_settings.VECTOR_FIELD,
        )
        try:
            results = await client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=candidate_top,
                select=_layout_select_fields(),
            )
        except Exception:
            results = await client.search(
                search_text=query,
                top=candidate_top,
                select=_layout_select_fields(),
            )

        chunks: list[str] = []
        visual_references: list[dict] = []
        seen_paths: set[str] = set()
        async for result in results:
            result_path = str(result.get(active_settings.PATH_FIELD, "") or "")
            if not _matches_layout_result(
                result_path,
                user_id=user_id,
                document_ids=document_ids,
            ):
                continue
            formatted = _format_layout_result(result)
            if formatted:
                chunks.append(formatted)
            visual_reference = _build_visual_reference(result)
            normalized_path = _normalize_layout_path(result_path)
            if visual_reference and normalized_path not in seen_paths:
                visual_references.append(visual_reference)
                seen_paths.add(normalized_path)
            if len(chunks) >= top_k:
                break
        return chunks, visual_references


async def _search_rag_v3_visual_bundle(
    query: str,
    top_k: int = 5,
    user_id: str | None = None,
    document_ids: list[str] | None = None,
) -> list[dict]:
    image_index_name = _active_image_index_name()
    if not image_index_name:
        return []

    query_vector = await _get_embedding(query)
    candidate_top = max(top_k * 6, 20)
    async with _search_client(image_index_name) as client:
        from azure.search.documents.models import VectorizedQuery

        vector_query = VectorizedQuery(
            vector=query_vector,
            k=max(top_k, 10),
            fields=RagV3Settings.IMAGE_VECTOR_FIELD,
        )
        try:
            results = await client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=candidate_top,
                select=[
                    RagV3Settings.CONTENT_FIELD,
                    RagV3Settings.TITLE_FIELD,
                    RagV3Settings.PAGE_FIELD,
                    RagV3Settings.PATH_FIELD,
                    RagV3Settings.IMAGE_PATH_FIELD,
                    RagV3Settings.IMAGE_CAPTION_FIELD,
                    RagV3Settings.SOURCE_KIND_FIELD,
                    RagV3Settings.SECTION_KIND_FIELD,
                ],
            )
        except Exception:
            results = await client.search(
                search_text=query,
                top=candidate_top,
                select=[
                    RagV3Settings.CONTENT_FIELD,
                    RagV3Settings.TITLE_FIELD,
                    RagV3Settings.PAGE_FIELD,
                    RagV3Settings.PATH_FIELD,
                    RagV3Settings.IMAGE_PATH_FIELD,
                    RagV3Settings.IMAGE_CAPTION_FIELD,
                    RagV3Settings.SOURCE_KIND_FIELD,
                    RagV3Settings.SECTION_KIND_FIELD,
                ],
            )

        visual_references: list[dict] = []
        seen_paths: set[str] = set()
        async for result in results:
            result_path = str(result.get(RagV3Settings.PATH_FIELD, "") or "")
            if not _matches_layout_result(
                result_path,
                user_id=user_id,
                document_ids=document_ids,
            ):
                continue
            visual_reference = _build_visual_reference(result)
            normalized_path = _normalize_layout_path(
                str(result.get(RagV3Settings.IMAGE_PATH_FIELD, "") or result_path)
            )
            if visual_reference and normalized_path not in seen_paths:
                visual_references.append(visual_reference)
                seen_paths.add(normalized_path)
            if len(visual_references) >= top_k:
                break
        return visual_references


async def layout_document_ready(
    blob_url: str | None,
    blob_name: str | None,
    user_id: str,
    document_id: str,
) -> bool:
    if not layout_rag_enabled():
        return False

    active_settings = _active_layout_settings()
    identifiers = [identifier for identifier in [blob_url, blob_name, document_id] if identifier]
    async with _search_client(active_settings.INDEX_NAME) as client:
        try:
            results = await client.search(
                search_text="*",
                top=200,
                select=[active_settings.PATH_FIELD],
            )
            async for result in results:
                result_path = str(result.get(active_settings.PATH_FIELD, "") or "")
                if _matches_layout_result(
                    result_path,
                    user_id=user_id,
                    document_ids=[document_id],
                ):
                    return True
        except Exception:
            pass

        for identifier in identifiers:
            try:
                results = await client.search(
                    search_text=str(identifier),
                    top=10,
                    select=[active_settings.PATH_FIELD],
                )
            except Exception:
                continue

            async for result in results:
                result_path = str(result.get(active_settings.PATH_FIELD, "") or "")
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
            k=top_k,
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


async def search_context_bundle(
    query: str,
    user_id: str,
    top_k: int = 5,
    document_ids: list[str] | None = None,
) -> tuple[list[str], list[dict]]:
    """Search chunks and optional visual references for the active retrieval mode."""
    if layout_rag_enabled():
        chunks, visual_references = await _search_filtered_layout_bundle(
            query,
            top_k=top_k,
            user_id=user_id,
            document_ids=document_ids,
        )
        if rag_v3_enabled():
            extra_visual_references = await _search_rag_v3_visual_bundle(
                query,
                top_k=top_k,
                user_id=user_id,
                document_ids=document_ids,
            )
            seen = {
                _normalize_layout_path(
                    str(reference.get("imageUrl") or reference.get("path") or "")
                )
                for reference in visual_references
            }
            for reference in extra_visual_references:
                ref_key = _normalize_layout_path(
                    str(reference.get("imageUrl") or reference.get("path") or "")
                )
                if ref_key and ref_key in seen:
                    continue
                visual_references.append(reference)
                if ref_key:
                    seen.add(ref_key)
        return chunks, visual_references

    chunks = await search_context(
        query,
        user_id=user_id,
        top_k=top_k,
        document_ids=document_ids,
    )
    return chunks, []


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
