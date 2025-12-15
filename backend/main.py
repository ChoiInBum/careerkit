"""
FastAPI 메인 애플리케이션
리팩토링된 버전 - 모듈화 및 try-except 개선
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
import asyncio

# 모듈 import (src 패키지에서)
from src.resume_parser import extract_text_from_pdf_bytes, openai_extract_resume, heuristic_extract_resume
from src.job_parser import load_jobs_from_txt
from src.vector_store import (
    initialize_vector_store_components, 
    initialize_vector_store as init_vector_store,
    add_resume_to_vector_store
)
from src.retriever import retrieve_similar_jobs
from src.reranker import rerank_jobs
from src.chat_handler import natural_conversation_collect_info
from src.llm_clients import USE_OPENAI
from src.cover_letter_generator import generate_cover_letter, review_and_improve_cover_letter
from src.interview_generator import (
    generate_interview_questions,
    evaluate_answer,
    generate_overall_evaluation
)
import json

# 세션 저장소
SESSIONS = {}

# ============================================
# FastAPI 앱 초기화
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 lifespan 이벤트 핸들러"""
    print("\n🚀 앱 시작 중...")
    
    # 벡터 스토어 컴포넌트 초기화 (컬렉션과 모델만 초기화, 데이터는 기존 것 사용)
    print("📊 벡터 스토어 컴포넌트 초기화 시작...")
    if initialize_vector_store_components(force_reload=False):
        print("✅ 벡터 스토어 컴포넌트 초기화 완료")
        
        # 기존 벡터 스토어에 채용공고 데이터가 있는지 확인
        from src.vector_store import VECTOR_STORE as VS
        if VS is not None:
            try:
                doc_count = VS.count()
                if doc_count > 0:
                    print(f"✅ 기존 벡터 스토어 사용 중 (문서 수: {doc_count}개)")
                else:
                    # 데이터가 없으면 처음 한 번만 초기화
                    print("📊 벡터 스토어가 비어있습니다. 채용공고 초기화 시작...")
                    try:
                        jobs = load_jobs_from_txt("jobs.txt")
                        if jobs:
                            print(f"✅ {len(jobs)}개의 채용공고를 로드했습니다.")
                            print("⏳ 벡터 스토어에 채용공고 저장 중... (이 작업은 몇 분이 걸릴 수 있습니다)")
                            # window + stride 방식으로 청킹 (window_size=500, stride=200)
                            success = await asyncio.to_thread(init_vector_store, jobs, chunk_size=0, force_reload=False, window_size=500, stride=200)
                            if success:
                                try:
                                    final_count = VS.count()
                                    print(f"✅ 벡터 스토어 초기화 완료! (문서 수: {final_count}개)")
                                except Exception as e:
                                    print(f"⚠️  벡터 스토어 카운트 확인 실패: {e}")
                            else:
                                print("⚠️  벡터 스토어에 데이터 저장 실패")
                        else:
                            print("⚠️  채용공고를 불러올 수 없습니다. jobs.txt 파일을 확인하세요.")
                    except Exception as e:
                        print(f"❌ 벡터 스토어 초기화 중 오류 발생: {e}")
                        import traceback
                        traceback.print_exc()
            except Exception as e:
                print(f"⚠️  벡터 스토어 상태 확인 중 오류: {e}")
    else:
        print("⚠️  벡터 스토어 컴포넌트 초기화 실패")
    
    yield
    
    print("\n🛑 앱 종료 중...")

