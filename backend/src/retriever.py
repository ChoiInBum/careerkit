"""
Retriever 모듈: 이력서와 챗봇 정보를 기반으로 유사 공고 추출
"""
from typing import List, Dict
from difflib import SequenceMatcher


def extract_experience_keyword(resume: Dict) -> str:
    """이력서에서 경력 정보를 추출하여 키워드 반환 (신입/경력)
    
    Args:
        resume: 이력서 딕셔너리
    
    Returns:
        "신입" 또는 "경력"
    """
    if not resume:
        return "신입"
    
    experience = resume.get('experience', [])
    
    # 경력 정보가 없거나 비어있으면 신입
    if not experience or len(experience) == 0:
        return "신입"
    
    # 경력 정보가 있으면 경력
    return "경력"


def build_weighted_query(resume: Dict, slots: Dict) -> tuple[List[str], Dict[str, float]]:
    """챗봇 정보와 이력서 경력 정보를 사용하여 가중치가 적용된 검색 쿼리 구성 (최대 5개)
    
    Returns:
        tuple: (query_keywords, keyword_weights)
    """
    query_keywords = []
    keyword_weights = {}  # 키워드별 중요도
    
    # 챗봇 정보 사용
    if slots:
        desired_job = slots.get('desired_job', '').strip()
        if desired_job:
            query_keywords.append(desired_job)
            keyword_weights[desired_job] = 3.0
        
        location = slots.get('location', '').strip()
        if location:
            query_keywords.append(location)
            keyword_weights[location] = 2.5
        
        job_type = slots.get('job_type', '').strip()
        if job_type:
            query_keywords.append(job_type)
            keyword_weights[job_type] = 2.0
        
        industry = slots.get('industry', '').strip()
        if industry:
            query_keywords.append(industry)
            keyword_weights[industry] = 2.0
        
        company_size = slots.get('company_size', '').strip()
        if company_size:
            query_keywords.append(company_size)
            keyword_weights[company_size] = 1.5
    
    # 이력서에서 경력 키워드 추출
    experience_keyword = extract_experience_keyword(resume)
    if experience_keyword:
        query_keywords.append(experience_keyword)
        keyword_weights[experience_keyword] = 2.5  # 경력 정보는 높은 가중치
    
    # 최대 5개로 제한 (경력 키워드 포함)
    query_keywords = query_keywords[:5]
    keyword_weights = {k: v for k, v in keyword_weights.items() if k in query_keywords}
    
    return query_keywords, keyword_weights


