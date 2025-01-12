"""
Arxiv MCP Server
===============

This module implements an MCP server for interacting with arXiv.
"""

import logging
import mcp.types as types
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from .config import Settings
from .tools import handle_search, handle_download, handle_list_papers, handle_read_paper
from .tools import search_tool, download_tool, list_tool, read_tool
from .prompts.handlers import list_prompts as handler_list_prompts
from .prompts.handlers import get_prompt as handler_get_prompt

settings = Settings()
logger = logging.getLogger("arxiv-mcp-server")
logger.setLevel(logging.INFO)

class ArxivServer(Server):
    """Custom server implementation with prompt handling."""
    
    def __init__(self, name: str):
        """Initialize the server with prompts capability."""
        super().__init__(name=name)
        self.capabilities = {
            "prompts": {},
            "tools": {},
        }
    
    async def list_prompts(self) -> List[types.Prompt]:
        """List available prompts."""
        return await handler_list_prompts()
    
    async def get_prompt(self, name: str, arguments: Dict[str, str] | None = None) -> types.GetPromptResult:
        """Get a specific prompt with arguments."""
        return await handler_get_prompt(name, arguments)
    
    async def list_tools(self) -> List[types.Tool]:
        """List available arXiv research tools."""
        return [search_tool, download_tool, list_tool, read_tool]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool calls for arXiv research functionality."""
        logger.debug(f"Calling tool {name} with arguments {arguments}")
        try:
            if name == "search_papers":
                return await handle_search(arguments)
            elif name == "download_paper":
                return await handle_download(arguments)
            elif name == "list_papers":
                return await handle_list_papers(arguments)
            elif name == "read_paper":
                return await handle_read_paper(arguments)
            else:
                return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]
        except Exception as e:
            logger.error(f"Tool error: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

# Initialize server instance
server = ArxivServer(name=settings.APP_NAME)

async def main():
    """Run the server async context."""
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name=settings.APP_NAME,
                server_version=settings.APP_VERSION,
                capabilities=server.get_capabilities(),
            ),
        )