"""
자기소개서 생성 모듈
이력서와 채용공고 정보를 바탕으로 자기소개서 생성
"""
from typing import Dict, List, Optional
from .llm_clients import OPENAI_CLIENT, USE_OPENAI, GEMINI_CLIENT, USE_GEMINI, initialize_gemini_client


def generate_draft_with_gemini(
    section_name: str,
    resume: Dict,
    job_info: Dict
) -> str:
    """Gemini 2.5-flash로 초안 작성 (1000자 이내, 한 단락)"""

    initialize_gemini_client()
    
    if not USE_GEMINI or not GEMINI_CLIENT:
        return f"[{section_name} 섹션] Gemini API가 필요합니다."
    
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
    
    # 섹션별 초안 작성 프롬프트
    draft_prompts = {
        "지원 동기": f"""
다음 이력서와 채용공고 정보를 바탕으로 '지원 동기' 자기소개서를 한 단락으로 작성해주세요.

이력서 정보:
{resume_summary}

채용공고 정보:
{job_summary}

요구사항:
- 회사와 직무에 대한 관심과 지원 동기를 구체적으로 작성
- 한 단락으로 작성 (단락 구분 없이 연속된 텍스트)
- 1000자 이내로 작성 (반드시 준수)
- 진솔하고 구체적인 내용으로 작성
- 구체적인 사례나 경험을 포함하여 설득력 있게 작성
""",
        "직무 관련 역량": f"""
다음 이력서와 채용공고 정보를 바탕으로 '직무 관련 역량' 자기소개서를 한 단락으로 작성해주세요.

이력서 정보:
{resume_summary}

채용공고 정보:
{job_summary}

요구사항:
- 직무 수행에 필요한 핵심 역량과 기술을 구체적으로 제시
- 한 단락으로 작성 (단락 구분 없이 연속된 텍스트)
- 1000자 이내로 작성 (반드시 준수)
- 실제 경험과 사례를 중심으로 작성
- 구체적인 성과나 결과를 포함하여 작성
""",
        "협업 관련 경험": f"""
다음 이력서와 채용공고 정보를 바탕으로 '협업 관련 경험' 자기소개서를 한 단락으로 작성해주세요.

이력서 정보:
{resume_summary}

채용공고 정보:
{job_summary}

요구사항:
- 팀 프로젝트나 협업 경험을 구체적으로 서술
- 한 단락으로 작성 (단락 구분 없이 연속된 텍스트)
- 1000자 이내로 작성 (반드시 준수)
- 구체적인 상황, 역할, 기여, 배운 점을 포함
- 협업 과정에서의 결과나 성과를 명시
""",
        "입사 후 포부": f"""
다음 이력서와 채용공고 정보를 바탕으로 '입사 후 포부' 자기소개서를 한 단락으로 작성해주세요.

이력서 정보:
{resume_summary}

채용공고 정보:
{job_summary}

요구사항:
- 입사 후 단기 목표와 장기 비전을 구체적으로 작성
- 한 단락으로 작성 (단락 구분 없이 연속된 텍스트)
- 1000자 이내로 작성 (반드시 준수)
- 회사와 직무에 기여할 수 있는 방안을 포함
- 현실적이고 구체적인 계획을 제시
"""
    }
    
    prompt = draft_prompts.get(section_name, draft_prompts["지원 동기"])
    
    try:
        response = GEMINI_CLIENT.generate_content(prompt)
        draft_text = response.text.strip()
        
        # 1000자 초과 시 자르기
        if len(draft_text) > 1000:
            draft_text = draft_text[:1000]
        
        return draft_text
    except Exception as e:
        print(f"❌ Gemini 초안 생성 중 오류: {e}")
        return f"[오류] 초안 생성 중 문제가 발생했습니다: {str(e)}"


