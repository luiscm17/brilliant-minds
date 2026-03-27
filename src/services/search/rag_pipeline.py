"""Coordinator for the RAG pipeline: create and ingest a knowledge source."""

from src.config.settings import (
    KnowledgeBaseSettings,
    KnowledgeSourceSettings,
)
from src.services.search.knowledge_base_service import KnowledgeBaseService
from src.services.search.knowledge_source_service import KnowledgeSourceService
from src.services.search.mcp_connection import create_or_update_mcp_connection


def run_pipeline(name: str, description: str) -> None:
    """Build and ingest a knowledge source and its knowledge base."""
    ks_service = KnowledgeSourceService()
    ks = ks_service.create_knowledge_source(name, description)
    ks_service.ingest(ks)

    kb_service = KnowledgeBaseService()
    kb_service.create_and_deploy(name)

    connection_id = create_or_update_mcp_connection()
    print(f"Knowledge Source '{name}' ingested successfully.")
    print("Knowledge Base deployed with documented retrieval settings.")
    print(f"Project connection synced: {connection_id}")


if __name__ == "__main__":
    KnowledgeSourceSettings.validate()
    KnowledgeBaseSettings.validate()
    run_pipeline(
        KnowledgeSourceSettings.get_name(),
        KnowledgeSourceSettings.get_description(),
    )
