# 요가 매칭 큐레이터 — 엔지니어링 빌드 덱
> **프로젝트:** `aiegoo/aeogeo`  ·  **브랜드:** `elbee.yogaman.club`  ·  **기준일:** 2026-04-26

---

## ▌ 0. 프로젝트 한 줄 정의

> **"요가 추천을 AI 인용 소스로 만드는 프로덕션급 매칭 플랫폼"**

프로젝트가 해결하는 네 가지 문제:

| 문제 | 해결 방식 |
|------|-----------|
| 매칭 점수가 항상 0 반환 | `GOAL_TAG_MAP`으로 UI 목표값 → DB 태그 어휘 확장 |
| 의료 금기 포즈가 추천됨 | 킬스위치 하드 차단 — 점수 0, 차단 사유 명시 반환 |
| AI 검색 엔진이 사이트를 인용하지 않음 | FAQPage + WebSite JSON-LD 이중 삽입 |
| "근처 스튜디오" 검색 불가 | Haversine 공식으로 반경 내 스튜디오 거리순 반환 |

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         자기 강화 플라이휠                                 │
│                                                                          │
│  공급 레이어              매칭 엔진                수요 레이어              │
│  ──────────              ──────────              ──────────              │
│  포즈 2700+   ─────────► 킬스위치 필터 ──────────► 사용자 세션             │
│  스튜디오 10  ─────────► 신뢰점수 랭킹 ──────────► 예약 전환              │
│  서울 강사 10 ─────────► 반경 내 검색  ──────────► 스튜디오 예약           │
│       │                      │                       │                  │
│       ▼                      ▼                       ▼                  │
│  Schema.org JSON-LD ───► AI 검색 인용 ──────────► 자연 유입              │
│  (HowTo / FAQPage)       Perplexity · Gemini      elbee.yogaman.club    │
│                          SearchGPT                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## ▌ 1. 인프라 스택

### 1-a. 런타임 레이어

| 레이어 | 기술 | 포트 | 비고 |
|--------|------|------|------|
| API 서버 | Spring Boot 3.2.2 / Java 17 | 19090 | Docker, Windows 호스트 |
| AI 파이프라인 | FastAPI / Python 3.11 | 8000 | `.venv` 로컬 |
| 프론트엔드 | Vite + React 18 | 5173 | `/api/v1` → 19090 프록시 |
| DB | PostgreSQL 16 | 5432 | Docker, Windows 호스트 |
| LLM | Ollama `mistral:latest` | 11434 | 로컬 추론 |
| 임베딩 | `nomic-embed-text` | 11434 | Ollama 공유 인스턴스 |

### 1-b. 빌드 도구

- **Maven Wrapper** (`./mvnw`) — Spring Boot 컴파일 + 패키징
- **Flyway** — V1–V6 마이그레이션 자동 실행 (앱 기동 시)
- **pip** — FastAPI 의존성 (`requirements.txt` / `requirements-api.txt`)

---

## ▌ 2. 저장소 레이아웃

```
aeogeo/
├── yoga-api/                 # Spring Boot 백엔드
│   ├── src/main/java/        # 도메인: pose, studio, session, matching, instructor
│   ├── src/main/resources/db/migration/   # V1–V6 Flyway SQL
│   └── src/test/             # 통합 테스트 (StudioControllerIT 등)
├── app/                      # FastAPI AI 레이어
│   ├── services/             # rag_service, search_service, agent, llm_service
│   └── api/                  # /search, /chat 엔드포인트
├── content/                  # OCR 파이프라인 원본 마크다운
├── data/                     # JSON 시드 (요가 위치, 포즈)
├── scripts/                  # 배치 스크립트 (enrich_poses, integrate 등)
├── ENGINEERING_DECK.md       # 영문 빌드 덱
└── ENGINEERING_DECK_KO.md    # 본 문서
```

---

## ▌ 3. Flyway 마이그레이션 타임라인

