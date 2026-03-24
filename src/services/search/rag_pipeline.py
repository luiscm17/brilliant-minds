"""Coordinator utilities for Azure AI Search agentic retrieval assets."""

from urllib.error import HTTPError

from src.config.settings import AgenticRagSettings
from src.services.search.knowledge_base_service import KnowledgeBaseService
from src.services.search.knowledge_source_service import KnowledgeSourceService
from src.services.search.mcp_connection import create_or_update_mcp_connection


def run_pipeline() -> None:
    """Create or update the default knowledge source and knowledge base."""
    knowledge_source_service = KnowledgeSourceService()
    knowledge_source = knowledge_source_service.create_knowledge_source(
        AgenticRagSettings.KNOWLEDGE_SOURCE_NAME,
        AgenticRagSettings.KNOWLEDGE_SOURCE_DESCRIPTION,
    )
    knowledge_source_service.create_or_update(knowledge_source)

    knowledge_base_service = KnowledgeBaseService()
    knowledge_base_service.create_and_deploy(knowledge_source.name)
    try:
        create_or_update_mcp_connection()
    except HTTPError as exc:
        print(f"MCP connection sync skipped: {exc.code} {exc.reason}")
