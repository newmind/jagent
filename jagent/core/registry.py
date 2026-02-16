"""Tool registry for managing available tools."""

from typing import Dict, List, Optional, Type
from jagent.core.tool import Tool


class ToolRegistry:
    """
    Registry for managing available tools.

    The registry keeps track of all tools that can be used by the agent.
    Tools can be registered, retrieved, and listed.

    Example:
        registry = ToolRegistry()
        registry.register(EchoTool())
        tool = registry.get("echo")
        all_tools = registry.list_tools()
    """

    def __init__(self) -> None:
        """Initialize an empty tool registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register

        Raises:
            ValueError: If a tool with the same name is already registered
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                f"Use unregister() first to replace it."
            )
        self._tools[tool.name] = tool

    def register_many(self, tools: List[Tool]) -> None:
        """
        Register multiple tools at once.

        Args:
            tools: List of tool instances to register
        """
        for tool in tools:
            self.register(tool)

    def unregister(self, name: str) -> Optional[Tool]:
        """
        Unregister a tool by name.

        Args:
            name: Name of the tool to unregister

        Returns:
            The unregistered tool, or None if not found
        """
        return self._tools.pop(name, None)

    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            name: Name of the tool

        Returns:
            The tool instance, or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        """
        Get all registered tools.

        Returns:
            List of all registered tool instances
        """
        return list(self._tools.values())

    def to_anthropic_tools(self) -> List[Dict]:
        """
        Convert all registered tools to Anthropic's tool format.

        Returns:
            List of tool definitions for Anthropic API
        """
        return [tool.to_anthropic_tool() for tool in self._tools.values()]

    def clear(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()

    def __len__(self) -> int:
        """Return the number of registered tools."""
        return len(self._tools)

    def __repr__(self) -> str:
        tool_names = ", ".join(self._tools.keys())
        return f"<ToolRegistry: [{tool_names}]>"
