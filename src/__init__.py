"""
AgnoAgent - Multi-Agent System with agno, a2a-sdk and MCP integration
"""

__version__ = "0.1.0"

from .core import AgentManager, MCPServerManager
from .agents import LektorAgent, OptimizerAgent, SentimentAgent, QueryRefAgent
from .mcp_services import SearchService, WebService, TimeService

__all__ = [
    "AgentManager",
    "MCPServerManager",
    "LektorAgent",
    "OptimizerAgent",
    "SentimentAgent",
    "QueryRefAgent",
    "SearchService",
    "WebService",
    "TimeService",
]
