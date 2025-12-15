"""
면접 질문 생성 및 평가 모듈
이력서, 채용공고, 자기소개서를 바탕으로 면접 질문 생성 및 답변 평가
"""
from typing import Dict, List, Optional
from .llm_clients import OPENAI_CLIENT, USE_OPENAI, GEMINI_CLIENT, USE_GEMINI


def generate_interview_questions(
    resume: Dict,
    job_info: Dict,
    cover_letter: Optional[Dict] = None,
    num_questions: int = 5
) -> List[str]:
    """면접 질문 생성"""
    if not USE_OPENAI:
        return [
            "자기소개를 해주세요.",
            "지원 동기를 말씀해주세요.",
            "직무 관련 경험을 설명해주세요.",
            "협업 경험에 대해 말씀해주세요.",
            "입사 후 포부를 말씀해주세요."
        ]
    
    # 이력서 정보 요약
    resume_summary = f"""
이름: {resume.get('name', 'N/A')}
학력: {resume.get('education', [])}
경력: {resume.get('experience', [])}
기술 스택: {', '.join(resume.get('skills', []))}
"""
    
    # 채용공고 정보
    job_summary = f"""
채용 제목: {job_info.get('title', 'N/A')}
회사명: {job_info.get('company', 'N/A')}
주요 업무: {job_info.get('work', 'N/A')}
자격 요건: {job_info.get('requirements', 'N/A')}
"""
    
    # 자기소개서 정보 (있는 경우)
    cover_letter_summary = ""
    if cover_letter and isinstance(cover_letter, dict):
        cover_letter_summary = "\n자기소개서 내용:\n"
        for section, content in cover_letter.items():
            if isinstance(content, dict):
                p1 = content.get('paragraph1', '')
                p2 = content.get('paragraph2', '')
                cover_letter_summary += f"- {section}: {p1} {p2}\n"
            elif isinstance(content, str):
                # content가 문자열인 경우
                cover_letter_summary += f"- {section}: {content}\n"
    
    prompt = f"""
다음 이력서와 채용공고 정보를 바탕으로 면접 질문 {num_questions}개를 생성해주세요.

이력서 정보:
{resume_summary}
{cover_letter_summary}

채용공고 정보:
{job_summary}

요구사항:
- 지원자의 이력서와 자기소개서를 바탕으로 구체적이고 실질적인 질문 생성
- 지원 동기, 직무 역량, 협업 경험, 입사 후 포부 등 다양한 주제 포함
- 각 질문은 한 줄로 작성

반드시 다음 JSON 형식으로 반환해주세요:
{{"questions": ["질문1", "질문2", "질문3", "질문4", "질문5"]}}
"""
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 면접관입니다. 지원자의 이력서와 자기소개서를 바탕으로 실질적이고 구체적인 면접 질문을 생성합니다. 반드시 JSON 형식으로 응답합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        # JSON 파싱
        import json
        default_questions = [
            "자기소개를 해주세요.",
            "지원 동기를 말씀해주세요.",
            "직무 관련 경험을 설명해주세요.",
            "협업 경험에 대해 말씀해주세요.",
            "입사 후 포부를 말씀해주세요."
        ]
        
        try:
            result = json.loads(content)
            # "questions" 키에서 질문 리스트 가져오기
            if "questions" in result and isinstance(result["questions"], list):
                questions = result["questions"]
            else:
                questions = default_questions[:num_questions]
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 질문 사용
            print(f"⚠️  JSON 파싱 실패, 기본 질문 사용: {content[:100]}")
            questions = default_questions[:num_questions]
        
        # 질문이 부족하면 기본 질문 추가
        while len(questions) < num_questions:
            questions.append(default_questions[len(questions) % len(default_questions)])
        
        return questions[:num_questions]
    except Exception as e:
        print(f"❌ 면접 질문 생성 중 오류: {e}")
        # 기본 질문 반환
        return [
            "자기소개를 해주세요.",
            "지원 동기를 말씀해주세요.",
            "직무 관련 경험을 설명해주세요.",
            "협업 경험에 대해 말씀해주세요.",
            "입사 후 포부를 말씀해주세요."
        ][:num_questions]


