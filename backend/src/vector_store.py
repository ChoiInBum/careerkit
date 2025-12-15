"""
벡터 스토어 관리 모듈
ChromaDB 벡터 스토어 초기화 및 관리
"""
from pathlib import Path
from typing import List, Dict, Optional

# 지연 로딩을 위해 모듈 레벨에서는 import하지 않음
CHROMADB_AVAILABLE = None
chromadb = None
SentenceTransformer = None

VECTOR_STORE = None
EMBEDDING_MODEL = None
_INITIALIZED = False


def _check_dependencies():
    """의존성 확인 및 지연 로딩"""
    global CHROMADB_AVAILABLE, chromadb, SentenceTransformer
    
    if CHROMADB_AVAILABLE is not None:
        return CHROMADB_AVAILABLE
    
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        CHROMADB_AVAILABLE = True
        return True
    except ImportError:
        CHROMADB_AVAILABLE = False
        chromadb = None
        SentenceTransformer = None
        return False


def initialize_vector_store_components(force_reload: bool = False):
    """벡터 스토어 및 임베딩 모델 초기화"""
    global VECTOR_STORE, EMBEDDING_MODEL, _INITIALIZED
    
    try:
        if not _check_dependencies():
            print("⚠️  chromadb 또는 sentence-transformers가 설치되지 않았습니다.")
            print("💡 실행: pip install chromadb sentence-transformers")
            _INITIALIZED = False
            return False
        
        # 임베딩 모델 초기화
        print("📦 임베딩 모델 로드 중...")
        EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ 임베딩 모델 로드 완료: paraphrase-multilingual-MiniLM-L12-v2")
        
        # ChromaDB 클라이언트 초기화 (프로젝트 루트 기준)
        project_root = Path(__file__).parent.parent
        chroma_db_path = project_root / "chroma_db"
        print(f"📁 ChromaDB 경로: {chroma_db_path}")
        
        chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))
        
        # 강제 재로드인 경우 기존 컬렉션 삭제
        if force_reload:
            try:
                chroma_client.delete_collection(name="saramin_jobs")
                print("🔄 기존 컬렉션 삭제 완료")
            except Exception as e:
                print(f"ℹ️  기존 컬렉션 삭제 시도 (없을 수 있음): {e}")
        
        VECTOR_STORE = chroma_client.get_or_create_collection(
            name="saramin_jobs",
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ ChromaDB 벡터 스토어 초기화 완료")
        
        # 초기화 상태 확인
        if VECTOR_STORE is not None:
            try:
                count = VECTOR_STORE.count()
                print(f"📊 현재 벡터 스토어 문서 수: {count}개")
            except AttributeError as e:
                print(f"⚠️  VECTOR_STORE에 count() 메서드가 없습니다: {e}")
            except Exception as e:
                print(f"⚠️  벡터 스토어 카운트 확인 실패: {e}")
        else:
            print("⚠️  VECTOR_STORE가 None입니다.")
        
        _INITIALIZED = True
        return True
        
    except Exception as e:
        print(f"❌ 벡터 스토어 초기화 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        _INITIALIZED = False
        VECTOR_STORE = None
        EMBEDDING_MODEL = None
        return False


def is_vector_store_initialized() -> bool:
    """벡터 스토어 초기화 상태 확인"""
    global VECTOR_STORE, EMBEDDING_MODEL, _INITIALIZED
    result = _INITIALIZED and VECTOR_STORE is not None and EMBEDDING_MODEL is not None
    if not result:
        print(f"🔍 is_vector_store_initialized() 체크:")
        print(f"   - _INITIALIZED: {_INITIALIZED}")
        print(f"   - VECTOR_STORE is None: {VECTOR_STORE is None}")
        print(f"   - EMBEDDING_MODEL is None: {EMBEDDING_MODEL is None}")
    return result


def initialize_vector_store(
    jobs: List[Dict], 
    chunk_size: int = 0, 
    force_reload: bool = False,
    window_size: int = 500,
    stride: int = 200
) -> bool:
    """채용공고를 window + stride 방식으로 청킹하여 벡터 스토어에 저장
    
    Args:
        jobs: 채용공고 리스트
        chunk_size: 레거시 파라미터 (0이면 window+stride 방식 사용, 호환성 유지)
        force_reload: 기존 데이터 강제 재로드 여부
        window_size: 청크 크기 (기본값: 500자)
        stride: 오버랩 크기 (기본값: 200자, 실제 이동 거리 = window_size - stride = 300자)
    
    Note:
        - window_size: 각 청크의 크기 (500자)
        - stride: 오버랩 크기 (200자) - 이전 청크와 겹치는 부분
        - 실제 이동 거리: window_size - stride = 300자
        - 예: 1000자 텍스트 → 청크1(0-500), 청크2(300-800), 청크3(600-1000)
    """
    if not is_vector_store_initialized():
        print("⚠️  벡터 스토어 또는 임베딩 모델이 초기화되지 않았습니다.")
        print(f"   - _INITIALIZED: {_INITIALIZED}")
        print(f"   - VECTOR_STORE: {VECTOR_STORE is not None}")
        print(f"   - EMBEDDING_MODEL: {EMBEDDING_MODEL is not None}")
        return False
    
    # force_reload가 False인 경우에만 기존 데이터 확인 (채용공고만 확인)
    if not force_reload and VECTOR_STORE is not None:
        try:
            # 전체 문서 수 확인
            total_count = VECTOR_STORE.count()
            if total_count > 0:
                # 채용공고 문서만 카운트 (type이 'resume'이 아닌 것들)
                # ChromaDB에서 메타데이터로 필터링하여 채용공고만 확인
                try:
                    # 샘플 조회로 채용공고가 있는지 확인
                    sample_results = VECTOR_STORE.get(limit=100)
                    if sample_results and 'metadatas' in sample_results:
                        job_count = sum(1 for meta in sample_results['metadatas'] 
                                      if meta.get('type') != 'resume')
                        if job_count > 0:
                            print(f"✅ 벡터 스토어에 이미 채용공고 데이터가 저장되어 있습니다. (전체 문서: {total_count}개)")
                            return True
                except Exception:
                    # 필터링 실패 시 전체 카운트로 판단
                    if total_count > 10:  # 이력서는 보통 1개 정도이므로, 10개 이상이면 채용공고가 있다고 판단
                        print(f"✅ 벡터 스토어에 이미 데이터가 저장되어 있습니다. (문서 수: {total_count}개)")
                        return True
        except (AttributeError, Exception) as e:
            print(f"⚠️  기존 데이터 확인 중 오류 (무시하고 계속 진행): {e}")
    
    if not jobs:
        print("⚠️  파싱된 채용공고가 없습니다.")
        return False
    
    # 각 공고를 청킹하여 벡터화하여 저장
    documents = []
    metadatas = []
    ids = []
    
    for idx, job in enumerate(jobs):
        # 검색에 사용할 전체 텍스트 구성
        full_text = f"""
제목: {job.get('title', '')}
회사: {job.get('company', '')}
지역: {job.get('location', '')}
고용형태: {job.get('job_type', '')}
기업규모: {job.get('company_size', '')}
산업군: {job.get('industry', '')}
주요업무: {job.get('work', '')}
자격요건: {job.get('requirements', '')}
근무조건: {job.get('conditions', '')}
급여및복리후생: {job.get('benefits', '')}
전체내용: {job.get('full_text', '')}
""".strip()
        
        # window + stride 방식으로 청킹
        text_length = len(full_text)
        
        # stride가 window_size보다 크거나 같으면 오류
        if stride >= window_size:
            print(f"⚠️  stride({stride})가 window_size({window_size})보다 크거나 같습니다. stride를 {window_size // 2}로 조정합니다.")
            stride = window_size // 2
        
        # 실제 이동 거리 (overlap = stride, step = window_size - stride)
        step_size = window_size - stride
        
        if text_length <= window_size:
            # 공고가 window_size보다 작으면 하나의 문서로 저장
            if full_text.strip():
                documents.append(full_text)
                metadatas.append({
                    "title": job.get('title', ''),
                    "company": job.get('company', ''),
                    "location": job.get('location', ''),
                    "job_type": job.get('job_type', ''),
                    "company_size": job.get('company_size', ''),
                    "industry": job.get('industry', ''),
                    "url": job.get('url', ''),
                    "job_id": idx,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "chunk_start": 0,
                    "chunk_end": text_length,
                    "chunk_length": text_length,
                    "window_size": window_size,
                    "stride": stride,
                    "full_text": full_text,  # 전체 공고 텍스트 저장
                    "type": "job"
                })
                ids.append(f"job_{idx}_chunk_0")
        else:
            # window + stride 방식으로 청킹
            chunks = []
            start_idx = 0
            chunk_idx = 0
            
            while start_idx < text_length:
                end_idx = min(start_idx + window_size, text_length)
                chunk_text = full_text[start_idx:end_idx]
                
                # 빈 청크는 제외
                if chunk_text.strip():
                    chunks.append({
                        "text": chunk_text,
                        "start": start_idx,
                        "end": end_idx,
                        "index": chunk_idx
                    })
                    chunk_idx += 1
                
                # 다음 시작 위치로 이동 (step_size만큼 이동, overlap = stride)
                start_idx += step_size
                
                # 마지막 부분 처리: 남은 텍스트가 step_size보다 작으면 마지막 청크로 추가
                if start_idx < text_length and start_idx + step_size >= text_length:
                    # 마지막 부분이 남아있고, 아직 추가하지 않았으면 추가
                    if end_idx < text_length:
                        last_chunk = full_text[start_idx:]
                        if last_chunk.strip() and len(last_chunk) >= stride:  # 최소 stride 크기는 되어야 의미 있음
                            chunks.append({
                                "text": last_chunk,
                                "start": start_idx,
                                "end": text_length,
                                "index": chunk_idx
                            })
                    break
            
            # 청크 저장
            total_chunks = len(chunks)
            for chunk_info in chunks:
                documents.append(chunk_info["text"])
                metadatas.append({
                    "title": job.get('title', ''),
                    "company": job.get('company', ''),
                    "location": job.get('location', ''),
                    "job_type": job.get('job_type', ''),
                    "company_size": job.get('company_size', ''),
                    "industry": job.get('industry', ''),
                    "url": job.get('url', ''),
                    "job_id": idx,
                    "chunk_index": chunk_info["index"],
                    "total_chunks": total_chunks,
                    "chunk_start": chunk_info["start"],
                    "chunk_end": chunk_info["end"],
                    "chunk_length": len(chunk_info["text"]),
                    "window_size": window_size,
                    "stride": stride,
                    "full_text": full_text,  # 전체 공고 텍스트 저장 (모든 청크에 동일하게 저장)
                    "type": "job"
                })
                ids.append(f"job_{idx}_chunk_{chunk_info['index']}")
    
    # 임베딩 생성 및 저장
    print(f"📊 {len(documents)}개의 청크 임베딩 생성 중... (원본 공고: {len(jobs)}개)")
    embeddings = EMBEDDING_MODEL.encode(documents, show_progress_bar=True)
    
    # ChromaDB에 저장
    VECTOR_STORE.add(
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ 벡터 스토어에 {len(documents)}개의 청크를 저장했습니다. (원본 공고: {len(jobs)}개)")
    return True


def add_resume_to_vector_store(resume: Dict, session_id: str) -> bool:
    """이력서를 벡터 스토어에 저장"""
    if not VECTOR_STORE or not EMBEDDING_MODEL:
        print("⚠️  벡터 스토어 또는 임베딩 모델이 초기화되지 않았습니다.")
        return False
    
    # 이력서 텍스트 구성
    resume_text = f"""
이름: {resume.get('name', '')}
학력: {resume.get('education', [])}
경력: {resume.get('experience', [])}
기술 스택: {', '.join(resume.get('skills', []))}
자격증: {', '.join([c.get('name', '') for c in resume.get('certificates', [])])}
프로젝트: {', '.join([p.get('name', '') for p in resume.get('projects', [])])}
전체 내용: {resume.get('full_text', '')}
""".strip()
    
    if not resume_text.strip():
        return False
    
    # 임베딩 생성
    embedding = EMBEDDING_MODEL.encode([resume_text])
    
    # 벡터 스토어에 저장
    VECTOR_STORE.add(
        embeddings=embedding.tolist(),
        documents=[resume_text],
        metadatas=[{
            "type": "resume",
            "session_id": session_id,
            "name": resume.get('name', ''),
            "resume_id": session_id
        }],
        ids=[f"resume_{session_id}"]
    )
    
    print(f"✅ 이력서를 벡터 스토어에 저장했습니다. (session_id: {session_id})")
    return True


def search_vector_store(keywords: List[str], top_k: int = 10) -> List[Dict]:
    """벡터 스토어에서 키워드로 검색"""
    # 전역 변수 참조 (함수 내부에서 global 선언 필요)
    global VECTOR_STORE, EMBEDDING_MODEL
    
    print(f"\n  [search_vector_store] 시작: keywords={len(keywords)}개, top_k={top_k}")
    print(f"     - 키워드 리스트: {keywords[:5]}{'...' if len(keywords) > 5 else ''}")
    
    if not VECTOR_STORE or not EMBEDDING_MODEL:
        print("  ❌ [search_vector_store] VECTOR_STORE 또는 EMBEDDING_MODEL이 None입니다.")
        print(f"     - VECTOR_STORE: {VECTOR_STORE is not None}")
        print(f"     - EMBEDDING_MODEL: {EMBEDDING_MODEL is not None}")
        return []
    
    # 벡터 스토어에 데이터가 있는지 확인
    if VECTOR_STORE is None:
        print("  ❌ [search_vector_store] VECTOR_STORE가 None입니다.")
        return []
    
    try:
        doc_count = VECTOR_STORE.count()
        print(f"  📊 [search_vector_store] 벡터 스토어 문서 수: {doc_count}개")
        if doc_count == 0:
            print("  ❌ [search_vector_store] 벡터 스토어가 비어있습니다. 초기화가 필요합니다.")
            return []
    except AttributeError as e:
        print(f"  ❌ [search_vector_store] VECTOR_STORE에 count() 메서드가 없습니다: {e}")
        return []
    except Exception as e:
        print(f"  ❌ [search_vector_store] 벡터 스토어 카운트 확인 중 오류: {e}")
        return []
    
    # 검색 쿼리 구성 (키워드 리스트를 하나의 텍스트로 결합)
    if not keywords:
        print("  ❌ [search_vector_store] 키워드 리스트가 비어있습니다.")
        return []
    
    query_text = " ".join(keywords)
    print(f"  🔍 [search_vector_store] 검색 쿼리 텍스트: {query_text[:200]}...")
    print(f"     - 키워드 개수: {len(keywords)}")
    print(f"     - 쿼리 길이: {len(query_text)} 문자")
    
    try:
        # 쿼리 임베딩 생성
        print(f"  ⏳ [search_vector_store] 임베딩 생성 중...")
        query_embedding = EMBEDDING_MODEL.encode([query_text])
        print(f"     - 임베딩 차원: {query_embedding.shape}")
        
        # 벡터 검색 (중복 제거를 위해 더 많이 가져오기)
        n_results = min(top_k * 2, doc_count)  # 문서 수보다 많이 요청하지 않도록
        print(f"  🔍 [search_vector_store] 벡터 검색 실행: n_results={n_results}")
        
        # query_embedding은 (1, 384) 형태이므로, tolist()하면 [[...]] 형태가 됨
        # ChromaDB는 query_embeddings에 리스트의 리스트를 기대하므로 그대로 사용
        embedding_list = query_embedding.tolist()
        print(f"     - 임베딩 리스트 형태: {len(embedding_list)}개 리스트, 각 {len(embedding_list[0]) if embedding_list else 0}차원")
        
        results = VECTOR_STORE.query(
            query_embeddings=embedding_list,  # 이미 [[...]] 형태이므로 그대로 전달
            n_results=n_results
        )
        
        raw_result_count = len(results.get('ids', [[]])[0]) if results.get('ids') else 0
        print(f"  📊 [search_vector_store] 벡터 검색 원시 결과: {raw_result_count}개")
        
        # 결과 변환 (중복 제거 없이 모든 chunk 반환)
        search_results = []
        resume_count = 0
        
        if results.get('ids') and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                doc_type = metadata.get('type', 'unknown')
                
                # 이력서는 제외하고 채용공고만 포함
                if doc_type == 'resume':
                    resume_count += 1
                    continue
                
                # 모든 chunk를 반환 (중복 제거 없음)
                search_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": metadata,
                    "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                })
        
        print(f"  ✅ [search_vector_store] 최종 검색 결과: {len(search_results)}개 chunk (중복 제거 없음)")
        if resume_count > 0:
            print(f"     - 제외된 이력서: {resume_count}개")
        
        return search_results
        
    except Exception as e:
        print(f"  ❌ [search_vector_store] 벡터 검색 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []

