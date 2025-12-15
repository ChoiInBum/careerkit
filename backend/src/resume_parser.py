"""
이력서 파싱 모듈
PDF/TXT 파일에서 이력서 정보 추출
"""
import re
import json
from io import BytesIO
from typing import Dict

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from .llm_clients import OPENAI_CLIENT, USE_OPENAI


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """PDF 바이트에서 텍스트 추출"""
    if pdfplumber:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages)
    
    if PyPDF2:
        reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        texts = []
        for p in reader.pages:
            txt = p.extract_text()
            if txt:
                texts.append(txt)
        return "\n".join(texts)
    
    return pdf_bytes.decode("utf-8", errors="ignore")


def heuristic_extract_resume(text: str) -> Dict:
    """휴리스틱 방식으로 이력서 정보 추출 (OpenAI 미사용 시)"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = lines[0] if lines else ""
    
    email_m = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_m = re.search(r"(\+?82|0?0?)-?\s*\d{1,3}[-\s]?\d{3,4}[-\s]?\d{4}", text) or \
              re.search(r"\d{2,4}[-\s]\d{3,4}[-\s]\d{4}", text)
    
    skills = []
    skill_candidates = ["Java", "Python", "Spring", "Django", "Flask", "Vue", "React", 
                       "MySQL", "PostgreSQL", "SQL", "AWS", "Docker", "Kubernetes", "Pandas"]
    for s in skill_candidates:
        if re.search(r"\b" + re.escape(s) + r"\b", text, flags=re.I):
            skills.append(s)
    
    yrs = 0
    m = re.search(r"(\d+)\s*년", text)
    if m:
        try:
            yrs = int(m.group(1))
        except ValueError:
            yrs = 0
    
    snippet = "\n".join(lines[:10])
    
    return {
        "name": name,
        "email": email_m.group(0) if email_m else "",
        "phone": phone_m.group(0) if phone_m else "",
        "skills": skills,
        "experience_years": yrs,
        "summary": snippet
    }


def openai_extract_resume(text: str) -> Dict:
    """OpenAI를 사용하여 이력서 정보 추출"""
    if not USE_OPENAI:
        return heuristic_extract_resume(text)
    
    prompt = f"""
다음 이력서에서 정보를 추출하여 JSON 형식으로 반환하세요.
반드시 아래 스키마를 따라주세요:
{{"name": "이름", "email": "이메일", "phone": "전화번호", "skills": ["기술1", "기술2"], "experience_years": 숫자, "summary": "요약"}}

이력서:
\"\"\"{text[:4000]}\"\"\"

JSON만 출력하세요 (마크다운 없이).
"""
    
    if hasattr(OPENAI_CLIENT, 'chat'):
        resp = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        txt = resp.choices[0].message.content.strip()
    else:
        resp = OPENAI_CLIENT.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        txt = resp.choices[0].message.content.strip()
    
    # JSON 파싱
    txt = txt.replace("```json", "").replace("```", "").strip()
    return json.loads(txt)