def evaluate_answer(
    question: str,
    answer: str,
    resume: Dict,
    job_info: Dict,
    cover_letter: Optional[Dict] = None
) -> Dict:
    """면접 답변 평가"""
    # cover_letter가 딕셔너리가 아닌 경우 처리
    if cover_letter and not isinstance(cover_letter, dict):
        cover_letter = None
    
    if not USE_OPENAI:
        return {
            "score": 70,
            "feedback": "답변이 적절합니다.",
            "strengths": ["구체적인 답변"],
            "improvements": ["더 구체적인 사례 추가"]
        }
    
    # 이력서 정보 요약
    resume_summary = f"""
이름: {resume.get('name', 'N/A')}
학력: {resume.get('education', [])}
경력: {resume.get('experience', [])}
기술 스택: {', '.join(resume.get('skills', []))}
"""
    
    # 채용공고 정보
    job_summary = f"""
채용 제목: {job_info.get('title', 'N/A')}
회사명: {job_info.get('company', 'N/A')}
주요 업무: {job_info.get('work', 'N/A')}
자격 요건: {job_info.get('requirements', 'N/A')}
"""
    
    prompt = f"""
다음 면접 질문과 답변을 평가해주세요.

면접 질문: {question}

지원자 답변: {answer}

이력서 정보:
{resume_summary}

채용공고 정보:
{job_summary}

평가 기준:
1. 답변의 구체성과 진정성
2. 이력서와의 일관성
3. 직무 적합성
4. 표현의 명확성

다음 JSON 형식으로 평가 결과를 반환해주세요:
{{
    "score": 0-100 점수,
    "feedback": "전체적인 피드백 (2-3문장)",
    "strengths": ["강점1", "강점2"],
    "improvements": ["개선점1", "개선점2"]
}}
"""
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 면접 평가관입니다. 지원자의 답변을 객관적이고 건설적으로 평가합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        import json
        try:
            result = json.loads(content)
            # score 검증 및 기본값 처리
            score = result.get("score")
            # score가 None이거나 숫자가 아니면 기본값 70 사용
            if score is None or not isinstance(score, (int, float)):
                print(f"⚠️  점수가 유효하지 않음: {score}, 기본값 70 사용")
                score = 70
            # score가 범위를 벗어나면 기본값 사용 (0점은 유효한 점수로 처리)
            elif score < 0 or score > 100:
                print(f"⚠️  점수가 범위를 벗어남: {score}, 기본값 70 사용")
                score = 70
            
            return {
                "score": int(score),
                "feedback": result.get("feedback", "답변이 적절합니다."),
                "strengths": result.get("strengths", []),
                "improvements": result.get("improvements", [])
            }
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 파싱 실패: {e}, 기본값 사용")
            print(f"응답 내용: {content[:200]}")
            return {
                "score": 70,
                "feedback": "답변을 평가했습니다.",
                "strengths": ["구체적인 답변"],
                "improvements": ["더 구체적인 사례 추가"]
            }
    except Exception as e:
        print(f"❌ 답변 평가 중 오류: {e}")
        return {
            "score": 70,
            "feedback": f"평가 중 오류가 발생했습니다: {str(e)}",
            "strengths": [],
            "improvements": []
        }