def refine_with_gpt4o(
    draft_text: str,
    section_name: str,
    resume: Dict,
    job_info: Dict
) -> str:
    """GPT-4o로 초안을 첨삭하여 완성도 높임 (1000자 이내, 한 단락)"""
    if not USE_OPENAI:
        return draft_text
    
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
    
    system_message = """당신은 15년 이상의 경력을 가진 자기소개서 첨삭 전문가입니다. 초안을 검토하고 완성도를 높여 최종 버전을 작성합니다.

당신의 역할:
1. 초안의 핵심 내용과 의도를 유지합니다
2. 표현을 더 명확하고 설득력 있게 개선합니다
3. 구체성과 진정성을 높입니다
4. 1000자 이내 한 단락 형식을 유지합니다
5. 채용 담당자가 인상깊게 읽을 수 있도록 다듬습니다"""
    
    user_prompt = f"""다음은 '{section_name}' 섹션의 자기소개서 초안입니다. 이를 첨삭하여 완성도를 높인 최종 버전을 작성해주세요.

【채용공고 정보】
{job_summary}

【이력서 정보】
{resume_summary}

【초안】
{draft_text}

요구사항:
- 초안의 핵심 내용과 의도는 유지합니다
- 표현을 더 명확하고 설득력 있게 개선합니다
- 구체성과 진정성을 높입니다
- 한 단락으로 작성합니다 (단락 구분 없이)
- 반드시 1000자 이내로 작성합니다
- 초안의 모든 중요한 내용을 포함합니다
- 개선된 최종 버전만 출력하세요 (설명이나 메타데이터 없이 자기소개서 본문만)
"""
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1200  # 1000자 + 여유
        )
        
        refined_text = response.choices[0].message.content.strip()
        
        # 마크다운 코드 블록이나 불필요한 텍스트 제거
        if "```" in refined_text:
            parts = refined_text.split("```")
            if len(parts) > 1:
                refined_text = parts[1].strip()
                if refined_text.startswith("markdown") or refined_text.startswith("text"):
                    refined_text = "\n".join(refined_text.split("\n")[1:]).strip()
        
        # 1000자 초과 시 자르기
        if len(refined_text) > 1000:
            refined_text = refined_text[:1000]
        
        return refined_text
    except Exception as e:
        print(f"❌ GPT-4o 첨삭 중 오류: {e}")
        return draft_text  # 오류 시 초안 반환


def generate_cover_letter_section(
    section_name: str,
    resume: Dict,
    job_info: Dict,
    chat_history: List = None
) -> str:
    """특정 섹션의 자기소개서 생성 (Gemini 초안 → GPT-4o 첨삭)
    
    Returns:
        str: 최종 자기소개서 텍스트 (한 단락, 1000자 이내)
    """
    # Step 1: Gemini 2.5-flash로 초안 작성
    draft = generate_draft_with_gemini(section_name, resume, job_info)
    
    # Step 2: GPT-4o로 첨삭하여 완성도 높임
    final_text = refine_with_gpt4o(draft, section_name, resume, job_info)
    
    return final_text


def generate_cover_letter(
    resume: Dict,
    job_info: Dict,
    sections: Optional[List[str]] = None,
    chat_history: List = None
) -> Dict:
    """전체 자기소개서 생성
    
    Returns:
        Dict: {섹션명: 자기소개서 텍스트} 형식 (한 단락, 1000자 이내)
    """
    # 기본 섹션 목록
    if sections is None or len(sections) == 0:
        sections = ["지원 동기", "직무 관련 역량", "협업 관련 경험", "입사 후 포부"]
    
    cover_letter = {}
    
    for section in sections:
        # 한 단락으로 생성된 최종 텍스트 반환
        final_text = generate_cover_letter_section(section, resume, job_info, chat_history)
        cover_letter[section] = final_text
    
    return cover_letter


