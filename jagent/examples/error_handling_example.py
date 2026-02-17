"""
Level 8: 에러 처리 패턴 예제

견고한 도구를 만드는 방법을 보여줍니다.
좋은 도구는 절대 예외를 밖으로 내보내지 않고 에러 메시지를 반환합니다.

학습 목표:
- 도구 에러 처리의 중요성 이해
- 입력 검증 패턴
- 에이전트가 에러를 어떻게 처리하는지 관찰
"""

import os
import json
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from jagent import Agent, Tool
from jagent.tools import FileRead


# =============================================================
# 나쁜 도구 예시 — 에러가 전파됨 (하지 마세요!)
# =============================================================

class BadFileReaderInput(BaseModel):
    path: str

class BadFileReader(Tool):
    """❌ 나쁜 예: 에러를 처리하지 않음"""
    name = "bad_file_reader"
    description = "파일을 읽습니다 (나쁜 예시)"
    input_schema = BadFileReaderInput

    def execute(self, path: str) -> str:
        # ❌ 예외가 발생하면 에이전트 전체가 중단됨
        with open(path, 'r') as f:
            return f.read()


# =============================================================
# 좋은 도구 예시 — 단계별 에러 처리
# =============================================================

class SafeFileReaderInput(BaseModel):
    file_path: str = Field(description="읽을 파일의 절대 경로 (예: /home/user/file.txt)")
    max_lines: Optional[int] = Field(
        default=None,
        description="최대 읽을 줄 수. 생략하면 전체 읽기",
        ge=1,      # 1 이상
        le=10000,  # 10000 이하
    )

    @field_validator('file_path')
    @classmethod
    def validate_path(cls, v):
        """경로 기본 검증"""
        if not v or not v.strip():
            raise ValueError("파일 경로가 비어있습니다")
        return v.strip()


class SafeFileReader(Tool):
    """
    ✅ 좋은 예: 단계적 에러 처리

    에러 처리 순서:
    1. 입력 검증 (Pydantic이 자동으로)
    2. 경로 안전성 검사
    3. 존재 확인
    4. 파일 여부 확인
    5. 실제 읽기 (예외 캐치)
    """
    name = "safe_file_reader"
    description = (
        "파일을 안전하게 읽습니다. "
        "절대 경로를 입력하면 내용을 반환합니다. "
        "파일이 없거나 권한이 없으면 명확한 에러 메시지를 반환합니다."
    )
    input_schema = SafeFileReaderInput

    def execute(self, file_path: str, max_lines: Optional[int] = None) -> str:
        # 단계 1: 경로 안전성 검사
        if ".." in file_path:
            return "오류: 상대 경로(..)는 보안상 허용되지 않습니다"

        if not os.path.isabs(file_path):
            return (
                f"오류: 절대 경로를 사용하세요. "
                f"현재 입력: '{file_path}' → "
                f"예시: '{os.path.abspath(file_path)}'"
            )

        # 단계 2: 존재 확인
        if not os.path.exists(file_path):
            # 비슷한 파일 제안
            parent = os.path.dirname(file_path)
            basename = os.path.basename(file_path)
            suggestions = []
            if os.path.isdir(parent):
                suggestions = [
                    f for f in os.listdir(parent)
                    if basename.lower()[:3] in f.lower()
                ][:3]

            msg = f"오류: 파일을 찾을 수 없습니다: {file_path}"
            if suggestions:
                msg += f"\n혹시 이 파일인가요? {suggestions}"
            return msg

        # 단계 3: 파일 여부 확인
        if os.path.isdir(file_path):
            files = os.listdir(file_path)[:5]
            return (
                f"오류: '{file_path}'는 디렉토리입니다. "
                f"파일을 지정하세요.\n"
                f"디렉토리 내 파일(최대 5개): {files}"
            )

        # 단계 4: 크기 확인
        size_mb = os.path.getsize(file_path) / 1024 / 1024
        if size_mb > 10:
            return (
                f"경고: 파일이 너무 큽니다 ({size_mb:.1f}MB). "
                f"max_lines 파라미터로 읽을 줄 수를 제한하세요."
            )

        # 단계 5: 실제 읽기
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                if max_lines:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append(f"... ({max_lines}줄에서 중단, 전체 파일은 더 깁니다)")
                            break
                        lines.append(line.rstrip())
                    content = "\n".join(lines)
                else:
                    content = f.read()

            line_count = content.count('\n') + 1
            return f"[{file_path}] ({line_count}줄)\n\n{content}"

        except PermissionError:
            return f"오류: 읽기 권한이 없습니다: {file_path}"
        except UnicodeDecodeError:
            return f"오류: 텍스트 파일이 아닌 것 같습니다 (바이너리 파일?): {file_path}"
        except Exception as e:
            return f"오류: {type(e).__name__}: {str(e)}"


# =============================================================
# JSON 파서 도구 — 에러 메시지를 LLM이 이해하기 쉽게
# =============================================================