def generate_overall_evaluation(
    questions: List[str],
    answers: List[str],
    evaluations: List[Dict],
    resume: Dict,
    job_info: Dict
) -> Dict:
    """전체 면접 평가 생성"""
    if not USE_OPENAI:
        return {
            "total_score": 70,
            "summary": "전체적으로 적절한 답변을 하셨습니다.",
            "recommendations": ["더 구체적인 사례 추가"]
        }
    
    # 평균 점수 계산 (score가 없거나 유효하지 않으면 기본값 70 사용, 0점은 유효한 점수로 처리)
    def get_score(eval_item):
        if not isinstance(eval_item, dict):
            return 70
        score = eval_item.get("score")
        if score is None or not isinstance(score, (int, float)):
            return 70
        if score < 0 or score > 100:
            return 70
        return score
    
    total_score = sum(get_score(eval_item) for eval_item in evaluations) / len(evaluations) if evaluations else 70
    
    # 질문과 답변 요약
    qa_summary = "\n".join([
        f"Q{i+1}. {q}\nA{i+1}. {a}\n평가: {eval.get('feedback', '')}\n"
        for i, (q, a, eval) in enumerate(zip(questions, answers, evaluations))
    ])
    
    prompt = f"""
다음 면접 질문, 답변, 개별 평가를 바탕으로 전체 면접 평가를 작성해주세요.

면접 질문 및 답변:
{qa_summary}

이력서 정보:
이름: {resume.get('name', 'N/A')}
경력: {resume.get('experience', [])}

채용공고 정보:
채용 제목: {job_info.get('title', 'N/A')}
회사명: {job_info.get('company', 'N/A')}

평가 기준:
1. 전체적인 답변의 질과 일관성
2. 직무 적합성
3. 표현력과 전달력
4. 구체성과 진정성

다음 JSON 형식으로 전체 평가를 반환해주세요:
{{
    "total_score": {total_score:.1f},
    "summary": "전체 평가 요약 (3-5문장)",
    "recommendations": ["권장사항1", "권장사항2", "권장사항3"],
    "strengths": ["강점1", "강점2"],
    "improvements": ["개선점1", "개선점2"]
}}

중요: total_score는 반드시 {total_score:.1f} 값을 사용하세요. 계산된 평균 점수를 그대로 사용합니다.
"""
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 면접 평가관입니다. 전체 면접을 종합적으로 평가합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        import json
        try:
            result = json.loads(content)
            # total_score 검증
            result_total_score = result.get("total_score")
            if result_total_score is None or not isinstance(result_total_score, (int, float)):
                result_total_score = total_score
            elif result_total_score < 0 or result_total_score > 100:
                result_total_score = total_score
            
            # 전체 평가 결과 반환 (app.py에서 기대하는 형식)
            return {
                "total_score": float(result_total_score),
                "final_score": float(result_total_score),  # app.py 호환성
                "summary": result.get("summary", "전체적으로 적절한 답변을 하셨습니다."),
                "overall_impression": result.get("summary", "전체적으로 적절한 답변을 하셨습니다."),  # app.py 호환성
                "recommendations": result.get("recommendations", []),
                "strengths": result.get("strengths", []),  # app.py 호환성
                "improvements": result.get("improvements", result.get("recommendations", [])),  # app.py 호환성
                "final_comment": result.get("summary", "전체적으로 적절한 답변을 하셨습니다."),  # app.py 호환성
                "recommendation": f"총점 {result_total_score:.1f}점으로 평가되었습니다."  # app.py 호환성
            }
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 파싱 실패: {e}, 기본값 사용")
            print(f"응답 내용: {content[:200]}")
            return {
                "total_score": float(total_score),
                "final_score": float(total_score),
                "summary": "전체적으로 적절한 답변을 하셨습니다.",
                "overall_impression": "전체적으로 적절한 답변을 하셨습니다.",
                "recommendations": ["더 구체적인 사례 추가"],
                "strengths": ["구체적인 답변"],
                "improvements": ["더 구체적인 사례 추가"],
                "final_comment": "전체적으로 적절한 답변을 하셨습니다.",
                "recommendation": f"총점 {total_score:.1f}점으로 평가되었습니다."
            }
    except Exception as e:
        print(f"❌ 전체 평가 생성 중 오류: {e}")
        return {
            "total_score": total_score,
            "summary": f"평가 중 오류가 발생했습니다: {str(e)}",
            "recommendations": []
        }

