"""
QueryRefAgent - Query refinement agent            "model": config.create_model(getattr(config, 'query_ref_model', config.ui_model)),using agno framework
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class QueryRefRequest(BaseModel):
    """Request model for query ref agent"""

    text: str


class QueryRefResponse(BaseModel):
    """Response model for query ref agent"""

    query: str
    original_text: str
    status: str = "success"
    message: str = "Query enhanced successfully"


class QueryRefAgent(BaseAgent):
    """
    Query refinement agent using rule-based enhancement with agno framework
    """

    def __init__(self, config):
        # Configure the agent for query refinement
        agent_config = {
            "name": "QueryRefAgent",
            "description": "Query refinement and enhancement agent",
            "instructions": [
                "Du bist ein Experte für Query-Optimierung.",
                "AUFGABE: Verbessere und erweitere gegebene Suchanfragen.",
                "Mache aus kurzen Anfragen detailliertere und präzisere Suchanfragen.",
                "Füge relevante Keywords und Kontext hinzu.",
            ],
            "model": getattr(config, "query_ref_model", config.ui_model),
        }
        super().__init__(agent_config)
        self.enhancement_rules = {}

    async def _setup(self):
        """Setup query enhancement rules"""
        self.enhancement_rules = self._load_enhancement_rules()

    def _load_enhancement_rules(self) -> Dict[str, str]:
        """Load query enhancement patterns"""
        return {
            "Erkläre KI": "Erkläre mir ausführlich die Grundlagen der Künstlichen Intelligenz, einschließlich ihrer wichtigsten Anwendungsbereiche und aktuellen Entwicklungen.",
            "Was ist KI": "Was ist Künstliche Intelligenz? Bitte erkläre die Definition, Geschichte und verschiedene Arten von KI-Systemen.",
            "KI": "Künstliche Intelligenz: Bitte gib mir eine umfassende Erklärung zu Definition, Funktionsweise und praktischen Anwendungen.",
            "maschinelles Lernen": "Erkläre mir maschinelles Lernen detailliert, einschließlich der verschiedenen Algorithmen, Anwendungsfälle und wie es sich von traditioneller Programmierung unterscheidet.",
            "Machine Learning": "Erkläre mir maschinelles Lernen detailliert, einschließlich der verschiedenen Algorithmen, Anwendungsfälle und wie es sich von traditioneller Programmierung unterscheidet.",
            "Deep Learning": "Was ist Deep Learning? Erkläre mir die Konzepte neuronaler Netzwerke, deren Architektur und praktische Anwendungen.",
            "Python": "Erkläre mir die Programmiersprache Python, ihre Syntax, wichtigsten Features und Anwendungsbereiche.",
            "JavaScript": "Was ist JavaScript? Erkläre mir die Grundlagen, Syntax und wie es in der Webentwicklung verwendet wird.",
        }

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "query_refinement",
            "query_enhancement",
            "search_optimization",
            "intent_clarification",
            "question_improvement",
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query refinement requests"""
        try:
            # Parse request
            if isinstance(request.get("data"), dict):
                text = request["data"].get("text", "")
            else:
                text = request.get("text", str(request.get("data", "")))

            if not text or not text.strip():
                return self._create_error_response(
                    "No text provided for query refinement"
                )

            self.logger.info(f"Refining query: '{text[:100]}...'")

            # Process query refinement
            enhanced_query = await self._enhance_query(text)

            response_data = QueryRefResponse(query=enhanced_query, original_text=text)

            return self._create_success_response(
                response_data.model_dump(), "Query enhanced successfully"
            )

        except Exception as e:
            self.logger.error(f"Error processing query ref request: {e}")
            return self._create_error_response("Query refinement failed", e)

    async def _enhance_query(self, text: str) -> str:
        """Enhance query using rule-based patterns"""
        try:
            # Extract actual query from instruction text
            query_to_improve = self._extract_query_from_input(text)

            # Apply specific enhancements
            for simple_query, enhanced_query in self.enhancement_rules.items():
                if simple_query.lower() in query_to_improve.lower():
                    return enhanced_query

            # Apply general enhancement rules if no specific match
            return self._apply_general_enhancements(query_to_improve)

        except Exception as e:
            self.logger.error(f"Error during query enhancement: {e}")
            return text  # Return original text on error

    def _extract_query_from_input(self, full_text: str) -> str:
        """Extract actual query from input text"""
        if ":" in full_text:
            parts = full_text.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip()

        return full_text

    def _apply_general_enhancements(self, query: str) -> str:
        """Apply general enhancement rules"""
        # For very short queries
        if len(query.split()) < 3:
            return f"Bitte erkläre mir ausführlich das Thema '{query}' mit praktischen Beispielen und Hintergrundinformationen."

        # For queries without question marks
        if not query.endswith("?"):
            return f"{query}? Bitte gib mir eine detaillierte Antwort mit Beispielen."

        # For existing questions
        return f"{query} Bitte strukturiere deine Antwort mit klaren Abschnitten und praktischen Beispielen."

    async def enhance_query(self, text: str) -> QueryRefResponse:
        """Direct method for query enhancement"""
        try:
            enhanced_query = await self._enhance_query(text)
            return QueryRefResponse(query=enhanced_query, original_text=text)
        except Exception as e:
            self.logger.error(f"Error enhancing query: {e}")
            return QueryRefResponse(
                query=text,  # Return original on error
                original_text=text,
                status="error",
                message=f"Enhancement failed: {str(e)}",
            )
