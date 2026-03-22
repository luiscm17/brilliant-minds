"""Coordinator for the RAG pipeline: create and ingest a knowledge source."""

from src.config.settings import KnowledgeSourceSettings
from src.services.search.knowledge_source_service import KnowledgeSourceService


def run_pipeline(name: str, description: str) -> None:
    """
    Build and ingest a knowledge source with the given name and description.

    Args:
        name: Unique identifier for the knowledge source.
        description: Human-readable description for the knowledge source.
    """
    service = KnowledgeSourceService()
    ks = service.create_knowledge_source(name, description)
    service.ingest(ks)
    print(f"Knowledge Source '{name}' ingested successfully.")


if __name__ == "__main__":
    KnowledgeSourceSettings.validate()
    run_pipeline(
        KnowledgeSourceSettings.get_name(),
        KnowledgeSourceSettings.get_description(),
    )
