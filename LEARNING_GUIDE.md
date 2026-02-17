# jagent 학습 가이드

> AI 에이전트를 처음부터 만들어보며 Claude Code, Codex 같은 도구들이 어떻게 동작하는지 배웁니다.

**학습 목표**: 이 가이드를 마치면 파일 조작, 명령 실행, 커스텀 도구 개발이 가능한 자신만의 AI 에이전트를 만들 수 있습니다.

**소요 시간**:
- 빠른 학습 (Level 0-4): 2-3시간
- 전체 과정 (Level 0-9): 6-8시간

**필요 사항**:
- Python 3.10+
- Anthropic API 키 ([발급하기](https://console.anthropic.com/))
- 기본 Python 지식 (클래스, 함수)

---

## 학습 방법: 확인 → 돌려보기 → 확장

이 가이드의 모든 레벨은 세 단계로 구성됩니다.

```
📖 확인       ▶️ 돌려보기      🔨 확장
─────────    ─────────────    ──────────
개념 이해    예제 실행 및      직접 바꿔보고
코드 읽기    결과 관찰         도전 과제 해결
```

---

## 목차

| 레벨 | 주제 | 난이도 | 시간 |
|------|------|--------|------|
| [Level 0](#level-0-환경-설정) | 환경 설정 | ⭐ | 15분 |
| [Level 1](#level-1-hello-agent-world) | Hello Agent World | ⭐ | 20분 |
| [Level 2](#level-2-tool-해부하기) | Tool 해부하기 | ⭐⭐ | 30분 |
| [Level 3](#level-3-파일-작업) | 파일 작업 | ⭐⭐ | 30분 |
| [Level 4](#level-4-커스텀-도구-만들기) | 커스텀 도구 만들기 | ⭐⭐ | 40분 |
| [Level 5](#level-5-도구-조합하기) | 도구 조합하기 | ⭐⭐⭐ | 40분 |
| [Level 6](#level-6-skills--플러그인) | Skills & 플러그인 | ⭐⭐⭐ | 30분 |
| [Level 7](#level-7-대화와-컨텍스트) | 대화와 컨텍스트 | ⭐⭐⭐ | 30분 |
| [Level 8](#level-8-에러-처리와-디버깅) | 에러 처리와 디버깅 | ⭐⭐⭐ | 30분 |
| [Level 9](#level-9-실전-프로젝트) | 실전 프로젝트 | ⭐⭐⭐⭐ | 60분+ |

---

## 학습 경로 선택

### 🚀 빠른 시작 (경험 있는 개발자)
```
Level 0 → Level 2 → Level 4 → Level 9
```
기본 개념은 훑고, 도구 만들기와 실전 프로젝트에 집중합니다.

### 📚 기초부터 (Python 입문자)
```
Level 0 → 1 → 2 → 3 → 4 → (연습 후) → 5 → 9
```
각 레벨을 충분히 소화하고 확장 과제를 모두 해봅니다.

### 🎯 프로젝트 중심
```
Level 0 → Level 1 → Level 9 선택 → 필요한 레벨 참조
```
만들고 싶은 프로젝트부터 시작하고, 막히면 관련 레벨로 돌아옵니다.

---

## 핵심 개념 미리보기

### AI 에이전트란?

```
┌─────────────────────────────────────────────────────┐
│                   Agent Loop                         │
│                                                     │
│  사용자 질문                                          │
│      │                                               │
│      ▼                                               │
│  ┌───────┐     도구 필요?    ┌──────────────┐       │
│  │  LLM  │ ──────Yes──────▶ │ Tool 실행     │       │
│  │(Claude)│ ◀────결과────── │ (파일읽기 등)  │       │
│  └───────┘                  └──────────────┘       │
│      │                                               │
│      │ No (완료)                                     │
│      ▼                                               │
│  최종 응답                                            │
└─────────────────────────────────────────────────────┘
```

**핵심 4가지 컴포넌트**:

| 컴포넌트 | 역할 | 파일 위치 |
|---------|------|---------|
| `Tool` | 에이전트가 할 수 있는 행동 | `jagent/core/tool.py` |
| `ToolRegistry` | 도구 목록 관리 | `jagent/core/registry.py` |
| `Agent` | 대화 루프 실행 | `jagent/core/agent.py` |
| `AnthropicClient` | LLM API 통신 | `jagent/llm/anthropic_client.py` |

---

## Level 0: 환경 설정

### 📖 확인

이 레벨에서는 jagent를 설치하고 작동 확인을 합니다.

### ▶️ 돌려보기

**1단계: 설치**

```bash
cd /home/user/jagent
pip install -e .
```

**2단계: API 키 설정**

```bash
export ANTHROPIC_API_KEY='sk-ant-...'

# 영구 저장 (선택)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
```

**3단계: 설치 확인**

```bash
python -c "
from jagent import Agent, Tool
from jagent.tools import FileRead, Bash, Glob, Grep
print('✅ jagent 설치 완료!')
print('사용 가능한 도구:', ['FileRead', 'FileWrite', 'FileEdit', 'Bash', 'Glob', 'Grep'])
"
```

**예상 출력**:
```
✅ jagent 설치 완료!
사용 가능한 도구: ['FileRead', 'FileWrite', 'FileEdit', 'Bash', 'Glob', 'Grep']
```

### 🔨 확장

- [ ] `pip list | grep anthropic` 로 설치된 anthropic 버전 확인
- [ ] `python -c "import jagent; print(jagent.__version__)"` 실행
- [ ] `jagent/` 디렉토리 구조를 `ls -R jagent/`로 살펴보기

### ✅ 성공 기준
- [ ] Import 에러 없이 `from jagent import Agent` 가능
- [ ] API 키가 환경 변수에 설정됨

---

## Level 1: Hello Agent World

### 📖 확인

**에이전트 루프의 흐름**을 이해합니다.

```python
agent.run("Python 파일을 찾아줘")
    │
    ├── 1. LLM에 질문 전달
    │
    ├── 2. LLM이 "glob 도구를 써야겠다" 결정
    │
    ├── 3. glob 도구 실행: glob(pattern="**/*.py")
    │
    ├── 4. 결과를 LLM에 돌려줌
    │
    └── 5. LLM이 결과를 해석해 최종 답변 생성
```

**읽어볼 코드**: `jagent/core/agent.py` 의 `run()` 메서드

핵심 로직:
```python
# agent.py의 run() 메서드 핵심 부분 (단순화)
for iteration in range(self.max_iterations):
    response = self.llm.create_message(messages, tools)   # LLM 호출
    tool_calls = self.llm.extract_tool_calls(response)    # 도구 호출 추출

    if not tool_calls:
        return self.llm.extract_text(response)            # 완료!

    results = self.executor.execute_tool_calls(tool_calls) # 도구 실행
    # 결과를 messages에 추가하고 다시 LLM 호출
```

### ▶️ 돌려보기

```bash
python -m jagent.examples.simple_agent
```

**관찰 포인트**:
1. 몇 개의 도구가 로드되었나요?
2. 에이전트가 어떤 도구를 사용했나요?
3. 응답이 어떻게 생겼나요?

**직접 실행해보기**:

새 파일 `hello_agent.py`를 만들어 실행해보세요:

```python
import os
from jagent import Agent
from jagent.tools import Bash

api_key = os.getenv("ANTHROPIC_API_KEY")
agent = Agent(api_key=api_key, tools=[Bash()])

response = agent.run("현재 디렉토리 경로를 알려줘")
print(response)
```

```bash
python hello_agent.py
```

### 🔨 확장

**연습 1** (쉬움): 질문 바꿔보기
```python
# 이 질문들을 하나씩 바꿔서 실행해보세요
response = agent.run("현재 날짜와 시간을 알려줘")
response = agent.run("Python이 설치된 경로를 찾아줘")
response = agent.run("현재 디렉토리에 있는 파일 목록을 알려줘")
```

**연습 2** (보통): 도구 없이 실행
```python
# tools=[] 로 도구 없이 에이전트 만들기
agent_no_tools = Agent(api_key=api_key, tools=[])
response = agent_no_tools.run("2 + 2는?")
# 도구 없이도 동작하나요? 어떻게 동작하나요?
```

**연습 3** (도전): max_iterations 조절
```python
agent = Agent(api_key=api_key, tools=[Bash()], max_iterations=1)
response = agent.run("모든 Python 파일을 찾아서 각각 줄 수를 세어줘")
# max_iterations=1 이면 어떤 일이 일어나나요?
```

**스스로 확인해보기**:
- 에이전트가 대화 중 몇 번이나 LLM을 호출했나요? (`len(agent.messages)` 확인)
- 도구를 10개 추가하면 속도가 달라지나요?

### ✅ 성공 기준
- [ ] `simple_agent.py` 정상 실행
- [ ] 에이전트 루프의 단계를 설명할 수 있음
- [ ] 질문을 바꾸면 다른 도구가 호출되는 것을 확인함

---

## Level 2: Tool 해부하기

### 📖 확인

모든 도구는 같은 구조를 따릅니다. `jagent/core/tool.py`를 열어보세요.

```python
class Tool(ABC):
    name: str           # 도구 이름 (LLM이 이 이름으로 호출)
    description: str    # 설명 (LLM이 읽고 언제 쓸지 결정!)
    input_schema: Type[BaseModel]  # 입력 검증 스키마

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass  # 실제 동작 구현
```

**Pydantic이 하는 일**:

```python
class FileReadInput(BaseModel):
    file_path: str        # 필수
    offset: Optional[int] # 선택

# LLM이 {"file_path": "/foo.py"} 를 보내면
# Pydantic이 자동으로 타입 체크 & 변환
```

**도구가 LLM에 전달되는 형태** (`to_anthropic_tool()` 결과):

```json
{
  "name": "file_read",
  "description": "Read a file from the filesystem...",
  "input_schema": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string", "description": "..."},
      "offset": {"type": "integer", "description": "..."}
    },
    "required": ["file_path"]
  }
}
```

### ▶️ 돌려보기

**도구를 독립적으로 테스트**:

```python
# tool_test.py
from jagent.tools import FileRead, Bash, Glob

# 1. 도구를 직접 실행 (에이전트 없이)
file_reader = FileRead()
result = file_reader.run(file_path="/home/user/jagent/README.md", limit=5)
print("FileRead 결과:")
print(result)

# 2. 도구의 Anthropic 형식 확인
print("\nLLM에 전달되는 도구 정의:")
import json
print(json.dumps(file_reader.to_anthropic_tool(), indent=2))

# 3. Glob 테스트
glob_tool = Glob()
result = glob_tool.run(pattern="**/*.py")
print("\nGlob 결과:")
print(result[:500])  # 처음 500자만
```

**나만의 첫 번째 도구 만들기**:

```python
# my_first_tool.py
from jagent import Tool, Agent
from pydantic import BaseModel, Field
import os

class EchoInput(BaseModel):
    message: str = Field(description="반복할 메시지")
    times: int = Field(default=1, description="반복 횟수 (기본: 1)")

class EchoTool(Tool):
    name = "echo"
    description = "메시지를 지정한 횟수만큼 반복합니다"
    input_schema = EchoInput

    def execute(self, message: str, times: int = 1) -> str:
        return "\n".join([message] * times)

# 1. 단독 테스트
tool = EchoTool()
print(tool.run(message="Hello!", times=3))

# 2. 에이전트와 함께
agent = Agent(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    tools=[EchoTool()]
)
response = agent.run("'파이썬 최고!'라는 메시지를 3번 반복해줘")
print(response)
```

### 🔨 확장

**연습 1** — `CountWordsTool` 만들기:
```python
# 목표: 문자열의 단어 수를 세는 도구
class CountWordsInput(BaseModel):
    text: str = Field(description="???")

class CountWordsTool(Tool):
    name = "count_words"
    description = "???"
    input_schema = CountWordsInput

    def execute(self, text: str) -> str:
        # 구현해보세요!
        pass
```

**연습 2** — `CurrentTimeTool` 만들기:
```python
# 힌트: import datetime 사용
# 입력: timezone (선택, 기본값: "UTC")
# 출력: 현재 시간 문자열
```

**연습 3** (도전) — 입력 검증 추가:
```python
from pydantic import BaseModel, Field, validator

class SafeEchoInput(BaseModel):
    message: str = Field(description="메시지 (최대 100자)")
    times: int = Field(default=1, ge=1, le=10)  # ge=최소, le=최대

    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError("메시지가 비어있습니다")
        return v
```

**핵심 이해 확인**:
- `name`이 왜 중요한가요? (LLM이 이 이름으로 도구를 선택!)
- `description`을 잘못 쓰면 어떻게 될까요?
- `execute()`가 에러를 내면 어떻게 될까요?

### ✅ 성공 기준
- [ ] 도구를 에이전트 없이 단독으로 실행 가능
- [ ] `EchoTool` 완성 및 에이전트와 연동
- [ ] `CountWordsTool` 직접 구현

---

## Level 3: 파일 작업

### 📖 확인

jagent의 파일 도구 3가지:

| 도구 | 언제 쓰나 | 주의 |
|------|---------|------|
| `FileRead` | 파일 내용 읽기 | 큰 파일은 `limit` 사용 |
| `FileWrite` | 파일 생성/덮어쓰기 | 기존 내용 사라짐! |
| `FileEdit` | 특정 부분만 수정 | `old_string`이 정확해야 함 |

### ▶️ 돌려보기

```bash
python -m jagent.examples.file_operations_example
```

**파일 도구 직접 사용**:

```python
# file_tools_test.py
from jagent.tools import FileRead, FileWrite, FileEdit
import os

# 1. 파일 쓰기
writer = FileWrite()
result = writer.run(
    file_path="/tmp/test_jagent.txt",
    content="첫 번째 줄\n두 번째 줄\n세 번째 줄\n"
)
print(result)

# 2. 파일 읽기 (전체)
reader = FileRead()
result = reader.run(file_path="/tmp/test_jagent.txt")
print(result)

# 3. 파일 읽기 (일부)
result = reader.run(
    file_path="/tmp/test_jagent.txt",
    offset=2,   # 2번째 줄부터
    limit=1     # 1줄만
)
print("2번째 줄만:", result)

# 4. 파일 편집
editor = FileEdit()
result = editor.run(
    file_path="/tmp/test_jagent.txt",
    old_string="두 번째 줄",
    new_string="수정된 줄"
)
print(result)

# 5. 결과 확인
print(reader.run(file_path="/tmp/test_jagent.txt"))
```

**에이전트로 파일 작업**:

```python
import os
from jagent import Agent
from jagent.tools import FileRead, FileWrite, FileEdit, Glob

agent = Agent(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    tools=[FileRead(), FileWrite(), FileEdit(), Glob()],
    system_prompt="당신은 파일 관리 도우미입니다. 요청한 파일 작업을 정확하게 수행하세요."
)

# 복잡한 파일 작업을 에이전트에게 위임
response = agent.run(
    "/tmp/notes.txt 파일을 만들고 '오늘 할 일: jagent 학습'을 적어줘. "
    "그 다음 파일을 읽어서 내용을 확인해줘."
)
print(response)
```

### 🔨 확장

**연습 1** — TODO 관리자:
```python
# 에이전트에게 이런 요청을 해보세요:
agent.run("/tmp/todo.txt 파일에 '빨래하기'와 '장보기' 할 일 추가해줘")
agent.run("/tmp/todo.txt 에서 '빨래하기'를 '빨래하기 ✓'로 바꿔줘")
agent.run("/tmp/todo.txt 내용 보여줘")
```

**연습 2** — 파일 분석기:
```python
# Python 파일들의 줄 수를 세는 에이전트
agent.run(
    "jagent/core/ 디렉토리의 모든 Python 파일을 읽고, "
    "각 파일의 줄 수와 총 합계를 알려줘"
)
```

**연습 3** (도전) — 파일 백업:
```python
# FileRead + FileWrite 조합
agent.run(
    "jagent/__init__.py 파일을 읽어서 "
    "/tmp/jagent_init_backup.py 로 백업해줘"
)
```

**스스로 만들어보기**: `safe_write_tool.py`
```python
# FileWrite를 상속해서 덮어쓰기 전에 백업하는 도구 만들기
class SafeFileWrite(Tool):
    """기존 파일이 있으면 .bak으로 백업 후 덮어씀"""
    name = "safe_file_write"
    description = "..."
    # 구현해보세요!
```

### ✅ 성공 기준
- [ ] FileRead/Write/Edit 각각 단독 실행 성공
- [ ] 에이전트를 통해 파일 생성-읽기-수정 완료
- [ ] TODO 관리 예제 실행

---

## Level 4: 커스텀 도구 만들기

### 📖 확인

**좋은 도구 설계의 3가지 원칙**:

1. **이름**: 명확하고 동사형으로 (`get_weather` ✅, `weather` ❌)
2. **설명**: LLM이 언제 써야 할지 알 수 있게 구체적으로
3. **에러 처리**: 예외를 절대 밖으로 내보내지 말고 문자열로 반환

```python
# ❌ 나쁜 예
class BadTool(Tool):
    name = "tool"
    description = "does stuff"

    def execute(self, x):
        return open(x).read()  # 에러 발생 시 에이전트 죽음!

# ✅ 좋은 예
class GoodTool(Tool):
    name = "read_config"
    description = "설정 파일을 읽어 내용을 반환합니다. JSON 형식이면 파싱합니다."

    def execute(self, file_path: str) -> str:
        try:
            with open(file_path) as f:
                return f.read()
        except FileNotFoundError:
            return f"오류: 파일을 찾을 수 없습니다: {file_path}"
        except Exception as e:
            return f"오류: {type(e).__name__}: {str(e)}"
```

**도구 만들기 템플릿**:

```python
from jagent import Tool
from pydantic import BaseModel, Field
from typing import Optional

# 1단계: 입력 정의
class MyToolInput(BaseModel):
    required_param: str = Field(description="이 파라미터가 하는 일")
    optional_param: Optional[int] = Field(default=None, description="선택 파라미터")

# 2단계: 도구 구현
class MyTool(Tool):
    name = "my_tool"          # 소문자, 언더스코어
    description = """이 도구가 하는 일을 설명합니다.
    언제 사용해야 하는지, 어떤 결과를 반환하는지 포함하세요.
    예시: '파일 경로를 받아 줄 수를 반환합니다.'"""
    input_schema = MyToolInput

    def execute(self, required_param: str, optional_param: Optional[int] = None) -> str:
        try:
            # 실제 로직
            result = f"처리 완료: {required_param}"
            return result
        except Exception as e:
            return f"오류: {type(e).__name__}: {str(e)}"
```

### ▶️ 돌려보기

```bash
python -m jagent.examples.custom_tool_example
```

**도구 5개 만들어보기**:

```python
# custom_tools_practice.py
import os, json
from datetime import datetime
from pydantic import BaseModel, Field
from jagent import Tool, Agent

# --- 도구 1: JSON 포맷터 ---
class JsonFormatInput(BaseModel):
    json_string: str = Field(description="포맷할 JSON 문자열")
    indent: int = Field(default=2, description="들여쓰기 공백 수")

class JsonFormatter(Tool):
    name = "format_json"
    description = "JSON 문자열을 보기 좋게 포맷합니다"
    input_schema = JsonFormatInput

    def execute(self, json_string: str, indent: int = 2) -> str:
        try:
            data = json.loads(json_string)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return f"오류: 유효하지 않은 JSON - {str(e)}"


# --- 도구 2: 타임스탬프 ---
class TimestampInput(BaseModel):
    format: str = Field(default="%Y-%m-%d %H:%M:%S", description="날짜 형식")

class GetTimestamp(Tool):
    name = "get_timestamp"
    description = "현재 날짜와 시간을 반환합니다"
    input_schema = TimestampInput

    def execute(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        try:
            return datetime.now().strftime(format)
        except Exception as e:
            return f"오류: 잘못된 형식 - {str(e)}"


# --- 도구 3: 단어 세기 ---
class WordCountInput(BaseModel):
    text: str = Field(description="단어를 셀 텍스트")

class WordCounter(Tool):
    name = "count_words"
    description = "텍스트의 단어 수, 문자 수, 줄 수를 반환합니다"
    input_schema = WordCountInput

    def execute(self, text: str) -> str:
        words = len(text.split())
        chars = len(text)
        lines = len(text.splitlines())
        return f"단어: {words}개, 문자: {chars}개, 줄: {lines}줄"


# --- 에이전트 테스트 ---
if __name__ == "__main__":
    api_key = os.getenv("ANTHROPIC_API_KEY")
    agent = Agent(
        api_key=api_key,
        tools=[JsonFormatter(), GetTimestamp(), WordCounter()]
    )

    tests = [
        '{"name":"jagent","version":"0.1.0"} 을 예쁘게 포맷해줘',
        "지금 몇 시야?",
        "'AI 에이전트는 정말 재미있다'라는 문장의 단어 수를 세줘",
    ]

    for query in tests:
        print(f"\n질문: {query}")
        print(f"답변: {agent.run(query, clear_history=True)}")
```

### 🔨 확장

**도전 과제: 유용한 도구 5개 만들기**

| 도구 이름 | 입력 | 출력 | 힌트 |
|---------|------|------|------|
| `reverse_text` | text | 뒤집힌 문자열 | `text[::-1]` |
| `base64_encode` | text | Base64 인코딩 | `import base64` |
| `count_lines_in_file` | file_path | 줄 수 | FileRead 참고 |
| `list_env_vars` | prefix | 환경변수 목록 | `os.environ` |
| `check_url` | url | 상태 코드 | `import urllib.request` |

**핵심 목표**: 각 도구를 에이전트 없이 단독으로 테스트한 뒤 에이전트와 연동하기

### ✅ 성공 기준
- [ ] 도구 3개 이상 직접 구현
- [ ] 에러 처리 포함
- [ ] 에이전트와 연동해서 사용

---

## Level 5: 도구 조합하기

### 📖 확인

에이전트의 진짜 힘은 **여러 도구를 순서대로 조합**하는 데 있습니다.

```
복잡한 질문 예시:
"Python 파일들을 찾아서 각각 읽고, import 목록을 정리해서 파일로 저장해줘"

에이전트 실행 계획:
1. glob("**/*.py") → 파일 목록 획득
2. file_read(file1) → 내용 읽기
3. file_read(file2) → 내용 읽기
4. [분석]
5. file_write("imports.txt", ...) → 결과 저장
```

**시스템 프롬프트로 에이전트 특화**:

```python
# 시스템 프롬프트가 있으면 에이전트가 특정 역할에 집중
agent = Agent(
    api_key=key,
    tools=[...],
    system_prompt="""당신은 코드 분석 전문가입니다.
    - 항상 파일을 먼저 읽고 분석하세요
    - 분석 결과는 명확하고 구조적으로 제공하세요
    - 불확실한 경우 명시하세요"""
)
```

### ▶️ 돌려보기

```bash
python -m jagent.examples.tool_chaining_example
```

**직접 멀티 도구 에이전트 실행**:

```python
# multi_tool_agent.py
import os
from jagent import Agent
from jagent.tools import Glob, FileRead, FileWrite, Grep

agent = Agent(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    tools=[Glob(), FileRead(), FileWrite(), Grep()],
    system_prompt="당신은 코드베이스 분석가입니다. 도구를 조합해 체계적으로 분석하세요."
)

# 시나리오 1: 프로젝트 구조 보고서
response = agent.run(
    "jagent/ 디렉토리의 Python 파일들을 찾아서, "
    "각 파일의 역할을 간단히 설명하는 PROJECT_OVERVIEW.md를 만들어줘"
)
print(response)
```

**도구 연결 패턴 3가지**:

```python
# 패턴 1: 검색 → 읽기 → 분석
agent.run("모든 Python 파일에서 'TODO' 주석을 찾아서 목록으로 만들어줘")

# 패턴 2: 읽기 → 수정 → 검증
agent.run("jagent/__init__.py를 읽고, 버전을 '0.2.0'으로 바꾼 뒤 확인해줘")

# 패턴 3: 분석 → 생성
agent.run("jagent/core/ 파일들을 분석해서 각 클래스의 API 문서를 만들어줘")
```

### 🔨 확장

**프로젝트 1**: 의존성 분석기
```python
agent.run(
    "모든 Python 파일에서 import 구문을 찾아서, "
    "중복 없이 정렬된 의존성 목록을 /tmp/dependencies.txt에 저장해줘"
)
```

**프로젝트 2**: 코드 통계
```python
agent.run(
    "jagent/ 의 Python 파일들을 분석해서: "
    "1) 총 파일 수, 2) 총 줄 수, 3) 가장 큰 파일을 알려줘"
)
```

**프로젝트 3** (도전): 자동 README 생성
```python
agent.run(
    "jagent/tools/ 디렉토리의 모든 도구 파일을 읽고, "
    "각 도구의 이름과 설명을 정리한 TOOLS.md를 만들어줘"
)
```

### ✅ 성공 기준
- [ ] `tool_chaining_example.py` 실행
- [ ] 3개 이상의 도구를 연결하는 질문 성공
- [ ] 에이전트가 자동으로 도구 순서를 결정하는 것 관찰

---

## Level 6: Skills & 플러그인

### 📖 확인

**Skills**는 도구 모음을 파일로 패키징하는 방법입니다.

```
# 인라인 도구 (지금까지 방식)
agent = Agent(tools=[Tool1(), Tool2(), Tool3()])

# Skills 방식 (파일에서 로드)
loader = SkillLoader()
tools = loader.load_from_file("my_skills.py")
agent = Agent(tools=tools)
```

**언제 Skills를 쓰나요?**

| 상황 | 방법 |
|------|------|
| 1-2개 도구, 한 번만 사용 | 인라인 |
| 여러 프로젝트에서 재사용 | Skills 파일 |
| 팀이 도구를 공유 | Skills 디렉토리 |
| 도구가 10개 이상 | Skills 패키지 |

### ▶️ 돌려보기

```bash
python -m jagent.examples.skill_loader_example
```

**나만의 Skills 파일 만들기**:

```python
# my_text_skills.py (별도 파일로 저장)
from jagent import Tool
from pydantic import BaseModel, Field

class UpperInput(BaseModel):
    text: str = Field(description="대문자로 바꿀 텍스트")

class UppercaseTool(Tool):
    name = "to_uppercase"
    description = "텍스트를 대문자로 변환합니다"
    input_schema = UpperInput

    def execute(self, text: str) -> str:
        return text.upper()


class ReverseInput(BaseModel):
    text: str = Field(description="뒤집을 텍스트")

class ReverseTool(Tool):
    name = "reverse_text"
    description = "텍스트를 뒤집습니다"
    input_schema = ReverseInput

    def execute(self, text: str) -> str:
        return text[::-1]
```

```python
# skills_loader_test.py
import os
from jagent import Agent
from jagent.skills import SkillLoader

loader = SkillLoader()
tools = loader.load_from_file("my_text_skills.py")

print(f"로드된 도구: {[t.name for t in tools]}")

agent = Agent(api_key=os.getenv("ANTHROPIC_API_KEY"), tools=tools)
print(agent.run("'Hello World'를 대문자로 바꾼 다음 뒤집어줘"))
```

### 🔨 확장

**프로젝트**: Skills 디렉토리 만들기
```
my_skills/
├── text_tools.py    # 텍스트 처리 도구
├── math_tools.py    # 수학 계산 도구
└── data_tools.py    # 데이터 변환 도구
```

```python
# 디렉토리 전체 로드
loader = SkillLoader()
all_tools = loader.load_from_directory("my_skills/")
print(f"총 {len(all_tools)}개 도구 로드됨")
```

### ✅ 성공 기준
- [ ] Skills 파일 생성 및 로드 성공
- [ ] 디렉토리에서 여러 Skills 파일 로드
- [ ] Skills 기반 에이전트 동작 확인

---

## Level 7: 대화와 컨텍스트

### 📖 확인

에이전트는 **대화 히스토리**를 유지합니다. 이전 대화를 기억한다는 의미입니다.

```python
agent.run("Python 파일들을 찾아줘")     # 메시지 2개 추가
agent.run("그 중 첫 번째 파일을 읽어줘") # "그 중"이 무엇인지 기억!
agent.run("거기서 import 구문만 뽑아줘") # 방금 읽은 내용 기억!
```

**히스토리 확인**:
```python
for msg in agent.messages:
    role = msg['role']
    # content는 텍스트 또는 도구 호출 목록
    print(f"{role}: {str(msg['content'])[:80]}...")
```

**컨텍스트 관리 패턴**:

```python
# 패턴 1: 연속 대화 (히스토리 유지)
agent.run("A 파일을 찾아줘")
agent.run("그 파일을 읽어줘")   # 이전 결과 참조 가능

# 패턴 2: 새 태스크 (히스토리 초기화)
agent.run("새 작업 시작", clear_history=True)

# 패턴 3: 수동 초기화
agent.clear_history()
```

### ▶️ 돌려보기

```bash
python -m jagent.examples.conversational_agent_example
```

```python
# conversation_test.py
import os
from jagent import Agent
from jagent.tools import FileRead, Glob

agent = Agent(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    tools=[FileRead(), Glob()]
)

# 연속 대화 테스트
responses = [
    agent.run("jagent/core/ 에 있는 파일들을 찾아줘"),
    agent.run("그 파일들 중 tool.py를 읽어줘"),
    agent.run("방금 읽은 파일에서 Tool 클래스가 하는 역할을 설명해줘"),
]

for i, resp in enumerate(responses, 1):
    print(f"\n--- 대화 {i} ---")
    print(resp[:300])

print(f"\n총 메시지 수: {len(agent.messages)}")
```

### 🔨 확장

**프로젝트**: 인터랙티브 코드 탐색기
```python
import os
from jagent import Agent
from jagent.tools import FileRead, Glob, Grep

agent = Agent(api_key=os.getenv("ANTHROPIC_API_KEY"), tools=[FileRead(), Glob(), Grep()])

print("jagent 코드 탐색기 (종료: 'quit')")
while True:
    question = input("\n질문: ").strip()
    if question.lower() == 'quit':
        break
    response = agent.run(question)  # 히스토리 유지!
    print(f"\n답변: {response}")
```

### ✅ 성공 기준
- [ ] 다단계 대화에서 이전 컨텍스트 참조 확인
- [ ] `clear_history`와 히스토리 유지 차이 이해
- [ ] 인터랙티브 대화 구현

---

## Level 8: 에러 처리와 디버깅

### 📖 확인

**3가지 주요 문제와 해결법**:

**문제 1: 도구가 호출되지 않음**
```python
# 진단
tool = agent.registry.get("my_tool")
print(tool.to_anthropic_tool())  # LLM에 전달되는 정의 확인

# 해결: description을 더 구체적으로
description = "파일 경로를 입력받아 줄 수를 반환합니다. 예: count_lines('/path/to/file.py')"
```

**문제 2: 검증 에러**
```python
# 진단
try:
    tool.validate_input(file_path=None)  # 잘못된 입력 테스트
except Exception as e:
    print(e)

# 해결: Field에 명확한 description 추가
file_path: str = Field(description="절대 경로 (예: /home/user/file.py)")
```

**문제 3: 무한 루프**
```python
# 진단
agent = Agent(max_iterations=3)  # 먼저 제한

# 해결: 도구가 충분한 정보를 반환하는지 확인
def execute(self, ...) -> str:
    return f"완료: {result}\n파일이 존재합니다: {os.path.exists(path)}"
```

### ▶️ 돌려보기

```bash
python -m jagent.examples.debugging_tools
```

**`run_once()`로 단계별 디버깅**:

```python
# debug_agent.py
import os
from jagent import Agent
from jagent.tools import Glob

agent = Agent(api_key=os.getenv("ANTHROPIC_API_KEY"), tools=[Glob()])

# 단 한 번만 실행 (루프 없음)
result = agent.run_once("Python 파일을 모두 찾아줘")

print("텍스트 응답:", result["text"])
print("\n도구 호출:", result["tool_calls"])
print("\n도구 결과:", result["results"])
```

### 🔨 확장

**견고한 도구 구현 패턴**:

```python
class RobustFileTool(Tool):
    name = "robust_file_read"
    description = "안전하게 파일을 읽습니다. 경로 검증 포함."
    input_schema = FileReadInput

    def execute(self, file_path: str, limit: Optional[int] = None) -> str:
        # 1. 입력 검증
        if not file_path:
            return "오류: 파일 경로가 비어있습니다"
        if ".." in file_path:
            return "오류: 상대 경로(..) 사용 불가"
        if not os.path.isabs(file_path):
            return f"오류: 절대 경로를 사용하세요 (현재: {file_path})"

        # 2. 존재 확인
        if not os.path.exists(file_path):
            return f"오류: 파일 없음: {file_path}"
        if not os.path.isfile(file_path):
            return f"오류: 파일이 아님: {file_path}"

        # 3. 실행
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            if limit:
                lines = lines[:limit]
            return "".join(lines)
        except PermissionError:
            return f"오류: 읽기 권한 없음: {file_path}"
        except Exception as e:
            return f"오류: {type(e).__name__}: {str(e)}"
```

### ✅ 성공 기준
- [ ] `run_once()`로 도구 호출 과정 확인
- [ ] 도구 미호출 문제 1개 이상 직접 디버깅
- [ ] 견고한 에러 처리가 포함된 도구 구현

---

## Level 9: 실전 프로젝트

### 📖 확인

지금까지 배운 모든 것을 종합합니다:

```
커스텀 도구 +  에이전트  + Skills  + 에러처리 = 실전 프로젝트
 (Level 4)    (Level 5)  (Level 6)  (Level 8)
```

**프로젝트 구조 패턴**:

```
my_project/
├── tools/
│   ├── __init__.py
│   └── custom_tools.py    # 프로젝트 전용 도구
├── agent.py               # 에이전트 설정 및 실행
├── config.py              # 설정 (API 키, 경로 등)
└── README.md              # 사용법
```

### ▶️ 돌려보기

`jagent/examples/project_template/` 참고:

```bash
ls jagent/examples/project_template/
python jagent/examples/project_template/agent.py
```

### 🔨 확장: 5가지 실전 프로젝트

**프로젝트 A**: 코드 문서화 도우미 ⭐⭐
```python
# 도구: Glob, FileRead, FileWrite
# 기능: Python 파일을 읽고 docstring이 없는 함수를 찾아 자동으로 추가
agent.run(
    "jagent/tools/filesystem.py 의 execute 메서드들에 docstring이 없으면 추가해줘"
)
```

**프로젝트 B**: 프로젝트 초기화 도구 ⭐⭐
```python
# 도구: FileWrite, Bash, 커스텀 도구
# 기능: 새 Python 프로젝트 구조 자동 생성
agent.run(
    "/tmp/my_new_project 디렉토리를 만들고, "
    "기본 Python 프로젝트 구조(src/, tests/, README.md, pyproject.toml)를 생성해줘"
)
```

**프로젝트 C**: 로그 분석기 ⭐⭐⭐
```python
# 도구: FileRead, FileWrite, Grep, 커스텀 LogParserTool
# 기능: 로그 파일 분석 및 요약 보고서 생성

class LogParserInput(BaseModel):
    log_content: str = Field(description="분석할 로그 내용")

class LogParser(Tool):
    name = "parse_log"
    description = "로그 내용을 분석해 ERROR/WARNING 통계를 반환합니다"
    input_schema = LogParserInput

    def execute(self, log_content: str) -> str:
        lines = log_content.split('\n')
        errors = [l for l in lines if 'ERROR' in l]
        warnings = [l for l in lines if 'WARNING' in l]
        return f"ERROR: {len(errors)}건, WARNING: {len(warnings)}건\n최근 에러: {errors[-1] if errors else '없음'}"
```

**프로젝트 D**: 개인 지식베이스 ⭐⭐⭐
```python
# 도구: FileRead, FileWrite, FileEdit, Glob, Grep
# 기능: Markdown 노트 생성, 검색, 연결

system_prompt = """당신은 개인 지식베이스 관리자입니다.
노트는 /tmp/notes/ 디렉토리에 .md 파일로 저장합니다.
각 노트 상단에는 날짜와 태그를 포함합니다."""

agent = Agent(api_key=key, tools=[...], system_prompt=system_prompt)
```

**프로젝트 E**: 코드 리뷰어 ⭐⭐⭐⭐
```python
# 도구: FileRead, FileEdit, Glob
# 기능: Python 파일을 분석하고 개선 제안 후 적용

agent.run(
    "jagent/tools/bash.py 를 읽고 코드 품질 관점에서 개선사항을 제안해줘. "
    "동의하면 직접 수정도 해줘."
)
```

**직접 시도**: `jagent/examples/project_template/` 의 구조를 복사해서 자신만의 프로젝트를 만들어보세요.

### ✅ 최종 성공 기준
- [ ] 프로젝트 A-E 중 하나 이상 완성
- [ ] 커스텀 도구 + 내장 도구 조합 사용
- [ ] 에러 처리 포함
- [ ] 다른 사람에게 설명 가능

---

## 부록

### 자주 묻는 질문 (FAQ)

**Q: 도구를 얼마나 많이 추가해도 되나요?**
A: 이론적으로는 제한이 없지만, 도구가 많을수록 LLM의 선택이 어려워집니다. 실용적으로는 10-15개가 적당합니다. 많으면 Skills로 묶어 필요할 때만 로드하세요.

**Q: description을 어떻게 써야 LLM이 잘 선택하나요?**
A: 구체적인 예시와 사용 시나리오를 포함하세요:
```python
# 나쁜 예
description = "파일 읽기"

# 좋은 예
description = "파일 내용을 읽어 반환합니다. 코드 파일, 설정 파일, 텍스트 파일 모두 지원합니다. 예: file_read('/path/to/script.py')"
```

**Q: API 비용이 걱정됩니다**
A: `run_once()`로 단일 호출 테스트를 먼저 하세요. 또한 claude-3-haiku 모델이 가장 저렴합니다:
```python
agent = Agent(api_key=key, model="claude-3-haiku-20240307")
```

**Q: 에이전트가 계속 도구를 호출하고 끝내지 않아요**
A: `max_iterations`를 낮추거나, 시스템 프롬프트에 "작업 완료 후 바로 결과를 알려주세요"를 추가하세요.

**Q: 대화 히스토리가 너무 길어지면요?**
A: 일정 메시지 수 이상이면 초기화하거나, 중요한 정보를 파일로 저장하는 패턴을 사용하세요.

---

### 트러블슈팅 빠른 참조

| 증상 | 원인 | 해결책 |
|------|------|--------|
| `ImportError: No module named 'jagent'` | 설치 안됨 | `pip install -e .` |
| `ANTHROPIC_API_KEY not set` | 환경변수 없음 | `export ANTHROPIC_API_KEY='...'` |
| 도구가 호출 안됨 | description 불명확 | description에 예시 추가 |
| `ValidationError` | 잘못된 입력 타입 | Field description 개선 |
| 무한 루프 | 도구 결과 불충분 | `max_iterations` 제한, 도구 반환값 개선 |
| 응답이 너무 느림 | 큰 파일 처리 | `limit` 파라미터 사용 |

---

### 핵심 파일 읽기 가이드

jagent의 동작 원리를 깊이 이해하려면 이 파일들을 순서대로 읽으세요:

```
1. jagent/core/tool.py          - Tool 추상 클래스 (모든 것의 기반)
2. jagent/core/registry.py      - ToolRegistry (도구 관리)
3. jagent/core/executor.py      - ToolExecutor (도구 실행)
4. jagent/llm/anthropic_client.py - LLM 통신 (API 호출 방식)
5. jagent/core/agent.py         - Agent (메인 루프, 가장 중요!)
6. jagent/tools/filesystem.py   - 실제 도구 구현 예시
```

---

### 나만의 에이전트 체크리스트

```
[ ] 목적 정의: 이 에이전트가 해결할 문제는?
[ ] 도구 선택: 어떤 내장 도구를 쓸까?
[ ] 커스텀 도구: 없는 기능은 만들어야 할까?
[ ] 시스템 프롬프트: 에이전트 역할 명확화
[ ] 에러 처리: 각 도구에 try/except 포함
[ ] 테스트: 도구 단독 테스트 → 에이전트 연동 테스트
[ ] 문서화: README 작성
```

---

### 다음 단계

이 가이드를 완료했다면 다음 주제를 탐색해보세요:

- **MCP (Model Context Protocol)**: 외부 서비스와 연동 — `jagent/mcp/client.py`
- **비동기 도구**: `asyncio`를 사용한 병렬 도구 실행
- **도구 캐싱**: 반복 호출 결과를 캐시해 비용 절감
- **웹 인터페이스**: FastAPI로 에이전트 HTTP API 만들기
- **Claude Code 소스**: 실제 프로덕션 구현과 비교

---

*이 가이드는 [Claude Code](https://github.com/anthropics/claude-code)의 아키텍처에서 영감을 받아 교육 목적으로 만들어졌습니다.*