app = FastAPI(title="Resume Chatbot API", lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# API 엔드포인트
# ============================================
async def _upload_resume_handler(file: UploadFile):
    """이력서 파일 업로드 및 파싱 공통 핸들러"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다.")
    
    # 파일 읽기
    file_bytes = await file.read()
    
    # 텍스트 추출
    if file.filename.endswith('.pdf'):
        text = extract_text_from_pdf_bytes(file_bytes)
    elif file.filename.endswith('.txt'):
        text = file_bytes.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. PDF 또는 TXT만 가능합니다.")
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다.")
    
    # 이력서 정보 추출
    if USE_OPENAI:
        resume = openai_extract_resume(text)
    else:
        resume = heuristic_extract_resume(text)
    
    # 세션 생성
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "resume": resume,
        "chat_history": [],
        "slots": {}
    }
    
    # 이력서를 벡터 스토어에 저장
    try:
        add_resume_to_vector_store(resume, session_id)
    except Exception as e:
        print(f"⚠️  이력서 벡터 스토어 저장 중 오류: {e}")
    
    # 환영 메시지 생성
    name = resume.get('name', '사용자')
    reply = f"안녕하세요, {name}님! 이력서를 성공적으로 분석했습니다. 이제 몇 가지 질문을 드려서 맞춤형 채용공고를 찾아드리겠습니다. 원하시는 직무는 무엇인가요?"
    
    return {
        "session_id": session_id,
        "resume": resume,
        "reply": reply
    }


@app.post("/api/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    """이력서 파일 업로드 및 파싱 (클라이언트 호환용)"""
    return await _upload_resume_handler(file)


@app.post("/api/upload-resume")
async def upload_resume_endpoint(file: UploadFile = File(...)):
    """이력서 파일 업로드 및 파싱"""
    return await _upload_resume_handler(file)


@app.post("/api/chat")
async def chat_endpoint(session_id: str = Form(...), user_message: str = Form(...)):
    """채팅 메시지 처리"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 사용자 메시지를 채팅 히스토리에 추가
    session["chat_history"].append({"from": "user", "text": user_message})
    
    if USE_OPENAI:
        # LLM을 사용한 자연스러운 대화
        result = natural_conversation_collect_info(
            session["resume"],
            session["chat_history"],
            session["slots"]
        )
        
        response_message = result.get("response", "알겠습니다.")
        slots_updated = result.get("slots_updated", {})
        completed = result.get("completed", False)
        
        # 슬롯 업데이트
        for key, value in slots_updated.items():
            if value is not None and value != "":
                session["slots"][key] = value
        
        # 응답을 채팅 히스토리에 추가
        session["chat_history"].append({"from": "system", "text": response_message})
        
        if completed:
            return {
                "reply": response_message,
                "completed": True,
                "slots": session["slots"],
                "resume": session["resume"]
            }
        else:
            return {
                "reply": response_message,
                "completed": False
            }
    else:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API가 필요합니다. OPENAI_API_KEY 환경 변수를 설정하세요."
        )


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """세션 정보 조회"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    return session


@app.post("/api/search-jobs")
async def search_jobs_endpoint(
    session_id: str = Form(...),
    desired_job: str = Form(""),
    location: str = Form(""),
    job_type: str = Form(""),
    company_size: str = Form("")
):
    """채용공고 검색 - Retriever + Reranker 기반 검색"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 세션에서 이력서와 챗봇 정보 가져오기
    resume = session.get("resume", {})
    slots = session.get("slots", {})
    
    # 사용자가 입력한 조건이 있으면 slots에 추가
    if desired_job:
        slots["desired_job"] = desired_job
    if location:
        slots["location"] = location
    if job_type:
        slots["job_type"] = job_type
    if company_size:
        slots["company_size"] = company_size
    
    try:
        # 채용공고 전체 데이터 로드 (먼저 로드)
        all_jobs = load_jobs_from_txt("jobs.txt")
        if not all_jobs:
            raise HTTPException(
                status_code=500, 
                detail="채용공고를 불러올 수 없습니다. jobs.txt 파일을 확인하세요."
            )
        
        print(f"📊 로드된 채용공고 수: {len(all_jobs)}")
        print(f"📝 이력서 정보: {resume.get('name', 'N/A')}, 스킬: {resume.get('skills', [])[:3]}")
        print(f"💬 챗봇 정보: {slots}")
        
        # 벡터 스토어 상태 확인 - 모듈에서 직접 가져오기
        from src.vector_store import VECTOR_STORE as VS, is_vector_store_initialized
        
        if not is_vector_store_initialized():
            error_msg = "VECTOR_STORE가 초기화되지 않았습니다. 앱을 재시작하거나 /api/initialize-vector-store 엔드포인트를 호출하세요."
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # VECTOR_STORE가 None이 아닌지 명시적으로 확인
        if VS is None:
            error_msg = "VECTOR_STORE가 None입니다. 벡터 스토어 초기화가 필요합니다."
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        try:
            doc_count = VS.count()
            print(f"📊 벡터 스토어 문서 수: {doc_count}개")
            if doc_count == 0:
                error_msg = "벡터 스토어가 비어있습니다. /api/initialize-vector-store 엔드포인트를 호출하여 데이터를 저장하세요."
                print(f"❌ {error_msg}")
                raise HTTPException(status_code=500, detail=error_msg)
        except AttributeError as e:
            error_msg = f"VECTOR_STORE에 count() 메서드가 없습니다: {e}"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        except Exception as e:
            error_msg = f"벡터 스토어 상태 확인 중 오류: {e}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Step 1: Retriever - 이력서와 챗봇 정보를 기반으로 유사 공고 10개 추출
        print("\n" + "="*80)
        print("🔍 Step 1: Retriever 실행 중...")
        print("="*80)
        retrieved_results = retrieve_similar_jobs(resume, slots, top_k=10)
        print(f"\n✅ Retriever 결과: {len(retrieved_results)}개 공고 추출")
        
        if not retrieved_results:
            error_msg = "Retriever가 결과를 반환하지 않았습니다. 검색 조건을 확인하거나 벡터 스토어를 확인하세요."
            print(f"❌ {error_msg}")
            print(f"   - 챗봇 정보: {slots}")
            print(f"   - 이력서 정보: {resume.get('name', 'N/A')}")
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Step 2: Reranker - 추출된 공고들을 정밀하게 재순위화
        print("\n" + "="*80)
        print("🎯 Step 2: Reranker 실행 중...")
        print("="*80)
        reranked_jobs = rerank_jobs(resume, slots, retrieved_results, all_jobs)
        print(f"\n✅ Reranker 결과: {len(reranked_jobs)}개 공고 재순위화 완료")
        
        if not reranked_jobs:
            error_msg = "Reranker가 결과를 반환하지 않았습니다. 검색 결과를 확인하세요."
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        print("\n" + "="*80)
        print(f"✅ 최종 검색 완료: {len(reranked_jobs)}개 공고 중 상위 10개 반환")
        print("="*80 + "\n")
        
        return {
            "jobs": reranked_jobs[:10],  # 상위 10개만 반환
            "total": len(reranked_jobs)
        }
        
    except HTTPException:
        # HTTPException은 그대로 전달
        raise
    except Exception as e:
        error_msg = f"채용공고 검색 중 오류 발생: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/generate-cover-letter")
