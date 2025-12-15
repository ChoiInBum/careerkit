"""
채팅 처리 모듈
사용자 메시지 처리 및 슬롯 추출
"""
import json
from typing import Dict, List, Optional
from .config import SLOT_ORDER, SLOT_DESCRIPTIONS, SLOT_QUESTIONS
from .llm_clients import OPENAI_CLIENT, USE_OPENAI


def next_unfilled_slot(session: Dict) -> Optional[str]:
    """다음 채워지지 않은 슬롯 반환"""
    for s in SLOT_ORDER:
        if s not in session["slots"]:
            return s
    return None


def heuristic_extract_slot(slot_name: str, message: str):
    """휴리스틱 방식으로 슬롯 값 추출"""
    message_lower = message.lower().strip()
    
    if slot_name == "company_size":
        # '상관없음' 등의 키워드 체크
        none_keywords = ["없음", "없어요", "상관없음", "상관없어요", "무관", "아무거나", "다", "전부"]
        if any(keyword in message_lower for keyword in none_keywords):
            return None
        
        # 기업 규모 키워드 매핑
        if any(keyword in message_lower for keyword in ["스타트업", "startup", "스타트", "초기"]):
            return "스타트업"
        if any(keyword in message_lower for keyword in ["중소", "중소기업"]):
            return "중소기업"
        if any(keyword in message_lower for keyword in ["중견", "중견기업"]):
            return "중견기업"
        if any(keyword in message_lower for keyword in ["대기업", "대기업", "대형"]):
            return "대기업"
        if any(keyword in message_lower for keyword in ["외국계", "글로벌"]):
            return "외국계"
        
        return message.strip()
    
    # 기타 슬롯: 원본 텍스트 반환
    return message.strip()


def openai_extract_slot_with_llm(slot_name: str, user_message: str, chat_history: List) -> Dict:
    """LLM을 사용하여 슬롯 값을 추출"""
    if not USE_OPENAI:
        return {
            "value": heuristic_extract_slot(slot_name, user_message),
            "confidence": "low",
            "response": None
        }
    
    slot_info = SLOT_DESCRIPTIONS.get(slot_name, {})
    
    # 최근 대화 히스토리 (최대 5개)
    recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
    history_text = "\n".join([f"{h['from']}: {h['text']}" for h in recent_history])
    
    prompt = f"""당신은 채용 정보를 수집하는 친절한 AI 챗봇입니다.

현재 수집하려는 정보: {slot_name}
- 설명: {slot_info.get('description', '')}
- 예시: {', '.join(slot_info.get('examples', []))}

최근 대화 내역:
{history_text}

사용자의 마지막 응답: "{user_message}"

작업:
1. 사용자 응답에서 '{slot_name}'에 해당하는 값을 추출하세요.
2. 만약 사용자가 엉뚱한 답변을 했다면, 자연스럽게 질문으로 다시 유도하세요.
3. 사용자가 질문이나 잡담을 했다면, 친절하게 답변한 후 원래 질문으로 돌아오세요.

**중요 규칙:**
- company_size (기업 규모) 질문에서 "상관없음", "없음", "무관" 등의 답변은 **null로 처리**하고 confidence를 "high"로 설정하세요.

응답 형식 (반드시 JSON):
{{
  "value": "추출된 값 또는 null",
  "confidence": "high 또는 low",
  "response": "사용자에게 보여줄 응답 메시지 (값을 추출했으면 확인 메시지, 못 추출했으면 다시 유도하는 질문)"
}}

JSON만 출력하세요 (마크다운 없이).
"""
    
    if hasattr(OPENAI_CLIENT, 'chat'):
        resp = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.6
        )
        txt = resp.choices[0].message.content.strip()
    else:
        resp = OPENAI_CLIENT.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.6
        )
        txt = resp.choices[0].message.content.strip()
    
    # JSON 파싱
    txt = txt.replace("```json", "").replace("```", "").strip()
    result = json.loads(txt)
    
    return result


