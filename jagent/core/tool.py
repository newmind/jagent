"""Base class for all tools in the jagent framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional
from pydantic import BaseModel


class Tool(ABC):
    """
    Base class for all agent tools.

    Each tool must define:
    - name: Unique identifier for the tool
    - description: What the tool does (shown to the LLM)
    - input_schema: Pydantic model for input validation
    - execute: The actual tool implementation

    Example:
        class EchoInput(BaseModel):
            message: str

        class EchoTool(Tool):
            name = "echo"
            description = "Echoes back the input message"
            input_schema = EchoInput

            def execute(self, message: str) -> str:
                return f"Echo: {message}"
    """

    # Must be overridden by subclasses
    name: str
    description: str
    input_schema: Type[BaseModel]

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the tool with validated inputs.

        Args:
            **kwargs: Validated inputs matching the input_schema

        Returns:
            Tool execution result (will be serialized to string for LLM)
        """
        pass

    def to_anthropic_tool(self) -> Dict[str, Any]:
        """
        Convert this tool to Anthropic's tool format.

        Returns:
            Dictionary matching Anthropic's tool specification
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.model_json_schema(),
        }

    def validate_input(self, **kwargs: Any) -> BaseModel:
        """
        Validate input against the schema.

        Args:
            **kwargs: Raw input parameters

        Returns:
            Validated Pydantic model instance

        Raises:
            ValidationError: If input doesn't match schema
        """
        return self.input_schema(**kwargs)

    def run(self, **kwargs: Any) -> Any:
        """
        Validate input and execute the tool.

        Args:
            **kwargs: Raw input parameters

        Returns:
            Tool execution result
        """
        # Validate input
        validated = self.validate_input(**kwargs)

        # Execute with validated data
        return self.execute(**validated.model_dump())

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
