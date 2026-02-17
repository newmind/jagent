"""
프로젝트 전용 커스텀 도구 모음.

이 파일을 복사해서 자신만의 도구를 만드는 시작점으로 사용하세요.
각 도구는 독립적으로 테스트 가능하며, 에이전트와 함께 사용할 수 있습니다.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from jagent import Tool


# =============================================================
# 도구 1: 텍스트 통계
# =============================================================

class WordCounterInput(BaseModel):
    text: str = Field(description="분석할 텍스트")

class WordCounter(Tool):
    """텍스트의 단어 수, 문자 수, 줄 수를 분석합니다."""

    name = "word_counter"
    description = (
        "텍스트를 분석해 단어 수, 문자 수, 줄 수, 고유 단어 수를 반환합니다. "
        "문서나 코드의 규모를 파악할 때 유용합니다."
    )
    input_schema = WordCounterInput

    def execute(self, text: str) -> str:
        try:
            words = text.split()
            unique_words = set(w.lower().strip('.,!?') for w in words)
            lines = text.splitlines()

            return (
                f"텍스트 분석 결과:\n"
                f"  총 단어 수: {len(words)}개\n"
                f"  고유 단어 수: {len(unique_words)}개\n"
                f"  총 문자 수: {len(text)}개 (공백 포함)\n"
                f"  줄 수: {len(lines)}줄\n"
                f"  평균 단어 길이: {sum(len(w) for w in words) / max(len(words), 1):.1f}자"
            )
        except Exception as e:
            return f"오류: {type(e).__name__}: {str(e)}"


# =============================================================
# 도구 2: 간단한 텍스트 요약
# =============================================================

class TextSummarizerInput(BaseModel):
    text: str = Field(description="요약할 텍스트")
    max_sentences: int = Field(
        default=3,
        description="요약에 포함할 최대 문장 수",
        ge=1, le=10
    )

class TextSummarizer(Tool):
    """
    텍스트를 요약합니다.
    (실제 AI 요약 아님 — 앞부분 문장을 추출하는 단순 구현)
    실제 프로젝트에서는 이 도구를 LLM 기반으로 교체하세요.
    """

    name = "summarize_text"
    description = (
        "긴 텍스트를 짧게 요약합니다. "
        "앞의 중요한 문장들을 추출해 반환합니다."
    )
    input_schema = TextSummarizerInput

    def execute(self, text: str, max_sentences: int = 3) -> str:
        try:
            # 문장 분리 (간단한 구현)
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            sentences = [s.strip() for s in sentences if s.strip()]

            if not sentences:
                return "요약할 내용이 없습니다"

            selected = sentences[:max_sentences]
            summary = ' '.join(selected)

            return (
                f"요약 ({len(sentences)}개 문장 → {len(selected)}개):\n"
                f"{summary}"
            )
        except Exception as e:
            return f"오류: {type(e).__name__}: {str(e)}"


# =============================================================
# 도구 3: 파일 통계
# =============================================================

class FileStatsInput(BaseModel):
    file_path: str = Field(description="분석할 파일의 절대 경로")

class FileStats(Tool):
    """파일의 크기, 수정일, 확장자 등 메타데이터를 반환합니다."""

    name = "file_stats"
    description = (
        "파일의 크기, 수정 날짜, 확장자 등 메타데이터를 반환합니다. "
        "파일 정보를 빠르게 확인할 때 사용하세요."
    )
    input_schema = FileStatsInput

    def execute(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                return f"오류: 파일을 찾을 수 없습니다: {file_path}"

            stat = os.stat(file_path)
            from datetime import datetime

            size_bytes = stat.st_size
            if size_bytes < 1024:
                size_str = f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes/1024:.1f}KB"
            else:
                size_str = f"{size_bytes/1024/1024:.1f}MB"

            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            ext = os.path.splitext(file_path)[1] or '(없음)'
            is_file = os.path.isfile(file_path)

            return (
                f"파일 정보: {os.path.basename(file_path)}\n"
                f"  경로: {file_path}\n"
                f"  종류: {'파일' if is_file else '디렉토리'}\n"
                f"  크기: {size_str}\n"
                f"  확장자: {ext}\n"
                f"  수정일: {modified}"
            )
        except Exception as e:
            return f"오류: {type(e).__name__}: {str(e)}"


# =============================================================
# 도구 직접 테스트 (이 파일을 직접 실행할 때)
# =============================================================

if __name__ == "__main__":
    print("커스텀 도구 단독 테스트\n")

    # WordCounter 테스트
    wc = WordCounter()
    print(wc.run(text="Hello World, this is jagent. An AI agent framework for learning."))

    print()

    # TextSummarizer 테스트
    ts = TextSummarizer()
    sample = "AI agents are powerful tools. They can read files and execute commands. jagent makes it easy to build them. You can add custom tools too. Start building today!"
    print(ts.run(text=sample, max_sentences=2))

    print()

    # FileStats 테스트
    fs = FileStats()
    import os
    this_file = os.path.abspath(__file__)
    print(fs.run(file_path=this_file))
