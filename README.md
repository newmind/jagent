# 🤖 jagent

**Educational AI Agent Framework** - Learn how AI coding assistants like Claude Code, Codex, and OpenCode work by building one from scratch!

## 📚 학습 시작하기

jagent를 처음 접한다면 **[학습 가이드(LEARNING_GUIDE.md)](./LEARNING_GUIDE.md)** 를 먼저 읽으세요.

Level 0 (환경 설정)부터 Level 9 (실전 프로젝트)까지 단계별로 배울 수 있습니다.

```
Level 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9
  설치   기초  도구  파일  커스텀  조합  스킬  대화  디버깅  프로젝트
```

각 레벨은 **확인 → 돌려보기 → 확장** 3단계로 구성됩니다.

---

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

## 📖 문서

| 문서 | 내용 |
|------|------|
| [LEARNING_GUIDE.md](./LEARNING_GUIDE.md) | 단계별 학습 가이드 (Level 0-9) |
| [USAGE.md](./USAGE.md) | API 레퍼런스 및 상세 사용법 |

## 🗂️ 예제 목록

| 파일 | 레벨 | 주제 |
|------|------|------|
| `examples/simple_agent.py` | Level 1 | 첫 번째 에이전트 |
| `examples/custom_tool_example.py` | Level 4 | 커스텀 도구 만들기 |
| `examples/file_operations_example.py` | Level 3 | 파일 작업 |
| `examples/skill_loader_example.py` | Level 6 | Skills 로딩 |
| `examples/tool_chaining_example.py` | Level 5 | 도구 체이닝 |
| `examples/conversational_agent_example.py` | Level 7 | 대화형 에이전트 |
| `examples/error_handling_example.py` | Level 8 | 에러 처리 |
| `examples/debugging_tools.py` | Level 8 | 디버깅 도구 |
| `examples/project_template/` | Level 9 | 프로젝트 템플릿 |

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
