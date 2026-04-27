---
marp: true
theme: default
paginate: true
backgroundColor: "#1a1a2e"
color: "#e2e8f0"
style: |
  section {
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
    font-size: 28px;
    padding: 48px 64px;
  }
  section.lead {
    text-align: center;
    justify-content: center;
  }
  h1 { color: #a78bfa; font-size: 2em; margin-bottom: 0.3em; }
  h2 { color: #7dd3fc; font-size: 1.4em; border-bottom: 2px solid #6C63FF; padding-bottom: 8px; }
  h3 { color: #86efac; font-size: 1.1em; }
  strong { color: #fbbf24; }
  table { width: 100%; border-collapse: collapse; font-size: 0.8em; }
  th { background: #312e81 !important; color: #e0d7ff !important; padding: 8px 12px; border: 1px solid #4c3fbd; }
  td { background: #1e1b4b !important; color: #e2e8f0 !important; padding: 8px 12px; border: 1px solid #2d2d55; }
  tr:nth-child(even) td { background: #25225e !important; }
  table strong { color: #fbbf24; }
  code { background: #2d2d44; color: #86efac; padding: 2px 6px; border-radius: 4px; }
  ul { line-height: 1.9; }
  .tag { background: #6C63FF; color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 0.75em; margin-right: 6px; }
  .blocked { color: #f87171; font-weight: bold; }
  .score { color: #34d399; font-weight: bold; }
---

<!-- _class: lead -->
<!-- slide: 01-intro -->

# 요가큐

### AI 기반 요가 포즈 매칭 & 안전 필터 플랫폼

<br>

**match.yogaman.club**  
elbee.yogaman.club

<br>

> 수련자의 신체 조건과 목표에 맞는  
> **안전하고 정확한** 포즈 추천 시스템

---

<!-- slide: 02-agenda -->

## 발표 순서

<br>

1. **프로젝트 배경** — 문제 정의
2. **기존 플랫폼 분석** — 검색·소셜 미디어 / 예약 플랫폼
3. **차별점** — 5대 한계와 해결 방향
4. **활용 데이터** — 포즈 DB · Q&A · OCR
5. **기술 스택** — Spring Boot · FastAPI · RAG
6. **주요 기능 시연**
7. **트러블슈팅** — 4가지 핵심 문제 해결
8. **향후 개선 방향**

---

<!-- slide: 03-background -->

## 프로젝트 배경

<br>

### 수련자의 안전 공백

- 허리 디스크·무릎 부상·고혈압 — 검증되지 않은 콘텐츠로 **부상 악화**
- "초보자 요가" 검색 → 척추 부담 포즈 상위 노출

### 강사의 디지털 가시성 부재

- 인스타그램은 고품질 프로필로 **포화 상태**  
  → 단편적 게시물만으로 전문성·자격 구별 불가
- 20년 경력 강사도 **파편화된 SNS 속에 묻혀** 신뢰 신호 전달 못함

<br>

> ⚡ **두 문제를 동시에 해결하는 신뢰 기반 AI 매칭 플랫폼**이 필요하다

---

<!-- slide: 04-platforms-social -->

## 기존 플랫폼 분석 ① — 검색·소셜 미디어

| 채널 | 장점 | 한계 |
|------|------|------|
| 네이버·구글 | 콘텐츠 양, 접근성 | 상위 = 광고·블로그, 신체 조건 미반영 |
| 유튜브 | 풍부한 영상 콘텐츠 | 조회수 중심 알고리즘 → 자격 무관 노출 |
| 인스타그램 | 실시간 강사 활동 확인 | 프로필 포화 → 전문성 구별 불가 |

<br>

### 공통 문제

<span class="blocked">❌ 금기 포즈 필터링 기능 전혀 없음</span>  
→ 부상자에게 오히려 위험한 콘텐츠 추천

---

<!-- slide: 05-platforms-booking -->

## 기존 플랫폼 분석 ② — 예약 마켓플레이스

**Mindbody · ClassPass**

✅ 장점
- 스튜디오 검색·예약 편의성 높음
- 글로벌 네트워크 보유

❌ 한계
- 단순 예약 인터페이스 — **건강 상태·목표 기반 추천 없음**
- Schema.org 구조화 데이터 미제공  
  → Gemini · SearchGPT · Perplexity **AI 검색엔진 인용 불가**

---

<!-- slide: 06-differentiation -->

## 차별점 — 5대 한계 해결

| 기존 문제 | 요가큐 해결 방식 |
|-----------|-----------------|
| 안전성 판단 불가 | **Kill-Switch** 금기사항 하드 차단 |
| 강사 자격 불투명 | `instructor_trust_score` + Schema.org JSON-LD |
| 개인화 필터 없음 | 경험 레벨 · 가용 시간 · 목표 다중 필터 |
| AI 인용 불가 | FAQPage · HowTo · DefinedTerm JSON-LD 자동 생성 |
| 위치 매칭 없음 | Haversine 반경 쿼리 + 전문 분야 가중치 랭킹 |

---

<!-- slide: 07-data -->

## 활용 데이터

<br>

| 데이터 | 규모 | 활용 |
|--------|------|------|
| 요가 포즈 DB | **2,700+** 아사나 | E-E-A-T 메타데이터 enrichment → PostgreSQL |
| Q&A 학습 데이터 | **2,899** FAQ 쌍 | GPT-4o-mini 생성 → FAQPage JSON-LD |
| 강사·스튜디오 | 서울 10개소 | 위치 기반 매칭 + Person JSON-LD |
| OCR 교육 자료 | 전문 도서 | Tesseract → 벡터 임베딩 → RAG 챗봇 인용 |

<br>

> 856개 포즈 자연어 설명 · nomic-embed-text 임베딩 · mistral:latest 로컬 LLM

---

<!-- slide: 08-stack -->

## 기술 스택

<br>

**Backend**  
`Spring Boot 3.x` `Java 17` `Spring Data JPA` `Flyway` `PostgreSQL 16`

**AI Layer**  
`FastAPI` `Ollama (mistral · nomic-embed-text)` `GPT-4o-mini` `LangChain RAG`

**Frontend**  
`React 18` `Vite 5` `Streamlit` *(매칭 점수 시각화 · 안전 필터 데모)*

**Infra**  
`Docker Compose` `Caddy` `Cloudflare Tunnel` `GitHub Actions CI`

**API Docs**  
`SpringDoc OpenAPI` → `match.yogaman.club/swagger-ui.html`

---

<!-- slide: 09-features -->

## 주요 기능

### 수련자
- 자연어 입력 → AI 포즈 매칭 (`/api/v1/match`)
- **Kill-Switch**: 금기 포즈 자동 차단 + 사유 반환
- 경험 레벨 · 가용 시간 필터
- 위치 기반 강사·스튜디오 추천
- RAG 챗봇 자유 질문 (`/chat`)

### 강사·스튜디오
- Schema.org **Person JSON-LD** 자동 생성 (`/instructors/{id}/jsonld`)
- 포즈별 **FAQPage · HowTo · DefinedTerm** JSON-LD API
- 아티클 콘텐츠 관리 (`/articles`)

---

<!-- slide: 10-demo -->
<!-- _class: lead -->

# 🎬 시연

<br>

**match.yogaman.club**

<br>

매칭 시연 → RAG 챗봇 → JSON-LD AEO → 안전 필터

---

<!-- slide: 11-troubleshooting -->

## 트러블슈팅

**① 매칭 점수 항상 0.0**  
원인: UI 목표값(`Spinal_Mobility`) ≠ DB 태그 어휘(`mobility`, `back`)  
해결: `GOAL_TAG_MAP` — UI 목표 → DB 태그 확장 매핑 도입

**② Kill-Switch 하드 차단 미작동**  
원인: 단순 조건 확인으로는 severity 단계 차단 불가  
해결: `score=0, blocked=true` 고정 반환 + 차단 사유 명시

**③ JSON-LD `@type` 필드 누락**  
원인: Jackson `null` 필드 직렬화 예외  
해결: `NON_NULL` 설정 + `LinkedHashMap` 명시적 구성

**④ Streamlit 컨테이너 404**  
원인: `--server.baseUrlPath /safety` → 루트 `/` 미응답  
해결: baseUrlPath 제거 + Caddyfile `/safety*` → 8501 라우팅 추가

---

<!-- slide: 12-roadmap -->

## 향후 개선 방향

<br>

1. **예약 시스템 통합** — Mindbody·1club API → 매칭 → 예약 전환 풀 파이프라인

2. **AI 인용 범위 확대** — 전체 2,700 포즈 JSON-LD → Perplexity·Gemini 인용 빈도 확대

3. **수련 이력 기반 개인화** — 세션 이력 축적 → 점진적 난이도 조절 · 목표 추적

4. **모바일 앱 전환** — React Native 확장 → 더 넓은 사용자층 도달

<br>

> **수련의 전 여정을 아우르는 신뢰 기반 AI 매칭 플랫폼**

<br>

## 감사합니다
