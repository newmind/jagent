"""Tool executor for running tools and handling results."""

import json
from typing import Any, Dict, List, Optional
from jagent.core.registry import ToolRegistry


class ToolExecutor:
    """
    Executes tools based on LLM tool calls.

    The executor:
    1. Parses tool calls from the LLM response
    2. Looks up tools in the registry
    3. Executes them with provided inputs
    4. Formats results for the LLM

    Example:
        executor = ToolExecutor(registry)
        result = executor.execute_tool("echo", {"message": "hello"})
    """

    def __init__(self, registry: ToolRegistry) -> None:
        """
        Initialize the executor with a tool registry.

        Args:
            registry: ToolRegistry containing available tools
        """
        self.registry = registry

    def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single tool call.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Dict with 'success', 'result', and optional 'error' keys
        """
        # Get the tool from registry
        tool = self.registry.get(tool_name)

        if tool is None:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found in registry",
                "result": None,
            }

        try:
            # Execute the tool
            result = tool.run(**tool_input)

            # Convert result to string if needed
            if not isinstance(result, str):
                result = json.dumps(result, indent=2, default=str)

            return {
                "success": True,
                "result": result,
                "error": None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}",
                "result": None,
            }

    def execute_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls (potentially in parallel in future).

        Args:
            tool_calls: List of tool call dictionaries with 'name' and 'input'

        Returns:
            List of execution results
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_input = tool_call.get("input", {})

            result = self.execute_tool(tool_name, tool_input)
            results.append({
                "tool_name": tool_name,
                **result,
            })

        return results

    def format_result_for_llm(self, result: Dict[str, Any]) -> str:
        """
        Format a tool execution result for the LLM.

        Args:
            result: Tool execution result

        Returns:
            Formatted string for LLM context
        """
        if result["success"]:
            return result["result"]
        else:
            return f"Error: {result['error']}"
