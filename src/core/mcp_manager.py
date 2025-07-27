"""
MCPServerManager - Management for MCP services integration
"""

import logging
from typing import Dict, Any, List, Optional
from mcp.server import Server as MCPServer
from mcp.client.session import ClientSession
from .config import config

logger = logging.getLogger(__name__)


class MCPServerManager:
    """
    Manager for MCP (Model Context Protocol) server integration
    """

    def __init__(self):
        self.server: Optional[MCPServer] = None
        self.clients: Dict[str, ClientSession] = {}
        self.services: Dict[str, Any] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize MCP server and services"""
        if self._initialized:
            return

        try:
            # Initialize MCP server
            self.server = MCPServer("AgnoAgent MCP Server")

            # Register MCP services
            await self._register_services()

            self._initialized = True
            logger.info(f"MCP server initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
            raise

    async def _register_services(self):
        """Register all MCP services"""
        from ..mcp_services import SearchService, WebService, TimeService

        service_classes = {
            "search": SearchService,
            "web": WebService,
            "time": TimeService,
        }

        for service_name, service_class in service_classes.items():
            try:
                service_instance = service_class()
                await service_instance.initialize()

                # Store service instance
                self.services[service_name] = service_instance

                logger.info(f"Registered MCP service: {service_name}")

            except Exception as e:
                logger.error(f"Failed to register MCP service {service_name}: {e}")

    async def get_service(self, service_name: str) -> Optional[Any]:
        """Get a specific MCP service"""
        return self.services.get(service_name)

    async def list_services(self) -> List[str]:
        """List all registered MCP services"""
        return list(self.services.keys())

    async def create_client(self, server_url: str, client_id: str) -> ClientSession:
        """Create a client connection to another MCP server"""
        # For now, return None as we're focusing on local services
        logger.info(
            f"MCP client creation requested for {server_url} (not implemented yet)"
        )
        return None

    async def call_service(
        self, service_name: str, method: str, params: Dict[str, Any]
    ) -> Any:
        """Call a method on a registered MCP service"""
        service = self.services.get(service_name)
        if not service:
            raise ValueError(f"Service not found: {service_name}")

        if not hasattr(service, method):
            raise ValueError(f"Method not found: {service_name}.{method}")

        method_func = getattr(service, method)
        return await method_func(**params)

    async def shutdown(self):
        """Shutdown MCP server and all connections"""
        try:
            # Close all client connections
            for client_id, client in self.clients.items():
                try:
                    if hasattr(client, "close"):
                        await client.close()
                except Exception as e:
                    logger.error(f"Error closing client {client_id}: {e}")

            # Shutdown services
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, "shutdown"):
                        await service.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down service {service_name}: {e}")

            # Stop MCP server
            if self.server:
                # MCP server shutdown (if needed)
                pass

            logger.info("MCP server shutdown completed")

        except Exception as e:
            logger.error(f"Error during MCP server shutdown: {e}")


# Global MCP server manager instance
mcp_manager = MCPServerManager()
