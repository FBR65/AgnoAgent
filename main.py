"""
AgnoAgent - Main entry point for the multi-agent system
"""

import asyncio
import logging
from src.core import AgentManager, MCPServerManager, Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to start the AgnoAgent system"""
    config = Config()

    logger.info("Starting AgnoAgent system...")

    # Initialize managers
    agent_manager = AgentManager()
    mcp_manager = MCPServerManager()

    try:
        # Initialize systems
        await agent_manager.initialize()
        await mcp_manager.initialize()

        logger.info("AgnoAgent system started successfully!")
        logger.info(f"MCP server running at: {config.mcp_url}")
        logger.info(f"A2A network: {config.a2a_network_id}")

        # Example usage
        test_requests = [
            {
                "type": "lektor",
                "data": {"text": "Das ist ein sehr schlechte Satz mit viele Fehler."},
            },
            {
                "type": "optimizer",
                "data": {"text": "Das ist Schrott!", "tonality": "friendly"},
            },
            {
                "type": "sentiment",
                "data": {
                    "text": "Ich bin sehr glücklich mit diesem Ergebnis!",
                    "detailed": True,
                },
            },
            {"type": "query_ref", "data": {"text": "KI"}},
        ]

        # Process test requests
        for i, request in enumerate(test_requests, 1):
            logger.info(f"\n--- Test {i}: {request['type']} ---")
            result = await agent_manager.process_request(request)
            logger.info(f"Result: {result}")

        # Test MCP services
        logger.info("\n--- Testing MCP Services ---")

        # Test search service
        search_service = await mcp_manager.get_service("search")
        if search_service:
            search_result = await search_service.search(
                "Python programming", num_results=3
            )
            logger.info(f"Search results: {len(search_result.results)} found")

        # Test time service
        time_service = await mcp_manager.get_service("time")
        if time_service:
            time_result = await time_service.get_current_time()
            logger.info(f"Current time: {time_result.formatted_time}")

        logger.info("\nAgnoAgent system is running. Press Ctrl+C to stop.")

        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")

    except Exception as e:
        logger.error(f"Error in main system: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down AgnoAgent system...")
        await agent_manager.shutdown()
        await mcp_manager.shutdown()
        logger.info("AgnoAgent system shutdown completed")


if __name__ == "__main__":
    asyncio.run(main())