class JsonParserInput(BaseModel):
    json_string: str = Field(description="파싱할 JSON 문자열")
    key_path: Optional[str] = Field(
        default=None,
        description="추출할 키 경로 (예: 'user.name', 'items.0'). 생략하면 전체 반환"
    )

class JsonParser(Tool):
    """
    JSON 문자열을 파싱하고 선택적으로 특정 키를 추출합니다.
    파싱 실패 시 어디서 실패했는지 명확히 알려줍니다.
    """
    name = "parse_json"
    description = (
        "JSON 문자열을 파싱합니다. "
        "key_path로 중첩된 값 추출 가능 (예: 'user.name'). "
        "파싱 실패 시 정확한 위치와 원인을 알려줍니다."
    )
    input_schema = JsonParserInput

    def execute(self, json_string: str, key_path: Optional[str] = None) -> str:
        # JSON 파싱
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            # 에러 위치를 명확히 표시
            lines = json_string.split('\n')
            error_line = lines[e.lineno - 1] if e.lineno <= len(lines) else ""
            return (
                f"JSON 파싱 오류: {e.msg}\n"
                f"위치: {e.lineno}번째 줄, {e.colno}번째 글자\n"
                f"해당 줄: {error_line}\n"
                f"     {'':>{e.colno-1}}^ 여기"
            )

        # 키 경로로 값 추출
        if key_path:
            try:
                value = data
                for key in key_path.split('.'):
                    if isinstance(value, list):
                        value = value[int(key)]
                    else:
                        value = value[key]
                return json.dumps(value, indent=2, ensure_ascii=False)
            except (KeyError, IndexError, TypeError) as e:
                available = list(data.keys()) if isinstance(data, dict) else f"리스트 (길이: {len(data)})"
                return (
                    f"키 '{key_path}'를 찾을 수 없습니다: {e}\n"
                    f"사용 가능한 키: {available}"
                )
            except ValueError:
                return f"오류: 리스트 인덱스는 숫자여야 합니다 (예: 'items.0')"

        return json.dumps(data, indent=2, ensure_ascii=False)


# =============================================================
# 에러 처리 테스트
# =============================================================

def demonstrate_error_handling():
    """에러 처리 패턴을 직접 보여줍니다 (에이전트 없이)"""
    print("\n" + "="*60)
    print("도구 에러 처리 데모 (에이전트 없이 직접 실행)")
    print("="*60)

    reader = SafeFileReader()
    parser = JsonParser()

    test_cases = [
        # (도구, 입력, 설명)
        (reader, {"file_path": "relative/path.py"},         "상대 경로 입력"),
        (reader, {"file_path": "/nonexistent/file.txt"},    "존재하지 않는 파일"),
        (reader, {"file_path": "/home/user/jagent"},        "디렉토리 입력"),
        (reader, {"file_path": "/home/user/jagent/jagent/core/tool.py", "max_lines": 3},
                                                             "정상 입력 (3줄만)"),
        (parser, {"json_string": '{"name": "jagent"'},      "JSON 오류 (괄호 없음)"),
        (parser, {"json_string": '{"name":"jagent"}', "key_path": "version"},
                                                             "없는 키 접근"),
        (parser, {"json_string": '{"name":"jagent","v":"0.1"}', "key_path": "name"},
                                                             "정상 JSON 파싱"),
    ]

    for tool, inputs, description in test_cases:
        print(f"\n테스트: {description}")
        print(f"  입력: {inputs}")
        result = tool.run(**inputs)
        print(f"  결과: {result[:150]}")


def example_with_agent():
    """에이전트와 함께 에러 처리 관찰"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return

    print("\n" + "="*60)
    print("에이전트와 함께 에러 처리 관찰")
    print("에이전트가 에러 메시지를 받으면 어떻게 복구하는지 보세요")
    print("="*60)

    agent = Agent(
        api_key=api_key,
        tools=[SafeFileReader(), JsonParser(), FileRead()],
        system_prompt="파일 작업을 수행합니다. 에러가 나면 이유를 분석하고 올바른 방법으로 재시도하세요."
    )

    # 에이전트가 에러를 받고 스스로 복구하는지 관찰
    response = agent.run(
        "jagent/core/tool.py 파일을 읽어줘 "
        "(상대 경로로 먼저 시도해보고, 안 되면 절대 경로로 시도해봐)"
    )
    print(f"\n에이전트 응답:\n{response}")


# =============================================================
# 메인
# =============================================================

def main():
    print("🛡️ jagent - 에러 처리 패턴 예제")

    # 1. 도구 직접 테스트 (에이전트 없이)
    demonstrate_error_handling()

    # 2. 에이전트와 함께
    example_with_agent()

    print("\n\n✅ 에러 처리 예제 완료!")
    print("\n💡 핵심 원칙:")
    print("  1. execute()에서 절대 예외를 발생시키지 마세요")
    print("  2. 에러 메시지는 LLM이 이해할 수 있게 구체적으로")
    print("  3. 가능하면 대안이나 수정 방법을 제안")
    print("  4. Pydantic Field 검증으로 1차 방어")


if __name__ == "__main__":
    main()
