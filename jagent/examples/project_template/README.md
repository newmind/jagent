# 프로젝트 템플릿

jagent 기반 프로젝트를 만들기 위한 시작점입니다.

## 구조

```
project_template/
├── tools/
│   ├── __init__.py       # 도구 임포트
│   └── custom_tools.py   # 커스텀 도구 구현
├── agent.py              # 메인 에이전트 (진입점)
├── config.py             # API 키, 모델 등 설정
└── README.md             # 이 파일
```

## 빠른 시작

```bash
# 1. 환경변수 설정
export ANTHROPIC_API_KEY='sk-ant-...'

# 2. 데모 실행
python -m jagent.examples.project_template.agent

# 3. 단일 질문
python -m jagent.examples.project_template.agent "jagent/README.md 를 읽어줘"
```

## 커스텀 도구 추가

`tools/custom_tools.py` 에 새 도구를 추가합니다:

```python
from jagent import Tool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(description="파라미터 설명")

class MyTool(Tool):
    name = "my_tool"
    description = "이 도구가 하는 일"
    input_schema = MyToolInput

    def execute(self, param: str) -> str:
        try:
            return f"처리 완료: {param}"
        except Exception as e:
            return f"오류: {e}"
```

그리고 `agent.py` 의 `create_agent()` 에 추가합니다:

```python
from jagent.examples.project_template.tools.custom_tools import MyTool

def create_agent():
    return Agent(
        ...
        tools=[
            ...,
            MyTool(),  # 추가
        ]
    )
```

## 설정 변경

`config.py` 또는 환경변수로 변경합니다:

```bash
export JAGENT_MODEL="claude-3-haiku-20240307"    # 빠르고 저렴한 모델
export JAGENT_MAX_ITERATIONS="5"                  # 반복 횟수 제한
export JAGENT_OUTPUT_DIR="/my/output/dir"         # 출력 경로
```

## 내장된 도구

| 도구 | 기능 |
|------|------|
| `file_read` | 파일 읽기 |
| `file_write` | 파일 쓰기 |
| `file_edit` | 파일 편집 (find & replace) |
| `glob` | 파일 패턴 검색 |
| `grep` | 내용 검색 |
| `bash` | 셸 명령 실행 |
| `word_counter` | 텍스트 통계 |
| `summarize_text` | 텍스트 요약 |
| `file_stats` | 파일 메타데이터 |

## 이 템플릿으로 만들 수 있는 것들

- **노트 관리자**: Markdown 노트 생성, 검색, 편집
- **코드 분석기**: Python 파일 구조 분석 및 리포트
- **프로젝트 초기화**: 보일러플레이트 코드 자동 생성
- **로그 분석기**: 로그 파일 파싱 및 통계
- **문서 업데이터**: README, docstring 자동 업데이트
