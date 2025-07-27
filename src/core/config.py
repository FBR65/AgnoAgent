"""
Configuration management for AgnoAgent
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from agno.models.openai import OpenAILike

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Central configuration for the AgnoAgent system"""

    # LLM Configuration
    llm_api_key: str = os.getenv("API_KEY", "ollama")
    llm_base_url: str = os.getenv("BASE_URL", "http://localhost:11434/v1")

    # Model names
    lektor_model: str = os.getenv("LEKTOR_MODEL", "qwen2.5:latest")
    optimizer_model: str = os.getenv("OPTIMIZER_MODEL", "qwen2.5:latest")
    sentiment_model: str = os.getenv("SENTIMENT_MODEL", "qwen2.5:latest")
    ui_model: str = os.getenv("USER_INTERFACE_MODEL", "qwen2.5:latest")
    interface_model: str = os.getenv("INTERFACE_MODEL", "qwen2.5:latest")
    default_model: str = os.getenv("DEFAULT_MODEL", "qwen2.5:latest")

    # MCP Server Configuration
    mcp_host: str = os.getenv("MCP_HOST", "localhost")
    mcp_port: int = int(os.getenv("MCP_PORT", "8000"))
    mcp_scheme: str = os.getenv("MCP_SCHEME", "http")

    # A2A Configuration
    a2a_network_id: str = os.getenv("A2A_NETWORK_ID", "agno-network")
    a2a_discovery_host: str = os.getenv("A2A_DISCOVERY_HOST", "localhost")
    a2a_discovery_port: int = int(os.getenv("A2A_DISCOVERY_PORT", "9000"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def mcp_url(self) -> str:
        """Get full MCP server URL"""
        return f"{self.mcp_scheme}://{self.mcp_host}:{self.mcp_port}"

    @property
    def a2a_discovery_url(self) -> str:
        """Get A2A discovery URL"""
        return f"http://{self.a2a_discovery_host}:{self.a2a_discovery_port}"

    def create_model(self, model_name: str) -> OpenAILike:
        """Create an OpenAI-compatible model instance for the given model name"""
        return OpenAILike(
            id=model_name,
            name=model_name,
            provider="Ollama",
            base_url=self.llm_base_url,
            api_key=self.llm_api_key if self.llm_api_key != "ollama" else "sk-dummy",
            temperature=0.7,
            max_tokens=2048,
        )


# Global config instance
config = Config()
