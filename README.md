# AgnoAgent - Multi-Agent System

Eine fortschrittliche Multi-Agent-Architektur mit **agno**, **a2a-sdk** und **MCP (Model Context Protocol)** Integration für intelligente Textverarbeitung und Web-Services.

![AgnoAgent](https://img.shields.io/badge/Agent-System-blue) ![Framework](https://img.shields.io/badge/agno-1.7.6-green) ![A2A](https://img.shields.io/badge/a2a--sdk-0.2.16-orange) ![MCP](https://img.shields.io/badge/MCP-1.0.0-purple) ![License](https://img.shields.io/badge/License-AGPLv3-red)

## Übersicht

AgnoAgent ist ein intelligentes Multi-Agent-System, das verschiedene spezialisierte Agenten für Textverarbeitung, Web-Suche und Analyse bereitstellt. Das System nutzt moderne Frameworks für Agent-zu-Agent-Kommunikation und bietet eine skalierbare, modulare Architektur mit einer benutzerfreundlichen Gradio-Weboberfläche.

### 🌟 Hauptfeatures

- 🤖 **LLM-basierte Agenten** mit OpenAI-kompatiblen Modellen
- 🔄 **Multi-Step Processing** für komplexe Workflows
- 🌐 **Echte Web-Suche** mit DuckDuckGo Integration
- 💬 **Gradio Webinterface** mit monochromatischem Design
- 🎯 **6 Tonalitäten** für Textoptimierung
- 📊 **Real-Time Services** ohne Mock-Implementierungen

## Architektur

### Core Components

- **AgentManager**: Zentrale Verwaltung aller Agenten mit agno Framework
- **MCPServerManager**: Verwaltung von MCP-Services
- **A2A Network**: Agent-zu-Agent-Kommunikation mit a2a-sdk

### Agents

1. **LektorAgent**: Grammatik- und Rechtschreibkorrektur mit LLM
2. **OptimizerAgent**: Text-Optimierung mit 6 Tonalitäten (LLM + Few-Shot)
3. **SentimentAgent**: Sentiment-Analyse und Emotionserkennung
4. **QueryRefAgent**: Query-Verbesserung und -Erweiterung
5. **InterfaceAgent**: Zentrale Koordination und Multi-Step Processing

### MCP Services

1. **SearchService**: Echte Web-Suche mit DuckDuckGo API
2. **WebService**: Web-Scraping mit Headless Browser (Selenium)
3. **TimeService**: NTP-basierte Zeit-Services

## Installation

```bash
# Repository klonen
git clone https://github.com/FBR65/AgnoAgent.git
cd AgnoAgent

# Virtuelle Umgebung erstellen
python -m venv .venv
.venv\Scripts\activate  # Windows

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

## Schnellstart

### 1. Gradio Webinterface starten

```bash
python main.py
# Öffnet automatisch: http://localhost:7860
```

### 2. Einzelne Agenten verwenden

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

- Grammatik- und Rechtschreibkorrektur mit LLM
- Deutsche Sprachverarbeitung
- Automatische Satzbau-Verbesserung
- Agno Framework Integration

### OptimizerAgent

- **LLM-basierte Text-Optimierung** mit Few-Shot Prompting
- **6 Tonalitäten verfügbar:**
  - `freundlich`: Höflich und respektvoll (Sie-Form)
  - `locker`: Casual und entspannt (Du-Form)
  - `direkt`: Kurz und sachlich
  - `begeistert`: Enthusiastisch mit Verstärkern
  - `sachlich`: Neutral und objektiv
  - `professionell`: Formal und geschäftsmäßig
- Negative-zu-Positive Transformationen
- Intelligente Anrede-Anpassung (Du vs. Sie)

### SentimentAgent

- Sentiment-Analyse (positiv/negativ/neutral)
- Emotions-Erkennung
- Konfidenz-Bewertung
- LLM-basierte Verarbeitung

### QueryRefAgent

- Query-Verbesserung und -Erweiterung
- Automatische Umformulierung
- Kontext-Anreicherung
- Suchanfrage-Optimierung

### InterfaceAgent

- **Multi-Step Processing**: Automatische Verkettung von Suche + Analyse
- Intelligente Agent-Koordination
- Zentrale Anfragen-Verteilung
- Workflow-Management

## MCP Service-Details

### SearchService

**Echte DuckDuckGo Integration** (keine Mock-Implementierung):

```python
# Web-Suche mit echten Ergebnissen
results = await search_service.search("KI", num_results=10)

# Bilder-Suche  
images = await search_service.search_images("Python logo")

# News-Suche
news = await search_service.search_news("Künstliche Intelligenz")
```

### WebService

**Echte Web-Extraktion** mit Selenium:

```python
# Text-Extraktion von echten Websites
content = await web_service.extract_text("https://example.com")

# Seiten-Informationen
info = await web_service.get_page_info("https://example.com")
```

### TimeService

**NTP-basierte Zeit-Services**:

```python
# Echte NTP-Zeit
time_result = await time_service.get_current_time()

# Zeitstempel formatieren
formatted = await time_service.format_timestamp(timestamp)

# Zeit-Differenz berechnen
diff = await time_service.time_difference(time1, time2)
```

## Konfiguration

Erstellen Sie eine `.env` Datei für die Konfiguration:

```env
# LLM Configuration (OpenAI-kompatible API)
API_KEY=ollama
BASE_URL=http://localhost:11434/v1

# Model Names (alle LLM-basiert, keine Regeln)
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

# Gradio Interface
GRADIO_HOST=0.0.0.0
GRADIO_PORT=7860
GRADIO_THEME=monochrome

# Logging
LOG_LEVEL=INFO
```

## Gradio Webinterface

Das System verfügt über eine moderne Gradio-Weboberfläche mit:

- **Monochromatisches Design** ohne Emojis
- **6 Tonalitäten** für Text-Optimierung
- **Multi-Step Processing** (Suche + Analyse)
- **Real-Time Feedback**
- **Responsive Design**

### Interface Features

```python
# Verfügbare Funktionen im Webinterface:
- Text-Optimierung (6 Tonalitäten)
- Grammatikkorrektur 
- Sentiment-Analyse
- Web-Suche mit Zusammenfassung
- Multi-Agent Koordination
```

## Entwicklung

### Neue Agenten hinzufügen

1. Erstellen Sie eine neue Agent-Klasse in `src/agents/`
2. Erben Sie von `BaseAgent` (agno.agent.Agent)
3. Implementieren Sie die abstrakten Methoden
4. Registrieren Sie den Agent in `AgentManager`

```python
# Beispiel: Neuer Agent
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, config):
        agent_config = {
            "name": "MyAgent",
            "description": "Custom agent description",
            "instructions": ["Your agent instructions"],
            "model": config.create_model(config.my_model),
        }
        super().__init__(agent_config)
    
    async def handle_request(self, request):
        # Agent Logic hier
        pass