```
V1  스키마 생성   : poses, benefits, contraindications, educational_metadata
V2  포즈 시드     : 2700+ 포즈 초기 데이터 삽입
V3  instructors  : instructors 테이블 추가
V4  sessions     : sessions 테이블 추가
V5  스튜디오/세션 시드 : 5개 도시, 10개 스튜디오, 16개 세션
V6  서울 강사 시드 : 10명, 사전 계산된 신뢰점수 포함
```

앱 기동 시 Flyway가 순서대로 실행한다. 멱등 마이그레이션 — 이미 적용된 버전은 건너뛴다.

---

## ▌ 4. 마일스톤 이력

### Milestone 1 — 포즈 데이터 파이프라인 구축

**목적**: 2700+ 포즈를 운영 가능한 관계형 구조로 변환한다.

OCR로 추출한 원본 마크다운(`content/`)을 Python 스크립트(`scripts/integrate.py`)로 파싱하여 PostgreSQL에 삽입한다. 수동 데이터 정제 과정 포함.

```
원본 PDF → OCR → 마크다운 → integrate.py → poses 테이블
```

**결과물**: V2 마이그레이션, 2700+ 포즈 레코드.

---

### Milestone 2 — Spring Boot REST 백엔드 초기 구조

**목적**: 포즈 도메인의 CRUD API를 프로덕션 구조로 확립한다.

패키지 구조를 `pose`, `studio`, `session`, `matching`, `instructor` 도메인으로 분리한다. 각 도메인은 Controller → Service → Repository 삼층 구조를 따른다.

```
GET  /api/v1/poses          포즈 전체 목록 반환
GET  /api/v1/poses/{id}     단건 포즈 상세 반환
POST /api/v1/match          매칭 점수 계산 후 추천 반환
```

---

### Milestone 3 — FastAPI AI 파이프라인 연결

**목적**: Ollama LLM과 벡터 검색을 REST 엔드포인트로 노출한다.

`app/services/rag_service.py`가 `nomic-embed-text`로 사용자 쿼리를 임베딩하고 가장 가까운 포즈 청크를 반환한다. `llm_service.py`가 `mistral:latest`로 응답을 생성한다.

```
POST /search   쿼리 → 임베딩 → 유사 포즈 반환
POST /chat     컨텍스트 + 쿼리 → LLM 응답 생성
```

---

### Milestone 4 — T-001: 매칭 점수 0 버그 수정

**목적**: 모든 추천 결과가 0.0점으로 반환되는 프로덕션 버그를 제거한다.

#### 버그 재현 경로

1. 프론트엔드가 UI 목표값 `"flexibility"` 를 POST 바디로 전송
2. `MatchService.java`가 `"flexibility"` 를 DB 태그 어휘와 직접 비교
3. DB에는 `"유연성"`, `"柔軟性"` 등 다국어 태그 존재
4. 어휘 불일치 → `benefit_score = 0` → 최종 점수 0.0 반환

#### 수정 내용 (`MatchService.java`)

```java
private static final Map<String, List<String>> GOAL_TAG_MAP = Map.of(
    "flexibility",   List.of("flexibility", "유연성", "range of motion"),
    "strength",      List.of("strength", "근력", "core strength"),
    "stress_relief", List.of("stress relief", "relaxation", "이완"),
    "balance",       List.of("balance", "균형", "stability"),
    "back_pain",     List.of("back pain", "허리", "spine health"),
    "weight_loss",   List.of("weight loss", "다이어트", "metabolism"),
    "breathing",     List.of("breathing", "pranayama", "호흡"),
    "meditation",    List.of("meditation", "mindfulness", "명상")
);
```

UI 목표값을 `GOAL_TAG_MAP`으로 확장한 뒤 DB 태그와 비교 → 점수 정상화.

**커밋**: `cd5e1b0`

---

### Milestone 5 — 킬스위치: 의료 금기 포즈 하드 차단

**목적**: 심혈관 질환, 임신 등 의료 조건을 입력한 사용자에게 금기 포즈가 절대 반환되지 않도록 강제한다.

#### 차단 로직

```java
if (pose.getContraindications().stream()
        .anyMatch(c -> userConditions.contains(c.getTag()))) {
    return MatchResult.blocked("금기 조건: " + matchedTags);
}
```

