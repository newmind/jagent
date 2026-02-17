"""
Level 8: 디버깅 유틸리티

에이전트 동작을 분석하고 문제를 찾는 도구들입니다.

학습 목표:
- run_once()로 단일 스텝 디버깅
- 도구 레지스트리 검사
- 메시지 히스토리 분석
- 도구가 호출되지 않는 이유 찾기
"""

import os
import json
from typing import Optional
from pydantic import BaseModel, Field
from jagent import Agent, Tool
from jagent.tools import Glob, FileRead, Bash


# =============================================================
# 디버깅 도구 1: 에이전트 상태 검사기
# =============================================================

def inspect_registry(agent: Agent):
    """에이전트의 도구 레지스트리를 출력합니다"""
    print("\n📋 도구 레지스트리 검사")
    print("-" * 40)
    tools = agent.registry.list_tools()
    print(f"등록된 도구 수: {len(tools)}개\n")
    for tool in tools:
        schema = tool.input_schema.model_json_schema()
        required = schema.get('required', [])
        properties = schema.get('properties', {})
        print(f"  [{tool.name}]")
        print(f"    설명: {tool.description[:80]}...")
        print(f"    필수 입력: {required}")
        print(f"    선택 입력: {[k for k in properties if k not in required]}")


def inspect_messages(agent: Agent, max_preview: int = 100):
    """에이전트의 대화 히스토리를 출력합니다"""
    print("\n💬 대화 히스토리 검사")
    print("-" * 40)
    print(f"총 메시지 수: {len(agent.messages)}개\n")

    for i, msg in enumerate(agent.messages):
        role = msg['role']
        content = msg['content']

        if isinstance(content, str):
            preview = content[:max_preview]
            print(f"  [{i+1}] {role}: \"{preview}{'...' if len(content)>max_preview else ''}\"")

        elif isinstance(content, list):
            # 도구 호출 또는 도구 결과 메시지
            for item in content:
                if isinstance(item, dict):
                    item_type = item.get('type', 'unknown')
                    if item_type == 'tool_use':
                        print(f"  [{i+1}] {role} [도구 호출]: {item['name']}({item.get('input', {})})")
                    elif item_type == 'tool_result':
                        result_content = str(item.get('content', ''))[:max_preview]
                        print(f"  [{i+1}] {role} [도구 결과]: {result_content}...")
                    elif item_type == 'text':
                        text = item.get('text', '')[:max_preview]
                        print(f"  [{i+1}] {role} [텍스트]: {text}...")
                    else:
                        print(f"  [{i+1}] {role} [{item_type}]")


# =============================================================
# 디버깅 도구 2: run_once()로 단일 스텝 분석
# =============================================================

def debug_single_step(agent: Agent, query: str):
    """
    run_once()를 사용해 단 한 번의 LLM 호출을 분석합니다.
    어떤 도구를 호출했는지, 결과는 무엇인지 확인합니다.
    """
    print(f"\n🔍 단일 스텝 분석: '{query}'")
    print("-" * 40)

    result = agent.run_once(query)

    print(f"텍스트 응답: {result['text'][:200] if result['text'] else '(없음)'}")

    if result['tool_calls']:
        print(f"\n도구 호출 ({len(result['tool_calls'])}개):")
        for call in result['tool_calls']:
            print(f"  → {call['name']}({json.dumps(call['input'], ensure_ascii=False)})")

        if result['results']:
            print(f"\n도구 결과:")
            for r in result['results']:
                outcome = r.get('result') or r.get('error', '?')
                status = '✅' if r.get('success') else '❌'
                print(f"  {status} {r['tool_name']}: {str(outcome)[:150]}")
    else:
        print("\n→ 도구 호출 없음 (LLM이 직접 답변)")


# =============================================================
# 디버깅 도구 3: 도구 description 테스터
# 어떤 description이 더 잘 선택되는지 비교
# =============================================================

class VagueToolInput(BaseModel):
    x: str

class VagueTool(Tool):
    """❌ 설명이 모호해서 LLM이 언제 써야 할지 모르는 도구"""
    name = "vague_tool"
    description = "뭔가를 합니다"
    input_schema = VagueToolInput

    def execute(self, x: str) -> str:
        return f"처리됨: {x}"


class ClearToolInput(BaseModel):
    text: str = Field(description="대문자로 변환할 텍스트")

class ClearTool(Tool):
    """✅ 설명이 명확해서 LLM이 정확히 언제 써야 할지 아는 도구"""
    name = "clear_tool"
    description = (
        "텍스트를 대문자로 변환합니다. "
        "예: 'hello' → 'HELLO'. "
        "대소문자 변환이 필요할 때 사용하세요."
    )
    input_schema = ClearToolInput

    def execute(self, text: str) -> str:
        return text.upper()


