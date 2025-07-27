# Migration Guide - Refactoring zu agno, a2a-sdk und MCP

## Übersicht der Änderungen

Die AgnoAgent-Architektur wurde komplett refaktoriert, um moderne Frameworks zu nutzen:

- **agno**: Intelligentes Agent-Framework für bessere Agent-Verwaltung
- **a2a-sdk**: Agent-zu-Agent-Kommunikation
- **MCP**: Model Context Protocol für Service-Integration

## Architektur-Vergleich

### Vorher (Alte Architektur)
```
agent_server/
├── lektor.py              # pydantic-ai basiert
├── optimizer.py           # Standalone Logik
├── sentiment.py           # pydantic-ai + MCP HTTP
├── query_ref.py           # Regel-basiert
├── prompt_engineer.py     # Complex intent detection
└── user_interface.py      # Monolithisches UI

mcp_server/
├── mcp_search/duck_search.py      # Standalone Klassen
├── mcp_time/ntp_time.py           # Standalone Klassen  
└── mcp_website/headless_browser.py # Standalone Klassen
```

### Nachher (Neue Architektur)
```
src/
├── core/
│   ├── agent_manager.py     # Zentrale Agent-Verwaltung mit agno
│   ├── mcp_manager.py       # MCP Service Management
│   └── config.py            # Einheitliche Konfiguration
├── agents/
│   ├── base_agent.py        # Basis-Klasse für alle Agenten
│   ├── lektor_agent.py      # agno LLMAgent Integration
│   ├── optimizer_agent.py   # Erweiterte regel-basierte Optimierung
│   ├── sentiment_agent.py   # agno + verbessertes Fallback
│   └── query_ref_agent.py   # Strukturierte Query-Verbesserung
└── mcp_services/
    ├── search_service.py    # MCP-kompatibel
    ├── web_service.py       # MCP-kompatibel
    └── time_service.py      # MCP-kompatibel
```

## Code-Migrations-Schritte

### 1. Abhängigkeiten aktualisieren

```toml
# Alte pyproject.toml
dependencies = [
    "a2a-sdk>=0.2.16",
    "agno>=1.7.6",
]

# Neue pyproject.toml  
dependencies = [
    "a2a-sdk>=0.2.16",
    "agno>=1.7.6", 
    "mcp>=1.0.0",
    "pydantic>=2.0.0",
    "httpx>=0.24.0",
    # ... weitere Abhängigkeiten
]
```

### 2. Agent-Migrationen

#### Lektor Agent Migration

**Vorher:**
```python
# agent_server/lektor.py
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

lektor_agent = Agent(
    model=model,
    result_type=LektorResponse,
    system_prompt="..."
)

async def lektor_a2a_function(messages):
    # Direkte pydantic-ai Nutzung
    result = await lektor_agent.run(text, ctx=context)
    return result.data
```

**Nachher:**
```python
# src/agents/lektor_agent.py
from agno import LLMAgent
from .base_agent import BaseAgent

class LektorAgent(BaseAgent):
    async def _setup(self):
        self.llm_agent = LLMAgent(
            model_name=self.config.lektor_model,
            api_key=self.config.llm_api_key,
            base_url=self.config.llm_base_url,
            system_prompt="..."
        )
    
    async def handle_request(self, request):
        text = request['data'].get('text', '')
        corrected_text = await self.llm_agent.process(text)
        return self._create_success_response({
            "corrected_text": corrected_text,
            "original_text": text
        })
```

#### MCP Services Migration

**Vorher:**
```python
# mcp_server/mcp_search/duck_search.py
class DuckDuckGoSearcher:
    def search(self, query: str, num_results: int = 10):
        # Standalone Implementierung
```

**Nachher:**
```python
# src/mcp_services/search_service.py
from mcp import MCPService

class SearchService(MCPService):
    def __init__(self):
        super().__init__(name="search_service")
    
    async def search(self, query: str, num_results: int = 10):
        # MCP-kompatible Implementierung
```

