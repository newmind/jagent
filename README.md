# 🤖 jagent

**Educational AI Agent Framework** - Learn how AI coding assistants like Claude Code, Codex, and OpenCode work by building one from scratch!

## 🎯 Purpose

This is a lightweight, educational implementation of an AI agent framework that demonstrates the core concepts behind modern AI coding assistants. Perfect for:

- 🎓 Learning how AI agents work internally
- 🔬 Experimenting with AI agent architectures
- 🛠️ Building custom AI tools and workflows
- 📚 Understanding Model Context Protocol (MCP) and Skills systems

## ✨ Features

- **🔧 Core Tools**: File operations (read/write/edit), shell command execution
- **🔍 Search Tools**: Fast file pattern matching (glob) and content search (grep)
- **🌐 MCP Client**: Connect to Model Context Protocol servers for extended capabilities
- **🧩 Skills/Plugins**: Extensible plugin system for custom tools
- **🎨 Clean Architecture**: Educational codebase focusing on clarity and simplicity
- **🐍 Pure Python**: Easy to understand and modify

## 🏗️ Architecture

```
jagent/
├── core/           # Core agent runtime, tool registry, and execution engine
├── llm/            # LLM API clients (Anthropic Claude)
├── tools/          # Built-in tools (filesystem, bash, search)
├── mcp/            # Model Context Protocol client
├── skills/         # Plugin system for custom tools
└── examples/       # Usage examples
```

## 📦 Installation

```bash
# Basic installation
pip install -e .

# With MCP support
pip install -e ".[mcp]"

# With development tools
pip install -e ".[dev]"

# Everything
pip install -e ".[all]"
```

## 🚀 Quick Start

```python
from jagent import Agent
from jagent.tools import FileRead, FileWrite, Bash

# Create an agent with tools
agent = Agent(
    api_key="your-anthropic-api-key",
    tools=[FileRead(), FileWrite(), Bash()]
)

# Run a task
response = agent.run("List all Python files in the current directory")
print(response)
```

## 🔨 Built-in Tools

### Filesystem Tools
- **FileRead**: Read files with support for offset/limit
- **FileWrite**: Create or overwrite files
- **FileEdit**: Edit files with find-and-replace

### Shell Tools
- **Bash**: Execute shell commands with timeout support

### Search Tools
- **Glob**: Find files by pattern (e.g., `**/*.py`)
- **Grep**: Search file contents with regex

## 🌐 MCP Integration

Connect to MCP servers to extend your agent's capabilities:

```python
from jagent import Agent
from jagent.mcp import MCPClient

# Connect to an MCP server
mcp_client = MCPClient("path/to/mcp/server")
agent = Agent(api_key="...", mcp_client=mcp_client)
```

## 🧩 Custom Skills

Create your own tools by extending the `Tool` base class:

```python
from jagent.core import Tool
from pydantic import BaseModel

class MyToolInput(BaseModel):
    message: str

class MyTool(Tool):
    name = "my_tool"
    description = "Does something cool"
    input_schema = MyToolInput

    def execute(self, message: str) -> str:
        return f"You said: {message}"
```

## 🎓 Learning Resources

This project is designed for education. Key concepts demonstrated:

1. **Tool-based Architecture**: How AI agents use tools to interact with the world
2. **LLM Integration**: How to integrate with Claude API for tool calling
3. **Conversation Loop**: The agent's main execution loop
4. **Tool Registry**: Dynamic tool discovery and registration
5. **MCP Protocol**: Extending agents with external tool providers
6. **Plugin System**: Creating modular, reusable tool packages

## 🤝 Inspiration

This project is inspired by:
- [Claude Code](https://github.com/anthropics/claude-code) - Anthropic's official CLI
- [OpenAI Codex](https://openai.com/blog/openai-codex)
- [OpenCode](https://github.com/OpenCodeInterpreter/OpenCodeInterpreter)

## 📄 License

MIT License - feel free to use for learning and experimentation!

## 🙏 Contributing

This is an educational project. Contributions that improve clarity, add comments, or demonstrate new concepts are welcome!

## ⚠️ Disclaimer

This is a **simplified educational implementation** for learning purposes. For production use cases, please use official tools like [Claude Code](https://github.com/anthropics/claude-code).
