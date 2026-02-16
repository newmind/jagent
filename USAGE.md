# jagent Usage Guide

This guide walks you through using jagent, from basic concepts to advanced features.

## Table of Contents

- [Installation](#installation)
- [Basic Concepts](#basic-concepts)
- [Quick Start](#quick-start)
- [Built-in Tools](#built-in-tools)
- [Creating Custom Tools](#creating-custom-tools)
- [Skills/Plugin System](#skillsplugin-system)
- [MCP Integration](#mcp-integration)
- [Examples](#examples)

## Installation

```bash
# Clone the repository
git clone https://github.com/newmind/jagent.git
cd jagent

# Install in development mode
pip install -e .

# Or with all optional dependencies
pip install -e ".[all]"
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Basic Concepts

### 1. Tools

Tools are the building blocks of jagent. Each tool is a Python class that:
- Inherits from `Tool` base class
- Defines a `name`, `description`, and `input_schema`
- Implements an `execute()` method

```python
from jagent import Tool
from pydantic import BaseModel

class EchoInput(BaseModel):
    message: str

class EchoTool(Tool):
    name = "echo"
    description = "Echoes back a message"
    input_schema = EchoInput

    def execute(self, message: str) -> str:
        return f"Echo: {message}"
```

### 2. Agent

The Agent orchestrates the LLM and tools:
- Manages conversation history
- Sends messages to the LLM
- Executes tool calls
- Returns results to the LLM

```python
from jagent import Agent

agent = Agent(api_key="your-key", tools=[EchoTool()])
response = agent.run("Echo 'hello world'")
```

### 3. Tool Registry

The registry keeps track of available tools:

```python
from jagent.core import ToolRegistry

registry = ToolRegistry()
registry.register(EchoTool())
registry.register(AnotherTool())

# Get all tools
all_tools = registry.list_tools()

# Get specific tool
echo_tool = registry.get("echo")
```

## Quick Start

### Simple Echo Bot

```python
from jagent import Agent, Tool
from pydantic import BaseModel

# 1. Define input schema
class EchoInput(BaseModel):
    message: str

# 2. Create tool
class EchoTool(Tool):
    name = "echo"
    description = "Echo a message back"
    input_schema = EchoInput

    def execute(self, message: str) -> str:
        return f"Echo: {message}"

# 3. Create agent
agent = Agent(
    api_key="your-key",
    tools=[EchoTool()]
)

# 4. Run task
response = agent.run("Echo 'Hello, World!'")
print(response)
```

### With Built-in Tools

```python
from jagent import Agent
from jagent.tools import FileRead, Bash, Glob

agent = Agent(
    api_key="your-key",
    tools=[FileRead(), Bash(), Glob()]
)

# The agent can now read files, run commands, and find files
response = agent.run("List all Python files in this directory")
print(response)
```

## Built-in Tools

### FileRead

Read files from the filesystem:

```python
from jagent.tools import FileRead

tool = FileRead()
result = tool.execute(file_path="/path/to/file.txt")

# With line ranges
result = tool.execute(
    file_path="/path/to/file.txt",
    offset=10,  # Start at line 10
    limit=20    # Read 20 lines
)
```

### FileWrite

Write content to files:

```python
from jagent.tools import FileWrite

tool = FileWrite()
result = tool.execute(
    file_path="/path/to/output.txt",
    content="Hello, World!"
)
```

### FileEdit

Edit files with find-and-replace:

```python
from jagent.tools import FileEdit

tool = FileEdit()
result = tool.execute(
    file_path="/path/to/file.txt",
    old_string="foo",
    new_string="bar",
    replace_all=True  # Replace all occurrences
)
```

### Bash

Execute shell commands:

```python
from jagent.tools import Bash

tool = Bash()
result = tool.execute(
    command="ls -la",
    timeout=30,  # seconds
    working_dir="/path/to/dir"
)
```

### Glob

Find files by pattern:

```python
from jagent.tools import Glob

tool = Glob()
result = tool.execute(pattern="**/*.py")  # All Python files
```

### Grep

Search file contents:

```python
from jagent.tools import Grep

tool = Grep()
result = tool.execute(
    pattern="import.*pandas",
    file_pattern="*.py",
    case_insensitive=True
)
```

## Creating Custom Tools

### Step 1: Define Input Schema

Use Pydantic to define the input:

```python
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    expression: str = Field(
        description="Math expression to evaluate"
    )
```

### Step 2: Create Tool Class

```python
from jagent import Tool

class Calculator(Tool):
    name = "calculator"
    description = "Evaluate mathematical expressions"
    input_schema = CalculatorInput

    def execute(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error: {e}"
```

### Step 3: Use the Tool

```python
from jagent import Agent

agent = Agent(
    api_key="your-key",
    tools=[Calculator()]
)

response = agent.run("What is 42 * 137?")
```

## Skills/Plugin System

### Loading Skills from Files

Create a skill file (`my_skill.py`):

```python
from jagent import Tool
from pydantic import BaseModel

class MyToolInput(BaseModel):
    data: str

class MyTool(Tool):
    name = "my_tool"
    description = "My custom tool"
    input_schema = MyToolInput

    def execute(self, data: str) -> str:
        return f"Processed: {data}"
```

Load it:

```python
from jagent import Agent
from jagent.skills import SkillLoader

loader = SkillLoader()
tools = loader.load_from_file("my_skill.py")

agent = Agent(api_key="your-key", tools=tools)
```

### Loading from Directory

```python
loader = SkillLoader()
tools = loader.load_from_directory("./my_skills/")

agent = Agent(api_key="your-key", tools=tools)
```

### Loading from Module

```python
loader = SkillLoader()
tools = loader.load_from_module("my_package.skills")

agent = Agent(api_key="your-key", tools=tools)
```

## MCP Integration

*Note: This is a simplified educational implementation.*

```python
from jagent import Agent
from jagent.mcp import MCPClient

# Create MCP client
mcp_client = MCPClient(server_command="path/to/mcp/server")
mcp_client.connect()

# Get tools from MCP server
mcp_tools = mcp_client.list_tools()

# Add to agent
agent = Agent(api_key="your-key", tools=mcp_tools)
```

## Examples

See the `jagent/examples/` directory for complete examples:

- `simple_agent.py` - Basic agent usage
- `custom_tool_example.py` - Creating custom tools
- `file_operations_example.py` - File manipulation
- `skill_loader_example.py` - Loading external skills

Run examples:

```bash
python -m jagent.examples.simple_agent
python -m jagent.examples.custom_tool_example
python -m jagent.examples.file_operations_example
python -m jagent.examples.skill_loader_example
```

## Advanced Usage

### Conversation History

```python
agent = Agent(api_key="your-key", tools=[...])

# First message
response1 = agent.run("What files are here?")

# Second message (maintains context)
response2 = agent.run("Read the first one")

# Clear history
agent.clear_history()

# Or clear for a specific run
response3 = agent.run("New task", clear_history=True)
```

### Custom System Prompt

```python
agent = Agent(
    api_key="your-key",
    tools=[...],
    system_prompt="You are a Python expert. Help users write clean, Pythonic code."
)
```

### Debug Mode

```python
# Run once and inspect
result = agent.run_once("List files")

print(result["text"])         # Text response
print(result["tool_calls"])   # Tool calls made
print(result["results"])      # Tool results
```

## Best Practices

1. **Clear Tool Descriptions**: The LLM uses these to decide when to use tools
2. **Validate Inputs**: Use Pydantic models for type safety
3. **Handle Errors**: Return descriptive error messages
4. **Document Examples**: Include usage examples in docstrings
5. **Test Tools**: Test tools independently before using with the agent

## Troubleshooting

### API Key Issues

```python
import os
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")
```

### Tool Not Being Called

- Check the tool's `description` - make it clear when to use it
- Verify the `input_schema` matches what the LLM is sending
- Use `agent.run_once()` to debug

### Import Errors

```bash
# Make sure jagent is installed
pip install -e .

# Or check PYTHONPATH
export PYTHONPATH=/path/to/jagent:$PYTHONPATH
```

## Next Steps

- Explore the source code in `jagent/core/`
- Study how Claude Code implements similar patterns
- Build your own custom tools
- Contribute improvements!

## Resources

- [Claude API Documentation](https://docs.anthropic.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
