"""
OptimizerAgent - Text optimization agent using agno framework
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OptimizerRequest(BaseModel):
    """Request model for optimizer agent"""

    text: str
    tonality: str = "friendly"


class OptimizerResponse(BaseModel):
    """Response model for optimizer agent"""

    optimized_text: str
    original_text: str
    tonality: str
    status: str = "success"
    message: str = "Text optimized successfully"


class OptimizerAgent(BaseAgent):
    """
    Text optimization agent using LLM with few-shot prompting via agno framework
    """

    def __init__(self, config):
        # Configure the agent for text optimization with few-shot examples
        agent_config = {
            "name": "OptimizerAgent",
            "description": "Text optimization and improvement agent using LLM with few-shot prompting",
            "instructions": self._create_few_shot_instructions(),
            "model": config.create_model(config.optimizer_model),
        }
        super().__init__(agent_config)

    def _create_few_shot_instructions(self) -> List[str]:
        """Create few-shot instruction prompt with examples"""
        return [
            "Du bist ein Experte für Textoptimierung. Optimiere Texte basierend auf der gewünschten Tonalität.",
            "",
            "AUFGABE: Optimiere den gegebenen Text entsprechend der angegebenen Tonalität.",
            "",
            "FEW-SHOT BEISPIELE:",
            "",
            "Beispiel 1 - Tonalität: locker",
            "Input: 'Sehr geehrte Damen und Herren, hiermit teile ich Ihnen mit, dass Ihr Antrag abgelehnt wurde.'",
            "Output: 'Hey! Leider konnten wir deinen Antrag diesmal nicht genehmigen. 😊'",
            "",
            "Beispiel 2 - Tonalität: freundlich",
            "Input: 'Sehr geehrte Damen und Herren, Ihr Antrag wurde abgelehnt.'",
            "Output: 'Vielen Dank für Ihre Anfrage. Leider können wir Ihrem Antrag diesmal nicht entsprechen. Gerne stehen wir Ihnen für Rückfragen zur Verfügung.'",
            "",
            "Beispiel 3 - Tonalität: freundlich",
            "Input: 'Das war Schrott und furchtbar schlecht gemacht.'",
            "Output: 'Das entspricht noch nicht ganz unseren Vorstellungen und könnte deutlich verbessert werden.'",
            "",
            "Beispiel 4 - Tonalität: direkt",
            "Input: 'Vielen Dank für Ihre Anfrage. Leider müssen wir Ihnen mitteilen, dass dies unmöglich ist.'",
            "Output: 'Das ist nicht umsetzbar.'",
            "",
            "Beispiel 5 - Tonalität: sachlich",
            "Input: 'Sehr geehrte Damen und Herren, Ihr Antrag wurde abgelehnt.'",
            "Output: 'Nach Prüfung der Unterlagen wurde der Antrag nicht genehmigt.'",
            "",
            "Beispiel 6 - Tonalität: professionell",
            "Input: 'Das war Schrott und furchtbar schlecht gemacht.'",
            "Output: 'Die Qualität entspricht nicht den geforderten Standards und bedarf einer umfassenden Überarbeitung.'",
            "",
            "Beispiel 7 - Tonalität: begeistert",
            "Input: 'Ihr Projekt wurde genehmigt.'",
            "Output: 'Das ist eine fantastische Nachricht: Ihr Projekt wurde genehmigt! 🌟'",
            "",
            "REGELN:",
            "- Ersetze negative Begriffe durch positive Alternativen",
            "- WICHTIG: Behalte die richtige Anrede bei:",
            "  * 'locker': Verwende 'du' statt 'Sie', casual Sprache",
            "  * 'freundlich': Behalte 'Sie', höflich und respektvoll",
            "  * 'direkt': Kurz und sachlich",
            "  * 'sachlich': Neutral und objektiv, ohne Emotion",
            "  * 'professionell': Formal und geschäftsmäßig",
            "  * 'begeistert': Enthusiastisch mit Verstärkern",
            "",
            "Antworte NUR mit dem optimierten Text, ohne zusätzliche Erklärungen.",
        ]

    async def _setup(self):
        """Setup method - no rules needed for LLM approach"""
        pass

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "text_optimization",
            "tonality_adjustment",
            "sentiment_improvement",
            "formal_to_casual_conversion",
            "business_communication",
            "llm_based_optimization",
            "few_shot_prompting",
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text optimization requests"""
        try:
            # Parse request
            if isinstance(request.get("data"), dict):
                text = request["data"].get("text", "")
                tonality = request["data"].get("tonality", "friendly")
            else:
                text = request.get("text", str(request.get("data", "")))
                tonality = request.get("tonality", "friendly")

            if not text or not text.strip():
                return self._create_error_response("No text provided for optimization")

            self.logger.info(
                f"Optimizing text with tonality '{tonality}': '{text[:100]}...'"
            )

            # Process optimization using LLM
            optimized_text = await self._optimize_text_with_llm(text, tonality)

            response_data = OptimizerResponse(
                optimized_text=optimized_text, original_text=text, tonality=tonality
            )

            return self._create_success_response(
                response_data.model_dump(), "Text optimized successfully"
            )

        except Exception as e:
            self.logger.error(f"Error processing optimizer request: {e}")
            return self._create_error_response("Text optimization failed", e)

    async def _optimize_text_with_llm(self, text: str, tonality: str) -> str:
        """Use LLM to optimize text based on tonality with few-shot prompting"""
        try:
            # Create prompt for the LLM
            prompt = f"""Tonalität: {tonality}
Text: {text}

Optimiere den Text entsprechend der angegebenen Tonalität basierend auf den Few-Shot-Beispielen."""

            # Use the agent's LLM to process the request
            response = self.run(prompt)

            # Extract the optimized text from response
            if hasattr(response, "data") and response.data:
                return str(response.data).strip()
            elif hasattr(response, "content"):
                return str(response.content).strip()
            else:
                return str(response).strip()

        except Exception as e:
            self.logger.error(f"Error during LLM text optimization: {e}")
            return text  # Return original text on error

    async def optimize_text(
        self, text: str, tonality: str = "friendly"
    ) -> OptimizerResponse:
        """Direct method for text optimization using LLM"""
        try:
            optimized_text = await self._optimize_text_with_llm(text, tonality)
            return OptimizerResponse(
                optimized_text=optimized_text, original_text=text, tonality=tonality
            )
        except Exception as e:
            self.logger.error(f"Error optimizing text: {e}")
            return OptimizerResponse(
                optimized_text=text,  # Return original on error
                original_text=text,
                tonality=tonality,
                status="error",
                message=f"Optimization failed: {str(e)}",
            )
