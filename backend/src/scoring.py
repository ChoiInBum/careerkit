"""
채용공고 매칭 점수 계산 모듈
"""
from typing import Dict
from .config import SCORE_WEIGHTS
from .llm_clients import OPENAI_CLIENT, USE_OPENAI


def normalize_employment_type(text: str) -> str:
    """텍스트에서 고용 형태를 추출하고 정규화합니다."""
    if not text:
        return '기타'
    text = text.strip().lower()
    if '정규직' in text or '정규' in text:
        return '정규직'
    elif '계약직' in text or '계약' in text:
        return '계약직'
    elif '인턴' in text or 'intern' in text:
        return '인턴'
    return '기타'


def llm_score(user_text: str, job_text: str, category: str, max_score: float = 1.0) -> float:
    """LLM을 사용하여 두 텍스트 간의 적합도 점수(0.00~1.00)를 산출"""
    if not USE_OPENAI:
        # LLM 미사용 시 더미 점수 반환
        return round(max_score * (0.6 + (hash(user_text + job_text + category) % 40) / 100), 2)
    
    # 실제 LLM 호출 로직 (향후 구현 가능)
    # 현재는 더미 점수 반환
    return round(max_score * (0.6 + (hash(user_text + job_text + category) % 40) / 100), 2)


def calculate_match_score(job: Dict, user_answers: Dict, resume: Dict) -> Dict:
    """사용자의 답변과 공고를 비교하여 매칭 점수 및 상세 점수를 계산합니다."""
    scores = {}
    
    # 1. 데이터 준비
    user_job = user_answers.get('desired_job', '') or user_answers.get('current_job', '')
    user_skills = user_answers.get('core_skill', '') or ', '.join(resume.get('skills', []))
    user_work = user_answers.get('work_condition', '')
    user_domain = user_answers.get('domain_experience', '') or user_answers.get('industry', '')
    user_achievement = user_answers.get('key_achievement', '')
    
    job_title = job.get('title', '')
    job_description = job.get('description', '')
    job_tasks = job.get('full_content', {}).get('work', '') or job.get('tasks', '')
    
    # 필수/우대 요건 추출
    requirements_text = job.get('full_content', {}).get('requirements', '') or ' '.join(job.get('requirements', []))
    preferences_text = ' '.join(job.get('preferences', []))
    
    mandatory_text = requirements_text
    preferred_text = preferences_text or requirements_text
    
    job_conditions = job.get('full_content', {}).get('conditions', '') or job.get('location', '')

    # 2. 항목별 점수 계산 (0.00 ~ 1.00 스케일)
    scores['job_title'] = llm_score(user_job, job_title + ' ' + job_description, '직무 일치도', max_score=1.0)
    scores['skills'] = llm_score(user_skills, mandatory_text + ' ' + preferred_text, '스킬 일치도', max_score=1.0)
    scores['mandatory'] = llm_score(user_achievement, mandatory_text, '필수 요건 충족도', max_score=1.0)
    scores['preferred'] = llm_score(user_achievement, preferred_text, '우대사항 충족도', max_score=1.0)
    scores['tasks'] = llm_score(user_achievement, job_tasks, '업무 내용 일치도', max_score=1.0)
    scores['domain'] = llm_score(user_domain, job_title + ' ' + job_tasks, '도메인 일치도', max_score=1.0)
    scores['work_condition'] = llm_score(user_work, job_conditions, '근무 조건 일치도', max_score=1.0)

    # 3. 최종 총점 계산 (가중치 적용)
    total_score = 0
    score_details = {}
    
    for key, weight in SCORE_WEIGHTS.items():
        base_score = scores.get(key, 0.0) 
        weighted_score = base_score * weight * 100 
        total_score += weighted_score
        score_details[key] = weighted_score
        
    return {
        "total_score": round(total_score / 100, 2),
        "score_details": score_details
    }