def natural_conversation_collect_info(resume: Dict, chat_history: List, slots: Dict) -> Dict:
    """자연스러운 대화로 정보 수집"""
    if not USE_OPENAI:
        return {
            "response": "죄송합니다. OpenAI API가 필요합니다.",
            "slots_updated": {},
            "completed": False
        }
    
    # 다음 채워지지 않은 슬롯 찾기
    next_slot = next_unfilled_slot({"slots": slots})
    
    if not next_slot:
        return {
            "response": "모든 정보를 수집했습니다! 이제 적합한 채용 공고를 찾아드릴 수 있습니다.",
            "slots_updated": {},
            "completed": True
        }
    
    # 사용자의 최신 메시지 확인 (마지막 메시지가 사용자 메시지인 경우)
    user_message = None
    if chat_history and chat_history[-1].get("from") == "user":
        user_message = chat_history[-1].get("text", "")
    
    slots_updated = {}
    
    # 사용자 메시지가 있고, 아직 채워지지 않은 슬롯이 있으면 슬롯 값 추출 시도
    if user_message and next_slot:
        # LLM을 사용하여 슬롯 값 추출
        extracted = openai_extract_slot_with_llm(next_slot, user_message, chat_history)
        extracted_value = extracted.get("value")
        
        if extracted_value and extracted_value.strip():
            # "상관없음", "없음" 등의 키워드 체크
            value_lower = extracted_value.lower().strip()
            none_keywords = ["없음", "없어요", "상관없음", "상관없어요", "무관", "아무거나", "다", "전부", "모르겠", "skip"]
            
            if any(keyword in value_lower for keyword in none_keywords):
                # None으로 저장 (선택사항임을 표시)
                slots_updated[next_slot] = None
            else:
                slots_updated[next_slot] = extracted_value.strip()
    
    # 슬롯이 업데이트되었는지 확인
    if slots_updated:
        # 다음 채워지지 않은 슬롯 다시 확인
        updated_slots = {**slots, **slots_updated}
        next_slot_after = next_unfilled_slot({"slots": updated_slots})
        
        if not next_slot_after:
            # 모든 슬롯이 채워짐
            return {
                "response": "감사합니다! 모든 정보를 수집했습니다. 이제 적합한 채용 공고를 찾아드리겠습니다.",
                "slots_updated": slots_updated,
                "completed": True
            }
        else:
            # 다음 슬롯으로 진행
            next_slot = next_slot_after
    
    slot_info = SLOT_DESCRIPTIONS.get(next_slot, {})
    recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
    history_text = "\n".join([f"{h['from']}: {h['text']}" for h in recent_history])
    
    # 슬롯이 업데이트된 경우 확인 메시지, 아니면 다음 질문
    if slots_updated:
        prompt = f"""사용자가 {next_slot}에 대해 "{user_message}"라고 답변했습니다.
이 답변을 확인하고 감사 인사를 한 후, 다음 정보를 물어보세요.

**다음 수집할 정보:** {next_slot}
- 설명: {slot_info.get('description', '')}
- 예시: {', '.join(slot_info.get('examples', []))}

**이미 수집한 정보:**
{json.dumps({**slots, **slots_updated}, ensure_ascii=False, indent=2)}

자연스럽고 친근하게 다음 질문을 이어가세요. 응답만 출력하세요.
"""
    else:
        prompt = f"""당신은 채용 정보를 수집하는 친절하고 자연스러운 AI 챗봇입니다.

**지원자 이력서 정보:**
- 이름: {resume.get('name', '지원자')}
- 경력: {resume.get('experience_years', 0)}년
- 기술: {', '.join(resume.get('skills', [])[:5])}

**이미 수집한 정보:**
{json.dumps(slots, ensure_ascii=False, indent=2)}

**현재 수집하려는 정보:** {next_slot}
- 설명: {slot_info.get('description', '')}
- 예시: {', '.join(slot_info.get('examples', []))}

**최근 대화 내역:**
{history_text}

위 정보를 바탕으로, 자연스럽고 친근하게 {next_slot}에 대한 정보를 물어보는 메시지를 작성하세요.
이미 수집한 정보를 언급하며 대화의 맥락을 유지하세요.

응답만 출력하세요 (설명이나 형식 없이).
"""
    
    if hasattr(OPENAI_CLIENT, 'chat'):
        resp = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7
        )
        txt = resp.choices[0].message.content.strip()
    else:
        resp = OPENAI_CLIENT.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7
        )
        txt = resp.choices[0].message.content.strip()
    
    return {
        "response": txt,
        "slots_updated": slots_updated,
        "completed": False
    }

