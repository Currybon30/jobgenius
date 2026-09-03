import logging

from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

mcp_client = None
mcp_client_tools = None


async def init_mcp_client():
    global mcp_client
    global mcp_client_tools
    mcp_client = MultiServerMCPClient(
        {
            "job_service": {
                "command": "python",
                "args": ["-m", "app.mcp.job_mcp"],
                "transport": "stdio",
            }
        }
    )
    mcp_client_tools = await mcp_client.get_tools()
    logger.info("MCP client initialized successfully")


async def get_mcp_client_tools():
    if not mcp_client_tools:
        raise ValueError("MCP client tools not initialized")
    return mcp_client_tools


async def close_mcp_client():
    global mcp_client
    global mcp_client_tools
    mcp_client = None
    mcp_client_tools = None
    logger.info("MCP client closed successfully")
