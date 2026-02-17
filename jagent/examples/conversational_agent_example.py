"""
Level 7: 대화와 컨텍스트 관리 예제

에이전트가 이전 대화를 기억하며 연속적인 질문에 답합니다.
'그 파일', '방금 읽은 내용' 같은 참조가 가능합니다.

학습 목표:
- 대화 히스토리(agent.messages)의 역할 이해
- 컨텍스트 유지 vs 초기화 시점 파악
- 인터랙티브 에이전트 루프 구현
"""

import os
from jagent import Agent
from jagent.tools import FileRead, Glob, Grep


# =============================================================
# 예제 1: 자동 멀티턴 대화 (코드베이스 Q&A)
# 이전 대화 내용을 참조하면서 질문이 이어집니다
# =============================================================

def example_multiturn_qa(agent: Agent):
    print("\n" + "="*60)
    print("예제 1: 멀티턴 대화 (코드베이스 Q&A)")
    print("이전 답변을 기억하며 연속 질문에 답합니다")
    print("="*60)

    # 연속된 질문 목록 — 이전 답변에 의존하는 질문들
    questions = [
        "jagent/core/ 디렉토리에 있는 파일 목록을 알려줘",
        "그 파일들 중에서 agent.py를 읽어줘",          # '그 파일들' → 이전 결과 참조
        "방금 읽은 파일에서 Agent 클래스의 __init__ 메서드를 설명해줘",  # '방금 읽은'
        "그 클래스의 run 메서드는 몇 번까지 반복할 수 있어?",  # '그 클래스'
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[질문 {i}] {question}")
        response = agent.run(question)  # clear_history=False (기본값) → 히스토리 유지
        print(f"[답변 {i}] {response[:400]}")
        if len(response) > 400:
            print("  ... (생략)")
        print(f"  (누적 메시지 수: {len(agent.messages)}개)")

    print(f"\n→ 최종 대화 히스토리: {len(agent.messages)}개 메시지")
    print("→ 에이전트가 이전 내용을 참조하며 답변했습니다")


# =============================================================
# 예제 2: 히스토리 초기화 vs 유지 비교
# =============================================================

def example_history_comparison(agent: Agent):
    print("\n" + "="*60)
    print("예제 2: 히스토리 유지 vs 초기화 비교")
    print("="*60)

    # 먼저 파일을 읽어 컨텍스트 형성
    agent.run("jagent/core/tool.py 를 읽어줘", clear_history=True)
    msg_count_after_read = len(agent.messages)
    print(f"\n파일 읽기 후 메시지 수: {msg_count_after_read}개")

    # [히스토리 유지] 이전 내용 참조 가능
    resp_with_history = agent.run("방금 읽은 파일에서 몇 개의 메서드가 정의되었어?")
    print(f"\n[히스토리 유지] '{resp_with_history[:150]}...'")

    # [히스토리 초기화] 이전 내용 없음
    resp_fresh = agent.run(
        "방금 읽은 파일에서 몇 개의 메서드가 정의되었어?",
        clear_history=True   # 새로 시작
    )
    print(f"\n[히스토리 초기화] '{resp_fresh[:150]}...'")
    print("\n→ 초기화하면 '방금 읽은 파일'을 모릅니다!")

    # 히스토리 직접 확인
    print(f"\n현재 메시지 수: {len(agent.messages)}개 (초기화 후 새 대화)")


# =============================================================
# 예제 3: 인터랙티브 REPL (실제 대화형 에이전트)
# 사용자가 직접 질문을 입력합니다
# =============================================================

def example_interactive_repl(agent: Agent):
    print("\n" + "="*60)
    print("예제 3: 인터랙티브 대화형 에이전트")
    print("명령어: 'quit' 종료 | 'clear' 히스토리 초기화 | 'history' 메시지 확인")
    print("="*60)
    print("\n💬 jagent 코드베이스 탐색기 시작!")
    print("   jagent 프로젝트에 대해 자유롭게 질문하세요\n")

    agent.clear_history()  # 새 세션 시작

    while True:
        try:
            user_input = input("당신: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다")
            break

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            print("대화를 종료합니다")
            break

        if user_input.lower() == 'clear':
            agent.clear_history()
            print("→ 히스토리를 초기화했습니다 (새 대화 시작)\n")
            continue

        if user_input.lower() == 'history':
            print(f"\n→ 현재 {len(agent.messages)}개 메시지:")
            for i, msg in enumerate(agent.messages):
                role = msg['role']
                content = msg['content']
                if isinstance(content, str):
                    preview = content[:80]
                elif isinstance(content, list):
                    preview = f"[도구 관련 메시지 {len(content)}개]"
                else:
                    preview = str(content)[:80]
                print(f"  {i+1}. {role}: {preview}")
            print()
            continue

        # 에이전트 실행 (히스토리 유지)
        print("에이전트: ", end="", flush=True)
        response = agent.run(user_input)
        print(response)
        print(f"  [메시지 수: {len(agent.messages)}개]\n")


# =============================================================
# 메인
# =============================================================

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("오류: ANTHROPIC_API_KEY 환경변수를 설정하세요")
        return

    agent = Agent(
        api_key=api_key,
        tools=[FileRead(), Glob(), Grep()],
        system_prompt="""당신은 jagent 프로젝트의 코드베이스를 안내하는 도우미입니다.
        사용자의 이전 질문과 문맥을 기억하며 연속적인 질문에 답하세요.
        코드를 설명할 때는 구체적인 파일 경로와 줄 번호를 포함하세요."""
    )

    print("💬 jagent - 대화형 에이전트 예제")
    print(f"도구: {[t.name for t in agent.registry.list_tools()]}")

    # 자동 멀티턴 데모
    example_multiturn_qa(agent)

    # 히스토리 비교
    example_history_comparison(agent)

    # 인터랙티브 모드 (선택)
    print("\n\n인터랙티브 모드를 실행하시겠습니까? (y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice == 'y':
            example_interactive_repl(agent)
    except (EOFError, KeyboardInterrupt):
        pass

    print("\n✅ 대화형 에이전트 예제 완료!")
    print("\n💡 학습 포인트:")
    print("  1. clear_history=False (기본값): 이전 대화 기억")
    print("  2. clear_history=True: 새 대화 시작 (이전 내용 없음)")
    print("  3. agent.messages 로 전체 히스토리 확인 가능")
    print("  4. 히스토리가 길어질수록 API 비용 증가 — 필요할 때 초기화")


if __name__ == "__main__":
    main()
