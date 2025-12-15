"""
Reranker 모듈: 추출된 공고들을 정밀하게 재순위화
"""
from typing import List, Dict


def rerank_jobs(resume: Dict, slots: Dict, retrieved_jobs: List[Dict], all_jobs: List[Dict]) -> List[Dict]:
    """추출된 공고들을 정밀하게 재순위화 (Reranker) - 벡터 거리로만 정렬"""
    reranked_jobs = []
    
    if not retrieved_jobs or not all_jobs:
        return []
    
    # job_dict 생성 (job_id로 빠른 조회)
    job_dict = {idx: job for idx, job in enumerate(all_jobs)}
    
    seen_job_ids = set()  # 중복 제거
    jobs_with_distance = []  # 거리와 함께 저장
    
    for result in retrieved_jobs:
        if not isinstance(result, dict):
            continue
            
        metadata = result.get("metadata", {})
        if not isinstance(metadata, dict):
            continue
            
        job_id = metadata.get("job_id")
        
        # job_id가 None이거나 이미 처리한 경우 스킵
        if job_id is None:
            continue
        
        # job_id를 정수로 변환 시도
        try:
            job_id = int(job_id)
        except (ValueError, TypeError):
            continue
        
        # 중복 제거
        if job_id in seen_job_ids:
            continue
        seen_job_ids.add(job_id)
        
        # job_dict에서 공고 찾기
        if job_id not in job_dict:
            continue
        
        job = job_dict[job_id].copy()
        
        # 벡터 거리 가져오기 (낮을수록 유사함)
        vector_distance = result.get("distance", 1.0)
        
        # 키워드 매칭 정보 가져오기 (retriever에서 계산된 정보)
        matched_keywords = metadata.get("matched_keywords", [])
        match_count = metadata.get("match_count", 0)
        total_keywords = metadata.get("total_keywords", 5)
        final_score = metadata.get("final_score", 0.0)
        
        # job 객체에 키워드 매칭 정보 추가
        job["matched_keywords"] = matched_keywords
        job["match_count"] = match_count
        job["total_keywords"] = total_keywords
        job["match_score"] = final_score
        
        jobs_with_distance.append((job, vector_distance, match_count))
    
    # 매칭 개수가 많은 순서대로 정렬 (매칭 개수가 같으면 벡터 거리로 정렬)
    # match_count는 높을수록 좋으므로 -match_count로 정렬 (내림차순)
    # vector_distance는 낮을수록 좋으므로 그대로 사용 (오름차순)
    jobs_with_distance.sort(key=lambda x: (-x[2], x[1]))
    
    # 점수 없이 공고만 반환
    reranked_jobs = [job for job, _, _ in jobs_with_distance]
    
    return reranked_jobs

