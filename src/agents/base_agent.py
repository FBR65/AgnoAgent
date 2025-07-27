"""
Base agent class for all AgnoAgent agents
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from agno.agent import Agent

logger = logging.getLogger(__name__)


class BaseAgent(Agent, ABC):
    """
    Base class for all agents in the AgnoAgent system
    """

    def __init__(self, config):
        # Initialize with agno Agent using config
        super().__init__(
            name=config.get("name", self.__class__.__name__),
            instructions=config.get("instructions", []),
            description=config.get("description", ""),
            model=config.get("model"),
        )
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False

    async def initialize(self):
        """Initialize the agent"""
        if self._initialized:
            return

        await self._setup()
        self._initialized = True
        self.logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    async def _setup(self):
        """Agent-specific setup logic"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass

    @abstractmethod
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming requests"""
        pass

    async def shutdown(self):
        """Shutdown the agent"""
        try:
            await self._cleanup()
            self.logger.info(f"{self.__class__.__name__} shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def _cleanup(self):
        """Agent-specific cleanup logic"""
        pass

    def _create_error_response(
        self, message: str, error: Exception = None
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "status": "error",
            "message": message,
            "error_details": str(error) if error else None,
            "agent": self.__class__.__name__,
        }

    def _create_success_response(
        self, data: Any, message: str = "Success"
    ) -> Dict[str, Any]:
        """Create standardized success response"""
        return {
            "status": "success",
            "message": message,
            "data": data,
            "agent": self.__class__.__name__,
        }
