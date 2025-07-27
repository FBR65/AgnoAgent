"""
InterfaceAgent - Central agent for coordinating all other agents and MCP services
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .base_agent import BaseAgent
import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.agent_manager import AgentManager

logger = logging.getLogger(__name__)


class InterfaceRequest(BaseModel):
    """Request model for interface agent"""

    query: str
    agent_type: Optional[str] = None  # lektor, sentiment, optimizer, query_ref
    service_type: Optional[str] = None  # search, web, time
    parameters: Optional[Dict[str, Any]] = None


class InterfaceResponse(BaseModel):
    """Response model for interface agent"""

    response: str
    agent_used: str
    original_query: str
    status: str = "success"
    message: str = "Request processed successfully"
    data: Optional[Dict[str, Any]] = None


class InterfaceAgent(BaseAgent):
    """
    Central interface agent that coordinates all other agents and MCP services
    """

    def __init__(self, config):
        # Configure the agent for interface coordination
        agent_config = {
            "name": "InterfaceAgent",
            "description": "Central coordination agent for multi-agent system",
            "instructions": self._create_coordination_instructions(),
            "model": config.create_model(
                config.interface_model
                if hasattr(config, "interface_model")
                else config.default_model
            ),
        }
        super().__init__(agent_config)
        self.config = config
        self.agent_manager = None

    def _create_coordination_instructions(self) -> List[str]:
        """Create instructions for agent coordination"""
        return [
            "Du bist der zentrale Koordinator für ein Multi-Agent-System.",
            "Deine Aufgabe ist es, Benutzeranfragen zu analysieren und an die passenden Agents weiterzuleiten.",
            "",
            "VERFÜGBARE AGENTS:",
            "- LektorAgent: Grammatik- und Rechtschreibprüfung",
            "- SentimentAgent: Sentiment-Analyse von Texten",
            "- OptimizerAgent: Textoptimierung mit verschiedenen Tonalitäten",
            "- QueryRefAgent: Verbesserung und Optimierung von Suchanfragen",
            "",
            "VERFÜGBARE MCP SERVICES:",
            "- SearchService: Web-Suche mit DuckDuckGo",
            "- WebService: Website-Extraktion und Analyse",
            "- TimeService: Zeitbezogene Anfragen",
            "",
            "KOORDINATIONSLOGIK:",
            "1. Analysiere die Benutzeranfrage",
            "2. Bestimme den passenden Agent oder Service",
            "3. Leite die Anfrage weiter",
            "4. Verarbeite die Antwort und formatiere sie benutzerfreundlich",
            "5. Bei komplexen Anfragen: Kombiniere mehrere Services/Agents",
            "",
            "ERWEITERTE FÄHIGKEITEN:",
            "- Multi-Step-Verarbeitung: Suche + Zusammenfassung",
            "- Intelligente Analyse von Benutzerintentionen",
            "- Kombination von Services und Agents",
            "",
            "Antworte immer hilfreich und präzise, ohne Emojis zu verwenden.",
        ]

    async def _setup(self):
        """Setup agent manager for coordination"""
        self.agent_manager = AgentManager()
        await self.agent_manager.initialize()

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "agent_coordination",
            "request_routing",
            "multi_agent_orchestration",
            "mcp_service_integration",
            "response_aggregation",
            "multi_step_processing",
            "search_and_summarize",
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle coordination requests"""
        try:
            # Parse request
            if isinstance(request.get("data"), dict):
                query = request["data"].get("query", "")
                agent_type = request["data"].get("agent_type")
                service_type = request["data"].get("service_type")
                parameters = request["data"].get("parameters", {})
            else:
                query = request.get("query", str(request.get("data", "")))
                agent_type = request.get("agent_type")
                service_type = request.get("service_type")
                parameters = request.get("parameters", {})

            if not query or not query.strip():
                return self._create_error_response("No query provided")

            self.logger.info(f"Processing interface request: '{query[:100]}...'")

            # Route request
            response_data = await self._route_request(
                query, agent_type, service_type, parameters
            )

            return self._create_success_response(
                response_data.model_dump(), "Request processed successfully"
            )

        except Exception as e:
            self.logger.error(f"Error processing interface request: {e}")
            return self._create_error_response("Request processing failed", e)

    async def _route_request(
        self,
        query: str,
        agent_type: Optional[str],
        service_type: Optional[str],
        parameters: Dict[str, Any],
    ) -> InterfaceResponse:
        """Route request to appropriate agent or service"""
        try:
            # Determine target if not specified
            if not agent_type and not service_type:
                agent_type, service_type = await self._determine_target(query)

            response_text = ""
            used_component = ""
            response_data = None

            # Handle multi-step processing
            if agent_type == "multi_step" and service_type == "search_and_analyze":
                response_text, response_data = await self._handle_search_and_analyze(
                    query, parameters
                )
                used_component = "InterfaceAgent (Multi-Step)"

            # Route to specific agent
            elif agent_type:
                response_text, response_data = await self._call_agent(
                    agent_type, query, parameters
                )
                used_component = f"{agent_type}Agent"

            # Route to specific service
            elif service_type:
                response_text, response_data = await self._call_service(
                    service_type, query, parameters
                )
                used_component = f"{service_type}Service"

            else:
                response_text = "Ich konnte nicht bestimmen, welcher Agent oder Service für diese Anfrage geeignet ist."
                used_component = "InterfaceAgent"

            return InterfaceResponse(
                response=response_text,
                agent_used=used_component,
                original_query=query,
                data=response_data,
            )

        except Exception as e:
            self.logger.error(f"Error routing request: {e}")
            return InterfaceResponse(
                response=f"Fehler bei der Anfrageverarbeitung: {str(e)}",
                agent_used="InterfaceAgent",
                original_query=query,
                status="error",
                message=f"Routing failed: {str(e)}",
            )

    async def _determine_target(
        self, query: str
    ) -> tuple[Optional[str], Optional[str]]:
        """Determine which agent or service to use based on query analysis"""
        query_lower = query.lower()

        # Check for multi-step requests (search + analysis/summary)
        has_search = any(
            word in query_lower
            for word in ["suche", "finde", "google", "web", "internet", "nachrichten"]
        )
        has_analysis = any(
            word in query_lower
            for word in [
                "zusammenfass",
                "essay",
                "analysier",
                "bewert",
                "erkläre",
                "bericht",
            ]
        )

        if has_search and has_analysis:
            # Multi-step: Search + Analysis - handled specially
            return "multi_step", "search_and_analyze"

        # Agent determination
        if any(
            word in query_lower
            for word in ["korrigier", "grammatik", "rechtschreib", "fehler", "überprüf"]
        ):
            return "lektor", None
        elif any(
            word in query_lower
            for word in [
                "sentiment",
                "stimmung",
                "emotion",
                "gefühl",
                "positiv",
                "negativ",
            ]
        ):
            return "sentiment", None
        elif any(
            word in query_lower
            for word in ["optimier", "tonalität", "stil", "umformulier", "verbessern"]
        ):
            return "optimizer", None
        elif any(
            word in query_lower
            for word in ["suchanfrage", "query", "suche verbessern", "suchbegriff"]
        ):
            return "query_ref", None

        # Service determination
        elif any(
            word in query_lower
            for word in ["suche", "finde", "google", "web", "internet"]
        ):
            return None, "search"
        elif any(
            word in query_lower
            for word in ["website", "url", "webseite", "extrahier", "inhalt"]
        ):
            return None, "web"
        elif any(word in query_lower for word in ["zeit", "datum", "uhrzeit", "wann"]):
            return None, "time"

        # Default to optimizer for general text requests
        return "optimizer", None

    async def _call_agent(
        self, agent_type: str, query: str, parameters: Dict[str, Any]
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """Call specific agent"""
        try:
            agent_map = {
                "lektor": "LektorAgent",
                "sentiment": "SentimentAgent",
                "optimizer": "OptimizerAgent",
                "query_ref": "QueryRefAgent",
            }

            agent_name = agent_map.get(agent_type)
            if not agent_name:
                return f"Unbekannter Agent-Typ: {agent_type}", None

            # Prepare request data based on agent type
            if agent_type == "lektor":
                request_data = {"text": query}
            elif agent_type == "sentiment":
                request_data = {
                    "text": query,
                    "language": parameters.get("language", "de"),
                }
            elif agent_type == "optimizer":
                request_data = {
                    "text": query,
                    "tonality": parameters.get("tonality", "friendly"),
                }
            elif agent_type == "query_ref":
                request_data = {
                    "query": query,
                    "context": parameters.get("context", ""),
                }

            # Use agent manager to call agent
            response = await self.agent_manager.call_agent(agent_name, request_data)

            if response.get("status") == "success":
                data = response.get("data", {})

                # Format response based on agent type
                if agent_type == "lektor":
                    return (
                        f"Korrigierter Text: {data.get('corrected_text', query)}",
                        data,
                    )
                elif agent_type == "sentiment":
                    sentiment = data.get("sentiment", {})
                    return (
                        f"Sentiment: {sentiment.get('label', 'unknown')} (Confidence: {sentiment.get('confidence', 0):.2f})",
                        data,
                    )
                elif agent_type == "optimizer":
                    return (
                        f"Optimierter Text: {data.get('optimized_text', query)}",
                        data,
                    )
                elif agent_type == "query_ref":
                    return (
                        f"Verbesserte Suchanfrage: {data.get('refined_query', query)}",
                        data,
                    )
            else:
                return (
                    f"Fehler bei {agent_name}: {response.get('message', 'Unbekannter Fehler')}",
                    None,
                )

        except Exception as e:
            return f"Fehler beim Aufruf von {agent_type}: {str(e)}", None

    async def _call_service(
        self, service_type: str, query: str, parameters: Dict[str, Any]
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """Call specific MCP service"""
        try:
            service_map = {
                "search": "SearchService",
                "web": "WebService",
                "time": "TimeService",
            }

            service_name = service_map.get(service_type)
            if not service_name:
                return f"Unbekannter Service-Typ: {service_type}", None

            # Prepare request data based on service type
            if service_type == "search":
                request_data = {
                    "query": query,
                    "max_results": parameters.get("max_results", 5),
                }
            elif service_type == "web":
                request_data = {"url": parameters.get("url", query)}
            elif service_type == "time":
                request_data = {"query": query}

            # Use agent manager to call service
            response = await self.agent_manager.call_service(service_name, request_data)

            if response.get("status") == "success":
                data = response.get("data", {})

                # Format response based on service type
                if service_type == "search":
                    results = data.get("results", [])
                    result_text = "\n".join(
                        [
                            f"- {r.get('title', 'No title')}: {r.get('url', 'No URL')}"
                            for r in results[:3]
                        ]
                    )
                    return f"Suchergebnisse:\n{result_text}", data
                elif service_type == "web":
                    return (
                        f"Website-Inhalt extrahiert: {data.get('content', 'Kein Inhalt')[:200]}...",
                        data,
                    )
                elif service_type == "time":
                    return (
                        f"Zeitinformation: {data.get('time_info', 'Keine Zeitinformation verfügbar')}",
                        data,
                    )
            else:
                return (
                    f"Fehler bei {service_name}: {response.get('message', 'Unbekannter Fehler')}",
                    None,
                )

        except Exception as e:
            return f"Fehler beim Aufruf von {service_type}: {str(e)}", None

    async def _handle_search_and_analyze(
        self, query: str, parameters: Dict[str, Any]
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """Handle multi-step: search + analysis/summary"""
        try:
            # Step 1: Extract search terms from query
            search_query = await self._extract_search_terms(query)

            # Step 2: Perform search
            search_request = {
                "query": search_query,
                "max_results": parameters.get("max_results", 5),
            }

            search_response = await self.agent_manager.call_service(
                "SearchService", search_request
            )

            if search_response.get("status") != "success":
                return f"Suche fehlgeschlagen: {search_response.get('message')}", None

            # Step 3: Collect search results
            search_data = search_response.get("data", {})
            results = search_data.get("results", [])

            if not results:
                return "Keine Suchergebnisse gefunden für die Analyse.", None

            # Step 4: Prepare content for analysis
            content_for_analysis = self._prepare_content_for_analysis(results, query)

            # Step 5: Use LLM to create summary/analysis
            analysis_prompt = f"""Basierend auf den folgenden Suchergebnissen zum Thema "{search_query}", erstelle eine zusammenfassende Analyse:

{content_for_analysis}

Benutzeranfrage: {query}

Erstelle eine strukturierte Zusammenfassung mit:
1. Überblick über die wichtigsten Trends und Entwicklungen
2. Konkrete Beispiele aus den Suchergebnissen
3. Fazit und Einschätzung

Antworte auf Deutsch und strukturiert."""

            # Use the agent's LLM for analysis
            analysis_response = self.run(analysis_prompt)

            # Extract analysis text
            if hasattr(analysis_response, "data") and analysis_response.data:
                analysis_text = str(analysis_response.data).strip()
            elif hasattr(analysis_response, "content"):
                analysis_text = str(analysis_response.content).strip()
            else:
                analysis_text = str(analysis_response).strip()

            # Combine search info with analysis
            final_response = f"""SUCHERGEBNISSE UND ANALYSE

Suchbegriff: {search_query}
Gefundene Artikel: {len(results)}

=== ZUSAMMENFASSUNG ===

{analysis_text}

=== QUELLENANGABEN ===
"""

            # Add source references
            for i, result in enumerate(results[:3], 1):
                final_response += f"{i}. {result.get('title', 'Unbekannter Titel')}\n   {result.get('url', 'Keine URL')}\n"

            return final_response, {
                "search_results": results,
                "analysis": analysis_text,
                "search_query": search_query,
                "multi_step": True,
            }

        except Exception as e:
            self.logger.error(f"Error in search and analyze: {e}")
            return f"Fehler bei der Suche und Analyse: {str(e)}", None

    async def _extract_search_terms(self, query: str) -> str:
        """Extract search terms from user query"""
        # Simple extraction - look for main topic after common phrases
        query_lower = query.lower()

        # Remove common phrases
        for phrase in [
            "suche nach",
            "finde",
            "informationen über",
            "nachrichten über",
            "berichte über",
        ]:
            if phrase in query_lower:
                query_lower = query_lower.replace(phrase, "").strip()

        # Remove summary-related terms
        for phrase in ["und fass", "zusammenfass", "essay", "bericht", "analyse"]:
            if phrase in query_lower:
                parts = query_lower.split(phrase)
                query_lower = parts[0].strip()
                break

        return query_lower.strip() or "aktuelle nachrichten"

    def _prepare_content_for_analysis(
        self, results: List[Dict], original_query: str
    ) -> str:
        """Prepare search results content for LLM analysis"""
        content = ""

        for i, result in enumerate(results, 1):
            title = result.get("title", "Unbekannter Titel")
            snippet = result.get("snippet", "Keine Beschreibung")
            url = result.get("url", "Keine URL")

            content += f"""
ARTIKEL {i}:
Titel: {title}
Inhalt: {snippet}
Quelle: {url}

"""

        return content

    async def coordinate_request(
        self,
        query: str,
        agent_type: Optional[str] = None,
        service_type: Optional[str] = None,
        **parameters,
    ) -> InterfaceResponse:
        """Direct method for request coordination"""
        try:
            return await self._route_request(
                query, agent_type, service_type, parameters
            )
        except Exception as e:
            self.logger.error(f"Error coordinating request: {e}")
            return InterfaceResponse(
                response=f"Koordinationsfehler: {str(e)}",
                agent_used="InterfaceAgent",
                original_query=query,
                status="error",
                message=f"Coordination failed: {str(e)}",
            )
