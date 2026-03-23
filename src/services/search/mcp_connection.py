"""Helpers to manage the MCP project connection for the knowledge base."""

import requests

from azure.identity import DefaultAzureCredential
from src.config.settings import MCPConnectionSettings


def _build_connection_details() -> tuple[str, str, str] | None:
    try:
        resource_id = MCPConnectionSettings.get_project_resource_id()
        connection_name = MCPConnectionSettings.get_project_connection_name()
        mcp_endpoint = MCPConnectionSettings.get_mcp_endpoint()
    except ValueError:
        return None
    return resource_id, connection_name, mcp_endpoint


def create_or_update_mcp_connection() -> str | None:
    """Create or update the project connection pointing to the KB's MCP endpoint."""
    details = _build_connection_details()
    if not details:
        return None

    resource_id, connection_name, mcp_endpoint = details
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default")

    url = f"https://management.azure.com{resource_id}/connections/{connection_name}?api-version=2025-10-01-preview"

    response = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
        },
        json={
            "name": connection_name,
            "type": "Microsoft.MachineLearningServices/workspaces/connections",
            "properties": {
                "authType": "ProjectManagedIdentity",
                "category": "RemoteTool",
                "target": mcp_endpoint,
                "isSharedToAll": True,
                "audience": "https://search.azure.com/",
                "metadata": {"ApiType": "Azure"},
            },
        },
    )

    response.raise_for_status()
    return f"{resource_id}/connections/{connection_name}"
