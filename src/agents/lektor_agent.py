"""
LektorAgent - Grammar correction agent using agno framework
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LektorRequest(BaseModel):
    """Request model for lektor agent"""

    text: str
    language: str = "de"


class LektorResponse(BaseModel):
    """Response model for lektor agent"""

    corrected_text: str
    original_text: str
    status: str = "success"
    message: str = "Grammar corrected successfully"


class LektorAgent(BaseAgent):
    """
    Grammar correction agent using agno framework
    """

    def __init__(self, config):
        # Configure the agent for grammar correction
        agent_config = {
            "name": "LektorAgent",
            "description": "Professional German grammar correction agent",
            "instructions": [
                "Du bist ein professioneller deutscher Lektor.",
                "AUFGABE: Korrigiere ALLE Grammatik-, Rechtschreib- und Satzbaufehler im gegebenen Text.",
                "Gib NUR den korrigierten Text zurück, KEINE Erklärungen oder Kommentare.",
                "WICHTIG: Bewerte die Korrektheit mit einer Bewertung von 1-100 am Ende.",
            ],
            "model": config.create_model(config.lektor_model),
        }
        super().__init__(agent_config)

    async def _setup(self):
        """Setup is handled by BaseAgent initialization"""
        self.logger.info("LektorAgent setup completed")

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "grammar_correction",
            "spelling_correction",
            "german_language_processing",
            "text_correction",
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle grammar correction requests"""
        try:
            # Parse request
            if isinstance(request.get("data"), dict):
                text = request["data"].get("text", "")
            else:
                text = request.get("text", str(request.get("data", "")))

            if not text or not text.strip():
                return self._create_error_response("No text provided for correction")

            self.logger.info(f"Processing text: '{text[:100]}...'")

            # Process with agno agent
            result = self.run(text)
            corrected_text = (
                result.content if hasattr(result, "content") else str(result)
            )

            response_data = LektorResponse(
                corrected_text=corrected_text, original_text=text
            )

            return self._create_success_response(
                response_data.model_dump(), "Text corrected successfully"
            )

        except Exception as e:
            self.logger.error(f"Error processing lektor request: {e}")
            return self._create_error_response("Grammar correction failed", e)

    async def correct_text(self, text: str) -> LektorResponse:
        """Direct method for text correction"""
        try:
            result = self.run(text)
            corrected_text = (
                result.content if hasattr(result, "content") else str(result)
            )
            return LektorResponse(corrected_text=corrected_text, original_text=text)
        except Exception as e:
            self.logger.error(f"Error correcting text: {e}")
            return LektorResponse(
                corrected_text=text,  # Return original on error
                original_text=text,
                status="error",
                message=f"Correction failed: {str(e)}",
            )

    async def shutdown(self):
        """Shutdown the agent"""
        self.logger.info("LektorAgent shutdown completed")