async def generate_cover_letter_endpoint(
    session_id: str = Form(...),
    job_title: str = Form(...),
    company_name: str = Form(...),
    sections: str = Form("")
):
    """자기소개서 생성"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 채용공고 정보 가져오기
    try:
        jobs = load_jobs_from_txt("jobs.txt")
        job_info = None
        
        # 제목과 회사명으로 채용공고 찾기
        for job in jobs:
            if job.get('title') == job_title and job.get('company') == company_name:
                job_info = job
                # load_jobs_from_txt 형식에 맞게 필드 매핑
                if 'work' not in job_info:
                    job_info['work'] = job_info.get('description', '')
                if 'requirements' not in job_info:
                    job_info['requirements'] = ' '.join(job_info.get('requirements', [])) if isinstance(job_info.get('requirements'), list) else job_info.get('requirements', '')
                break
        
        # 채용공고를 찾지 못한 경우 기본 정보로 생성
        if not job_info:
            job_info = {
                "title": job_title,
                "company": company_name,
                "work": "",
                "requirements": "",
                "conditions": "",
                "benefits": ""
            }
    except Exception as e:
        print(f"⚠️  채용공고 정보를 가져오는 중 오류: {e}")
        # 기본 정보로 생성
        job_info = {
            "title": job_title,
            "company": company_name,
            "work": "",
            "requirements": "",
            "conditions": "",
            "benefits": ""
        }
    
    # 섹션 목록 파싱
    section_list = []
    if sections:
        try:
            section_list = json.loads(sections)
        except Exception:
            # JSON 파싱 실패 시 줄바꿈으로 분리
            section_list = [s.strip() for s in sections.split('\n') if s.strip()]
    
    # 자기소개서 생성
    try:
        resume = session.get("resume", {})
        chat_history = session.get("chat_history", [])
        
        cover_letter = generate_cover_letter(
            resume=resume,
            job_info=job_info,
            sections=section_list if section_list else None,
            chat_history=chat_history
        )
        
        # 세션에 자기소개서 저장
        session["cover_letter"] = cover_letter
        
        return {
            "success": True,
            "cover_letter": cover_letter
        }
    except Exception as e:
        print(f"❌ 자기소개서 생성 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"자기소개서 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/review-cover-letter")
async def review_cover_letter_endpoint(
    session_id: str = Form(...),
    section_name: str = Form(...),
    cover_letter_text: str = Form(...),
    job_title: str = Form(""),
    company_name: str = Form("")
):
    """자기소개서 첨삭 및 개선 (GPT-4o 사용)"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 채용공고 정보 가져오기
    job_info = None
    if job_title and company_name:
        try:
            jobs = load_jobs_from_txt("jobs.txt")
            for job in jobs:
                if job.get('title') == job_title and job.get('company') == company_name:
                    job_info = job
                    if 'work' not in job_info:
                        job_info['work'] = job_info.get('description', '')
                    if 'requirements' not in job_info:
                        job_info['requirements'] = ' '.join(job_info.get('requirements', [])) if isinstance(job_info.get('requirements'), list) else job_info.get('requirements', '')
                    break
        except Exception as e:
            print(f"⚠️  채용공고 정보를 가져오는 중 오류: {e}")
    
    # 채용공고 정보가 없으면 기본값 사용
    if not job_info:
        job_info = {
            "title": job_title or "N/A",
            "company": company_name or "N/A",
            "work": "",
            "requirements": ""
        }
    
    try:
        resume = session.get("resume", {})
        
        # 자기소개서 첨삭 실행
        review_result = review_and_improve_cover_letter(
            cover_letter_text=cover_letter_text,
            section_name=section_name,
            resume=resume,
            job_info=job_info
        )
        
        return {
            "success": True,
            "review": review_result
        }
    except Exception as e:
        print(f"❌ 자기소개서 첨삭 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"자기소개서 첨삭 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/start-interview")
async def start_interview_endpoint(
    session_id: str = Form(...),
    job_title: str = Form(...),
    company_name: str = Form(...)
):
    """면접 시작"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 채용공고 정보 가져오기
    try:
        jobs = load_jobs_from_txt("jobs.txt")
        job_info = None
        
        # 제목과 회사명으로 채용공고 찾기
        for job in jobs:
            if job.get('title') == job_title and job.get('company') == company_name:
                job_info = job
                # load_jobs_from_txt 형식에 맞게 필드 매핑
                if 'work' not in job_info:
                    job_info['work'] = job_info.get('description', '')
                if 'requirements' not in job_info:
                    job_info['requirements'] = ' '.join(job_info.get('requirements', [])) if isinstance(job_info.get('requirements'), list) else job_info.get('requirements', '')
                break
        
        # 채용공고를 찾지 못한 경우 기본 정보로 생성
        if not job_info:
            job_info = {
                "title": job_title,
                "company": company_name,
                "work": "",
                "requirements": "",
                "conditions": "",
                "benefits": ""
            }
    except Exception as e:
        print(f"⚠️  채용공고 정보를 가져오는 중 오류: {e}")
        job_info = {
            "title": job_title,
            "company": company_name,
            "work": "",
            "requirements": "",
            "conditions": "",
            "benefits": ""
        }
    
    # 자기소개서 정보 가져오기 (세션에 저장되어 있다면)
    cover_letter = session.get("cover_letter")
    
    try:
        resume = session.get("resume", {})
        
        # 면접 질문 생성
        questions = generate_interview_questions(
            resume=resume,
            job_info=job_info,
            cover_letter=cover_letter,
            num_questions=5
        )
        
        # 면접 데이터 저장
        interview_data = {
            "job_title": job_title,
            "company_name": company_name,
            "questions": questions,
            "answers": [],
            "evaluations": []
        }
        
        session["interview"] = interview_data
        
        return {
            "success": True,
            "interview": interview_data
        }
    except Exception as e:
        print(f"❌ 면접 시작 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"면접 시작 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/api/interview-status/{session_id}")
async def get_interview_status(session_id: str):
    """면접 상태 조회"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    interview = session.get("interview")
    
    if interview:
        return {
            "success": True,
            "interview": interview
        }
    else:
        return {
            "success": False,
            "interview": None
        }


@app.post("/api/submit-answer")
async def submit_answer_endpoint(
    session_id: str = Form(...),
    question_index: int = Form(...),
    answer: str = Form(...)
):
    """면접 답변 제출 및 평가"""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    interview = session.get("interview")
    if not interview:
        raise HTTPException(status_code=404, detail="면접 세션을 찾을 수 없습니다.")
    
    questions = interview.get("questions", [])
    if question_index < 0 or question_index >= len(questions):
        raise HTTPException(status_code=400, detail="잘못된 질문 인덱스입니다.")
    
    try:
        resume = session.get("resume", {})
        cover_letter = session.get("cover_letter")
        
        # 채용공고 정보 가져오기
        job_info = {
            "title": interview.get("job_title", ""),
            "company": interview.get("company_name", ""),
            "work": "",
            "requirements": "",
            "conditions": "",
            "benefits": ""
        }
        
        # 답변 평가
        evaluation = evaluate_answer(
            question=questions[question_index],
            answer=answer,
            resume=resume,
            job_info=job_info,
            cover_letter=cover_letter
        )
        
        # 답변과 평가 저장
        answers = interview.get("answers", [])
        evaluations = interview.get("evaluations", [])
        
        # 기존 답변이 있으면 업데이트, 없으면 추가
        if question_index < len(answers):
            answers[question_index] = answer
            evaluations[question_index] = evaluation
        else:
            # 부족한 부분 채우기 (기본 평가 점수 포함)
            while len(answers) < question_index:
                answers.append("")
                evaluations.append({
                    "score": 70,
                    "feedback": "답변 대기 중",
                    "strengths": [],
                    "improvements": []
                })
            answers.append(answer)
            evaluations.append(evaluation)
        
        interview["answers"] = answers
        interview["evaluations"] = evaluations
        
        # 모든 질문에 답했는지 확인
        all_answered = len(answers) >= len(questions) and all(a for a in answers)
        
        overall_evaluation = None
        if all_answered and not interview.get("overall_evaluation"):
            # 전체 평가 생성
            overall_evaluation = generate_overall_evaluation(
                questions=questions,
                answers=answers,
                evaluations=evaluations,
                resume=resume,
                job_info=job_info
            )
            interview["overall_evaluation"] = overall_evaluation
        
        return {
            "success": True,
            "interview": interview,
            "answer": {
                "question_index": question_index,
                "answer": answer,
                "evaluation": evaluation
            },
            "completed": all_answered,
            "overall_evaluation": overall_evaluation
        }
    except Exception as e:
        print(f"❌ 답변 제출 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"답변 제출 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/initialize-vector-store")
async def initialize_vector_store_endpoint():
    """벡터 스토어 초기화"""
    try:
        jobs = load_jobs_from_txt("jobs.txt")
        if not jobs:
            print("⚠️  load_jobs_from_txt()가 빈 리스트를 반환했습니다.")
            return {
                "success": False,
                "message": "채용공고를 불러올 수 없습니다. jobs.txt 파일을 확인하세요."
            }
    except Exception as e:
        print(f"❌ 채용공고 파싱 중 오류 발생: {e}")
        return {
            "success": False,
            "message": f"채용공고를 불러오는 중 오류가 발생했습니다: {str(e)}"
        }
    
    # window + stride 방식으로 청킹 (window_size=500, stride=200)
    success = init_vector_store(jobs, chunk_size=0, force_reload=True, window_size=500, stride=200)
    
    if success:
        # 벡터 스토어 문서 수 확인
        from src.vector_store import VECTOR_STORE as VS
        doc_count = 0
        if VS is not None:
            try:
                doc_count = VS.count()
            except Exception:
                pass
        
        return {
            "success": True,
            "message": "벡터 스토어 초기화 완료",
            "document_count": doc_count
        }
    else:
        return {
            "success": False,
            "message": "벡터 스토어 초기화 실패"
        }
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)