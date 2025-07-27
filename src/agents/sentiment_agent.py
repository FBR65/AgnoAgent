"""
SentimentAgent - Sentiment analysis agent using agno framework
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SentimentRequest(BaseModel):
    """Request model for sentiment agent"""

    text: str
    language: str = "de"
    detailed: bool = False


class SentimentScore(BaseModel):
    """Sentiment score model"""

    label: str  # positive, negative, neutral
    confidence: float
    score: float  # -1 to 1


class EmotionItem(BaseModel):
    """Single emotion with intensity"""

    emotion: str
    intensity: float


class SentimentResponse(BaseModel):
    """Response model for sentiment agent"""

    sentiment: SentimentScore
    emotions: List[EmotionItem] = []
    original_text: str
    status: str = "success"
    message: str = "Sentiment analysis completed"


class SentimentAgent(BaseAgent):
    """
    Sentiment analysis agent using agno framework
    """

    def __init__(self, config):
        # Configure the agent for sentiment analysis
        agent_config = {
            "name": "SentimentAgent",
            "description": "Expert sentiment analysis agent",
            "instructions": [
                "Du bist ein Experte für Sentiment-Analyse.",
                "AUFGABE: Analysiere das Sentiment des gegebenen Textes.",
                "Gib das Ergebnis in folgendem JSON-Format zurück:",
                '{"label": "positive|negative|neutral", "confidence": 0.0-1.0, "score": -1.0 bis 1.0, "emotions": [{"emotion": "name", "intensity": 0.0-1.0}]}',
                "REGELN: label: positive (>0.1), negative (<-0.1), neutral (-0.1 bis 0.1)",
            ],
            "model": config.create_model(config.sentiment_model),
        }
        super().__init__(agent_config)

    async def _setup(self):
        """Setup is handled by BaseAgent initialization"""
        self.logger.info("SentimentAgent setup completed")

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "sentiment_analysis",
            "emotion_detection",
            "text_polarity_analysis",
            "confidence_scoring",
            "german_sentiment_processing",
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sentiment analysis requests"""
        try:
            # Parse request
            if isinstance(request.get("data"), dict):
                text = request["data"].get("text", "")
                detailed = request["data"].get("detailed", False)
            else:
                text = request.get("text", str(request.get("data", "")))
                detailed = request.get("detailed", False)

            if not text or not text.strip():
                return self._create_error_response(
                    "No text provided for sentiment analysis"
                )

            self.logger.info(f"Analyzing sentiment for: '{text[:100]}...'")

            # Process with LLM agent
            analysis_result = await self._analyze_sentiment(text, detailed)

            return self._create_success_response(
                analysis_result.model_dump(), "Sentiment analysis completed"
            )

        except Exception as e:
            self.logger.error(f"Error processing sentiment request: {e}")
            return self._create_error_response("Sentiment analysis failed", e)

    async def _analyze_sentiment(
        self, text: str, detailed: bool = False
    ) -> SentimentResponse:
        """Perform sentiment analysis on text"""
        try:
            # Get agno agent analysis
            result = self.run(text)
            llm_response = result.content if hasattr(result, "content") else str(result)

            # Parse LLM response (expecting JSON)
            import json

            try:
                sentiment_data = json.loads(llm_response)
            except json.JSONDecodeError:
                # Fallback to rule-based analysis if LLM doesn't return valid JSON
                sentiment_data = self._fallback_sentiment_analysis(text)

            # Create sentiment score
            sentiment_score = SentimentScore(
                label=sentiment_data.get("label", "neutral"),
                confidence=float(sentiment_data.get("confidence", 0.5)),
                score=float(sentiment_data.get("score", 0.0)),
            )

            # Extract emotions if detailed analysis requested
            emotions = []
            if detailed and "emotions" in sentiment_data:
                for emotion_data in sentiment_data["emotions"]:
                    try:
                        emotion = EmotionItem(
                            emotion=emotion_data.get("emotion", "unknown"),
                            intensity=float(emotion_data.get("intensity", 0.0)),
                        )
                        emotions.append(emotion)
                    except (ValueError, TypeError) as e:
                        self.logger.warning(
                            f"Failed to parse emotion data: {emotion_data}, error: {e}"
                        )
                        continue

            return SentimentResponse(
                sentiment=sentiment_score, emotions=emotions, original_text=text
            )

        except Exception as e:
            self.logger.error(f"Error during sentiment analysis: {e}")
            # Return neutral sentiment on error
            return SentimentResponse(
                sentiment=SentimentScore(label="neutral", confidence=0.0, score=0.0),
                original_text=text,
                status="error",
                message=f"Analysis failed: {str(e)}",
            )

    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Rule-based fallback sentiment analysis"""
        positive_words = [
            "gut",
            "toll",
            "super",
            "fantastisch",
            "großartig",
            "wunderbar",
            "perfekt",
            "ausgezeichnet",
        ]
        negative_words = [
            "schlecht",
            "schrecklich",
            "furchtbar",
            "katastrophal",
            "schlimm",
            "ärgerlich",
            "enttäuschend",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return {
                "label": "positive",
                "confidence": min(0.8, 0.5 + positive_count * 0.1),
                "score": min(1.0, positive_count * 0.3),
                "emotions": [{"freude": min(1.0, positive_count * 0.3)}],
            }
        elif negative_count > positive_count:
            return {
                "label": "negative",
                "confidence": min(0.8, 0.5 + negative_count * 0.1),
                "score": max(-1.0, -negative_count * 0.3),
                "emotions": [{"ärger": min(1.0, negative_count * 0.3)}],
            }
        else:
            return {"label": "neutral", "confidence": 0.6, "score": 0.0, "emotions": []}

    async def analyze_sentiment(
        self, text: str, detailed: bool = False
    ) -> SentimentResponse:
        """Direct method for sentiment analysis"""
        return await self._analyze_sentiment(text, detailed)

    async def shutdown(self):
        """Shutdown the agent"""
        self.logger.info("SentimentAgent shutdown completed")
