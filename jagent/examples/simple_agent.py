"""
Simple agent example.

This demonstrates the basic usage of jagent with built-in tools.
"""

import os
from jagent import Agent
from jagent.tools import FileRead, FileWrite, Bash, Glob


def main():
    """Run a simple agent example."""

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Create agent with tools
    agent = Agent(
        api_key=api_key,
        tools=[
            FileRead(),
            FileWrite(),
            Bash(),
            Glob(),
        ]
    )

    print("🤖 jagent - Simple Agent Example")
    print("=" * 50)
    print(f"Loaded {len(agent.registry)} tools")
    print(f"Tools: {', '.join(t.name for t in agent.registry.list_tools())}")
    print("=" * 50)
    print()

    # Example task
    task = "List all Python files in the current directory"

    print(f"📝 Task: {task}")
    print()

    # Run the agent
    response = agent.run(task)

    print("✅ Response:")
    print(response)
    print()

    # Show conversation history
    print(f"💬 Conversation history: {len(agent.messages)} messages")


if __name__ == "__main__":
    main()
