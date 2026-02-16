"""
File operations example.

Demonstrates file reading, writing, and editing with jagent.
"""

import os
from jagent import Agent
from jagent.tools import FileRead, FileWrite, FileEdit, Glob, Grep


def main():
    """Run file operations example."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Create agent with file tools
    agent = Agent(
        api_key=api_key,
        tools=[
            FileRead(),
            FileWrite(),
            FileEdit(),
            Glob(),
            Grep(),
        ],
        system_prompt="""You are a helpful file management assistant.
Help users read, write, and organize their files.
Always explain what you're doing before taking action."""
    )

    print("🤖 jagent - File Operations Example")
    print("=" * 50)
    print()

    # Example 1: Create a file
    print("Example 1: Create a test file")
    task1 = "Create a file called 'test.txt' with a simple greeting message"
    print(f"📝 Task: {task1}")
    response1 = agent.run(task1, clear_history=True)
    print(f"✅ Response: {response1}")
    print()

    # Example 2: Read the file
    print("Example 2: Read the file we created")
    task2 = "Read the contents of test.txt"
    print(f"📝 Task: {task2}")
    response2 = agent.run(task2, clear_history=True)
    print(f"✅ Response: {response2}")
    print()

    # Example 3: Edit the file
    print("Example 3: Edit the file")
    task3 = "In test.txt, replace 'greeting' with 'hello' if it exists"
    print(f"📝 Task: {task3}")
    response3 = agent.run(task3, clear_history=True)
    print(f"✅ Response: {response3}")
    print()

    # Example 4: Find Python files
    print("Example 4: Find Python files")
    task4 = "Find all Python files in the current directory and subdirectories"
    print(f"📝 Task: {task4}")
    response4 = agent.run(task4, clear_history=True)
    print(f"✅ Response: {response4}")
    print()


if __name__ == "__main__":
    main()
