"""
프로젝트 설정.

API 키, 모델, 경로 등 설정을 한 곳에서 관리합니다.
실제 프로젝트에서는 .env 파일이나 환경변수를 사용하세요.
"""

import os


# =============================================================
# LLM 설정
# =============================================================

# API 키 (환경변수에서 가져옴)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# 사용할 모델
# 빠르고 저렴한 모델: claude-3-haiku-20240307
# 균형: claude-3-5-sonnet-20241022
# 가장 강력: claude-3-5-sonnet-20241022
MODEL = os.getenv("JAGENT_MODEL", "claude-3-5-sonnet-20241022")

# 최대 반복 횟수 (도구 체이닝 깊이)
MAX_ITERATIONS = int(os.getenv("JAGENT_MAX_ITERATIONS", "10"))


# =============================================================
# 경로 설정
# =============================================================

# 프로젝트 루트
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 출력 디렉토리 (보고서, 결과 파일 등)
OUTPUT_DIR = os.getenv("JAGENT_OUTPUT_DIR", "/tmp/jagent_output")


# =============================================================
# 에이전트 설정
# =============================================================

SYSTEM_PROMPT = """당신은 파일 분석 전문가입니다.
요청된 파일 작업을 정확하고 체계적으로 수행하세요.
에러가 발생하면 원인을 설명하고 대안을 제시하세요."""


# =============================================================
# 설정 검증
# =============================================================

def validate_config():
    """설정이 올바른지 확인합니다."""
    errors = []

    if not ANTHROPIC_API_KEY:
        errors.append(
            "ANTHROPIC_API_KEY가 설정되지 않았습니다.\n"
            "  → export ANTHROPIC_API_KEY='sk-ant-...'"
        )

    # 출력 디렉토리 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if errors:
        print("설정 오류:")
        for e in errors:
            print(f"  ❌ {e}")
        return False

    print(f"✅ 설정 확인 완료")
    print(f"   모델: {MODEL}")
    print(f"   출력 디렉토리: {OUTPUT_DIR}")
    return True


if __name__ == "__main__":
    validate_config()
