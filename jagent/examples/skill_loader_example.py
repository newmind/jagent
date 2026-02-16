"""
Skill loader example.

Demonstrates how to load custom tools from external files.
"""

import os
from pathlib import Path
from jagent import Agent
from jagent.skills import SkillLoader


def create_example_skill():
    """Create an example skill file."""

    skill_code = '''"""Example custom skill."""

from jagent import Tool
from pydantic import BaseModel, Field


class ReverseInput(BaseModel):
    """Input for reverse tool."""
    text: str = Field(description="Text to reverse")


class ReverseTool(Tool):
    """Reverses text."""

    name = "reverse"
    description = "Reverse a string"
    input_schema = ReverseInput

    def execute(self, text: str) -> str:
        return text[::-1]


class UppercaseInput(BaseModel):
    """Input for uppercase tool."""
    text: str = Field(description="Text to uppercase")


class UppercaseTool(Tool):
    """Converts text to uppercase."""

    name = "uppercase"
    description = "Convert text to uppercase"
    input_schema = UppercaseInput

    def execute(self, text: str) -> str:
        return text.upper()
'''

    # Write to a temporary skill file
    skill_path = Path("/tmp/example_skill.py")
    skill_path.write_text(skill_code)

    return str(skill_path)


def main():
    """Run skill loader example."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    print("🤖 jagent - Skill Loader Example")
    print("=" * 50)
    print()

    # Create example skill file
    skill_file = create_example_skill()
    print(f"✅ Created example skill file: {skill_file}")
    print()

    # Load skills
    loader = SkillLoader()
    print("📦 Loading skills from file...")
    skills = loader.load_from_file(skill_file)
    print(f"✅ Loaded {len(skills)} tools: {', '.join(s.name for s in skills)}")
    print()

    # Create agent with loaded skills
    agent = Agent(api_key=api_key, tools=skills)

    # Test the skills
    print("Testing loaded skills:")
    print()

    task1 = "Reverse the text 'Hello World'"
    print(f"📝 Task 1: {task1}")
    response1 = agent.run(task1, clear_history=True)
    print(f"✅ Response: {response1}")
    print()

    task2 = "Convert 'hello world' to uppercase"
    print(f"📝 Task 2: {task2}")
    response2 = agent.run(task2, clear_history=True)
    print(f"✅ Response: {response2}")
    print()


if __name__ == "__main__":
    main()
