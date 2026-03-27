"""Reusable MCP tool integration for Agent Framework agents."""

from azure.ai.projects.models import MCPTool
from src.config.settings import MCPConnectionSettings


def build_mcp_tool() -> MCPTool:
    """Create an MCPTool configured to talk to the knowledge base."""
    endpoint = MCPConnectionSettings.get_mcp_endpoint()
    connection_id = MCPConnectionSettings.get_project_connection_id()

    return MCPTool(
        server_label="knowledge-base",
        server_url=endpoint,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=connection_id,
    )
