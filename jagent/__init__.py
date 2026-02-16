"""
jagent - Educational AI Agent Framework

A lightweight implementation for learning how AI coding assistants work.
"""

__version__ = "0.1.0"

from jagent.core.tool import Tool
from jagent.core.registry import ToolRegistry
from jagent.core.agent import Agent

__all__ = ["Tool", "ToolRegistry", "Agent", "__version__"]
