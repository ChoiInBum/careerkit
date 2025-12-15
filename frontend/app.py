import streamlit as st
import requests
import json



# ============================================================
# 1. 로그인 페이지 (기존 m1.py 내용 활용)
# ============================================================

def run_login_page():
    # 페이지 설정함
    st.set_page_config(
        page_title="CareerKit 로그인",
        layout="centered"
    )

    # 스타일 유지 적용함
    st.markdown("""
    <style>
    .main {
        display: flex;
        flex-direction: column;
        align-items: center;
        background-color: white;
        color: #e0e0e0;
    }

    .login-container {
        padding: 30px;
        border-radius: 10px;
        font-size: 40px;
        text-align: center;
        background-color: white;
        box-shadow: 0 4px 15px #ded4f1;
        max-width: 700px;
        width: 100%;
        margin-top: 40px;
        margin-bottom: 40px;        
    }
    
    .login-title {
        color: purple;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
                
    .login-subtitle {
        color: black;
        text-align: center;
        margin-bottom: 40px;
        font-size: 1em;
    }
 /* 텍스트박스 스타일 */
    div[data-testid="stTextInput"] {
        margin-bottom: 20px;
    }

    div[data-testid="stTextInput"] input {
        color: #8888aa !important;
        background-color: transparent !important;
        border-radius: 0 !important;
        border: none !important;
        padding: 12px 15px !important;
        font-size: 0.95em !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #b0a4d8 !important;
    }

    /* 비밀번호 버튼 숨김 */
    div[data-testid="stTextInput"] button {
        display: none !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #b0a4d8 !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        border-radius: 10px;
        padding: 0.8em 0;
        margin-top: 10px;
        font-size: 0.95em;
        color: white;
        border: none;
        cursor: pointer;
        font-weight: 600;
    }

    /* 로그인 버튼 - 중앙 정렬 및 크기 확대 */
    .primary-btn {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 20px 0;
    }
    
    .primary-btn button {
        background-image: linear-gradient(135deg, #667eea, #764ba2);
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        width: 100%;
        max-width: 400px;
        padding: 1em 2em;
        font-size: 1.1em;
        font-weight: 700;
    }

    .primary-btn button:hover {
        background-image: linear-gradient(135deg, #5a67d8, #6b46c1);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
    }

    /* 전체 로그인 박스 컨테이너 */
    .login-box-container {
        background-color: #faf9ff;
        border-radius: 15px;
        padding: 30px;
        max-width: 500px;
        width: 100%;
        margin: 0 auto;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
    }
    
    /* 게스트 버튼 - 테두리 없이 */
    .guest-btn-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 20px 0 0 0;
        padding: 0;
    }
    
    .guest-btn {
        width: 100%;
        max-width: 400px;
    }
    
    .guest-btn button {
        background-color: white;
        color: #6b46c1;
        border: none;
        box-shadow: 0 2px 5px rgba(107, 70, 193, 0.1);
        width: 100%;
        padding: 1em 2em;
        font-size: 1.1em;
        font-weight: 700;
    }

    .guest-btn button:hover {
        background-color: #f3e8ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(107, 70, 193, 0.2);
    }

    /* 공통 텍스트 */
    p {
        color: #5a5a7a;
        font-size: 0.9em;
    }

    .stMarkdown a {
        color: #6b46c1;
        text-decoration: none;
    }

    .stMarkdown a:hover {
        text-decoration: underline;
    }

    .stMarkdown span {
        color: #5a5a7a;
        font-size: 0.9em;
    }

    </style>
    """, unsafe_allow_html=True)

    # 컨테이너 시작함
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="login-container">💼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;📃&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;💁', unsafe_allow_html=True)

    # 헤더 출력함
    st.markdown(
        """
        <div class="login-title">
            Career<em style="font-style: italic !important;">K</em>it
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="login-subtitle">AI로 완성하는 맞춤형 취업 준비</div>', unsafe_allow_html=True)

    # 전체 로그인 박스 컨테이너 시작
    st.markdown('<div class="login-box-container">', unsafe_allow_html=True)
    
    # 로그인 폼
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("이메일 입력", label_visibility="collapsed", placeholder="이메일 입력")
        password = st.text_input("입력비밀번호", type="password", label_visibility="collapsed", placeholder="입력비밀번호")

        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        login_submitted = st.form_submit_button("로그인", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if login_submitted:
            # 간단한 예시용: 이메일/비밀번호 체크 (실제 서비스에서는 DB나 인증 서버와 연동해야 함)
            if email == "test@test.com" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.login_type = "user"
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("이메일 또는 비밀번호가 잘못되었습니다.")

    # 구분선
    st.markdown("<p style='text-align: center; margin-top: 20px; margin-bottom: 20px; font-size: 0.9em; color: #888;'>또는</p>", unsafe_allow_html=True)

    # 게스트로 시작 버튼 - 테두리 없이 박스 안에 넣기
    st.markdown('<div class="guest-btn-container">', unsafe_allow_html=True)
    st.markdown('<div class="guest-btn">', unsafe_allow_html=True)
    guest_login = st.button("게스트로 시작하기", key="guest_start_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 전체 로그인 박스 컨테이너 종료
    st.markdown('</div>', unsafe_allow_html=True)

    # 페이지 이동 로직
    if guest_login:
        st.session_state.logged_in = True
        st.session_state.login_type = "guest"
        st.rerun()

    # 링크
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <a href="#" style="text-decoration: none; color: #a07dff; font-size: 0.9em;">회원가입</a> 
        <span style="color: #5a5a7a;">|</span> 
        <a href="#" style="text-decoration: none; color: #a07dff; font-size: 0.9em;">비밀번호 찾기</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



# ============================================================
# 2. 메인 앱 (기존 app.py 내용 활용)
# ============================================================

def run_main_app():
    # 페이지 설정
    st.set_page_config(
        page_title="AI 이력서 분석 & 채용 매칭",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # FastAPI 백엔드 URL
    BACKEND_URL = "http://localhost:8000"

    # 세션 상태 초기화 (CSS보다 먼저!)
    if 'page' not in st.session_state:
        st.session_state.page = 'upload'
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'collected_data' not in st.session_state:
        st.session_state.collected_data = None
    if 'job_listings' not in st.session_state:
        st.session_state.job_listings = []
    if 'selected_job' not in st.session_state:
        st.session_state.selected_job = None
    if 'interview_data' not in st.session_state:
        st.session_state.interview_data = None
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

    # 스타일 정의
    st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    body {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 50%, #f3f0ff 100%);
        background-attachment: fixed;
    }
    .main-header {
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 50%, #7c3aed 100%);
        border-radius: 18px;
        padding: 1.5rem 2rem;
        color: white;
        margin-bottom: 1.0rem;
        box-shadow: 0 10px 25px rgba(139, 92, 246, 0.25);
    }
    .main-header h1 {
        font-size: 1.7rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .main-header p {
        font-size: 0.95rem;
        opacity: 0.95;
    }
    .sub-text-info {
        font-size: 0.8rem;
        margin-top: 0.3rem;
        opacity: 0.9;
    }
    .sub-text-warning {
        font-size: 0.8rem;
        margin-top: 0.3rem;
        color: #fef3c7;
    }

    /* 사이드바 스타일 - 연보라 계통 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f3f0ff 0%, #ede9fe 50%, #e9d5ff 100%);
        color: #5b21b6;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #6d28d9;
        font-weight: 700;
    }
    /* 사이드바 버튼 텍스트 색상 */
    [data-testid="stSidebar"] button {
        color: #5b21b6 !important;
        background-color: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid rgba(167, 139, 250, 0.3) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        padding: 0.7rem 0.5rem !important;
        margin-bottom: 0.4rem !important;
        border-radius: 12px !important;
        text-align: left !important;
        white-space: normal !important;
        line-height: 1.4 !important;
        box-shadow: 0 2px 4px rgba(167, 139, 250, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(167, 139, 250, 0.2) !important;
        border-color: #a78bfa !important;
        transform: translateX(4px);
        box-shadow: 0 4px 8px rgba(167, 139, 250, 0.2) !important;
    }
    [data-testid="stSidebar"] button:disabled {
        background: linear-gradient(135deg, #c084fc 0%, #a78bfa 100%) !important;
        border-color: #8b5cf6 !important;
        color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
    }
    .sidebar-step {
        padding: 0.7rem 0.5rem;
        margin-bottom: 0.4rem;
        border-radius: 10px;
    }
    .sidebar-step.current {
        background: linear-gradient(135deg, rgba(167, 139, 250, 0.3) 0%, rgba(139, 92, 246, 0.2) 100%);
        border-left: 4px solid #8b5cf6;
    }
    .sidebar-step.completed {
        background-color: rgba(196, 181, 253, 0.2);
        border-left: 4px solid #a78bfa;
    }
    .sidebar-step.pending {
        background-color: rgba(255, 255, 255, 0.5);
        border-left: 4px solid rgba(167, 139, 250, 0.3);
    }
    .sidebar-step-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6d28d9;
    }
    .sidebar-step-desc {
        font-size: 0.8rem;
        color: #7c3aed;
        margin-top: 0.1rem;
    }

    /* 카드 스타일 */
    .info-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 18px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 4px 15px rgba(167, 139, 250, 0.15);
        margin-bottom: 1rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
        backdrop-filter: blur(10px);
    }
    .info-card h3 {
        font-size: 1.0rem;
        font-weight: 650;
        margin-bottom: 0.6rem;
        color: #6d28d9;
    }
    .info-card p {
        font-size: 0.9rem;
        color: #5b21b6;
        margin-bottom: 0.2rem;
    }
    .info-label {
        font-weight: 600;
        color: #7c3aed;
    }
    .badge {
        display: inline-block;
        padding: 0.15rem 0.45rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 0.3rem;
        background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
        color: #6d28d9;
        border: 1px solid rgba(167, 139, 250, 0.3);
    }

    /* 채팅 메시지 스타일 */
    .chat-message {
        padding: 0.8rem 1rem;
        border-radius: 16px;
        margin-bottom: 0.6rem;
        max-width: 100%;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(167, 139, 250, 0.15);
    }
    .chat-user {
        background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
        margin-left: 20%;
        border: 1px solid rgba(167, 139, 250, 0.4);
    }
    .chat-bot {
        background: linear-gradient(135deg, #f3e8ff 0%, #ede9fe 100%);
        margin-right: 20%;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    .chat-user-header,
    .chat-bot-header {
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 0.3rem;
    }
    .chat-user-header {
        color: #6d28d9;
    }
    .chat-bot-header {
        color: #7c3aed;
    }
    .chat-time {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.3rem;
        text-align: right;
    }

    /* 채용공고 카드 스타일 */
    .job-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(167, 139, 250, 0.3);
        border-radius: 18px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.1);
    }
    .job-card:hover {
        border-color: #a78bfa;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.25);
        transform: translateY(-4px);
        background: rgba(255, 255, 255, 1);
    }
    .job-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        color: #1a202c;
    }
    .job-company {
        font-size: 0.9rem;
        font-weight: 500;
        color: #4a5568;
        margin-bottom: 0.3rem;
    }
    .job-meta {
        font-size: 0.82rem;
        color: #718096;
        margin-bottom: 0.5rem;
    }
    .job-meta span {
        margin-right: 0.6rem;
    }
    .job-tags {
        margin-top: 0.6rem;
    }
    .job-tag {
        display: inline-block;
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
        color: #6d28d9;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        border: 1px solid rgba(167, 139, 250, 0.3);
    }
    .job-score {
        font-size: 0.8rem;
        font-weight: 500;
        color: #7c3aed;
        padding: 0.25rem 0.5rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
        display: inline-block;
        margin-bottom: 0.4rem;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }

    /* 상세 공고 섹션 카드 */
    .section-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 18px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.12);
        margin-bottom: 1rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    .section-card h4 {
        font-size: 0.95rem;
        font-weight: 650;
        margin-bottom: 0.5rem;
        color: #6d28d9;
    }
    .section-card ul {
        padding-left: 1.1rem;
        margin-bottom: 0;
    }
    .section-card li {
        font-size: 0.88rem;
        color: #4a5568;
        margin-bottom: 0.25rem;
    }
    .section-card p {
        font-size: 0.88rem;
        color: #4a5568;
        margin-bottom: 0.25rem;
    }

    /* 사이트 정보 카드 */
    .site-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 18px;
        padding: 1.0rem 1.1rem;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.12);
        margin-bottom: 1rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    .site-card span {
        font-size: 0.85rem;
        color: #5b21b6;
    }
    .site-badge {
        display: inline-block;
        font-size: 0.72rem;
        padding: 0.1rem 0.45rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
        color: #6d28d9;
        margin-right: 0.3rem;
        border: 1px solid rgba(167, 139, 250, 0.3);
    }

    /* 커버레터 섹션 */
    .cover-section {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 18px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.12);
        margin-bottom: 1rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    .cover-section h3 {
        font-size: 1.0rem;
        font-weight: 650;
        margin-bottom: 0.4rem;
        color: #6d28d9;
    }

    /* 기타 공통 요소 */
    .muted-text {
        font-size: 0.78rem;
        color: #a0aec0;
    }
    .highlight-text {
        font-weight: 600;
        color: #7c3aed;
    }
    .section-badge {
        display: inline-block;
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
        color: #6d28d9;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(167, 139, 250, 0.3);
    }
    
    /* Streamlit 버튼 스타일 통일 */
    .stButton > button {
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        box-shadow: 0 6px 18px rgba(139, 92, 246, 0.4);
        transform: translateY(-2px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary 버튼 강조 */
    button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.5) !important;
    }
    
    /* Secondary 버튼 */
    button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.8) !important;
        color: #6d28d9 !important;
        border: 2px solid rgba(167, 139, 250, 0.4) !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(167, 139, 250, 0.2) !important;
        border-color: #a78bfa !important;
    }
    
    /* Progress bar 스타일 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #a78bfa 0%, #8b5cf6 50%, #7c3aed 100%);
    }
    
    /* Success/Error 메시지 스타일 */
    .stSuccess {
        background: linear-gradient(135deg, #d8b4fe 0%, #c084fc 100%);
        border-left: 4px solid #8b5cf6;
        border-radius: 12px;
    }
    .stError {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
    }
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
    }
    
    /* Input 필드 스타일 */
    .stTextInput > div > div > input {
        border: 2px solid rgba(167, 139, 250, 0.3);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #a78bfa;
        box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
    }
    
    /* Text area 스타일 */
    .stTextArea > div > div > textarea {
        border: 2px solid rgba(167, 139, 250, 0.3);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #a78bfa;
        box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
    }
    
    /* File uploader 스타일 - 크기 줄이고 영어 텍스트 숨기기 */
    .stFileUploader {
        font-size: 0.85rem;
    }
    
    .stFileUploader label {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #6d28d9 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stFileUploader > div {
        border: 2px dashed rgba(167, 139, 250, 0.4);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.7);
        transition: all 0.3s ease;
        padding: 0.8rem !important;
        min-height: auto !important;
        max-width: 500px;
        margin: 0 auto;
    }
    
    .stFileUploader > div:hover {
        border-color: #a78bfa;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* 파일 업로더 내부 영어 텍스트 숨기기 */
    .stFileUploader [data-testid="stMarkdownContainer"] p,
    .stFileUploader [data-testid="stMarkdownContainer"] span {
        font-size: 0.8rem !important;
    }
    
    /* "Browse files" 버튼 스타일 조정 */
    .stFileUploader button[data-testid="baseButton-secondary"],
    .stFileUploader button[type="button"] {
        font-size: 0.8rem !important;
        padding: 0.4rem 0.8rem !important;
        min-width: auto !important;
    }
    
    /* 파일 업로더 내부 텍스트 스타일 */
    .stFileUploader .uploadedFile {
        font-size: 0.8rem !important;
    }
    
    /* "Drop files here" 같은 영어 텍스트 숨기기 */
    .stFileUploader [data-testid="stMarkdownContainer"]:has-text("Drop"),
    .stFileUploader [data-testid="stMarkdownContainer"]:has-text("Browse") {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI 이력서 분석 & 채용 매칭</h1>
    </div>
    """, unsafe_allow_html=True)

    # 사이드바: 단계별 진행상황 표시
    with st.sidebar:
        st.header("📊 진행 상황")

        steps = [
            ("upload", "1️⃣ 이력서 업로드", "PDF/TXT 이력서를 업로드합니다."),
            ("chat", "2️⃣ 정보 수집", "희망 직무/경력/지역 등 추가 정보를 수집합니다."),
            ("jobs", "3️⃣ 채용공고 매칭", "수집된 정보를 바탕으로 채용공고를 추천합니다."),
            ("job_detail", "4️⃣ 공고 상세페이지", "관심 공고의 상세 내용을 확인합니다."),
            ("cover_letter", "5️⃣ 자기소개서 작성", "선택한 공고에 맞춰 자기소개서를 생성합니다."),
            ("interview", "6️⃣ 모의면접", "선택한 공고에 대한 모의면접을 진행합니다."),
        ]

        current_page = st.session_state.page

        for step_key, step_title, step_desc in steps:
            # 각 단계를 클릭 가능한 버튼으로 만들기
            button_key = f"nav_{step_key}"
            is_current = (current_page == step_key)
            
            if st.button(
                f"{step_title}\n{step_desc}",
                key=button_key,
                use_container_width=True,
                disabled=is_current,
                type="primary" if is_current else "secondary"
            ):
                st.session_state.page = step_key
                st.rerun()

        st.markdown("---")
        st.markdown("**ℹ️ 사용 방법**")
        st.markdown("- 이력서를 먼저 업로드해주세요.")
        st.markdown("- 추가 질문에 답하면서 정보를 입력합니다.")
        st.markdown("- 추천된 채용공고 목록에서 공고를 선택하면 상세페이지와 자기소개서 작성까지 이어집니다.")

    # 메인 영역
    # 1) 이력서 업로드 페이지
    if st.session_state.page == 'upload':
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.subheader("📄 이력서 업로드")

            uploaded_file = st.file_uploader(
                "파일 업로드",
                type=['pdf', 'txt'],
                help="이력서를 업로드하면 AI가 자동으로 정보를 추출합니다",
                label_visibility="visible"
            )

            if uploaded_file is not None:
                with st.spinner('이력서를 분석하고 있습니다. 🤖'):
                    try:
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                        response = requests.post(f"{BACKEND_URL}/api/upload", files=files)

                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.session_id = data['session_id']
                            st.session_state.resume_data = data['resume']

                            # reply가 있으면 사용하고, 없으면 기본 메시지 사용
                            reply_message = data.get('reply', '이력서 분석이 완료되었습니다. 원하시는 직무는 무엇인가요?')
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': reply_message
                            })

                            st.session_state.page = 'chat'
                            st.success("✅ 이력서 분석 완료! 다음 단계로 이동합니다.")
                            st.balloons()
                            st.rerun()
                        else:
                            try:
                                err_msg = response.json().get('detail', '이력서 분석 중 오류가 발생했습니다.')
                            except Exception:
                                err_msg = f"이력서 분석 중 오류가 발생했습니다. (상태 코드: {response.status_code})"
                            st.error(err_msg)

                    except requests.exceptions.RequestException as e:
                        st.error(f"서버와 통신 중 오류가 발생했습니다: {e}")

            if st.session_state.resume_data:
                st.markdown("### 🔍 추출된 기본 이력 정보 (요약)")
                resume = st.session_state.resume_data

                col_info1, col_info2 = st.columns(2)

                with col_info1:
                    st.markdown("""
                    <div class="info-card">
                        <h3>👤 기본 정보</h3>
                    """, unsafe_allow_html=True)

                    st.markdown(f"- **이름:** {resume.get('name', 'N/A')}")
                    st.markdown(f"- **이메일:** {resume.get('email', 'N/A')}")
                    st.markdown(f"- **연락처:** {resume.get('phone', 'N/A')}")
                    st.markdown(f"- **경력:** {resume.get('experience_years', 0)}년")

                    st.markdown("</div>", unsafe_allow_html=True)

                with col_info2:
                    st.markdown("""
                    <div class="info-card">
                        <h3>🛠 보유 스킬 (상위)</h3>
                    """, unsafe_allow_html=True)

                    skills = resume.get('skills', [])
                    if skills:
                        skill_str = ", ".join(skills[:10])
                        st.markdown(f"- {skill_str}")
                    else:
                        st.markdown("- (추출된 스킬 정보가 없습니다.)")

                    st.markdown("</div>", unsafe_allow_html=True)


    # 2) 정보 수집(채팅) 페이지
    elif st.session_state.page == 'chat':
        st.subheader("💬 채용 정보 수집")

        if not st.session_state.session_id:
            st.warning("세션 정보가 없습니다. 먼저 이력서를 업로드해주세요.")
            if st.button("이력서 업로드 화면으로 이동", use_container_width=True):
                st.session_state.page = 'upload'
                st.rerun()
            return

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                role = msg.get('role', 'assistant')
                content = msg.get('content', '')

                if role == 'user':
                    st.markdown(f"""
                    <div class="chat-message chat-user">
                        <div class="chat-user-header">👤 사용자</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message chat-bot">
                        <div class="chat-bot-header">🤖 CareerKit 봇</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("메시지를 입력하세요", key='user_input')
            col_btn1, col_btn2 = st.columns([3, 1])
            with col_btn1:
                submit_button = st.form_submit_button("전송 📤", use_container_width=True)
            with col_btn2:
                skip_button = st.form_submit_button("잘 모르겠어요/건너뛰기 ⏭", use_container_width=True)

        if submit_button and user_input:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })

            with st.spinner('응답을 기다리는 중입니다... 🤔'):
                try:
                    form_data = {
                        'session_id': st.session_state.session_id,
                        'user_message': user_input
                    }
                    response = requests.post(f"{BACKEND_URL}/api/chat", data=form_data)

                    if response.status_code == 200:
                        data = response.json()

                        reply_message = data.get('reply', '알겠습니다.')
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': reply_message
                        })

                        if data.get('completed'):
                            st.session_state.collected_data = data
                            st.session_state.page = 'jobs'
                            st.success("✅ 모든 정보를 수집했습니다! 맞춤 채용공고를 찾습니다.")
                            st.balloons()

                        st.rerun()
                    else:
                        try:
                            err_msg = response.json().get('detail', '채팅 처리 중 오류가 발생했습니다.')
                        except Exception:
                            err_msg = f"채팅 처리 중 오류가 발생했습니다. (상태 코드: {response.status_code})"
                        st.error(err_msg)
                except requests.exceptions.RequestException as e:
                    st.error(f"서버와 통신 중 오류가 발생했습니다: {e}")

        if skip_button:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': '모르겠어요'
            })

            with st.spinner('다음 질문을 준비 중입니다...'):
                try:
                    form_data = {
                        'session_id': st.session_state.session_id,
                        'user_message': '모르겠어요'
                    }
                    response = requests.post(f"{BACKEND_URL}/api/chat", data=form_data)

                    if response.status_code == 200:
                        data = response.json()

                        reply_message = data.get('reply', '알겠습니다.')
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': reply_message
                        })

                        if data.get('completed'):
                            st.session_state.collected_data = data
                            st.session_state.page = 'jobs'
                            st.success("✅ 모든 정보를 수집했습니다! 맞춤 채용공고를 찾습니다.")
                            st.balloons()

                        st.rerun()
                    else:
                        try:
                            err_msg = response.json().get('detail', '채팅 처리 중 오류가 발생했습니다.')
                        except Exception:
                            err_msg = f"채팅 처리 중 오류가 발생했습니다. (상태 코드: {response.status_code})"
                        st.error(err_msg)
                except requests.exceptions.RequestException as e:
                    st.error(f"서버와 통신 중 오류가 발생했습니다: {e}")

        st.markdown("---")
        col_prev, col_next = st.columns(2)

        with col_prev:
            if st.button("◀️ 이력서 업로드 화면으로 돌아가기", use_container_width=True):
                st.session_state.page = 'upload'
                st.rerun()

        with col_next:
            if st.button("다음 단계로 (채용공고 매칭 보기) ▶️", use_container_width=True):
                st.session_state.page = 'jobs'
                st.rerun()

    # 3) 채용공고 매칭 페이지
    elif st.session_state.page == 'jobs':
        st.subheader("🎯 맞춤 채용공고 추천")

        if not st.session_state.session_id:
            st.warning("세션 정보가 없습니다. 먼저 이력서를 업로드해주세요.")
            if st.button("이력서 업로드 화면으로 이동", use_container_width=True):
                st.session_state.page = 'upload'
                st.rerun()
            return

        if not st.session_state.job_listings:
            with st.spinner('맞춤 채용공고를 불러오는 중입니다... 🔍'):
                try:
                    form_data = {
                        'session_id': st.session_state.session_id
                    }
                    response = requests.post(f"{BACKEND_URL}/api/search-jobs", data=form_data)

                    if response.status_code == 200:
                        data = response.json()

                        if data.get('jobs') is not None:
                            st.session_state.job_listings = data.get('jobs', [])
                            total = data.get('total', 0)
                            st.success(f"✅ {total}개의 맞춤 채용공고를 찾았습니다!")
                        else:
                            st.error(f"❌ 오류: {data.get('error', '채용공고를 불러올 수 없습니다')}")
                            st.session_state.job_listings = []
                    else:
                        try:
                            err_msg = response.json().get('detail', '채용공고를 불러오는 중 오류가 발생했습니다.')
                        except Exception:
                            err_msg = f"채용공고를 불러오는 중 오류가 발생했습니다. (상태 코드: {response.status_code})"
                        st.error(err_msg)
                except requests.exceptions.RequestException as e:
                    st.error(f"서버와 통신 중 오류가 발생했습니다: {e}")

        col_filters, col_jobs = st.columns([1, 3])

        with col_filters:
            st.markdown("""
            <div class="info-card">
                <h3>🔎 필터 / 내 정보 요약</h3>
            """, unsafe_allow_html=True)

            collected = st.session_state.collected_data or {}
            slots = collected.get('slots', {})
            resume = collected.get('resume', st.session_state.resume_data or {})

            st.markdown("**📌 수집된 주요 정보**", unsafe_allow_html=True)
            st.markdown(f"- 희망 직무: `{slots.get('desired_job', '미입력')}`")
            st.markdown(f"- 희망 지역: `{slots.get('location', '미입력')}`")
            st.markdown(f"- 희망 고용형태: `{slots.get('job_type', '미입력')}`")
            st.markdown(f"- 선호 산업: `{slots.get('industry', '미입력')}`")
            st.markdown(f"- 최소 연봉: `{slots.get('min_salary', '미입력')}`")
            st.markdown(f"- 경력: `{resume.get('experience_years', 0)}년`")

            st.markdown("<br><p class='muted-text'>현재는 필터 UI만 제공되며, 실제 필터링은 백엔드에서 수행합니다.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_jobs:
            jobs = st.session_state.job_listings

            if not jobs:
                st.warning("표시할 채용공고가 없습니다. 조건을 다시 입력하거나, 나중에 다시 시도해 주세요.")
            else:
                st.markdown("### 추천된 채용공고 목록")

                for idx, job in enumerate(jobs):
                    if not isinstance(job, dict):
                        continue

                    title = job.get('title', '제목 없음')
                    company = job.get('company', '회사명 없음')
                    location = job.get('location', '지역 정보 없음')
                    job_type = job.get('job_type_filtered', job.get('job_type', '고용형태 정보 없음'))
                    salary = job.get('salary', '연봉 정보 없음')
                    experience = job.get('experience_level', job.get('experience', '경력 정보 없음'))
                    skills = job.get('skills', [])
                    
                    # 키워드 매칭 정보
                    matched_keywords = job.get('matched_keywords', [])
                    match_count = job.get('match_count', 0)
                    total_keywords = job.get('total_keywords', 5)
                    
                    url = job.get('url', None)
                    source_site = job.get('source', 'Saramin(가정)')

                    # 공고 헤더 - '-' 제거 및 빈 '()' 제거
                    # title, company, job_type에서 '-' 제거
                    title_clean = title.replace('-', '').strip() if title else '제목 없음'
                    company_clean = company.replace('-', '').strip() if company else '회사명 없음'
                    job_type_clean = job_type.replace('-', '').strip() if job_type else ''
                    
                    # 빈 job_type이면 괄호 없이 표시
                    if job_type_clean and job_type_clean != '고용형태 정보 없음':
                        header_text = f"## 🏆 {company_clean} [{title_clean}] ({job_type_clean})"
                    else:
                        header_text = f"## 🏆 {company_clean} [{title_clean}]"
                    
                    st.markdown(header_text)
                    
                    # 키워드 매칭 결과 표시 (매칭된 키워드만 표시)
                    if matched_keywords:
                        # 매칭 개수에 따라 색상 결정
                        if match_count == total_keywords:
                            match_color = "#10b981"  # 초록색 (완벽 매칭)
                            match_bg = "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)"
                        elif match_count >= total_keywords * 0.6:
                            match_color = "#3b82f6"  # 파란색 (양호)
                            match_bg = "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)"
                        else:
                            match_color = "#f59e0b"  # 주황색 (보통)
                            match_bg = "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)"
                        
                        # 매칭된 키워드 태그 생성
                        matched_tags = ""
                        for kw in matched_keywords:
                            matched_tags += f'<span class="job-tag" style="background: {match_bg}; border-color: {match_color};">✓ {kw}</span>'
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%); 
                                    border-radius: 12px; padding: 0.8rem 1rem; margin: 0.6rem 0;
                                    border: 2px solid rgba(167, 139, 250, 0.3);">
                            <div style="font-size: 0.8rem; color: #7c3aed; margin-bottom: 0.4rem; font-weight: 500;">매칭된 키워드:</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.3rem;">
                                {matched_tags}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 스킬 태그
                    if skills:
                        st.markdown("**필요 스킬:**")
                        for s in skills[:8]:
                            st.markdown(f"<span class='job-tag'>{s}</span>", unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # 버튼
                    btn_cols = st.columns([3, 1])
                    
                    with btn_cols[0]:
                        if st.button("🔍 이 공고 상세 보기", key=f"detail_{idx}", use_container_width=True):
                            st.session_state.selected_job = job
                            st.session_state.page = 'job_detail'
                            st.rerun()
                    
                    with btn_cols[1]:
                        if url:
                            st.markdown(f"[원문 링크 열기 🌐]({url})", unsafe_allow_html=True)
                        else:
                            st.markdown("<span class='muted-text'>원문 링크 정보 없음</span>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        col_prev, col_next = st.columns(2)

        with col_prev:
            if st.button("◀️ 정보 수집 단계로 돌아가기", use_container_width=True):
                st.session_state.page = 'chat'
                st.rerun()

        with col_next:
            if st.button("처음부터 다시 시작 🔄", use_container_width=True):
                st.session_state.session_id = None
                st.session_state.chat_history = []
                st.session_state.page = 'upload'
                st.session_state.resume_data = None
                st.session_state.collected_data = None
                st.session_state.job_listings = []
                st.session_state.selected_job = None
                st.rerun()

    # 4) 공고 상세페이지
    elif st.session_state.page == 'job_detail':
        st.subheader("📋 공고 상세정보")

        job = st.session_state.selected_job
        if not job:
            st.warning("상세 정보를 표시할 공고가 없습니다. 먼저 채용공고 목록에서 공고를 선택해주세요.")
            if st.button("채용공고 목록으로 돌아가기", use_container_width=True):
                st.session_state.page = 'jobs'
                st.rerun()
            return

        title = job.get('title', '제목 없음')
        company = job.get('company', '회사명 없음')
        location = job.get('location', '지역 정보 없음')
        job_type = job.get('job_type', '고용형태 정보 없음')
        salary = job.get('salary', '연봉 정보 없음')
        experience = job.get('experience_level', '경력 정보 없음')
        skills = job.get('skills', [])
        url = job.get('url', None)
        source_site = job.get('source', 'Saramin(가정)')
        full_content = job.get('full_content', {})

        col_main, col_side = st.columns([2, 1])

        with col_main:
            st.markdown("""
            <div class="info-card">
                <h3>📌 공고 기본 정보</h3>
            """, unsafe_allow_html=True)

            # '-' 제거 및 빈 값 처리
            title_clean = title.replace('-', '').strip() if title and title != '제목 없음' else '제목 없음'
            company_clean = company.replace('-', '').strip() if company and company != '회사명 없음' else '회사명 없음'
            location_clean = location.replace('-', '').strip() if location and location != '지역 정보 없음' else '지역 정보 없음'
            job_type_clean = job_type.replace('-', '').strip() if job_type and job_type != '고용형태 정보 없음' else '고용형태 정보 없음'
            experience_clean = experience.replace('-', '').strip() if experience and experience != '경력 정보 없음' else '경력 정보 없음'
            salary_clean = salary.replace('-', '').strip() if salary and salary != '연봉 정보 없음' else '연봉 정보 없음'
            
            st.markdown(f"**제목:** {title_clean}")
            st.markdown(f"**회사명:** {company_clean}")
            st.markdown(f"**근무지:** {location_clean}")
            st.markdown(f"**고용형태:** {job_type_clean}")
            st.markdown(f"**경력:** {experience_clean}")
            st.markdown(f"**연봉/급여:** {salary_clean}")
            
            # 채용공고 링크 표시 - jobs.txt에서 파싱한 URL 사용
            if url:
                st.markdown(f"**🔗 채용공고 링크:** [원문 공고 페이지 열기]({url})")
            else:
                st.markdown("**🔗 채용공고 링크:** 링크 정보 없음")

            st.markdown("</div>", unsafe_allow_html=True)

            if full_content:
                section_map = {
                    "job_description": "🧭 주요 업무",
                    "requirements": "✅ 자격 요건",
                    "preferred": "✨ 우대 사항",
                    "conditions": "💼 근무 조건",
                    "benefits": "🎁 급여 및 복리후생",
                    "process": "🧪 전형 절차",
                    "how_to_apply": "📬 지원 방법",
                    "etc": "📎 기타 참고사항"
                }

                st.markdown("### 📄 공고 상세 내용")

                for key, title_label in section_map.items():
                    text = full_content.get(key, "").strip()
                    if not text:
                        continue

                    st.markdown(f"""
                    <div class="section-card">
                        <h4>{title_label}</h4>
                    """, unsafe_allow_html=True)

                    if "\n" in text or "·" in text or "-" in text:
                        lines = [line.strip() for line in text.splitlines() if line.strip()]
                        is_bulleted = any(line.startswith(("·", "-", "*", "•")) for line in lines)
                        if is_bulleted:
                            st.markdown("<ul>", unsafe_allow_html=True)
                            for line in lines:
                                clean_line = line.lstrip("·-*• ").strip()
                                st.markdown(f"<li>{clean_line}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                        else:
                            for line in lines:
                                st.markdown(f"- {line}")
                    else:
                        st.markdown(text)

                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="section-card">
                    <h4>📄 상세 텍스트 정보</h4>
                    <p>이 공고는 아직 구조화된 상세 텍스트 정보가 정리되어 있지 않습니다.<br>
                    추후 TXT 파싱/크롤링 로직이 정교해지면, 여기서 '주요업무/자격요건/근무조건/복리후생/전형절차/지원방법' 등으로 자동 분리해서 보여줄 수 있습니다.</p>
                </div>
                """, unsafe_allow_html=True)

        with col_side:
            st.markdown("""
            <div class="site-card">
                <h3 style="font-size: 1rem; margin-bottom: 0.5rem;">🌐 공고 출처</h3>
            """, unsafe_allow_html=True)

            st.markdown(f"<span class='site-badge'>{source_site}</span>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # 채용공고 링크를 클릭 가능한 버튼으로 표시
            if url:
                st.markdown(f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <a href="{url}" target="_blank" style="
                        display: inline-block;
                        padding: 0.8rem 2rem;
                        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 12px;
                        font-weight: 600;
                        font-size: 0.95rem;
                        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
                        transition: all 0.3s ease;
                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 18px rgba(139, 92, 246, 0.4)';" 
                       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(139, 92, 246, 0.3)';">
                        🔗 원문 공고 페이지 열기
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # 링크 URL도 텍스트로 표시
                st.markdown(f"""
                <div style="margin-top: 0.5rem; padding: 0.5rem; background: #f3f0ff; border-radius: 8px; word-break: break-all;">
                    <small style="color: #6d28d9; font-size: 0.75rem;">{url}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<span class='muted-text'>원문 링크 정보 없음</span>", unsafe_allow_html=True)

            st.markdown("<br><div class='muted-text'>원문 공고 페이지를 열어 실제 지원 조건, 마감일, 상세 내용을 반드시 다시 확인해주세요.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("""
            <div class="info-card">
                <h3>🧠 이 공고로 자기소개서 작성</h3>
                <p>이 공고를 바탕으로, 이력서와 수집된 정보를 활용해 자기소개서를 만들 수 있습니다.</p>
                <p class="muted-text">지원동기/성장과정/입사 후 포부/강점 등 항목을 자유롭게 설정할 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-card">
                <h3>🎤 이 공고로 모의면접 시작</h3>
                <p>이 공고를 바탕으로, AI 면접관과 모의면접을 진행할 수 있습니다.</p>
                <p class="muted-text">5개의 질문에 답변하고, 각 답변에 대한 평가와 종합 피드백을 받을 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col_prev, col_mid, col_next = st.columns(3)

        with col_prev:
            if st.button("◀️ 채용공고 목록으로 돌아가기", use_container_width=True):
                st.session_state.page = 'jobs'
                st.rerun()

        with col_mid:
            if st.button("📝 이 공고로 자기소개서 작성하기", use_container_width=True):
                st.session_state.page = 'cover_letter'
                st.rerun()
        
        with col_next:
            if st.button("🎤 이 공고로 모의면접 시작하기", use_container_width=True):
                st.session_state.page = 'interview'
                st.rerun()

    # 5) 자기소개서 작성 페이지
    elif st.session_state.page == 'cover_letter':
        st.subheader("✍️ 자기소개서 작성")

        job = st.session_state.selected_job
        if not job:
            st.warning("자기소개서를 작성할 공고가 선택되지 않았습니다. 먼저 채용공고 상세페이지로 이동해주세요.")
            if st.button("채용공고 목록으로 돌아가기", use_container_width=True):
                st.session_state.page = 'jobs'
                st.rerun()
            return

        title = job.get('title', '제목 없음')
        company = job.get('company', '회사명 없음')
        url = job.get('url', None)

        st.markdown(f"""
        <div class="info-card">
            <h3>📌 선택한 공고</h3>
            <p><strong>제목:</strong> {title}</p>
            <p><strong>회사:</strong> {company}</p>
        """, unsafe_allow_html=True)

        if url:
            st.markdown(f"<p><a href='{url}' target='_blank'>🔗 원문 공고 페이지 열기</a></p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 기존에 생성된 자기소개서가 있으면 표시
        if 'cover_letter' in st.session_state and st.session_state.cover_letter:
            st.markdown("---")
            st.markdown("### 📄 생성된 자기소개서")
            cover_letter = st.session_state.cover_letter
            
            for section, content_data in cover_letter.items():
                st.markdown(f"### {section}")
                
                # 한 단락으로 표시 (문자열) - 이미 첨삭된 결과
                section_key = f"section_{section}"
                st.text_area(
                    f"{section} (수정 가능)",
                    value=str(content_data),
                    height=200,
                    key=section_key
                )
                
                st.divider()
            
            # 다운로드용 전체 텍스트 생성
            full_text_parts = []
            for section, content_data in cover_letter.items():
                # 현재 수정된 값 가져오기
                section_key = f"section_{section}"
                full_section = st.session_state.get(section_key, str(content_data))
                full_text_parts.append(f"【{section}】\n{full_section}")
            full_text = "\n\n".join(full_text_parts)
            st.download_button(
                "📥 자기소개서 다운로드 (TXT)",
                data=full_text,
                file_name=f"자기소개서_{job['company']}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("### ✍️ 새로운 자기소개서 작성")
        
        st.markdown("""
        <div class="info-card">
            <h3>🧩 자기소개서 작성 안내</h3>
            <p>아래에 작성하고 싶은 항목을 한 줄에 하나씩 입력하면, 각 항목별로 자기소개서 내용을 생성합니다.</p>
            <p class="muted-text">예: 지원 동기, 성장 과정, 입사 후 포부, 자신의 강점, 직무 역량, 성격의 장단점 등</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📝 자기소개서 항목")

        cover_letter_sections = st.text_area(
            "작성할 항목을 입력하세요 (한 줄에 하나씩)",
            placeholder="예:\n지원 동기\n성장 과정\n입사 후 포부\n자신의 강점",
            height=150
        )

        if st.button("🤖 AI로 자기소개서 생성하기", type="primary", use_container_width=True):
            if cover_letter_sections:
                sections = [s.strip() for s in cover_letter_sections.split('\n') if s.strip()]

                with st.spinner('AI가 자기소개서를 작성하고 있습니다. ✍️'):
                    try:
                        form_data = {
                            'session_id': st.session_state.session_id,
                            'job_title': job['title'],
                            'company_name': job['company'],
                            'sections': json.dumps(sections, ensure_ascii=False)
                        }
                        response = requests.post(f"{BACKEND_URL}/api/generate-cover-letter", data=form_data)

                        if response.status_code == 200:
                            data = response.json()

                            if data.get('success'):
                                st.success("✅ 자기소개서 생성 완료!")

                                cover_letter = data.get('cover_letter', {})
                                # 세션 상태에 자기소개서 저장
                                st.session_state.cover_letter = cover_letter

                                for section, content_data in cover_letter.items():
                                    st.markdown(f"### {section}")
                                    
                                    # 한 단락으로 표시 (문자열) - 이미 첨삭된 결과
                                    section_key = f"section_{section}"
                                    st.text_area(
                                        f"{section} (수정 가능)",
                                        value=str(content_data),
                                        height=200,
                                        key=section_key
                                    )
                                    
                                    st.divider()

                                # 다운로드용 전체 텍스트 생성 (현재 수정된 값 사용)
                                full_text_parts = []
                                for section, content_data in cover_letter.items():
                                    section_key = f"section_{section}"
                                    full_section = st.session_state.get(section_key, str(content_data))
                                    full_text_parts.append(f"【{section}】\n{full_section}")
                                full_text = "\n\n".join(full_text_parts)
                                st.download_button(
                                    "📥 자기소개서 다운로드 (TXT)",
                                    data=full_text,
                                    file_name=f"자기소개서_{job['company']}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ 오류: {data.get('error', '자기소개서를 생성할 수 없습니다')}")
                        else:
                            try:
                                err_msg = response.json().get('detail', '자기소개서 생성 중 오류가 발생했습니다.')
                            except Exception:
                                err_msg = f"자기소개서 생성 중 오류가 발생했습니다. (상태 코드: {response.status_code})"
                            st.error(err_msg)
                    except requests.exceptions.RequestException as e:
                        st.error(f"서버와 통신 중 오류가 발생했습니다: {e}")
            else:
                st.warning("먼저 작성할 항목을 입력해주세요.")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("◀️ 공고 상세페이지로 돌아가기", use_container_width=True):
                st.session_state.page = 'job_detail'
                st.rerun()

        with col2:
            if st.button("🔄 처음부터 다시 시작", use_container_width=True):
                st.session_state.session_id = None
                st.session_state.chat_history = []
                st.session_state.page = 'upload'
                st.session_state.resume_data = None
                st.session_state.collected_data = None
                st.session_state.job_listings = []
                st.session_state.selected_job = None
                st.session_state.interview_data = None
                st.session_state.current_question_index = 0
                st.rerun()

    # 6) 모의면접 페이지
    elif st.session_state.page == 'interview':
        st.subheader("🎤 모의면접")

        job = st.session_state.selected_job
        if not job:
            st.warning("모의면접을 진행할 공고가 선택되지 않았습니다. 먼저 채용공고 상세페이지로 이동해주세요.")
            if st.button("채용공고 목록으로 돌아가기", use_container_width=True):
                st.session_state.page = 'jobs'
                st.rerun()
            return

        title = job.get('title', '제목 없음')
        company = job.get('company', '회사명 없음')

        # 면접 데이터가 없으면 백엔드에서 상태 확인
        if not st.session_state.interview_data:
            try:
                response = requests.get(f"{BACKEND_URL}/api/interview-status/{st.session_state.session_id}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('interview'):
                        st.session_state.interview_data = data.get('interview')
            except Exception:
                pass  # 면접 데이터가 없으면 새로 시작
        
        # 면접 시작 또는 상태 확인
        if not st.session_state.interview_data:
            st.markdown(f"""
            <div class="info-card">
                <h3>📌 선택한 공고</h3>
                <p><strong>제목:</strong> {title}</p>
                <p><strong>회사:</strong> {company}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="info-card">
                <h3>🎤 모의면접 안내</h3>
                <p>AI 면접관이 5개의 질문을 드립니다. 각 질문에 답변하면 즉시 평가를 받을 수 있습니다.</p>
                <p class="muted-text">모든 질문에 답변하면 종합 평가와 피드백을 받을 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🎤 모의면접 시작하기", type="primary", use_container_width=True):
                with st.spinner('면접 질문을 생성하고 있습니다... 🤔'):
                    try:
                        form_data = {
                            'session_id': st.session_state.session_id,
                            'job_title': job['title'],
                            'company_name': job['company']
                        }
                        response = requests.post(f"{BACKEND_URL}/api/start-interview", data=form_data)

                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                st.session_state.interview_data = data.get('interview', {})
                                st.session_state.current_question_index = 0
                                st.success("✅ 면접이 시작되었습니다!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ 오류: {data.get('error', '면접을 시작할 수 없습니다')}")
                        else:
                            try:
                                err_msg = response.json().get('detail', '면접 시작 중 오류가 발생했습니다.')
                            except Exception:
                                err_msg = f"면접 시작 중 오류가 발생했습니다. (상태 코드: {response.status_code})"
                            st.error(err_msg)
                    except requests.exceptions.RequestException as e:
                        st.error(f"서버와 통신 중 오류가 발생했습니다: {e}")
        else:
            # 면접 진행 중
            interview = st.session_state.interview_data
            questions = interview.get('questions', [])
            answers = interview.get('answers', [])
            completed = interview.get('completed', False)
            
            # 완료되었으면 current_question_index를 -1로 설정하여 종합 평가 화면 표시
            if completed:
                current_idx = -1
            else:
                current_idx = st.session_state.current_question_index

            # 진행 상황 표시
            total_questions = len(questions)
            answered_count = len(answers)
            progress = (answered_count / total_questions * 100) if total_questions > 0 else 0

            st.markdown(f"""
            <div class="info-card">
                <h3>📊 면접 진행 상황</h3>
                <p><strong>진행률:</strong> {answered_count}/{total_questions}개 질문 완료 ({progress:.0f}%)</p>
                <p><strong>공고:</strong> {title} - {company}</p>
            </div>
            """, unsafe_allow_html=True)

            if completed or current_idx == -1:
                # 면접 완료 - 종합 결과 표시
                st.success("🎉 모든 면접 질문에 답변하셨습니다!")
                
                overall_eval = interview.get('overall_evaluation')
                if overall_eval:
                    st.markdown("### 📋 종합 평가 결과")
                    
                    # 전체 평가 요약 (summary 우선, 없으면 overall_impression, 없으면 final_comment)
                    summary = overall_eval.get('summary', overall_eval.get('overall_impression', overall_eval.get('final_comment', '')))
                    if summary:
                        st.markdown("""
                        <div class="section-card">
                            <h4>💭 전체 평가 요약</h4>
                        """, unsafe_allow_html=True)
                        st.markdown(summary)
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("""
                    <div class="section-card">
                        <h4>✨ 강점</h4>
                    """, unsafe_allow_html=True)
                    strengths = overall_eval.get('strengths', [])
                    if strengths:
                        for strength in strengths:
                            st.markdown(f"- {strength}")
                    else:
                        st.markdown("- 강점 정보가 없습니다.")
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("""
                    <div class="section-card">
                        <h4>🔧 개선이 필요한 부분</h4>
                    """, unsafe_allow_html=True)
                    improvements = overall_eval.get('improvements', [])
                    if improvements:
                        for improvement in improvements:
                            st.markdown(f"- {improvement}")
                    else:
                        st.markdown("- 개선점 정보가 없습니다.")
                    st.markdown("</div>", unsafe_allow_html=True)

                    final_score = overall_eval.get('final_score', overall_eval.get('total_score', 0))
                    st.markdown(f"""
                    <div class="section-card">
                        <h4>📊 종합 점수</h4>
                        <p><strong>{final_score:.1f}/100점</strong></p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("""
                    <div class="section-card">
                        <h4>💬 최종 의견</h4>
                    """, unsafe_allow_html=True)
                    st.markdown(overall_eval.get('final_comment', '의견이 없습니다.'))
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("""
                    <div class="section-card">
                        <h4>🎯 채용 추천도</h4>
                    """, unsafe_allow_html=True)
                    st.markdown(overall_eval.get('recommendation', '추천도 정보가 없습니다.'))
                    st.markdown("</div>", unsafe_allow_html=True)

                # 질문별 답변 및 평가 보기
                st.markdown("### 📝 질문별 답변 및 평가")
                for i, question in enumerate(questions):
                    # question이 문자열인 경우 처리
                    if isinstance(question, str):
                        question_text = question
                    else:
                        question_text = question.get('question', str(question))
                    
                    # answers가 리스트인 경우 인덱스로 접근
                    answer_text = ""
                    evaluation = {}
                    if i < len(answers):
                        if isinstance(answers[i], dict):
                            answer_text = answers[i].get('answer', '')
                            evaluation = answers[i].get('evaluation', {})
                        else:
                            answer_text = str(answers[i])
                    
                    # evaluations가 있는 경우
                    evaluations_list = interview.get('evaluations', [])
                    if i < len(evaluations_list) and evaluations_list[i]:
                        evaluation = evaluations_list[i]
                    
                    with st.expander(f"질문 {i+1}: {question_text[:50]}...", expanded=(i == 0)):
                        st.markdown(f"**질문:** {question_text}")
                        
                        if answer_text:
                            st.markdown(f"**답변:** {answer_text}")
                            
                            if evaluation:
                                score = evaluation.get('score', 0)
                                
                                st.markdown("**평가 점수:**")
                                st.markdown(f"**점수:** {score}/100점")
                                st.markdown(f"**피드백:** {evaluation.get('feedback', '피드백이 없습니다.')}")
                                
                                if evaluation.get('strengths'):
                                    st.markdown("**강점:**")
                                    for strength in evaluation.get('strengths', []):
                                        st.markdown(f"- {strength}")
                                
                                if evaluation.get('improvements'):
                                    st.markdown("**개선점:**")
                                    for improvement in evaluation.get('improvements', []):
                                        st.markdown(f"- {improvement}")
                        else:
                            st.markdown("*아직 답변하지 않은 질문입니다.*")

            elif not completed:
                # 면접 진행 중 - 현재 질문 표시
                if current_idx >= 0 and current_idx < len(questions):
                    current_question = questions[current_idx]
                    # question이 문자열인 경우 처리
                    if isinstance(current_question, str):
                        question_text = current_question
                    else:
                        question_text = current_question.get('question', str(current_question))
                    
                    st.markdown(f"""
                    <div class="section-card">
                        <h4>질문 {current_idx + 1}/{total_questions}</h4>
                        <p><strong>질문:</strong> {question_text}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.form(key=f'interview_answer_form_{current_idx}', clear_on_submit=False):
                        answer_text = st.text_area(
                            "답변을 입력하세요",
                            height=200,
                            placeholder="질문에 대한 답변을 작성해주세요. 구체적이고 명확하게 작성하면 더 좋은 평가를 받을 수 있습니다.",
                            key=f'answer_{current_idx}'
                        )
                        
                        submit_button = st.form_submit_button("답변 제출 📤", use_container_width=True)

                    if submit_button and answer_text:
                        with st.spinner('답변을 평가하고 있습니다... 🤔'):
                            try:
                                form_data = {
                                    'session_id': st.session_state.session_id,
                                    'question_index': current_idx,
                                    'answer': answer_text
                                }
                                response = requests.post(f"{BACKEND_URL}/api/submit-answer", data=form_data)

                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get('success'):
                                        # 면접 데이터 업데이트
                                        st.session_state.interview_data = data.get('interview', st.session_state.interview_data)
                                        
                                        answer_data = data.get('answer', {})
                                        evaluation = answer_data.get('evaluation', {})
                                        
                                        if evaluation:
                                            st.success("✅ 답변이 제출되었고 평가가 완료되었습니다!")
                                            
                                            # 평가 결과 표시
                                            score = evaluation.get('score', 0)
                                            
                                            st.markdown("### 📊 평가 결과")
                                            st.markdown(f"**점수:** {score}/100점")
                                            st.markdown(f"**피드백:** {evaluation.get('feedback', '피드백이 없습니다.')}")
                                            
                                            # 강점 표시
                                            strengths = evaluation.get('strengths', [])
                                            if strengths:
                                                st.markdown("**✅ 강점:**")
                                                for strength in strengths:
                                                    st.markdown(f"- {strength}")
                                            
                                            # 개선점 표시
                                            improvements = evaluation.get('improvements', [])
                                            if improvements:
                                                st.markdown("**🔧 개선점:**")
                                                for improvement in improvements:
                                                    st.markdown(f"- {improvement}")
                                        
                                        # 다음 질문으로 이동 또는 완료
                                        if data.get('completed'):
                                            # 모든 질문 완료 - 면접 상태를 다시 가져와서 최신 데이터로 업데이트
                                            try:
                                                status_response = requests.get(f"{BACKEND_URL}/api/interview-status/{st.session_state.session_id}")
                                                if status_response.status_code == 200:
                                                    status_data = status_response.json()
                                                    if status_data.get('success') and status_data.get('interview'):
                                                        st.session_state.interview_data = status_data.get('interview')
                                            except Exception:
                                                pass  # 상태 가져오기 실패해도 계속 진행
                                            # 완료 화면 표시를 위해 current_question_index를 -1로 설정
                                            st.session_state.current_question_index = -1
                                            st.balloons()
                                        else:
                                            st.session_state.current_question_index = current_idx + 1
                                        
                                        st.rerun()
                                    else:
                                        st.error(f"❌ 오류: {data.get('error', '답변 제출 중 오류가 발생했습니다')}")
                                else:
                                    try:
                                        err_msg = response.json().get('detail', '답변 제출 중 오류가 발생했습니다.')
                                    except Exception:
                                        err_msg = f"답변 제출 중 오류가 발생했습니다. (상태 코드: {response.status_code})"
                                    st.error(err_msg)
                            except requests.exceptions.RequestException as e:
                                st.error(f"서버와 통신 중 오류가 발생했습니다: {e}")

                # 이전/다음 질문 네비게이션
                st.markdown("---")
                col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
                
                with col_nav1:
                    if current_idx > 0 and st.button("◀️ 이전 질문", use_container_width=True):
                        st.session_state.current_question_index = current_idx - 1
                        st.rerun()
                
                with col_nav2:
                    if st.button("📋 모든 질문 보기", use_container_width=True):
                        st.session_state.current_question_index = -1  # 모든 질문 보기 모드
                        st.rerun()
                
                with col_nav3:
                    if current_idx < len(questions) - 1 and st.button("다음 질문 ▶️", use_container_width=True):
                        st.session_state.current_question_index = current_idx + 1
                        st.rerun()

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("◀️ 공고 상세페이지로 돌아가기", use_container_width=True):
                st.session_state.page = 'job_detail'
                st.rerun()

        with col2:
            if st.button("🔄 처음부터 다시 시작", use_container_width=True):
                st.session_state.session_id = None
                st.session_state.chat_history = []
                st.session_state.page = 'upload'
                st.session_state.resume_data = None
                st.session_state.collected_data = None
                st.session_state.job_listings = []
                st.session_state.selected_job = None
                st.session_state.interview_data = None
                st.session_state.current_question_index = 0
                st.rerun()

# ============================================================
# 3. 진입점: 로그인 여부에 따라 페이지 분기
# ============================================================

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.login_type = None

    if st.session_state.get('logged_in', False):
        run_main_app()
    else:
        run_login_page()


if __name__ == '__main__':
    main()
