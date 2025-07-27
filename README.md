# AgnoAgent - Multi-Agent System

Eine fortschrittliche Multi-Agent-Architektur mit **agno**, **a2a-sdk** und **MCP (Model Context Protocol)** Integration.

## Übersicht

AgnoAgent ist ein intelligentes Agent-System, das verschiedene spezialisierte Agenten für Textverarbeitung, Suche und Analyse bereitstellt. Das System nutzt moderne Frameworks für Agent-zu-Agent-Kommunikation und bietet eine skalierbare, modulare Architektur.

## Architektur

### Core Components

- **AgentManager**: Zentrale Verwaltung aller Agenten mit agno Framework
- **MCPServerManager**: Verwaltung von MCP-Services
- **A2A Network**: Agent-zu-Agent-Kommunikation mit a2a-sdk

### Agents

1. **LektorAgent**: Grammatik- und Rechtschreibkorrektur
2. **OptimizerAgent**: Text-Optimierung mit verschiedenen Tonalitäten
3. **SentimentAgent**: Sentiment-Analyse und Emotionserkennung
4. **QueryRefAgent**: Query-Verbesserung und -Erweiterung

### MCP Services

1. **SearchService**: Web-Suche mit DuckDuckGo
2. **WebService**: Web-Scraping mit Headless Browser
3. **TimeService**: Zeit-Services mit NTP

## Installation

```bash
# Abhängigkeiten installieren
pip install -e .

# Umgebungsvariablen konfigurieren (optional .env erstellen)
API_KEY=ollama
BASE_URL=http://localhost:11434/v1
LEKTOR_MODEL=qwen2.5:latest
MCP_HOST=localhost
MCP_PORT=8000
A2A_NETWORK_ID=agno-network
```

## Verwendung

### Basis-Verwendung

```python
import asyncio
from src.core import AgentManager

async def main():
    agent_manager = AgentManager()
    await agent_manager.initialize()
    
    # Grammatikkorrektur
    request = {
        "type": "lektor",
        "data": {"text": "Das ist ein schlechte Satz."}
    }
    result = await agent_manager.process_request(request)
    print(result["data"]["corrected_text"])

asyncio.run(main())
```

### System starten

```bash
python main.py
```

### MCP Services nutzen

```python
from src.core import MCPServerManager

async def use_mcp():
    mcp_manager = MCPServerManager()
    await mcp_manager.initialize()
    
    # Suche durchführen
    search_service = await mcp_manager.get_service("search")
    results = await search_service.search("Python", num_results=5)
    
    # Website-Inhalt extrahieren
    web_service = await mcp_manager.get_service("web")
    content = await web_service.extract_text("https://example.com")
    
    # Aktuelle Zeit abrufen
    time_service = await mcp_manager.get_service("time")
    current_time = await time_service.get_current_time()
```

## Agent-Funktionalitäten

### LektorAgent
- Grammatik- und Rechtschreibkorrektur
- Deutsche Sprachverarbeitung
- Automatische Satzbau-Verbesserung

### OptimizerAgent
- Text-Optimierung nach Tonalität
- Unterstützte Tonalitäten: freundlich, locker, direkt, begeistert
- Negative-zu-Positive Transformationen

### SentimentAgent
- Sentiment-Analyse (positiv/negativ/neutral)
- Emotions-Erkennung
- Konfidenz-Bewertung

### QueryRefAgent
- Query-Verbesserung und -Erweiterung
- Automatische Umformulierung
- Kontext-Anreicherung

## MCP Service-Details

### SearchService
```python
# Web-Suche
results = await search_service.search("KI", num_results=10)

# Bilder-Suche  
images = await search_service.search_images("Python logo")

# News-Suche
news = await search_service.search_news("Künstliche Intelligenz")
```

### WebService
```python
# Text-Extraktion
content = await web_service.extract_text("https://example.com")

# Seiten-Informationen
info = await web_service.get_page_info("https://example.com")
```

### TimeService
```python
# NTP-Zeit
time_result = await time_service.get_current_time()

# Zeitstempel formatieren
formatted = await time_service.format_timestamp(timestamp)

# Zeit-Differenz berechnen
diff = await time_service.time_difference(time1, time2)
```

## Konfiguration

Erstellen Sie eine `.env` Datei für die Konfiguration:

```env
# LLM Configuration
API_KEY=ollama
BASE_URL=http://localhost:11434/v1

# Model Names
LEKTOR_MODEL=qwen2.5:latest
OPTIMIZER_MODEL=qwen2.5:latest
SENTIMENT_MODEL=qwen2.5:latest
USER_INTERFACE_MODEL=qwen2.5:latest

# MCP Configuration
MCP_HOST=localhost
MCP_PORT=8000
MCP_SCHEME=http

# A2A Configuration
A2A_NETWORK_ID=agno-network
A2A_DISCOVERY_HOST=localhost
A2A_DISCOVERY_PORT=9000

# Logging
LOG_LEVEL=INFO
```

## Entwicklung

### Neue Agenten hinzufügen

1. Erstellen Sie eine neue Agent-Klasse in `src/agents/`
2. Erben Sie von `BaseAgent`
3. Implementieren Sie die abstrakten Methoden
4. Registrieren Sie den Agent in `AgentManager`

### Neue MCP Services hinzufügen

1. Erstellen Sie eine neue Service-Klasse in `src/mcp_services/`
2. Erben Sie von `MCPService`
3. Implementieren Sie die Service-Methoden
4. Registrieren Sie den Service in `MCPServerManager`

## Technologie-Stack

- **agno**: Agent-Framework für intelligente Agent-Systeme
- **a2a-sdk**: Agent-zu-Agent-Kommunikation
- **MCP**: Model Context Protocol für Service-Integration
- **Pydantic**: Datenvalidierung und -serialisierung
- **Selenium**: Web-Scraping und Browser-Automatisierung
- **DuckDuckGo Search**: Web-Suche-API
- **NTPlib**: Netzwerk-Zeit-Protokoll

## Lizenz

AGPLv3 License

