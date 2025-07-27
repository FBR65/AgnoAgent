"""
Beispielskripte für die Verwendung des refaktorierten AgnoAgent Systems
"""

import asyncio
import logging
from src.core import AgentManager, MCPServerManager

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_agent_usage():
    """Beispiel für die Verwendung der Agenten"""
    logger.info("=== Agent Usage Examples ===")

    agent_manager = AgentManager()
    await agent_manager.initialize()

    try:
        # 1. Lektor Agent - Grammatikkorrektur
        logger.info("\n1. Lektor Agent - Grammatikkorrektur")
        lektor_request = {
            "type": "lektor",
            "data": {"text": "Das ist ein sehr schlechte Satz mit viele Fehler."},
        }
        result = await agent_manager.process_request(lektor_request)
        if result["status"] == "success":
            logger.info(f"Original: {result['data']['original_text']}")
            logger.info(f"Korrigiert: {result['data']['corrected_text']}")

        # 2. Optimizer Agent - Text-Optimierung
        logger.info("\n2. Optimizer Agent - Text-Optimierung")
        optimizer_request = {
            "type": "optimizer",
            "data": {"text": "Sehr geehrte Damen und Herren", "tonality": "locker"},
        }
        result = await agent_manager.process_request(optimizer_request)
        if result["status"] == "success":
            logger.info(f"Original: {result['data']['original_text']}")
            logger.info(f"Optimiert: {result['data']['optimized_text']}")

        # 3. Sentiment Agent - Sentiment-Analyse
        logger.info("\n3. Sentiment Agent - Sentiment-Analyse")
        sentiment_request = {
            "type": "sentiment",
            "data": {
                "text": "Ich bin sehr glücklich mit diesem fantastischen Ergebnis!",
                "detailed": True,
            },
        }
        result = await agent_manager.process_request(sentiment_request)
        if result["status"] == "success":
            sentiment = result["data"]["sentiment"]
            logger.info(f"Text: {result['data']['original_text']}")
            logger.info(
                f"Sentiment: {sentiment['label']} (Score: {sentiment['score']}, Confidence: {sentiment['confidence']})"
            )

        # 4. Query Ref Agent - Query-Verbesserung
        logger.info("\n4. Query Ref Agent - Query-Verbesserung")
        query_ref_request = {"type": "query_ref", "data": {"text": "KI"}}
        result = await agent_manager.process_request(query_ref_request)
        if result["status"] == "success":
            logger.info(f"Original: {result['data']['original_text']}")
            logger.info(f"Verbessert: {result['data']['query']}")

    finally:
        await agent_manager.shutdown()


async def example_mcp_usage():
    """Beispiel für die Verwendung der MCP Services"""
    logger.info("\n=== MCP Services Examples ===")

    mcp_manager = MCPServerManager()
    await mcp_manager.initialize()

    try:
        # 1. Search Service - Web-Suche
        logger.info("\n1. Search Service - Web-Suche")
        search_service = await mcp_manager.get_service("search")
        if search_service:
            search_result = await search_service.search(
                "Python programming", num_results=3
            )
            logger.info(
                f"Suchergebnisse für 'Python programming': {search_result.total_results} gefunden"
            )
            for i, result in enumerate(search_result.results[:2], 1):
                logger.info(f"  {i}. {result.title[:50]}...")

        # 2. Time Service - Aktuelle Zeit
        logger.info("\n2. Time Service - Aktuelle Zeit")
        time_service = await mcp_manager.get_service("time")
        if time_service:
            time_result = await time_service.get_current_time()
            if time_result.status == "success":
                logger.info(f"Aktuelle Zeit: {time_result.formatted_time}")

        # 3. Web Service - Website-Extraktion (Beispiel)
        logger.info("\n3. Web Service - Website-Extraktion")
        web_service = await mcp_manager.get_service("web")
        if web_service:
            # Beispiel mit einer einfachen Website
            page_info = await web_service.get_page_info("https://httpbin.org/html")
            if page_info.get("status") == "success":
                logger.info(f"Seitentitel: {page_info.get('title', 'Kein Titel')}")

    finally:
        await mcp_manager.shutdown()


async def example_combined_workflow():
    """Beispiel für einen kombinierten Workflow mit Agenten und MCP Services"""
    logger.info("\n=== Combined Workflow Example ===")

    agent_manager = AgentManager()
    mcp_manager = MCPServerManager()

    await agent_manager.initialize()
    await mcp_manager.initialize()

    try:
        # 1. Query verbessern
        query_ref_request = {"type": "query_ref", "data": {"text": "Python Tutorials"}}
        query_result = await agent_manager.process_request(query_ref_request)
        improved_query = (
            query_result["data"]["query"]
            if query_result["status"] == "success"
            else "Python Tutorials"
        )

        logger.info(f"Verbesserte Suchanfrage: {improved_query}")

        # 2. Suche durchführen
        search_service = await mcp_manager.get_service("search")
        if search_service:
            search_results = await search_service.search(improved_query, num_results=2)
            logger.info(f"Gefunden: {search_results.total_results} Ergebnisse")

            # 3. Ersten Suchergebnis-Snippet optimieren
            if search_results.results:
                snippet = search_results.results[0].snippet
                optimizer_request = {
                    "type": "optimizer",
                    "data": {"text": snippet, "tonality": "friendly"},
                }
                optimized_result = await agent_manager.process_request(
                    optimizer_request
                )

                if optimized_result["status"] == "success":
                    logger.info(f"Original Snippet: {snippet[:100]}...")
                    logger.info(
                        f"Optimiert: {optimized_result['data']['optimized_text'][:100]}..."
                    )

    finally:
        await agent_manager.shutdown()
        await mcp_manager.shutdown()


async def main():
    """Hauptfunktion zum Ausführen aller Beispiele"""
    logger.info("AgnoAgent Refactored System - Examples")
    logger.info("=" * 50)

    try:
        # Agent-Beispiele
        await example_agent_usage()

        # MCP Service-Beispiele
        await example_mcp_usage()

        # Kombinierter Workflow
        await example_combined_workflow()

        logger.info("\n=== Alle Beispiele erfolgreich ausgeführt ===")

    except Exception as e:
        logger.error(f"Fehler in den Beispielen: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
