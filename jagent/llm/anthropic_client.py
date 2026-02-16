"""Anthropic Claude API client wrapper."""

from typing import Any, Dict, List, Optional
import anthropic
from anthropic.types import Message, ContentBlock, ToolUseBlock, TextBlock


class AnthropicClient:
    """
    Wrapper around Anthropic's Python SDK.

    Provides a simplified interface for:
    - Creating messages with tool support
    - Handling tool calls
    - Managing conversation history

    Example:
        client = AnthropicClient(api_key="sk-...")
        response = client.create_message(
            messages=[{"role": "user", "content": "Hello!"}],
            tools=tools
        )
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
    ) -> None:
        """
        Initialize the Anthropic client.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: Claude 3.5 Sonnet)
            max_tokens: Maximum tokens for responses
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def create_message(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: Optional[int] = None,
    ) -> Message:
        """
        Create a message using the Anthropic API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system: Optional system prompt
            tools: Optional list of tool definitions
            max_tokens: Override default max_tokens

        Returns:
            Anthropic Message object
        """
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
        }

        if system:
            kwargs["system"] = system

        if tools:
            kwargs["tools"] = tools

        return self.client.messages.create(**kwargs)

    def extract_tool_calls(self, message: Message) -> List[Dict[str, Any]]:
        """
        Extract tool calls from a message.

        Args:
            message: Anthropic Message object

        Returns:
            List of tool calls with 'id', 'name', and 'input'
        """
        tool_calls = []

        for block in message.content:
            if isinstance(block, ToolUseBlock):
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        return tool_calls

    def extract_text(self, message: Message) -> str:
        """
        Extract text content from a message.

        Args:
            message: Anthropic Message object

        Returns:
            Concatenated text from all text blocks
        """
        text_parts = []

        for block in message.content:
            if isinstance(block, TextBlock):
                text_parts.append(block.text)

        return "\n".join(text_parts)

    def build_tool_result_message(
        self,
        tool_calls: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build a message with tool results.

        Args:
            tool_calls: List of tool calls that were made
            results: List of execution results

        Returns:
            Message dictionary with tool results
        """
        content = []

        for tool_call, result in zip(tool_calls, results):
            content.append({
                "type": "tool_result",
                "tool_use_id": tool_call["id"],
                "content": result.get("result", result.get("error", "Unknown error")),
            })

        return {
            "role": "user",
            "content": content,
        }