def test_tool_descriptions(agent: Agent):
    """두 도구의 description을 비교합니다"""
    print("\n📝 Description 품질 비교 테스트")
    print("-" * 40)

    # 두 도구의 Anthropic 형식 출력
    vague = VagueTool()
    clear = ClearTool()

    print("❌ 모호한 도구:")
    print(f"   name: {vague.name}")
    print(f"   description: {vague.description}")

    print("\n✅ 명확한 도구:")
    print(f"   name: {clear.name}")
    print(f"   description: {clear.description}")

    # 두 도구를 모두 등록하고 어떤 게 선택되는지 확인
    agent.registry.unregister("vague_tool") if agent.registry.get("vague_tool") else None
    agent.registry.unregister("clear_tool") if agent.registry.get("clear_tool") else None
    agent.registry.register(vague)
    agent.registry.register(clear)

    result = agent.run_once("'hello world'를 대문자로 바꿔줘")

    print(f"\n질문: 'hello world'를 대문자로 바꿔줘")
    if result['tool_calls']:
        called = result['tool_calls'][0]['name']
        print(f"→ 선택된 도구: {called}")
        print(f"→ {'명확한 도구가 선택됨 ✅' if called == 'clear_tool' else '모호한 도구가 선택됨 — description 개선 필요!'}")
    else:
        print("→ 도구가 호출되지 않음")


# =============================================================
# 디버깅 도구 4: 에이전트 진단
# 흔한 문제 자동 감지
# =============================================================

def diagnose_agent(agent: Agent):
    """에이전트의 일반적인 문제를 진단합니다"""
    print("\n🔧 에이전트 진단")
    print("-" * 40)
    issues = []
    warnings = []

    # 1. 도구 수 확인
    tool_count = len(agent.registry)
    if tool_count == 0:
        issues.append("도구가 없습니다! 최소 1개 이상 추가하세요")
    elif tool_count > 20:
        warnings.append(f"도구가 너무 많습니다 ({tool_count}개). LLM이 선택하기 어려울 수 있습니다")

    # 2. description 품질 확인
    for tool in agent.registry.list_tools():
        if len(tool.description) < 20:
            warnings.append(f"'{tool.name}' 도구의 description이 너무 짧습니다: '{tool.description}'")
        if not any(c in tool.description for c in ['합니다', '반환합니다', 'returns', 'provides']):
            warnings.append(f"'{tool.name}' 도구의 description이 동작을 명확히 설명하지 않습니다")

    # 3. max_iterations 확인
    if agent.max_iterations < 3:
        warnings.append(f"max_iterations={agent.max_iterations}이 너무 낮습니다. 복잡한 작업이 중단될 수 있습니다")

    # 결과 출력
    if not issues and not warnings:
        print("✅ 진단 완료: 문제가 발견되지 않았습니다")
    else:
        for issue in issues:
            print(f"  ❌ 오류: {issue}")
        for warning in warnings:
            print(f"  ⚠️  경고: {warning}")

    # 요약
    print(f"\n요약:")
    print(f"  도구 수: {tool_count}개")
    print(f"  max_iterations: {agent.max_iterations}")
    print(f"  시스템 프롬프트 길이: {len(agent.system_prompt)}자")
    print(f"  현재 대화 메시지 수: {len(agent.messages)}개")


# =============================================================
# 메인
# =============================================================

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("오류: ANTHROPIC_API_KEY 환경변수를 설정하세요")
        return

    print("🔧 jagent - 디버깅 도구 예제")
    print("="*60)

    agent = Agent(
        api_key=api_key,
        tools=[Glob(), FileRead(), Bash()],
    )

    # 1. 레지스트리 검사
    inspect_registry(agent)

    # 2. 진단
    diagnose_agent(agent)

    # 3. 단일 스텝 분석
    debug_single_step(agent, "현재 디렉토리의 Python 파일을 찾아줘")

    # 4. 히스토리 검사 (실제 run 후)
    agent.run("jagent/ 디렉토리 구조를 알려줘")
    inspect_messages(agent)

    # 5. Description 품질 테스트
    test_tool_descriptions(agent)

    print("\n\n✅ 디버깅 도구 예제 완료!")
    print("\n💡 핵심 디버깅 명령어:")
    print("  agent.run_once(query)          # 단일 LLM 호출")
    print("  agent.registry.list_tools()    # 등록된 도구 목록")
    print("  agent.registry.get('name')     # 특정 도구 가져오기")
    print("  agent.messages                 # 전체 대화 히스토리")
    print("  tool.to_anthropic_tool()       # LLM에 전달되는 도구 정의")


if __name__ == "__main__":
    main()
