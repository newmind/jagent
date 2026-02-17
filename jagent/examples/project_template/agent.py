"""
프로젝트 템플릿 — 메인 에이전트

이 파일을 시작점으로 자신만의 에이전트를 만드세요.

사용법:
    python agent.py                     # 데모 실행
    python agent.py "질문을 입력하세요"  # 단일 질문
"""

import os
import sys

# jagent 임포트
from jagent import Agent
from jagent.tools import FileRead, FileWrite, FileEdit, Glob, Grep, Bash
from jagent.skills import SkillLoader

# 프로젝트 설정과 커스텀 도구
from jagent.examples.project_template.config import (
    ANTHROPIC_API_KEY, MODEL, MAX_ITERATIONS, SYSTEM_PROMPT, OUTPUT_DIR,
    validate_config
)
from jagent.examples.project_template.tools.custom_tools import (
    WordCounter, TextSummarizer, FileStats
)


def create_agent() -> Agent:
    """
    에이전트를 설정하고 반환합니다.

    내장 도구 + 커스텀 도구를 모두 포함합니다.
    """
    return Agent(
        api_key=ANTHROPIC_API_KEY,
        model=MODEL,
        max_iterations=MAX_ITERATIONS,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            # 내장 도구
            FileRead(),
            FileWrite(),
            FileEdit(),
            Glob(),
            Grep(),
            Bash(),

            # 커스텀 도구 (tools/custom_tools.py)
            WordCounter(),
            TextSummarizer(),
            FileStats(),
        ]
    )


def run_demo(agent: Agent):
    """에이전트 기능 데모"""
    print("\n" + "="*60)
    print("프로젝트 템플릿 에이전트 데모")
    print("="*60)

    demo_tasks = [
        # (설명, 질문)
        (
            "파일 통계",
            f"jagent/core/agent.py 파일의 정보를 file_stats 도구로 확인해줘"
        ),
        (
            "내용 분석",
            f"jagent/README.md 를 읽고 word_counter 도구로 단어 수를 세줘"
        ),
        (
            "파일 검색 + 분석",
            f"jagent/tools/ 의 Python 파일들을 찾아서 "
            f"각 파일의 file_stats 를 확인해줘"
        ),
    ]

    for title, task in demo_tasks:
        print(f"\n--- {title} ---")
        print(f"질문: {task[:80]}...")
        response = agent.run(task, clear_history=True)
        print(f"답변: {response[:400]}")
        if len(response) > 400:
            print("  ... (생략)")


def run_interactive(agent: Agent):
    """인터랙티브 모드"""
    print("\n" + "="*60)
    print("인터랙티브 모드 (종료: Ctrl+C 또는 'quit')")
    print("="*60)
    print(f"\n사용 가능한 도구: {[t.name for t in agent.registry.list_tools()]}\n")

    while True:
        try:
            user_input = input("질문: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다")
            break

        if not user_input:
            continue

        if user_input.lower() in ('quit', 'exit', 'q'):
            break

        if user_input.lower() == 'clear':
            agent.clear_history()
            print("→ 대화 히스토리 초기화\n")
            continue

        response = agent.run(user_input)
        print(f"\n에이전트: {response}\n")


def main():
    # 설정 검증
    if not validate_config():
        sys.exit(1)

    # 에이전트 생성
    agent = create_agent()
    print(f"\n에이전트 준비 완료: {len(agent.registry)}개 도구")

    # 명령행 인수로 단일 질문 처리
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n질문: {query}")
        response = agent.run(query)
        print(f"\n답변: {response}")
        return

    # 데모 실행
    print("\n실행 모드를 선택하세요:")
    print("  1. 데모 실행")
    print("  2. 인터랙티브 모드")
    print("  3. 종료")

    try:
        choice = input("\n선택 (1/2/3): ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    if choice == "1":
        run_demo(agent)
    elif choice == "2":
        run_interactive(agent)
    else:
        print("종료합니다")


if __name__ == "__main__":
    main()
