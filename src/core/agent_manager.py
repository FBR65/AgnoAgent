"""
AgentManager - Central management for all agents using agno framework and a2a SDK
"""

import logging
from typing import Dict, Any, List, Optional
from agno.agent import Agent
from a2a.client import A2AClient
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentProvider
import httpx
from .config import config

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Central agent manager using agno framework for coordinating all agents
    """

    def __init__(self):
        self.a2a_client: Optional[A2AClient] = None
        self.httpx_client: Optional[httpx.AsyncClient] = None
        self.agents: Dict[str, Any] = {}  # Store agent instances
        self.agno_agents: Dict[str, Agent] = {}  # Store agno Agent wrappers
        self._initialized = False

    async def initialize(self):
        """Initialize the agent system and A2A network"""
        if self._initialized:
            return

        try:
            # Initialize httpx client
            self.httpx_client = httpx.AsyncClient()

            # Create AgentCard for A2A communication
            agent_card = AgentCard(
                name="AgnoAgent-System",
                description="Multi-agent system with grammar correction, sentiment analysis, optimization and query refinement capabilities",
                version="1.0.0",
                url="http://localhost:8000",
                capabilities=AgentCapabilities(
                    textGeneration=True, textAnalysis=True, languageProcessing=True
                ),
                skills=[
                    AgentSkill(
                        id="grammar_correction",
                        name="grammar_correction",
                        description="German grammar and spelling correction",
                        tags=["grammar", "correction", "german", "text"],
                    ),
                    AgentSkill(
                        id="sentiment_analysis",
                        name="sentiment_analysis",
                        description="Emotion and sentiment detection",
                        tags=["sentiment", "emotion", "analysis", "text"],
                    ),
                    AgentSkill(
                        id="query_refinement",
                        name="query_refinement",
                        description="Query optimization and refinement",
                        tags=["query", "optimization", "refinement", "search"],
                    ),
                    AgentSkill(
                        id="text_optimization",
                        name="text_optimization",
                        description="Text improvement and optimization",
                        tags=["text", "optimization", "improvement", "enhancement"],
                    ),
                ],
                defaultInputModes=["text"],
                defaultOutputModes=["text", "json"],
            )

            # Initialize A2A client with AgentCard
            self.a2a_client = A2AClient(
                httpx_client=self.httpx_client, agent_card=agent_card
            )
            logger.info("A2A client initialized successfully")

            # Register agents in the system
            await self._register_agents()

            self._initialized = True
            logger.info("AgentManager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AgentManager: {e}")
            raise

    async def _register_agents(self):
        """Register all agents in the agno system"""
        import sys
        import os

        # Add src to path for imports
        src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if src_path not in sys.path:
            sys.path.append(src_path)

        from agents import LektorAgent, OptimizerAgent, SentimentAgent, QueryRefAgent

        # Create and register agents
        agent_classes = {
            "lektor": LektorAgent,
            "optimizer": OptimizerAgent,
            "sentiment": SentimentAgent,
            "query_ref": QueryRefAgent,
        }

        for agent_id, agent_class in agent_classes.items():
            try:
                # Create agent instance
                agent_instance = agent_class(config=config)
                await agent_instance.initialize()

                # Create agno Agent wrapper
                agno_agent = Agent(
                    name=f"{agent_class.__name__}",
                    instructions=f"Agent for {agent_id} operations",
                )

                # Store both
                self.agents[agent_id] = agent_instance
                self.agno_agents[agent_id] = agno_agent

                logger.info(f"Registered agent: {agent_id}")

            except Exception as e:
                logger.error(f"Failed to register agent {agent_id}: {e}")

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request through the agent system
        """
        try:
            if not self._initialized:
                await self.initialize()

            # Extract agent type from request
            agent_type = request.get("type")
            if not agent_type:
                return {
                    "status": "error",
                    "message": "No agent type specified in request",
                    "data": None,
                }

            # Get agent instance
            agent = self.agents.get(agent_type)
            if not agent:
                return {
                    "status": "error",
                    "message": f"Agent type '{agent_type}' not found",
                    "data": None,
                }

            # Process request with agent
            result = await agent.handle_request(request)
            return result

        except Exception as e:
            logger.error(f"Failed to process request: {e}")
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "data": None,
            }

    async def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get a specific agent by ID"""
        return self.agents.get(agent_id)

    async def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())

    async def call_agent(
        self, agent_name: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a specific agent directly"""
        try:
            # Convert agent name to agent_id
            agent_id_map = {
                "LektorAgent": "lektor",
                "OptimizerAgent": "optimizer",
                "SentimentAgent": "sentiment",
                "QueryRefAgent": "query_ref",
            }

            agent_id = agent_id_map.get(agent_name)
            if not agent_id:
                return {
                    "status": "error",
                    "message": f"Unknown agent: {agent_name}",
                    "data": None,
                }

            # Get agent instance
            agent = self.agents.get(agent_id)
            if not agent:
                return {
                    "status": "error",
                    "message": f"Agent {agent_id} not available",
                    "data": None,
                }

            # Call agent's handle_request method
            request = {"data": request_data}
            response = await agent.handle_request(request)
            return response

        except Exception as e:
            logger.error(f"Error calling agent {agent_name}: {e}")
            return {"status": "error", "message": str(e), "data": None}

    async def call_service(
        self, service_name: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a specific MCP service"""
        try:
            if service_name == "SearchService":
                return await self._call_search_service(request_data)
            elif service_name == "WebService":
                return await self._call_web_service(request_data)
            elif service_name == "TimeService":
                return await self._call_time_service(request_data)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown service: {service_name}",
                    "data": None,
                }
        except Exception as e:
            logger.error(f"Error calling service {service_name}: {e}")
            return {"status": "error", "message": str(e), "data": None}

    async def _call_search_service(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call the search service with DuckDuckGo"""
        try:
            from ddgs import DDGS

            query = request_data.get("query", "")
            max_results = request_data.get("max_results", 5)

            if not query:
                return {
                    "status": "error",
                    "message": "No search query provided",
                    "data": None,
                }

            # Perform DuckDuckGo search
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "title": result.get("title", "No title"),
                        "url": result.get("href", "No URL"),
                        "snippet": result.get("body", "No description"),
                    }
                )

            return {
                "status": "success",
                "message": f"Found {len(formatted_results)} search results",
                "data": {
                    "results": formatted_results,
                    "query": query,
                    "total_results": len(formatted_results),
                },
            }

        except Exception as e:
            logger.error(f"Error in search service: {e}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}",
                "data": None,
            }

    async def _call_web_service(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the web extraction service"""
        try:
            import trafilatura
            import httpx

            url = request_data.get("url", "")
            if not url:
                return {"status": "error", "message": "No URL provided", "data": None}

            # Download and extract content
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                html = response.text

            # Extract main content
            content = trafilatura.extract(html)

            if not content:
                content = "Could not extract meaningful content from the webpage"

            return {
                "status": "success",
                "message": "Website content extracted",
                "data": {
                    "url": url,
                    "content": content[:1000] + "..."
                    if len(content) > 1000
                    else content,
                    "full_length": len(content),
                },
            }

        except Exception as e:
            logger.error(f"Error in web service: {e}")
            return {
                "status": "error",
                "message": f"Web extraction failed: {str(e)}",
                "data": None,
            }

    async def _call_time_service(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the time service"""
        try:
            import datetime
            import ntplib

            # Get current time
            now = datetime.datetime.now()

            # Try to get NTP time
            try:
                client = ntplib.NTPClient()
                response = client.request("pool.ntp.org")
                ntp_time = datetime.datetime.fromtimestamp(response.tx_time)
                time_info = f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}, NTP time: {ntp_time.strftime('%Y-%m-%d %H:%M:%S')}"
            except Exception:
                time_info = f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} (NTP not available)"

            return {
                "status": "success",
                "message": "Time information retrieved",
                "data": {
                    "time_info": time_info,
                    "timestamp": now.timestamp(),
                    "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }

        except Exception as e:
            logger.error(f"Error in time service: {e}")
            return {
                "status": "error",
                "message": f"Time service failed: {str(e)}",
                "data": None,
            }

    async def send_to_agent(
        self, agent_id: str, message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a message to a specific agent via A2A
        """
        if not self.a2a_client:
            raise RuntimeError("A2A client not initialized")

        try:
            # For now, process locally since we have agents in the same system
            request = {"type": agent_id, "data": message}
            return await self.process_request(request)
        except Exception as e:
            logger.error(f"Error sending message to agent {agent_id}: {e}")
            return {"status": "error", "message": str(e), "data": None}

    async def shutdown(self):
        """Shutdown the agent system and A2A client"""
        try:
            # Shutdown all agents
            for agent_id, agent in self.agents.items():
                try:
                    await agent.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down agent {agent_id}: {e}")

            # Close A2A client connection (if needed)
            self.a2a_client = None

            # Close httpx client
            if self.httpx_client:
                await self.httpx_client.aclose()
                self.httpx_client = None

            logger.info("AgentManager shutdown completed")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global agent manager instance
agent_manager = AgentManager()
