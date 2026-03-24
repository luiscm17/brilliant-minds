"""CLI helper for provisioning the scalable rag-v2 ingestion pipeline."""

from src.services.search.layout_rag_provisioner import LayoutRagProvisioner


def main() -> None:
    provisioner = LayoutRagProvisioner()
    provisioner.provision()
    print("Layout RAG v2 assets created or updated.")


if __name__ == "__main__":
    main()