def review_and_improve_cover_letter(
    cover_letter_text: str,
    section_name: str,
    resume: Dict,
    job_info: Dict
) -> Dict:
    """자기소개서 첨삭 및 개선 (GPT-4o 사용)
    
    Args:
        cover_letter_text: 첨삭할 자기소개서 텍스트
        section_name: 섹션 이름 (예: "지원 동기")
        resume: 이력서 정보
        job_info: 채용공고 정보
    
    Returns:
        Dict: {
            "original": 원본 텍스트,
            "improved": 개선된 텍스트,
            "review": 첨삭 의견,
            "strengths": 강점 목록,
            "improvements": 개선점 목록
        }
    """
    if not USE_OPENAI:
        return {
            "original": cover_letter_text,
            "improved": cover_letter_text,
            "review": "OpenAI API가 필요합니다.",
            "strengths": [],
            "improvements": []
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
    
    # 시스템 메시지: 자기소개서 첨삭 전문가 페르소나
    system_message = """당신은 15년 이상의 경력을 가진 자기소개서 첨삭 전문가입니다.

당신의 전문성:
- 대기업, 중견기업, 스타트업 등 다양한 기업의 채용 프로세스를 완벽히 이해하고 있습니다
- 수천 명의 지원자들의 자기소개서를 검토하고 합격으로 이끈 경험이 있습니다
- HR 전문가, 커리어 컨설턴트, 면접관으로서의 풍부한 노하우를 보유하고 있습니다
- 한국 기업문화와 채용 트렌드를 깊이 있게 이해하고 있습니다

당신의 첨삭 철학:
- 지원자의 진정성을 해치지 않으면서도 효과적으로 어필할 수 있도록 돕습니다
- 구체적인 사례와 성과 중심의 서술을 강조합니다
- 채용 담당자의 관점에서 무엇이 인상적인지 명확히 제시합니다
- 개선점을 지적할 때는 대안도 함께 제시합니다

당신의 역할:
1. 자기소개서의 내용, 구조, 표현을 철저히 검토합니다
2. 강점을 찾아내고 부각시킵니다
3. 약점을 발견하고 구체적인 개선 방안을 제시합니다
4. 채용공고와의 연관성을 강화합니다
5. 더 효과적이고 설득력 있는 버전으로 개선합니다"""
    
    # 사용자 프롬프트
    user_prompt = f"""다음 자기소개서를 첨삭하고 개선해주세요.

【섹션명】{section_name}

【채용공고 정보】
{job_summary}

【이력서 정보】
{resume_summary}

【첨삭 대상 자기소개서】
{cover_letter_text}

다음 형식으로 응답해주세요:

1. **검수 의견** (전체적인 평가 및 주요 검토 사항)

2. **강점** (현재 자기소개서의 잘된 부분, 3-5개 항목으로 나열)
- 항목1
- 항목2
- ...

3. **개선점** (보완이 필요한 부분, 3-5개 항목으로 나열)
- 항목1 (개선 이유와 구체적인 개선 방안 포함)
- 항목2
- ...

4. **개선된 자기소개서** (검수 의견과 개선점을 반영하여 재작성한 버전)
(원본의 의도와 핵심 내용은 유지하되, 더 효과적으로 표현하고 구체성을 높인 버전)
"""
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o",  # GPT-4o 모델 사용
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # 첨삭은 일관성 있게
            max_tokens=2000
        )
        
        review_text = response.choices[0].message.content.strip()
        
        # 응답 파싱 (간단한 파싱)
        # 실제로는 더 정교한 파싱이 필요할 수 있음
        improved_text = cover_letter_text  # 기본값은 원본
        strengths = []
        improvements = []
        review_comment = review_text  # 전체 검수 의견
        
        # 개선된 버전 추출 시도
        if "개선된 자기소개서" in review_text:
            parts = review_text.split("개선된 자기소개서")
            if len(parts) > 1:
                improved_part = parts[1].strip()
                # 마크다운 코드 블록이나 불필요한 텍스트 제거
                improved_text = improved_part.split("```")[0].strip()
                if improved_text.startswith(":"):
                    improved_text = improved_text[1:].strip()
        
        # 강점 추출 시도
        if "강점" in review_text and "-" in review_text:
            strengths_section = review_text.split("강점")[1].split("개선점")[0] if "개선점" in review_text else review_text.split("강점")[1]
            for line in strengths_section.split("\n"):
                if line.strip().startswith("-"):
                    strengths.append(line.strip()[1:].strip())
        
        # 개선점 추출 시도
        if "개선점" in review_text and "-" in review_text:
            improvements_section = review_text.split("개선점")[1].split("개선된 자기소개서")[0] if "개선된 자기소개서" in review_text else review_text.split("개선점")[1]
            for line in improvements_section.split("\n"):
                if line.strip().startswith("-"):
                    improvements.append(line.strip()[1:].strip())
        
        return {
            "original": cover_letter_text,
            "improved": improved_text if improved_text != cover_letter_text else cover_letter_text,
            "review": review_comment,
            "strengths": strengths[:5],  # 최대 5개
            "improvements": improvements[:5],  # 최대 5개
            "model": "GPT-4o"
        }
    except Exception as e:
        print(f"❌ 자기소개서 첨삭 중 오류: {e}")
        return {
            "original": cover_letter_text,
            "improved": cover_letter_text,
            "review": f"첨삭 중 오류가 발생했습니다: {str(e)}",
            "strengths": [],
            "improvements": []
        }