점수 계산 전 단계에서 차단 — 점수 0이 아니라 `blocked=true` + `reason` 필드를 포함한 별도 응답 구조를 반환한다.

#### 응답 구조

```json
{
  "pose_id": 42,
  "score": 0.0,
  "blocked": true,
  "block_reason": "금기 조건: cardiovascular_disease"
}
```

---

### Milestone 6 — V5/V6: 스튜디오 · 세션 · 강사 시드

**목적**: 빈 DB로는 검색 API 개발이 불가하다. 실제 데이터 구조와 동일한 시드로 채운다.

#### V5 시드 내용

- **스튜디오**: 서울·부산·대구·대전·광주 5개 도시, 10개 스튜디오
- **세션**: 3개 사용자 계정 기반 16개 예약 세션

#### V6 시드 내용

- **강사 10명** (서울 집중), 사전 계산된 `instructor_trust_score` 포함

#### 신뢰점수 공식

```
trust_score =
    cert_weight                          # E-RYT-500=1.0, E-RYT-200=0.8, RYT-500=0.6, RYT-200=0.4, YACEP=0.2
  + (avg_rating / 5.0) * 0.3
  + min(lineage_depth, 4) * 0.05
  + min(log10(ig_followers) / 7.0, 0.1)
  [최대 1.000으로 상한 설정]
```

**커밋**: `b4067c6` (V5), `159764f` (V6)

---

### Milestone 7 — T-022: AEO용 JSON-LD 삽입

**목적**: Perplexity · Gemini · SearchGPT 같은 AI 검색 엔진이 이 사이트를 인용 소스로 채택하게 만든다.

#### 배경

일반 SEO는 키워드 밀도 최적화를 목표로 한다. AEO(Answer Engine Optimization)는 다르다 — AI가 응답을 생성할 때 참조하는 구조화 데이터의 정확성이 인용 여부를 결정한다.

#### 삽입한 Schema.org 타입

| 타입 | 위치 | 목적 |
|------|------|------|
| `FAQPage` | `/` 홈페이지 `<head>` | "요가란?" 류 직접 질문 응답에 인용 유도 |
| `WebSite` | `/` 홈페이지 `<head>` | 사이트 엔티티 등록 — 브랜드 검색에서 sitelinks 확보 |

#### 삽입 코드 (Spring Boot `SchemaOrgService.java`)

```java
public String buildFaqPage(List<FaqItem> items) {
    // @context, @type: FAQPage, mainEntity 배열 구성
    // 각 항목: Question + acceptedAnswer 포함
}

public String buildWebSite(String name, String url) {
    // @type: WebSite, potentialAction: SearchAction 포함
}
```

**커밋**: `1a15b4f`

---

### Milestone 8 — /studios/nearby: Haversine 거리 정렬

**목적**: 사용자 현재 위치에서 지정 반경 내 스튜디오를 거리 오름차순으로 반환한다.

#### Haversine 알고리즘 (`StudioService.java`)

```java
private static final double EARTH_RADIUS_KM = 6371.0;

private double haversineKm(double lat1, double lng1, double lat2, double lng2) {
    double dLat = toRadians(lat2 - lat1);
    double dLng = toRadians(lng2 - lng1);
    double a = sin(dLat/2) * sin(dLat/2)
             + cos(toRadians(lat1)) * cos(toRadians(lat2))
             * sin(dLng/2) * sin(dLng/2);
    return EARTH_RADIUS_KM * 2 * atan2(sqrt(a), sqrt(1 - a));
}
```

#### 엔드포인트

```
GET /api/v1/studios/nearby?lat={위도}&lng={경도}&radius={반경km, 기본값 10}
```

#### 응답 구조

```json
[
  {
    "studio": { "id": 1, "name": "강남 요가 스튜디오", ... },
    "distanceKm": 1.23
  },
  {
    "studio": { "id": 3, "name": "홍대 요가 센터", ... },
    "distanceKm": 4.87
  }
]
```

#### 통합 테스트 (`StudioControllerIT.java`)