### 3. Konfiguration zentralisieren

**Vorher:**
```python
# Verteilte Konfiguration in jeder Datei
llm_api_key = os.getenv("API_KEY", "ollama")
llm_endpoint = os.getenv("BASE_URL", "http://localhost:11434/v1")
```

**Nachher:**
```python
# src/core/config.py - Zentrale Konfiguration
@dataclass
class Config:
    llm_api_key: str = os.getenv("API_KEY", "ollama")
    llm_base_url: str = os.getenv("BASE_URL", "http://localhost:11434/v1")
    # ... weitere Konfiguration

# Verwendung in Agenten
from ..core.config import config
```

## Verwendung der neuen Architektur

### 1. System initialisieren

```python
from src.core import AgentManager, MCPServerManager

async def main():
    # Manager initialisieren
    agent_manager = AgentManager()
    mcp_manager = MCPServerManager()
    
    await agent_manager.initialize()
    await mcp_manager.initialize()
```

### 2. Agenten verwenden

```python
# Neue Request-Struktur
request = {
    "type": "lektor",
    "data": {
        "text": "Text zum korrigieren"
    }
}

result = await agent_manager.process_request(request)
```

### 3. MCP Services verwenden

```python
# Service direkt abrufen und verwenden
search_service = await mcp_manager.get_service("search")
results = await search_service.search("query", num_results=5)
```

## Vorteile der neuen Architektur

### 1. Bessere Modularität
- Klare Trennung zwischen Agenten und Services
- Standardisierte Basis-Klassen
- Einheitliche Fehlerbehandlung

### 2. Verbesserte Skalierbarkeit
- **agno** Framework für intelligente Agent-Verwaltung
- **a2a-sdk** für Agent-zu-Agent-Kommunikation
- **MCP** für Service-Integration

### 3. Einfachere Wartung
- Zentrale Konfiguration
- Konsistente API-Struktur
- Standardisierte Response-Formate

### 4. Erweiterte Funktionen
- Intelligentes Agent-Routing mit agno
- Automatische Service-Discovery
- Verbesserte Fehlerbehandlung und Logging

## Migration-Checkliste

- [ ] Alte `agent_server/` und `mcp_server/` Verzeichnisse als Backup sichern
- [ ] Neue `src/` Struktur implementieren
- [ ] `pyproject.toml` mit neuen Abhängigkeiten aktualisieren
- [ ] `.env` Datei für zentrale Konfiguration erstellen
- [ ] Agenten auf neue BaseAgent-Klasse migrieren
- [ ] MCP Services auf neue MCPService-Basis migrieren
- [ ] Tests für neue Architektur implementieren
- [ ] Dokumentation aktualisieren

## Testverfahren

1. **Einzelne Agenten testen:**
```bash
python -c "
import asyncio
from src.agents import LektorAgent
from src.core.config import config

async def test():
    agent = LektorAgent(config)
    await agent.initialize()
    result = await agent.correct_text('Das ist ein schlechte Satz.')
    print(result.corrected_text)

asyncio.run(test())
"
```

2. **MCP Services testen:**
```bash
python -c "
import asyncio
from src.mcp_services import SearchService

async def test():
    service = SearchService()
    await service.initialize()
    result = await service.search('Python')
    print(f'Found {len(result.results)} results')

asyncio.run(test())
"
```

3. **Vollständiges System testen:**
```bash
python main.py
```

## Troubleshooting

### Häufige Probleme

1. **Import-Fehler:** Stellen Sie sicher, dass alle neuen Abhängigkeiten installiert sind
2. **Konfigurationsfehler:** Prüfen Sie die `.env` Datei
3. **Agent-Kommunikation:** Überprüfen Sie A2A-Network-Konfiguration
4. **MCP-Services:** Stellen Sie sicher, dass MCP-Server läuft

### Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detailliertes Logging für Debugging
```

Die neue Architektur bietet eine robuste, skalierbare Basis für die weitere Entwicklung des AgnoAgent-Systems.
