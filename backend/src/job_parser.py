"""
채용공고 파싱 모듈
TXT 파일에서 채용공고 정보 추출
"""
import re
from pathlib import Path
from typing import List, Dict


def load_jobs_from_txt(txt_file_path: str = "jobs.txt") -> List[Dict]:
    """TXT 파일에서 채용공고 리스트를 읽어옵니다."""
    jobs = []
    # 프로젝트 루트에서 파일 찾기
    project_root = Path(__file__).parent.parent
    txt_path = project_root / txt_file_path
    
    if not txt_path.exists():
        print(f"⚠️  {txt_file_path} 파일을 찾을 수 없습니다: {txt_path}")
        return jobs
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # "[공고 #"로 시작하는 섹션을 찾아서 구분 (더 정확한 파싱)
    pattern = r'\[공고\s*#(\d+)\](.*?)(?=\[공고\s*#\d+\]|$)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    job_sections = []
    for match in matches:
        section_content = match.group(0)
        job_sections.append(section_content)
    
    # 만약 "[공고 #" 패턴이 없으면 "---"로 구분 (하위 호환성)
    if not job_sections:
        job_sections = content.split('---')
    
    print(f"📄 총 {len(job_sections)}개의 공고 섹션 발견")
    
    for job_idx, section in enumerate(job_sections, 1):
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        print(f"📝 {job_idx}번째 공고 파싱 중...")
        job = {
            "id": job_idx,
            "title": "",
            "company": "",
            "location": "",
            "experience": "",
            "salary": "",
            "job_type": "",
            "tech_stack": [],
            "company_size": "",
            "industry": "",
            "description": "",
            "requirements": [],
            "preferences": [],
            "benefits": [],
            "match_score": 0,
            "url": "",
            "full_content": {}
        }
        
        # URL 파싱: "[공고 #N] 제목" 다음 줄에 "URL: ..." 형식으로 있는 경우
        url_match = re.search(r'URL:\s*(https?://[^\s]+)', section)
        if url_match:
            job["url"] = url_match.group(1).strip()
        
        # "10. 채용공고 링크" 섹션에서도 URL 찾기
        if not job["url"]:
            link_section_match = re.search(r'10\.\s*채용공고\s*링크\s*[-:]\s*(https?://[^\s]+)', section, re.MULTILINE)
            if link_section_match:
                job["url"] = link_section_match.group(1).strip()
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 섹션 헤더 감지
            if re.match(r'^1\.\s*(채용\s*제목/포지션|포지션)', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "title"
                current_content = []
            elif re.match(r'^2\.\s*회사명', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "company"
                current_content = []
            elif re.match(r'^3\.\s*주요\s*업무', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "work"
                current_content = []
            elif re.match(r'^4\.\s*자격\s*요건', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "requirements"
                current_content = []
            elif re.match(r'^5\.\s*근무\s*조건', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "conditions"
                current_content = []
            elif re.match(r'^6\.\s*(급여\s*및\s*복리후생|급여)', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "benefits"
                current_content = []
            elif re.match(r'^7\.\s*전형\s*절차', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "process"
                current_content = []
            elif re.match(r'^8\.\s*(지원\s*방법|마감일)', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "application"
                current_content = []
            elif re.match(r'^9\.\s*(기타\s*정보|기타)', line):
                if current_section:
                    job["full_content"][current_section] = "\n".join(current_content)
                current_section = "etc"
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # 마지막 섹션 저장
        if current_section:
            job["full_content"][current_section] = "\n".join(current_content)
        
        # 기본 필드 매핑
        job["title"] = job["full_content"].get("title", "").split('\n')[0] if job["full_content"].get("title") else ""
        job["company"] = job["full_content"].get("company", "").split('\n')[0] if job["full_content"].get("company") else ""
        job["description"] = job["full_content"].get("work", "")
        
        jobs.append(job)
    
    print(f"✅ {len(jobs)}개의 채용공고 파싱 완료")
    return jobs


def parse_saramin_job_summary(file_path: str = "saramin_job_summary_20251203.txt") -> List[Dict]:
    """saramin_job_summary 파일을 파싱하여 채용공고 리스트 반환"""
    jobs = []
    # 프로젝트 루트에서 파일 찾기
    project_root = Path(__file__).parent.parent
    txt_path = project_root / file_path
    
    if not txt_path.exists():
        print(f"⚠️  {file_path} 파일을 찾을 수 없습니다: {txt_path}")
        return jobs
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # "[공고 #"로 시작하는 섹션을 찾아서 구분
    pattern = r'\[공고\s*#(\d+)\](.*?)(?=\[공고\s*#\d+\]|$)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    job_sections = []
    for match in matches:
        section_content = match.group(0)
        job_sections.append(section_content)
    
    print(f"📄 총 {len(job_sections)}개의 공고 섹션 발견")
    
    for section_idx, section in enumerate(job_sections, 1):
        if not section.strip():
            continue
        
        job = {
            "title": "",
            "company": "",
            "location": "",
            "job_type": "",
            "company_size": "",
            "industry": "",
            "work": "",
            "requirements": "",
            "conditions": "",
            "benefits": "",
            "url": "",
            "full_text": section.strip()
        }
        
        lines = section.split('\n')
        current_section = None
        
        for line in lines:
            original_line = line
            line = line.strip()
            if not line:
                continue
            
            # 섹션 헤더 감지 (들여쓰기 무시)
            stripped_for_header = line.lstrip()
            if re.match(r'^1\.\s*채용\s*제목', stripped_for_header) or \
               re.match(r'^1\.\s*포지션', stripped_for_header) or \
               re.match(r'^1\.\s*채용\s*제목/포지션', stripped_for_header):
                current_section = "title"
                continue
            elif re.match(r'^2\.\s*회사명', stripped_for_header):
                current_section = "company"
                continue
            elif re.match(r'^3\.\s*주요\s*업무', stripped_for_header):
                current_section = "work"
                continue
            elif re.match(r'^4\.\s*자격\s*요건', stripped_for_header):
                current_section = "requirements"
                continue
            elif re.match(r'^5\.\s*근무\s*조건', stripped_for_header):
                current_section = "conditions"
                continue
            elif re.match(r'^6\.\s*급여', stripped_for_header):
                current_section = "benefits"
                continue
            elif re.match(r'^9\.\s*기업\s*정보', stripped_for_header):
                current_section = "company_info"
                continue
            elif re.match(r'^10\.\s*채용공고\s*링크', stripped_for_header):
                current_section = "url"
                continue
            
            # URL이 헤더에 있는 경우
            if "URL:" in line and not job["url"]:
                url_match = re.search(r'URL:\s*(https?://[^\s]+)', line)
                if url_match:
                    job["url"] = url_match.group(1).strip()
            
            # 항목 내용 추출 (들여쓰기된 "- " 또는 "* "로 시작하는 줄)
            stripped_line = line.lstrip()
            if (stripped_line.startswith('-') or stripped_line.startswith('*')) and current_section:
                item = re.sub(r'^[*-]\s*', '', stripped_line).strip()
                if not item:
                    continue
                
                if current_section == "title" and not job["title"]:
                    job["title"] = item
                elif current_section == "company" and not job["company"]:
                    job["company"] = item
                elif current_section == "work":
                    if job["work"]:
                        job["work"] += " " + item
                    else:
                        job["work"] = item
                elif current_section == "requirements":
                    if job["requirements"]:
                        job["requirements"] += " " + item
                    else:
                        job["requirements"] = item
                elif current_section == "conditions":
                    if job["conditions"]:
                        job["conditions"] += " " + item
                    else:
                        job["conditions"] = item
                    # 지역 추출
                    if "지역:" in item or "지역" in item:
                        location_match = re.search(r'지역[:\s]*([^,\n]+)', item)
                        if location_match:
                            job["location"] = location_match.group(1).strip()
                    # 고용 형태 추출
                    if "형태:" in item or "형태" in item:
                        type_match = re.search(r'형태[:\s]*([^,\n]+)', item)
                        if type_match:
                            job["job_type"] = type_match.group(1).strip()
                elif current_section == "benefits":
                    if job["benefits"]:
                        job["benefits"] += " " + item
                    else:
                        job["benefits"] = item
                elif current_section == "company_info":
                    if "업종:" in item:
                        industry_match = re.search(r'업종[:\s]*([^\n]+)', item)
                        if industry_match:
                            job["industry"] = industry_match.group(1).strip()
                    if "기업형태:" in item or "기업 형태:" in item:
                        size_match = re.search(r'기업\s*형태[:\s]*([^\n]+)', item)
                        if size_match:
                            job["company_size"] = size_match.group(1).strip()
                elif current_section == "url" and "http" in item:
                    job["url"] = item.strip()
        
        # URL이 공고 헤더에 있는 경우
        if not job["url"]:
            url_match = re.search(r'URL:\s*(https?://[^\s]+)', section)
            if url_match:
                job["url"] = url_match.group(1).strip()
        
        # 제목과 회사명이 있는 경우만 추가
        if job["title"] and job["company"]:
            jobs.append(job)
            print(f"  ✅ 공고 #{section_idx} 파싱 완료: {job['title']} - {job['company']}")
        else:
            print(f"  ⚠️  공고 #{section_idx} 스킵: 제목='{job['title']}', 회사명='{job['company']}'")
            print(f"  📄 섹션 샘플 (처음 500자):\n{section[:500]}")
    
    print(f"✅ {file_path}에서 {len(jobs)}개의 채용공고를 파싱했습니다.")
    return jobs