| 테스트 | 검증 내용 |
|--------|-----------|
| `nearbyReturnsOnlyStudiosWithinRadius` | 반경 외 스튜디오(부산) 제외 확인 |
| `nearbyResultsSortedByAscendingDistance` | 거리 오름차순 정렬 확인 |
| `nearbyDefaultRadiusIs10km` | `radius` 파라미터 미입력 시 10km 기본값 적용 |
| `nearbyEmptyWhenRadiusTooSmall` | 반경 0.001km 입력 시 빈 배열 반환 |

**커밋**: `534d3e5`

---

## ▌ 5. 현재 동작하는 전체 API 목록

### Spring Boot (`:19090`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/poses` | 포즈 전체 목록 |
| GET | `/api/v1/poses/{id}` | 단건 포즈 상세 |
| POST | `/api/v1/match` | 목표·조건 기반 매칭 점수 계산 |
| GET | `/api/v1/studios` | 스튜디오 전체 목록 |
| GET | `/api/v1/studios/{id}` | 단건 스튜디오 상세 |
| GET | `/api/v1/studios/nearby` | 반경 내 스튜디오 거리순 반환 |
| GET | `/api/v1/sessions` | 세션 목록 |
| GET | `/api/v1/instructors` | 강사 목록 (신뢰점수 포함) |

### FastAPI (`:8000`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/search` | 쿼리 → RAG → 유사 포즈 반환 |
| POST | `/chat` | 컨텍스트 + 쿼리 → LLM 응답 생성 |

### Vite 프론트엔드 (`:5173`)

탭 기반 SPA — 세 개의 패널이 단일 페이지에서 전환된다.

| 탭 | 컴포넌트 | 프록시 대상 | 기능 |
|----|----------|------------|------|
| 🧘 Chat | `ChatPanel` | `/chat` → `:8000` | 자연어 질의 → LLM 응답 |
| 🔍 Search | `SearchPanel` | `/search` → `:8000` | 포즈 벡터 검색 |
| ✨ Match | `MatchPanel` | `/api/v1` → `:19090` | 목표·조건 기반 포즈 매칭 |

**Vite 프록시 규칙** (`vite.config.js`):

```
/api/v1  →  http://localhost:19090   (Spring Boot)
/search  →  http://localhost:8000    (FastAPI, SEARCH_PORT 환경변수로 오버라이드 가능)
/chat    →  http://localhost:8000    (FastAPI, CHAT_PORT 환경변수로 오버라이드 가능)
```

Docker 환경에서는 `DOCKER_HOST=host.docker.internal`로 설정하면 위 세 대상이 자동 전환된다.

---

## ▌ 6. 데이터 흐름

### 매칭 요청 흐름

```
프론트엔드 (Vite:5173)
    │  POST /api/v1/match { goals: ["flexibility"], conditions: [] }
    ▼
Spring Boot (:19090)
    │  MatchService.findMatches()
    │  ① GOAL_TAG_MAP으로 목표값 태그 확장
    │  ② 금기 조건 킬스위치 검사
    │  ③ benefit_score 계산
    │  ④ 거리 가중치 적용 (스튜디오 있을 경우)
    ▼
PostgreSQL (:5432)
    │  SELECT poses JOIN benefits JOIN contraindications
    ▼
MatchResult[] (score, blocked, pose_detail)
    ▼
프론트엔드 렌더링
```

### RAG 검색 흐름

```
POST /search { query: "허리 통증에 좋은 포즈" }
    │
FastAPI (:8000)
    │  ① nomic-embed-text로 쿼리 임베딩
    │  ② 벡터 DB에서 코사인 유사도 상위 K 청크 검색
    │  ③ 청크 컨텍스트 + 원본 쿼리를 mistral:latest에 전달
    ▼
LLM 응답 (포즈 추천 + 설명)
```

---

## ▌ 7. AEO 파이프라인 전체 구조

```
콘텐츠 레이어              구조화 데이터 레이어           AI 인용 레이어
────────────              ──────────────────           ──────────────
포즈 2700+     ─────────► Schema.org HowTo   ────────► Perplexity 인용
스튜디오 데이터 ─────────► Schema.org FAQPage ────────► Gemini 인용
강사 프로필    ─────────► Schema.org Person  ────────► SearchGPT 인용
               
                          WebSite + SearchAction        브랜드 검색 sitelinks
```

