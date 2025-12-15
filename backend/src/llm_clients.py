"""
LLM 클라이언트 초기화 모듈
OpenAI, Gemini 클라이언트 관리
"""
from .config import OPENAI_API_KEY, GEMINI_API_KEY, USE_GEMINI

# OpenAI 클라이언트 초기화
import openai

openai_version = openai.__version__
print(f"📦 OpenAI 버전: {openai_version}")

if hasattr(openai, 'OpenAI'):
    OPENAI_CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 신버전 클라이언트 초기화 완료")
else:
    openai.api_key = OPENAI_API_KEY
    OPENAI_CLIENT = openai
    print("✅ OpenAI 구버전 API 키 설정 완료")

USE_OPENAI = True
print(f"✅ OpenAI API 키 로드 성공")

# Gemini 클라이언트 초기화 (선택적)
GEMINI_CLIENT = None
GEMINI_MODEL_NAME = None

def initialize_gemini_client():
    """Gemini 클라이언트를 초기화합니다. LLM 기능 사용 직전에 호출되어야 합니다."""
    global GEMINI_CLIENT, GEMINI_MODEL_NAME
    
    # 이미 초기화 되었다면 종료
    if GEMINI_CLIENT is not None:
        return True
    
    # config에서 환경 변수를 다시 임포트 (함수 내에서 사용하기 위함)
    # NOTE: .config 모듈에서 직접 변수를 가져옵니다.
    from .config import GEMINI_API_KEY, USE_GEMINI

    if USE_GEMINI and GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GEMINI_API_KEY)
            print("🔍 Gemini 모델 초기화 중...")
            
            model_name = 'gemini-2.5-flash'
            GEMINI_CLIENT = genai.GenerativeModel(model_name)
            GEMINI_MODEL_NAME = model_name
            print(f"✅ Gemini 모델 초기화 완료: {model_name}")
            return True
        except ImportError:
            # 모듈이 없는 경우, 에러 대신 경고만 출력하고 넘어갑니다.
            print("❌ 'google.generativeai' 모듈이 없습니다. Gemini 기능 비활성화.")
            return False
    
    print("⚠️  GEMINI_API_KEY가 설정되지 않아 Gemini를 사용할 수 없습니다.")