def calculate_string_similarity(str1: str, str2: str) -> float:
    """두 문자열의 유사도를 계산 (0.0 ~ 1.0)"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def find_similar_keywords(keyword: str, text: str, threshold: float = 0.6) -> List[str]:
    """텍스트에서 유사한 키워드를 찾기 (유사 의미까지 인정)
    
    Args:
        keyword: 검색할 키워드
        text: 검색 대상 텍스트
        threshold: 유사도 임계값 (0.0 ~ 1.0)
    
    Returns:
        유사한 키워드 리스트
    """
    keyword_lower = keyword.lower()
    text_lower = text.lower()
    similar_keywords = []
    
    # 경력 관련 키워드의 유사 의미 매핑
    experience_synonyms = {
        "신입": ["신입사원", "신입 개발자", "신입자", "주니어", "junior", "newbie", 
                "신입 지원 가능", "신입 가능", "신입 환영", "신입 채용", "신입 모집",
                "경력 무관", "경력 제한 없음", "신입도 가능", "신입도 환영"],
        "경력": ["경력사원", "경력 개발자", "경력자", "시니어", "senior", "경력 채용",
                "경력 모집", "경력 우대", "경력 필수", "경력 3년", "경력 5년", 
                "경력 7년", "경력 10년", "경력직", "경력 인재"]
    }
    
    # 1. 정확한 매칭 (공백 제거 후)
    keyword_no_space = keyword_lower.replace(' ', '')
    if keyword_lower in text_lower or keyword_no_space in text_lower.replace(' ', ''):
        return [keyword]  # 정확한 매칭이 있으면 바로 반환
    
    # 2. 부분 문자열 매칭 (키워드가 텍스트에 포함되어 있는지)
    if keyword_lower in text_lower:
        return [keyword]
    
    # 3. 경력 관련 키워드의 경우 유사 의미 확인
    if keyword in experience_synonyms:
        synonyms = experience_synonyms[keyword]
        for synonym in synonyms:
            if synonym.lower() in text_lower:
                return [keyword]  # 유사 의미 발견 시 매칭으로 인정
    
    # 4. 단어 단위로 분리하여 유사도 계산
    text_words = text_lower.split()
    keyword_words = keyword_lower.split()
    
    # 키워드의 각 단어가 텍스트에 있는지 확인
    matched_words = []
    for kw_word in keyword_words:
        for text_word in text_words:
            similarity = calculate_string_similarity(kw_word, text_word)
            if similarity >= threshold:
                matched_words.append(text_word)
                break
    
    # 키워드의 모든 단어가 매칭되면 유사 키워드로 인정
    if len(matched_words) >= len(keyword_words) * 0.7:  # 70% 이상 매칭
        return [keyword]
    
    # 5. 텍스트의 각 단어와 키워드의 유사도 계산
    for text_word in text_words:
        if len(text_word) < 2:  # 너무 짧은 단어는 제외
            continue
        similarity = calculate_string_similarity(keyword_lower, text_word)
        if similarity >= threshold:
            similar_keywords.append(text_word)
    
    return similar_keywords if similar_keywords else []


def calculate_weighted_score(result: Dict, keyword_weights: Dict[str, float], query_keywords: List[str]) -> tuple:
    """벡터 유사도와 키워드 가중치를 결합한 최종 점수 계산 (유사 키워드 매칭 포함)
    
    Args:
        result: search_vector_store에서 반환된 결과 딕셔너리
        keyword_weights: 키워드별 가중치 딕셔너리
        query_keywords: 검색 쿼리 키워드 리스트
    
    Returns:
        tuple: (final_score, matched_keywords)
    """
    # distance를 점수로 변환 (distance는 작을수록 유사도가 높음)
    # cosine distance는 0~2 범위이므로, 1 - (distance / 2)로 변환하여 0~1 범위의 점수로 만듦
    distance = result.get('distance', 1.0)
    vector_score = max(0.0, 1.0 - (distance / 2.0))  # 0~1 범위로 정규화
    
    # 공고 텍스트에서 키워드 매칭 보너스
    # metadata의 full_text를 우선 사용 (전체 공고 텍스트)
    metadata = result.get('metadata', {})
    
    # 1. metadata에서 full_text 가져오기 (전체 공고 텍스트)
    full_text = metadata.get('full_text', '')
    
    # 2. full_text가 없으면 구조화된 정보로 구성 (하위 호환성)
    if not full_text:
        # document 텍스트 (청크) - 하위 호환성
        job_text = result.get('document', '')
        
        # metadata에서 구조화된 정보
        metadata_text_parts = [
            metadata.get('title', ''),
            metadata.get('company', ''),
            metadata.get('location', ''),
            metadata.get('job_type', ''),
            metadata.get('company_size', ''),
            metadata.get('industry', ''),
        ]
        metadata_text = ' '.join([str(part) for part in metadata_text_parts if part])
        
        # 전체 텍스트 결합 (청크 + 메타데이터)
        full_text = f"{job_text} {metadata_text}"
    
    full_text_lower = full_text.lower()
    
    keyword_bonus = 0.0
    matched_keywords = []
    matched_details = {}  # 키워드별 매칭 상세 정보
    
    for keyword in query_keywords:
        keyword_lower = keyword.lower()
        weight = keyword_weights.get(keyword, 1.0)
        match_found = False
        match_type = None
        
        # 1. 정확한 매칭 (가장 높은 점수)
        if keyword_lower in full_text_lower:
            keyword_bonus += weight * 0.15  # 정확한 매칭은 더 높은 보너스
            matched_keywords.append(keyword)
            match_found = True
            match_type = "정확"
        
        # 2. 공백 제거 후 매칭
        elif keyword_lower.replace(' ', '') in full_text_lower.replace(' ', ''):
            keyword_bonus += weight * 0.12
            if keyword not in matched_keywords:
                matched_keywords.append(keyword)
            match_found = True
            match_type = "공백제거"
        
        # 3. 유사 키워드 매칭
        if not match_found:
            similar_keywords = find_similar_keywords(keyword, full_text, threshold=0.6)
            if similar_keywords:
                # 유사도에 따라 점수 조정
                similarity_score = 0.08  # 유사 매칭은 약간 낮은 보너스
                keyword_bonus += weight * similarity_score
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)
                match_type = f"유사({', '.join(similar_keywords[:2])})"
        
        # 매칭 상세 정보 저장
        if match_type:
            matched_details[keyword] = match_type
    
    # 최종 점수 = 벡터 유사도 + 키워드 매칭 보너스
    final_score = vector_score + keyword_bonus
    
    return final_score, matched_keywords


def retrieve_similar_jobs(resume: Dict, slots: Dict, top_k: int = 10) -> List[Dict]:
    """이력서와 챗봇 정보를 기반으로 유사 공고 추출 (Retriever)
    
    개선사항:
    - 복합 키워드 보존 (분리하지 않음)
    - 가중치 기반 점수 계산
    - 벡터 유사도 + 키워드 매칭 결합
    - 폴백 로직 제거 (단일 검색 전략)
    """
    print("\n" + "="*80)
    print("🔍 Retriever 시작")
    print("="*80)
    print("📝 입력 정보:")
    print(f"   - 이력서: {resume.get('name', 'N/A') if resume else 'None'}")
    print(f"   - 챗봇 정보: {slots}")
    
    # 함수 내부에서 최신 상태를 가져오기 위해 import
    from .vector_store import search_vector_store, EMBEDDING_MODEL, VECTOR_STORE
    
    if not VECTOR_STORE or not EMBEDDING_MODEL:
        print("❌ 벡터 스토어 또는 임베딩 모델이 초기화되지 않았습니다.")
        print(f"   - VECTOR_STORE: {VECTOR_STORE is not None}")
        print(f"   - EMBEDDING_MODEL: {EMBEDDING_MODEL is not None}")
        print("   💡 벡터 스토어가 초기화되지 않았습니다. 앱을 재시작하거나 /api/initialize-vector-store를 호출하세요.")
        return []
    
    try:
        # 가중치가 적용된 쿼리 구성
        print("\n📋 쿼리 구성 중...")
        query_keywords, keyword_weights = build_weighted_query(resume, slots)
        
        print(f"   - 키워드 리스트: {query_keywords}")
        print(f"   - 키워드 개수: {len(query_keywords)}")
        
        if not query_keywords:
            print("❌ 검색 키워드가 비어있습니다.")
            print(f"   - 이력서 정보: {bool(resume)}")
            print(f"   - 챗봇 정보: {slots}")
            return []
        
        print(f"\n🔍 검색 키워드: {query_keywords}")
        print(f"📊 키워드 가중치 ({len(keyword_weights)}개):")
        for keyword, weight in sorted(keyword_weights.items(), key=lambda x: x[1], reverse=True):
            print(f"   - '{keyword}': {weight}")
        
        # 통합 검색 (한 번의 벡터 검색으로 처리, 충분히 많은 chunk 가져오기)
        chunks_per_job = 3  # 각 공고에서 가져올 chunk 개수
        search_top_k = top_k * chunks_per_job * 2  # 충분히 많은 chunk 가져오기
        print(f"\n🔎 벡터 스토어 검색 실행 (top_k={search_top_k}, 공고당 {chunks_per_job}개 chunk)...")
        search_results = search_vector_store(query_keywords, top_k=search_top_k)
        
        print("\n📊 검색 결과:")
        print(f"   - 반환된 chunk 수: {len(search_results)}개")
        
        if not search_results:
            print("❌ 검색 결과가 없습니다.")
            print(f"   - 검색 키워드: {query_keywords}")
            print("   💡 벡터 스토어에 데이터가 있는지, 검색 키워드가 적절한지 확인하세요.")
            return []
        
        # job_id별로 chunk 그룹핑
        from collections import defaultdict
        job_chunks = defaultdict(list)
        
        for result in search_results:
            metadata = result.get('metadata', {})
            job_id = metadata.get('job_id')
            if job_id is not None:
                job_chunks[job_id].append(result)
        
        print(f"✅ 초기 검색 결과: {len(search_results)}개 chunk, {len(job_chunks)}개 공고")
        
        # 각 공고의 전체 텍스트(full_text)에서 키워드 매칭 확인
        print(f"\n📊 각 공고 전체에서 키워드 매칭 확인 중... ({len(job_chunks)}개 공고)")
        print(f"   검색 키워드 (5개): {query_keywords}")
        job_scores = {}  # job_id -> (최종 점수, matched_keywords, chunks)
        
        for job_id, chunks in job_chunks.items():
            try:
                # 공고의 full_text 가져오기 (첫 번째 chunk의 metadata에서)
                if not chunks:
                    continue
                
                first_chunk_metadata = chunks[0].get('metadata', {})
                full_text = first_chunk_metadata.get('full_text', '')
                
                # full_text가 없으면 구조화된 정보로 구성
                if not full_text:
                    metadata_text_parts = [
                        first_chunk_metadata.get('title', ''),
                        first_chunk_metadata.get('company', ''),
                        first_chunk_metadata.get('location', ''),
                        first_chunk_metadata.get('job_type', ''),
                        first_chunk_metadata.get('company_size', ''),
                        first_chunk_metadata.get('industry', ''),
                    ]
                    metadata_text = ' '.join([str(part) for part in metadata_text_parts if part])
                    # 모든 chunk의 document 결합
                    all_chunk_texts = ' '.join([chunk.get('document', '') for chunk in chunks])
                    full_text = f"{metadata_text} {all_chunk_texts}"
                
                # 공고 전체 텍스트에서 키워드 매칭 확인
                full_text_lower = full_text.lower()
                matched_keywords = []
                matched_count = 0
                
                for keyword in query_keywords:
                    keyword_lower = keyword.lower()
                    # 정확한 매칭 확인
                    if keyword_lower in full_text_lower:
                        matched_keywords.append(keyword)
                        matched_count += 1
                    # 공백 제거 후 매칭 확인
                    elif keyword_lower.replace(' ', '') in full_text_lower.replace(' ', ''):
                        if keyword not in matched_keywords:
                            matched_keywords.append(keyword)
                            matched_count += 1
                    # 유사 키워드 매칭 확인
                    else:
                        similar_keywords = find_similar_keywords(keyword, full_text, threshold=0.6)
                        if similar_keywords and keyword not in matched_keywords:
                            matched_keywords.append(keyword)
                            matched_count += 1
                
                # 각 chunk의 점수 계산 (벡터 유사도 기반)
                chunk_scores = []
                for chunk in chunks:
                    distance = chunk.get('distance', 1.0)
                    vector_score = max(0.0, 1.0 - (distance / 2.0))
                    chunk_scores.append({
                        'chunk': chunk,
                        'score': vector_score
                    })
                
                # chunk들을 점수 기준으로 정렬
                chunk_scores.sort(key=lambda x: x['score'], reverse=True)
                
                # 상위 N개 chunk 선택
                top_chunks = chunk_scores[:chunks_per_job]
                
                # 공고의 최종 점수 = 상위 chunk들의 평균 벡터 점수 + 키워드 매칭 보너스
                if top_chunks:
                    avg_vector_score = sum(c['score'] for c in top_chunks) / len(top_chunks)
                    # 키워드 매칭 보너스: 매칭된 키워드 개수에 비례
                    keyword_bonus = sum(keyword_weights.get(kw, 1.0) * 0.1 for kw in matched_keywords)
                    final_score = avg_vector_score + keyword_bonus
                else:
                    final_score = 0.0
                
                job_scores[job_id] = {
                    'final_score': final_score,
                    'matched_keywords': matched_keywords,
                    'matched_count': matched_count,  # 매칭된 키워드 개수
                    'total_keywords': len(query_keywords),  # 전체 키워드 개수
                    'chunks': [c['chunk'] for c in top_chunks],
                    'chunk_count': len(top_chunks),
                    'total_chunks': len(chunks)
                }
                
                # 매칭 결과 출력 (각 공고마다 몇 개의 키워드가 포함되는지)
                matched_str = ', '.join(matched_keywords) if matched_keywords else '(없음)'
                print(f"   공고 {job_id}: {matched_count}/{len(query_keywords)}개 키워드 매칭")
                print(f"      → 매칭된 키워드: {matched_str}")
                
            except Exception as e:
                print(f"   ⚠️  공고 {job_id} 처리 중 오류: {e}")
                continue
        
        if not job_scores:
            print("❌ 점수 계산 후 결과가 없습니다.")
            return []
        
        # 최종 점수 기준으로 정렬
        sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1]['final_score'], reverse=True)
        
        # 상위 결과 출력 (매칭 개수 기준으로도 정렬 가능)
        print(f"\n📈 상위 {min(5, len(sorted_jobs))}개 공고 (점수 기준):")
        print("=" * 80)
        for i, (job_id, job_data) in enumerate(sorted_jobs[:5], 1):
            final_score = job_data['final_score']
            matched = job_data['matched_keywords']
            matched_count = job_data['matched_count']
            total_keywords = job_data['total_keywords']
            chunk_count = job_data['chunk_count']
            
            print(f"{i}. 공고 ID: {job_id}")
            print(f"   최종 점수: {final_score:.3f} (상위 {chunk_count}개 chunk 평균)")
            print(f"   키워드 매칭: {matched_count}/{total_keywords}개")
            if matched:
                print(f"   매칭된 키워드: {', '.join(matched)}")
            else:
                print("   매칭된 키워드: (없음)")
            print()
        print("=" * 80)
        
        # 매칭 개수 기준 정렬 (비교용) - 공고마다 몇 개의 키워드가 포함되는지 비교
        sorted_by_match = sorted(job_scores.items(), key=lambda x: (x[1]['matched_count'], x[1]['final_score']), reverse=True)
        print(f"\n📊 매칭 개수 기준 상위 {min(5, len(sorted_by_match))}개 공고 (키워드 포함 개수 비교):")
        print("=" * 80)
        for i, (job_id, job_data) in enumerate(sorted_by_match[:5], 1):
            matched_count = job_data['matched_count']
            total_keywords = job_data['total_keywords']
            matched = job_data['matched_keywords']
            final_score = job_data['final_score']
            
            print(f"{i}. 공고 ID: {job_id}")
            print(f"   키워드 매칭: {matched_count}/{total_keywords}개 포함")
            if matched:
                print(f"   매칭된 키워드: {', '.join(matched)}")
            else:
                print("   매칭된 키워드: (없음)")
            print(f"   최종 점수: {final_score:.3f}")
            print()
        print("=" * 80)
        
        # 전체 공고별 매칭 개수 요약
        print("\n📋 전체 공고별 키워드 매칭 요약:")
        print("=" * 80)
        match_count_distribution = {}
        for job_id, job_data in job_scores.items():
            count = job_data['matched_count']
            match_count_distribution[count] = match_count_distribution.get(count, 0) + 1
        
        for count in sorted(match_count_distribution.keys(), reverse=True):
            job_num = match_count_distribution[count]
            print(f"   {count}/{total_keywords}개 매칭: {job_num}개 공고")
        print("=" * 80)
        
        # 상위 top_k개 공고 반환 (각 공고의 상위 chunk들 포함)
        final_results = []
        for job_id, job_data in sorted_jobs[:top_k]:
            # 대표 chunk 선택 (가장 점수가 높은 chunk)
            if job_data['chunks']:
                representative_chunk = job_data['chunks'][0].copy()
                # 메타데이터에 통합 정보 추가
                representative_chunk['metadata']['final_score'] = job_data['final_score']
                representative_chunk['metadata']['matched_keywords'] = job_data['matched_keywords']
                representative_chunk['metadata']['match_count'] = job_data['matched_count']  # 매칭된 키워드 개수
                representative_chunk['metadata']['total_keywords'] = job_data['total_keywords']  # 전체 키워드 개수
                representative_chunk['metadata']['chunk_count'] = job_data['chunk_count']
                representative_chunk['metadata']['total_chunks'] = job_data['total_chunks']
                final_results.append(representative_chunk)
        
        print(f"\n✅ Retriever 완료: {len(final_results)}개 공고 반환 (각 공고당 평균 {sum(job_scores[jid]['chunk_count'] for jid, _ in sorted_jobs[:top_k]) / len(final_results) if final_results else 0:.1f}개 chunk)")
        print("="*80 + "\n")
        return final_results
        
    except Exception as e:
        print(f"❌ Retriever 오류: {e}")
        import traceback
        traceback.print_exc()
        return []
