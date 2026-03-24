"""Helpers to sync the MCP project connection for the active knowledge base."""

import json
from urllib import request

from azure.identity import DefaultAzureCredential

from src.config.settings import MCPConnectionSettings


def _build_connection_details() -> tuple[str, str, str] | None:
    if not MCPConnectionSettings.configured():
        return None
    return (
        MCPConnectionSettings.get_project_resource_id(),
        MCPConnectionSettings.get_project_connection_name(),
        MCPConnectionSettings.get_mcp_endpoint(),
    )


def create_or_update_mcp_connection() -> str | None:
    """Create or update the Azure AI Project connection to the KB MCP endpoint."""
    details = _build_connection_details()
    if not details:
        return None

    resource_id, connection_name, mcp_endpoint = details
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default")
    url = (
        f"https://management.azure.com{resource_id}/connections/{connection_name}"
        "?api-version=2025-10-01-preview"
    )
    payload = {
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
    }
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="PUT",
        headers={
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(req, timeout=30):
        pass
    return f"{resource_id}/connections/{connection_name}"
