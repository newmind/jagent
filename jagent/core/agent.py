"""Main agent runtime with conversation loop."""

from typing import Any, Dict, List, Optional
from jagent.core.registry import ToolRegistry
from jagent.core.executor import ToolExecutor
from jagent.core.tool import Tool
from jagent.llm.anthropic_client import AnthropicClient


class Agent:
    """
    Main agent that orchestrates the LLM and tools.

    The agent:
    1. Maintains a tool registry
    2. Manages conversation history
    3. Executes the main conversation loop:
       - User query → LLM
       - LLM generates tool calls (if needed)
       - Execute tools
       - Return results to LLM
       - LLM generates final response

    Example:
        agent = Agent(api_key="sk-...")
        agent.add_tool(FileReadTool())
        response = agent.run("What files are in the current directory?")
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        system_prompt: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        max_iterations: int = 10,
    ) -> None:
        """
        Initialize the agent.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            system_prompt: System prompt for the agent
            tools: Initial list of tools
            max_iterations: Maximum number of tool-use iterations
        """
        self.llm = AnthropicClient(api_key=api_key, model=model)
        self.registry = ToolRegistry()
        self.executor = ToolExecutor(self.registry)

        self.system_prompt = system_prompt or self._default_system_prompt()
        self.max_iterations = max_iterations

        # Conversation history
        self.messages: List[Dict[str, Any]] = []

        # Register initial tools
        if tools:
            self.registry.register_many(tools)

    def _default_system_prompt(self) -> str:
        """Default system prompt for the agent."""
        return """You are a helpful AI assistant with access to various tools.
Use the available tools to help users accomplish their tasks.
Always explain what you're doing and provide clear, helpful responses."""

    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to the agent.

        Args:
            tool: Tool instance to add
        """
        self.registry.register(tool)

    def add_tools(self, tools: List[Tool]) -> None:
        """
        Add multiple tools to the agent.

        Args:
            tools: List of tool instances to add
        """
        self.registry.register_many(tools)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.messages.clear()

    def run(
        self,
        user_message: str,
        clear_history: bool = False,
    ) -> str:
        """
        Run the agent with a user message.

        Args:
            user_message: User's input message
            clear_history: Whether to clear history before running

        Returns:
            Agent's final response
        """
        if clear_history:
            self.clear_history()

        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_message,
        })

        # Main conversation loop
        for iteration in range(self.max_iterations):
            # Get response from LLM
            response = self.llm.create_message(
                messages=self.messages,
                system=self.system_prompt,
                tools=self.registry.to_anthropic_tools() if len(self.registry) > 0 else None,
            )

            # Check if we're done (no tool calls)
            tool_calls = self.llm.extract_tool_calls(response)

            if not tool_calls:
                # No tool calls - extract final text response
                final_response = self.llm.extract_text(response)

                # Add assistant message to history
                self.messages.append({
                    "role": "assistant",
                    "content": response.content,
                })

                return final_response

            # We have tool calls - execute them
            # First, add the assistant's message (with tool calls) to history
            self.messages.append({
                "role": "assistant",
                "content": response.content,
            })

            # Execute the tool calls
            results = self.executor.execute_tool_calls(tool_calls)

            # Build tool result message
            tool_result_msg = self.llm.build_tool_result_message(tool_calls, results)
            self.messages.append(tool_result_msg)

            # Continue the loop - LLM will process tool results

        # If we hit max iterations, return what we have
        return f"Warning: Reached maximum iterations ({self.max_iterations}). " \
               f"The task may be incomplete."

    def run_once(
        self,
        user_message: str,
    ) -> Dict[str, Any]:
        """
        Run a single iteration (for debugging/testing).

        Args:
            user_message: User's input message

        Returns:
            Dict with 'response', 'tool_calls', and 'results'
        """
        messages = [{
            "role": "user",
            "content": user_message,
        }]

        response = self.llm.create_message(
            messages=messages,
            system=self.system_prompt,
            tools=self.registry.to_anthropic_tools() if len(self.registry) > 0 else None,
        )

        tool_calls = self.llm.extract_tool_calls(response)
        text = self.llm.extract_text(response)

        results = None
        if tool_calls:
            results = self.executor.execute_tool_calls(tool_calls)

        return {
            "text": text,
            "tool_calls": tool_calls,
            "results": results,
        }

    def __repr__(self) -> str:
        return f"<Agent: {len(self.registry)} tools, {len(self.messages)} messages>"