```

### Neue MCP Services hinzufügen

1. Erstellen Sie eine neue Service-Klasse in `src/mcp_services/`
2. Erben Sie von `MCPServiceBase`
3. Implementieren Sie die Service-Methoden
4. Registrieren Sie den Service in `MCPServerManager`

```python
# Beispiel: Neuer MCP Service
from mcp import MCPServiceBase

class MyService(MCPServiceBase):
    async def my_method(self, param: str) -> dict:
        # Service Logic hier
        return {"result": "processed"}
```

### Framework-Prinzipien

- ✅ **Nur LLM-basierte Agenten** (keine Regelverarbeitung)
- ✅ **OpenAI-kompatible APIs** für alle Modelle
- ✅ **Echte Services** (keine Mock-Implementierungen)
- ✅ **Agno Framework** für Agent-Architektur
- ✅ **A2A-SDK** für Agent-zu-Agent-Kommunikation
- ✅ **MCP Protocol** für Service-Integration

## Technologie-Stack

- **agno >= 1.7.6**: Agent-Framework für intelligente Agent-Systeme
- **a2a-sdk >= 0.2.16**: Agent-zu-Agent-Kommunikation
- **MCP >= 1.0.0**: Model Context Protocol für Service-Integration
- **Gradio 5.35.0**: Moderne Webinterface-Entwicklung
- **Pydantic**: Datenvalidierung und -serialisierung
- **Selenium**: Web-Scraping und Browser-Automatisierung
- **DuckDuckGo Search (ddgs)**: Echte Web-Suche-API
- **NTPlib**: Netzwerk-Zeit-Protokoll
- **Trafilatura**: Web-Content-Extraktion
- **OpenAI-kompatible APIs**: Via Ollama oder andere Provider

## Lizenz

AGPLv3 License

**AgnoAgent** - Intelligente Multi-Agent-Systeme mit echter KI-Integration 🤖