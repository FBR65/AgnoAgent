"""
Launcher script for AgnoAgent Gradio Interface
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)


def main():
    from interface.gradio_app import main as gradio_main

    gradio_main()


if __name__ == "__main__":
    main()