#### 다음 구현 대상 (우선순위 순)

1. **HowTo** — 포즈 글로서리 페이지 (`/poses/{slug}/`) 각각에 삽입
2. **Course** — 강사 수업 시퀀스 마크업
3. **DefinedTerm** — 요가 용어 사전 페이지

---

## ▌ 8. Git 커밋 이력

| 커밋 | 내용 |
|------|------|
| `cd5e1b0` | fix: T-001 매칭 점수 0 버그 — GOAL_TAG_MAP 삽입 |
| `b4067c6` | feat: V5 스튜디오 + 세션 시드 |
| `1a15b4f` | feat: T-022 FAQPage + WebSite JSON-LD |
| `159764f` | feat: V6 서울 강사 10명 시드 |
| `534d3e5` | feat: Milestone 8 /studios/nearby Haversine |
| `c405512` | docs: ENGINEERING_DECK.md 영문 빌드 덱 작성 |

---

## ▌ 9. 테스트 커버리지

| 테스트 파일 | 테스트 수 | 커버 영역 |
|-------------|----------|-----------|
| `StudioControllerIT.java` | 4 | 반경 필터, 거리 정렬, 기본값, 빈 배열 |
| `MatchServiceTest.java` | (계획) | GOAL_TAG_MAP 확장, 킬스위치 |
| `SchemaOrgServiceTest.java` | (계획) | FAQPage JSON 구조 검증 |

---

## ▌ 10. 로드맵

### 즉시 실행 (다음 2주)

| 항목 | 설명 |
|------|------|
| 강사 신뢰점수 일괄 재계산 | Python cron 스크립트 — 일 1회 DB 전체 갱신 |
| HowTo JSON-LD | `SchemaOrgService.buildHowTo()` → 실제 DB 데이터 연결 |
| 포즈 글로서리 랜딩 페이지 | `/poses/{slug}/` Jekyll 정적 페이지 생성 |

### 단기 (1개월)

| 항목 | 설명 |
|------|------|
| MindbodyAdapter | 외부 예약 API 연동 |
| OneClubAdapter | 회원권 통합 연동 |
| Playwright YA 스크래퍼 | BeautifulSoup 대체 — JS 렌더링 처리 |

### 중기 (분기)

| 항목 | 설명 |
|------|------|
| Course + DefinedTerm JSON-LD | AEO 마크업 완성 |
| 강사 추천 알고리즘 고도화 | 신뢰점수 + 세션 이력 결합 |
| 다국어 지원 | 포즈명 영·한·산스크리트 통합 검색 |

---

## ▌ 11. 핵심 설계 결정

| 결정 | 선택지 | 결정 근거 |
|------|--------|-----------|
| Haversine vs PostGIS | Haversine 직접 구현 | PostGIS 설치 오버헤드 없이 서비스 초기 단계 요건 충족. 데이터 1만건 미만에서 성능 차이 없음 |
| 킬스위치 위치 | 점수 계산 전 단계 | 점수 0 반환은 UI에서 추천 목록에 포함될 수 있음. 차단 플래그를 별도 반환해야 프론트엔드가 이유 표시 가능 |
| JSON-LD vs RDFa | JSON-LD | Google 공식 권장 방식. 마크업이 HTML 구조와 분리되어 유지보수 용이 |
| Ollama 로컬 추론 | OpenAI API vs 로컬 | API 비용 없이 개발 반복 속도 확보. 프로덕션 전환 시 교체 가능한 어댑터 구조 유지 |
| Flyway vs Liquibase | Flyway | SQL 기반 마이그레이션으로 가시성 확보. 팀 전원이 SQL 읽기 가능 |
| 신뢰점수 사전 계산 | 사전 계산 vs 쿼리 시 계산 | 실시간 계산 시 `log10(ig_followers)` 등 집계 함수가 매 쿼리에 실행됨. 일 1회 배치로 충분 |

---

*본 문서는 빌드 진행에 따라 갱신된다.*
