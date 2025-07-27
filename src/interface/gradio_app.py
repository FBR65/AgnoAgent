"""
Gradio Web Interface for AgnoAgent Multi-Agent System
"""

import asyncio
import logging
import gradio as gr
from typing import Tuple
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.config import Config
from agents.interface_agent import InterfaceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgnoAgentInterface:
    """Gradio interface for the AgnoAgent system"""

    def __init__(self):
        self.config = Config()
        self.interface_agent = None
        self._setup_complete = False

    async def _setup_async(self):
        """Async setup of the interface agent"""
        if not self._setup_complete:
            self.interface_agent = InterfaceAgent(self.config)
            await self.interface_agent._setup()
            self._setup_complete = True
            logger.info("AgnoAgent Interface initialized successfully")

    def _run_async(self, coro):
        """Helper to run async functions in Gradio"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    def process_query(
        self,
        query: str,
        agent_type: str = "Auto",
        service_type: str = "Auto",
        tonality: str = "freundlich",
        language: str = "de",
        max_results: int = 5,
    ) -> Tuple[str, str, str]:
        """Process user query through the interface agent"""
        try:
            # Setup if not done
            if not self._setup_complete:
                self._run_async(self._setup_async())

            if not query.strip():
                return "Bitte geben Sie eine Anfrage ein.", "", ""

            # Prepare parameters
            parameters = {
                "tonality": tonality,
                "language": language,
                "max_results": max_results,
            }

            # Convert UI selections to internal format
            agent_type_internal = None if agent_type == "Auto" else agent_type.lower()
            service_type_internal = (
                None if service_type == "Auto" else service_type.lower()
            )

            # Process request
            response = self._run_async(
                self.interface_agent.coordinate_request(
                    query, agent_type_internal, service_type_internal, **parameters
                )
            )

            # Format response
            main_response = response.response
            agent_used = f"Verwendet: {response.agent_used}"

            # Additional details
            details = (
                f"Status: {response.status}\nOriginal Query: {response.original_query}"
            )
            if response.data:
                details += "\nZusätzliche Daten verfügbar"

            return main_response, agent_used, details

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Fehler bei der Verarbeitung: {str(e)}", "Fehler", ""

    def create_interface(self):
        """Create the Gradio interface"""

        # Custom CSS for monochrome theme
        custom_css = """
        .gradio-container {
            background-color: #f8f9fa !important;
            color: #212529 !important;
        }
        .dark .gradio-container {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        .gr-button {
            background-color: #6c757d !important;
            border-color: #6c757d !important;
            color: white !important;
        }
        .gr-button:hover {
            background-color: #545862 !important;
            border-color: #545862 !important;
        }
        .gr-textbox, .gr-dropdown {
            border-color: #ced4da !important;
        }
        .dark .gr-textbox, .dark .gr-dropdown {
            border-color: #495057 !important;
            background-color: #343a40 !important;
            color: #ffffff !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #212529 !important;
        }
        .dark h1, .dark h2, .dark h3, .dark h4, .dark h5, .dark h6 {
            color: #ffffff !important;
        }
        """

        with gr.Blocks(
            theme=gr.themes.Monochrome(),
            css=custom_css,
            title="AgnoAgent - Multi-Agent System",
        ) as interface:
            gr.Markdown(
                """
                # AgnoAgent Multi-Agent System
                
                Intelligente Textverarbeitung durch spezialisierte Agents und Services.
                Geben Sie Ihre Anfrage ein und das System wird automatisch den passenden Agent auswählen.
                """
            )

            with gr.Row():
                with gr.Column(scale=2):
                    # Input section
                    gr.Markdown("## Eingabe")

                    query_input = gr.Textbox(
                        label="Ihre Anfrage",
                        placeholder="z.B. 'Korrigiere diesen Text', 'Analysiere die Stimmung', 'Optimiere für lockere Tonalität'",
                        lines=3,
                    )

                    with gr.Row():
                        agent_selector = gr.Dropdown(
                            choices=[
                                "Auto",
                                "Lektor",
                                "Sentiment",
                                "Optimizer",
                                "Query_Ref",
                            ],
                            value="Auto",
                            label="Agent auswählen",
                            info="Lassen Sie 'Auto' für automatische Auswahl",
                        )

                        service_selector = gr.Dropdown(
                            choices=["Auto", "Search", "Web", "Time"],
                            value="Auto",
                            label="Service auswählen",
                            info="Lassen Sie 'Auto' für automatische Auswahl",
                        )

                    # Advanced parameters
                    with gr.Accordion("Erweiterte Einstellungen", open=False):
                        tonality_input = gr.Dropdown(
                            choices=[
                                "freundlich",
                                "locker",
                                "direkt",
                                "sachlich",
                                "professionell",
                                "begeistert",
                            ],
                            value="freundlich",
                            label="Tonalität (für Optimizer)",
                        )

                        language_input = gr.Dropdown(
                            choices=["de", "en"],
                            value="de",
                            label="Sprache (für Sentiment)",
                        )

                        max_results_input = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=5,
                            step=1,
                            label="Max. Suchergebnisse (für Search)",
                        )

                    process_btn = gr.Button("Verarbeiten", variant="primary")

                with gr.Column(scale=2):
                    # Output section
                    gr.Markdown("## Ergebnis")

                    response_output = gr.Textbox(
                        label="Antwort", lines=8, interactive=False
                    )

                    agent_used_output = gr.Textbox(
                        label="Verwendeter Agent/Service", interactive=False
                    )

                    details_output = gr.Textbox(
                        label="Details", lines=3, interactive=False
                    )

            # Examples section
            gr.Markdown("## Beispiele")

            with gr.Row():
                example_buttons = [
                    gr.Button("Grammatikprüfung"),
                    gr.Button("Sentiment-Analyse"),
                    gr.Button("Text optimieren"),
                    gr.Button("Web-Suche"),
                ]

            # Event handlers
            process_btn.click(
                fn=self.process_query,
                inputs=[
                    query_input,
                    agent_selector,
                    service_selector,
                    tonality_input,
                    language_input,
                    max_results_input,
                ],
                outputs=[response_output, agent_used_output, details_output],
            )

            # Example button handlers
            example_buttons[0].click(
                lambda: "Das ist ein Beispiel text mit eingen rechtschreibfehlern.",
                outputs=query_input,
            )

            example_buttons[1].click(
                lambda: "Ich bin sehr glücklich mit diesem fantastischen Ergebnis!",
                outputs=query_input,
            )

            example_buttons[2].click(
                lambda: "Sehr geehrte Damen und Herren, Ihr Antrag wurde abgelehnt.",
                outputs=query_input,
            )

            example_buttons[3].click(
                lambda: "Suche nach aktuellen Nachrichten über Künstliche Intelligenz",
                outputs=query_input,
            )

            # Footer
            gr.Markdown(
                """
                ---
                **AgnoAgent** - Powered by agno, a2a-sdk, and MCP
                """
            )

        return interface

    def launch(self, share=False, server_name="127.0.0.1", server_port=7860):
        """Launch the Gradio interface"""
        interface = self.create_interface()

        logger.info(f"Starting AgnoAgent Interface on {server_name}:{server_port}")

        interface.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            show_error=True,
            quiet=False,
        )


def main():
    """Main entry point"""
    try:
        app = AgnoAgentInterface()
        app.launch()
    except KeyboardInterrupt:
        logger.info("AgnoAgent Interface stopped by user")
    except Exception as e:
        logger.error(f"Error launching interface: {e}")
        raise


if __name__ == "__main__":
    main()
