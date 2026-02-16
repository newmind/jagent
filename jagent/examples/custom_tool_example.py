"""
Custom tool example.

This demonstrates how to create and use custom tools with jagent.
"""

import os
from pydantic import BaseModel, Field
from jagent import Agent, Tool
from jagent.tools import Bash


# Define input schema
class CalculatorInput(BaseModel):
    """Input for calculator tool."""
    expression: str = Field(
        description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')"
    )


# Create custom tool
class Calculator(Tool):
    """A simple calculator tool that evaluates mathematical expressions."""

    name = "calculator"
    description = "Evaluate mathematical expressions. Supports +, -, *, /, **, etc."
    input_schema = CalculatorInput

    def execute(self, expression: str) -> str:
        """
        Evaluate a mathematical expression.

        Args:
            expression: Math expression to evaluate

        Returns:
            Result or error message
        """
        try:
            # WARNING: eval is dangerous! This is just for educational purposes.
            # In production, use a safe math parser like ast.literal_eval or sympy
            result = eval(expression, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"


# Another custom tool
class WeatherInput(BaseModel):
    """Input for weather tool."""
    city: str = Field(description="City name to get weather for")


class MockWeather(Tool):
    """A mock weather tool (for demonstration)."""

    name = "get_weather"
    description = "Get current weather for a city (mock data for demo)"
    input_schema = WeatherInput

    def execute(self, city: str) -> str:
        """Get mock weather data."""
        # In a real implementation, this would call a weather API
        return f"Weather in {city}: Sunny, 72°F (mock data)"


def main():
    """Run custom tool example."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Create agent with custom tools
    agent = Agent(
        api_key=api_key,
        tools=[
            Calculator(),
            MockWeather(),
            Bash(),
        ]
    )

    print("🤖 jagent - Custom Tool Example")
    print("=" * 50)
    print(f"Loaded {len(agent.registry)} tools:")
    for tool in agent.registry.list_tools():
        print(f"  - {tool.name}: {tool.description}")
    print("=" * 50)
    print()

    # Test the calculator
    task1 = "What is 42 * 137?"
    print(f"📝 Task 1: {task1}")
    response1 = agent.run(task1, clear_history=True)
    print(f"✅ Response: {response1}")
    print()

    # Test the weather tool
    task2 = "What's the weather in San Francisco?"
    print(f"📝 Task 2: {task2}")
    response2 = agent.run(task2, clear_history=True)
    print(f"✅ Response: {response2}")
    print()


if __name__ == "__main__":
    main()
