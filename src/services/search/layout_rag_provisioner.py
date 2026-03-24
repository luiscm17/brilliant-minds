"""Provisioning helpers for the versioned layout-based RAG pipeline.

This module is the foundation for rag-v2. It keeps the ingestion path separate
from the current production index so we can evolve to rag-v3 later by extending
the same skillset/index pattern with knowledge store and multimodal fields.
"""

from azure.search.documents.indexes.models import (
    AzureOpenAIEmbeddingSkill,
    DocumentIntelligenceLayoutSkill,
    DocumentIntelligenceLayoutSkillChunkingProperties,
    DocumentIntelligenceLayoutSkillChunkingUnit,
    DocumentIntelligenceLayoutSkillExtractionOptions,
    DocumentIntelligenceLayoutSkillOutputFormat,
    DocumentIntelligenceLayoutSkillOutputMode,
    FieldMapping,
    HnswAlgorithmConfiguration,
    IndexProjectionMode,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexingParameters,
    SearchIndexerSkillset,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from src.config.settings import BlobStorageSettings, LayoutRagSettings, OpenAISettings
from src.services.search.search_index_service import SearchIndexService


class LayoutRagProvisioner:
    """Creates the Azure AI Search assets required for rag-v2 ingestion."""

    def __init__(self) -> None:
        BlobStorageSettings.validate()
        self._service = SearchIndexService()

    def _build_datasource(self) -> SearchIndexerDataSourceConnection:
        return SearchIndexerDataSourceConnection(
            name=LayoutRagSettings.DATASOURCE_NAME,
            type="azureblob",
            connection_string=BlobStorageSettings.CONNECTION_STRING or "",
            container=SearchIndexerDataContainer(name=BlobStorageSettings.CONTAINER or ""),
        )

    def _build_index(self) -> SearchIndex:
        fields = [
            SearchableField(
                name="chunk_id",
                key=True,
                filterable=True,
                sortable=True,
                analyzer_name="keyword",
            ),
            SimpleField(
                name="parent_id",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
            ),
            SimpleField(
                name="document_title",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
            ),
            SimpleField(
                name="metadata_storage_path",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
            ),
            SimpleField(
                name="page_number",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=True,
            ),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="layout_text", type=SearchFieldDataType.String),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=LayoutRagSettings.embedding_dimensions(),
                vector_search_profile_name="layout-rag-profile",
            ),
        ]

        return SearchIndex(
            name=LayoutRagSettings.INDEX_NAME,
            fields=fields,
            vector_search=VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="layout-rag-hnsw")],
                profiles=[
                    VectorSearchProfile(
                        name="layout-rag-profile",
                        algorithm_configuration_name="layout-rag-hnsw",
                    )
                ],
            ),
            semantic_search=SemanticSearch(
                default_configuration_name="layout-rag-semantic",
                configurations=[
                    SemanticConfiguration(
                        name="layout-rag-semantic",
                        prioritized_fields=SemanticPrioritizedFields(
                            title_field=SemanticField(field_name="document_title"),
                            content_fields=[SemanticField(field_name="content")],
                        ),
                    )
                ],
            ),
        )

    def _build_skillset(self) -> SearchIndexerSkillset:
        layout_outputs = [
            OutputFieldMappingEntry(name="text_sections", target_name="text_sections"),
        ]
        extraction_options = [DocumentIntelligenceLayoutSkillExtractionOptions.LOCATION_METADATA]
        if LayoutRagSettings.ENABLE_IMAGE_REFERENCES:
            extraction_options.append(DocumentIntelligenceLayoutSkillExtractionOptions.IMAGES)
            layout_outputs.append(
                OutputFieldMappingEntry(name="normalized_images", target_name="normalized_images")
            )

        skills = [
            DocumentIntelligenceLayoutSkill(
                name="layout-skill",
                description="Layout extraction with controlled chunking for rag-v2",
                context="/document",
                output_format=DocumentIntelligenceLayoutSkillOutputFormat.TEXT,
                output_mode=DocumentIntelligenceLayoutSkillOutputMode.ONE_TO_MANY,
                markdown_header_depth=None,
                extraction_options=extraction_options,
                chunking_properties=DocumentIntelligenceLayoutSkillChunkingProperties(
                    unit=DocumentIntelligenceLayoutSkillChunkingUnit.CHARACTERS,
                    maximum_length=LayoutRagSettings.MAX_CHUNK_LENGTH,
                    overlap_length=LayoutRagSettings.OVERLAP_LENGTH,
                ),
                inputs=[
                    InputFieldMappingEntry(name="file_data", source="/document/file_data")
                ],
                outputs=layout_outputs,
            ),
            AzureOpenAIEmbeddingSkill(
                name="embedding-skill",
                description="Embeddings for each extracted layout chunk",
                context="/document/text_sections/*",
                resource_url=OpenAISettings.ENDPOINT,
                deployment_name=OpenAISettings.EMBEDDING_DEPLOYMENT,
                api_key=OpenAISettings.API_KEY,
                model_name=OpenAISettings.EMBEDDING_MODEL,
                dimensions=LayoutRagSettings.embedding_dimensions(),
                inputs=[
                    InputFieldMappingEntry(
                        name="text",
                        source="/document/text_sections/*/content",
                    )
                ],
                outputs=[
                    OutputFieldMappingEntry(
                        name="embedding",
                        target_name="content_vector",
                    )
                ],
            ),
        ]

        return SearchIndexerSkillset(
            name=LayoutRagSettings.SKILLSET_NAME,
            description="rag-v2 layout pipeline ready to evolve into rag-v3",
            skills=skills,
            index_projection=SearchIndexerIndexProjection(
                selectors=[
                    SearchIndexerIndexProjectionSelector(
                        target_index_name=LayoutRagSettings.INDEX_NAME,
                        parent_key_field_name="parent_id",
                        source_context="/document/text_sections/*",
                        mappings=[
                            InputFieldMappingEntry(
                                name="document_title",
                                source="/document/metadata_storage_name",
                            ),
                            InputFieldMappingEntry(
                                name="metadata_storage_path",
                                source="/document/metadata_storage_path",
                            ),
                            InputFieldMappingEntry(
                                name="page_number",
                                source="/document/text_sections/*/location_metadata/page_number",
                            ),
                            InputFieldMappingEntry(
                                name="content",
                                source="/document/text_sections/*/content",
                            ),
                            InputFieldMappingEntry(
                                name="layout_text",
                                source="/document/text_sections/*/content",
                            ),
                            InputFieldMappingEntry(
                                name="content_vector",
                                source="/document/text_sections/*/content_vector",
                            ),
                        ],
                    )
                ],
                parameters=SearchIndexerIndexProjectionsParameters(
                    projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
                ),
            ),
        )

    def _build_indexer(self) -> SearchIndexer:
        return SearchIndexer(
            name=LayoutRagSettings.INDEXER_NAME,
            data_source_name=LayoutRagSettings.DATASOURCE_NAME,
            target_index_name=LayoutRagSettings.INDEX_NAME,
            skillset_name=LayoutRagSettings.SKILLSET_NAME,
            parameters=IndexingParameters(
                configuration={"allowSkillsetToReadFileData": True}
            ),
            field_mappings=[
                FieldMapping(
                    source_field_name="metadata_storage_name",
                    target_field_name="document_title",
                )
            ],
        )

    def provision(self) -> None:
        index_client = self._service.get_client()
        indexer_client = self._service.get_indexer_client()

        indexer_client.create_or_update_data_source_connection(self._build_datasource())
        index_client.create_or_update_index(self._build_index())
        indexer_client.create_or_update_skillset(self._build_skillset())
        indexer_client.create_or_update_indexer(self._build_indexer())

    def run_indexer(self) -> None:
        self._service.get_indexer_client().run_indexer(LayoutRagSettings.INDEXER_NAME)
