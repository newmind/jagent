"""
Level 5: 도구 조합 예제 (Tool Chaining)

여러 도구를 순서대로 연결해서 복잡한 작업을 수행합니다.
패턴: Glob → FileRead → 분석 → FileWrite

학습 목표:
- 도구 체이닝이 자동으로 이루어지는 방식 이해
- 복잡한 멀티스텝 질문 작성법
- 시스템 프롬프트로 에이전트 역할 특화
"""

import os
import json
from pydantic import BaseModel, Field
from jagent import Agent, Tool
from jagent.tools import Glob, FileRead, FileWrite, Grep


# =============================================================
# 커스텀 분석 도구: 도구 체인의 마지막 단계에 사용
# =============================================================

class CodeMetricsInput(BaseModel):
    code_content: str = Field(description="분석할 Python 코드 내용")
    file_name: str = Field(description="파일 이름 (리포트 용)")

class CodeMetrics(Tool):
    """
    Python 코드의 기본 메트릭을 계산합니다.
    줄 수, 함수 수, 클래스 수, import 수를 반환합니다.
    """
    name = "analyze_code_metrics"
    description = (
        "Python 코드를 분석해 줄 수, 함수 수, 클래스 수, import 수 등 "
        "기본 메트릭을 반환합니다. 코드 내용을 직접 입력받습니다."
    )
    input_schema = CodeMetricsInput

    def execute(self, code_content: str, file_name: str) -> str:
        lines = code_content.split('\n')
        metrics = {
            "파일": file_name,
            "총 줄 수": len(lines),
            "코드 줄 수": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            "주석 줄 수": len([l for l in lines if l.strip().startswith('#')]),
            "빈 줄 수": len([l for l in lines if not l.strip()]),
            "함수 수": len([l for l in lines if l.strip().startswith('def ')]),
            "클래스 수": len([l for l in lines if l.strip().startswith('class ')]),
            "import 수": len([l for l in lines if l.strip().startswith(('import ', 'from '))]),
        }
        result = "\n".join(f"  {k}: {v}" for k, v in metrics.items())
        return f"=== {file_name} 분석 결과 ===\n{result}"


# =============================================================
# 예제 1: 기본 도구 체이닝
# 패턴: Glob(파일 찾기) → FileRead(읽기) → 분석
# =============================================================

def example_basic_chaining(agent: Agent):
    print("\n" + "="*60)
    print("예제 1: 기본 도구 체이닝")
    print("패턴: Glob → FileRead → 분석")
    print("="*60)

    query = """
    jagent/core/ 디렉토리에 있는 Python 파일 목록을 찾고,
    그 중 tool.py 파일의 내용을 읽어서,
    파일의 목적과 주요 클래스를 간단히 요약해줘.
    """

    print(f"\n질문: {query.strip()}")
    print("\n실행 중... (여러 도구가 순서대로 호출됩니다)\n")

    response = agent.run(query, clear_history=True)
    print(f"답변:\n{response}")

    # 몇 번의 LLM 호출이 있었는지 확인
    tool_calls = len([m for m in agent.messages if m['role'] == 'user'
                      and isinstance(m['content'], list)])
    print(f"\n→ 도구 결과 메시지 수: {tool_calls}개")
    print(f"→ 총 대화 메시지 수: {len(agent.messages)}개")


# =============================================================
# 예제 2: 검색 → 읽기 → 보고서 생성
# 패턴: Grep(내용 검색) → FileRead(전체 읽기) → FileWrite(보고서)
# =============================================================

def example_search_and_report(agent: Agent):
    print("\n" + "="*60)
    print("예제 2: 검색 → 읽기 → 보고서 생성")
    print("패턴: Grep → FileRead → FileWrite")
    print("="*60)

    query = """
    jagent/ 디렉토리의 Python 파일에서 'Tool' 단어가 포함된 클래스 정의를 찾아줘.
    (class.*Tool 패턴으로 검색)
    찾은 클래스들의 파일 위치와 이름을 정리해서 /tmp/tool_classes.txt에 저장해줘.
    """

    print(f"\n질문: {query.strip()}")
    print("\n실행 중...\n")

    response = agent.run(query, clear_history=True)
    print(f"답변:\n{response}")

    # 결과 파일 확인
    result_file = "/tmp/tool_classes.txt"
    if os.path.exists(result_file):
        print(f"\n→ 생성된 파일 ({result_file}):")
        with open(result_file) as f:
            print(f.read()[:300])


# =============================================================
# 예제 3: 다단계 분석 파이프라인
# 패턴: Glob → FileRead(각 파일) → CodeMetrics(분석) → FileWrite(보고서)
# =============================================================

def example_analysis_pipeline(agent: Agent):
    print("\n" + "="*60)
    print("예제 3: 코드 분석 파이프라인")
    print("패턴: Glob → FileRead → CodeMetrics → FileWrite")
    print("="*60)

    query = """
    jagent/tools/ 디렉토리의 Python 파일들을 모두 찾아서,
    각 파일을 읽고 analyze_code_metrics 도구로 분석한 뒤,
    분석 결과를 /tmp/code_report.txt 파일에 저장해줘.
    마지막에 어떤 파일이 가장 큰지도 알려줘.
    """

    print(f"\n질문: {query.strip()}")
    print("\n실행 중... (여러 파일을 순서대로 처리합니다)\n")

    response = agent.run(query, clear_history=True)
    print(f"답변:\n{response}")

    if os.path.exists("/tmp/code_report.txt"):
        print("\n→ 생성된 보고서 미리보기:")
        with open("/tmp/code_report.txt") as f:
            print(f.read()[:500])


# =============================================================
# 메인
# =============================================================

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("오류: ANTHROPIC_API_KEY 환경변수를 설정하세요")
        return

    # 분석 전문 에이전트 생성
    agent = Agent(
        api_key=api_key,
        tools=[
            Glob(),
            FileRead(),
            FileWrite(),
            Grep(),
            CodeMetrics(),   # 커스텀 분석 도구
        ],
        system_prompt="""당신은 코드베이스 분석 전문가입니다.
        도구를 순서대로 체계적으로 사용해서 복잡한 작업을 완수하세요.
        각 단계의 결과를 다음 단계에 활용하세요.""",
        max_iterations=15,  # 복잡한 체이닝을 위해 반복 횟수 늘림
    )

    print("🔗 jagent - 도구 체이닝 예제")
    print(f"로드된 도구: {[t.name for t in agent.registry.list_tools()]}")

    example_basic_chaining(agent)
    example_search_and_report(agent)
    example_analysis_pipeline(agent)

    print("\n\n✅ 도구 체이닝 예제 완료!")
    print("\n💡 학습 포인트:")
    print("  1. 에이전트가 자동으로 도구 순서를 결정합니다")
    print("  2. 복잡한 질문일수록 더 많은 도구 호출이 발생합니다")
    print("  3. 커스텀 도구를 체인 중간에 삽입할 수 있습니다")


if __name__ == "__main__":
    main()
