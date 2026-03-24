"""Reusable MCP tool integration for Azure AI Project agents."""

from azure.ai.projects.models import MCPTool

from src.config.settings import MCPConnectionSettings


def build_mcp_tool() -> MCPTool:
    """Create an MCP tool configured for the active knowledge base."""
    return MCPTool(
        server_label="knowledge-base",
        server_url=MCPConnectionSettings.get_mcp_endpoint(),
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=MCPConnectionSettings.get_project_connection_id(),
    )
