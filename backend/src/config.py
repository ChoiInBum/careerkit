"""
설정 관리 모듈
환경 변수 로드 및 설정값 관리
"""
import os
from pathlib import Path

# dotenv import (없으면 에러 발생)
from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트에서 찾기)
current_dir = Path(__file__).parent
project_root = current_dir.parent
env_paths = [
    project_root / ".env",
    current_dir / ".env",
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ .env 파일 로드: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    raise FileNotFoundError(
        f".env 파일을 찾을 수 없습니다. 다음 경로 중 하나에 .env 파일을 생성하세요:\n"
        f"  - {env_paths[0]}\n"
        f"  - {env_paths[1]}"
    )

# API 키 설정 (환경 변수에서만 로드)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 필수 환경 변수 검증
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.\n"
        ".env 파일에 다음을 추가하세요:\n"
        "OPENAI_API_KEY=your_api_key_here"
    )

# 선택적 환경 변수
USE_GEMINI = bool(GEMINI_API_KEY)

# 슬롯 정의
SLOT_ORDER = ["desired_job", "location", "job_type", "company_size"]
SLOT_QUESTIONS = {
    "desired_job": "희망 직무가 무엇인가요? (예: 백엔드 개발자, 데이터 분석가 등)",
    "location": "근무 희망 지역을 알려주세요. (예: 서울, 원격, 부산 등)",
    "job_type": "선호하는 고용형태가 있나요? (예: 정규직, 계약직, 프리랜서)",
    "company_size": "선호하는 기업 규모가 있나요? (예: 스타트업, 중견기업, 대기업, 또는 '상관없음')"
}

SLOT_DESCRIPTIONS = {
    "desired_job": {
        "description": "사용자가 원하는 직무나 포지션",
        "examples": ["백엔드 개발자", "프론트엔드 개발자", "풀스택", "데이터 분석가", "AI 엔지니어", "DevOps"],
        "validation": "직무 관련 키워드가 있는지 확인"
    },
    "location": {
        "description": "근무를 희망하는 지역",
        "examples": ["서울", "경기", "부산", "대전", "원격", "재택", "anywhere"],
        "validation": "지역명 또는 원격/재택 키워드 확인"
    },
    "job_type": {
        "description": "선호하는 고용 형태",
        "examples": ["정규직", "계약직", "인턴", "프리랜서", "파트타임"],
        "validation": "고용 형태 키워드 확인"
    },
    "company_size": {
        "description": "선호하는 기업 규모",
        "examples": ["스타트업", "중소기업", "중견기업", "대기업", "외국계", "상관없음"],
        "validation": "기업 규모 키워드 확인, 상관없음은 null 처리"
    }
}

# 매칭 점수 가중치
SCORE_WEIGHTS = {
    "job_title": 0.30,
    "skills": 0.20,
    "mandatory": 0.15,
    "preferred": 0.10,
    "tasks": 0.10,
    "domain": 0.10,
    "work_condition": 0.05
}

