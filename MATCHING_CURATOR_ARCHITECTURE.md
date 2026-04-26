# 요가 매칭 큐레이터 — 솔루션 구성도

> AnyFrame 엔터프라이즈 아키텍처 패턴 적용  
> 기준일: 2026-04-26 | 대상: `aiegoo/yogayogi` + Java Spring Boot API (`yoga-api/`)

---

## 솔루션 구성도

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              요가 매칭 큐레이터  솔루션 구성도                                                    │
├──────────────────────────┬─────────────────────────────────────────────────────────┬─────────────────────────────┤
│  개발                    │  실행                                                    │                             │
├──────────────────────────┼───────────────────────┬─────────────────┬───────────────┤  운영                       │
│  개발 도구               │  온라인               │  배치           │  AEO/GEO      │                             │
└──────────────────────────┴───────────────────────┴─────────────────┴───────────────┴─────────────────────────────┘
```

---

## 1. 개발 (Development)

| 분류 | 구성 요소 | 상세 |
|------|-----------|------|
| **분석/설계** | 도메인 모델링 | E-E-A-T 포즈 스키마 설계 (pose_id / difficulty_rank / anatomical_focus) |
| | 매칭 알고리즘 설계 | Kill-Switch 플로우 차트, 유사도 벡터 설계 (benefits[].weight) |
| | API 설계/테스트 지원 | OpenAPI 3 spec 작성, Swagger UI, Spring REST Docs |
| | 데이터 마이그레이션 설계 | `poses_database.json` (2700+) → PostgreSQL Flyway 스크립트 |
| **개발 도구** | Spring Boot 스타터 | `yoga-api/` — Spring Boot 3.x, Gradle, Java 21 |
| | 포즈 JSON 생성기 | Python enrichment 파이프라인: poses_database.json → E-E-A-T JSON 초안 |
| | OpenAPI 자동 문서화 | `springdoc-openapi-ui` → `/swagger-ui.html` |
| | DB Access 생성 | Spring Data JPA + Flyway 마이그레이션 (`db/migration/`) |
| | 테스트 지원 | JUnit 5, Testcontainers (PostgreSQL), MockMvc |

---

## 2. 실행 (Execution)

### 2-1. 온라인 (Online)

| 분류 | 구성 요소 | 상세 |
|------|-----------|------|
| **특화 기능** | 매칭 알고리즘 | `POST /api/v1/match` — benefits 코사인 유사도 + difficulty_rank 필터 |
| | Kill-Switch 필터 | Contraindication.severity = CRITICAL/MEDICAL_CLEARANCE → 매칭 점수 즉시 0 |
| | Trust Score 산출 | FYT100/200 인증 + 계보(lineage) 깊이 + 리뷰 평점 → `instructor_trust_score` |
| | 수련 이력 추적 | 사용자별 세션 이력 → 점진 추천 알고리즘 (difficulty_rank 단계 상승) |
| | 레거시 연계 | Flask/Typesense `search_api.py` ← Java 게이트웨이 프록시 (레거시 유지) |
| **인터페이스** | REST API 어댑터 | `PoseController`, `MatchController`, `SessionController`, `StudioController` |
| | Instagram 연동 | Instagram Graph API → 포즈 Reel 링크 → `/glossary/:pose/` 랜딩 |
| | AI 플랫폼 어댑터 | Perplexity / SearchGPT / Gemini 크롤러 대응 (Schema.org JSON-LD 응답) |
| | JWT 인증 | Spring Security OAuth2 Resource Server → Bearer 토큰 |
| **서비스** | 세션 추천 서비스 | `SessionService` — 시간대 / 위치 / 온오프라인 / 가격 필터 |
| | Studio 어댑터 | `MindbodyAdapter` / `OneClubAdapter` → 실시간 예약 슬롯 동기화 |
| | 강사 매칭 서비스 | `MatchService` — Kill-Switch 체크 → 점수 산출 → 상위 N명 반환 |
| | 예외 처리 | `@ControllerAdvice` — 400/404/409/500 표준 에러 응답 |
| | 동기/비동기 연계 | 예약 확정 이벤트 → Kafka 토픽 → 알림 서비스 (비동기) |
| **데이터** | PostgreSQL/PostGIS | 포즈, 강사, 스튜디오, 사용자 프로필, 세션 이력 |
| | 포즈 DB | `poses` 테이블 (2700+ asanas), `benefits`, `contraindications`, `educational_metadata` |
| | Redis 캐시 | 매칭 결과 캐시 (TTL 5분), 스튜디오 스케줄 캐시 |
| | Typesense | 전문 검색 — 포즈명 / geo_keywords / aeo_summary 인덱스 |
| **Foundation** | 트랜잭션 관리 | `@Transactional` — 매칭 요청 ↔ 예약 생성 원자성 보장 |
| | 설정/구성 관리 | `application.yml` + Spring Cloud Config (환경별 분리) |
| | 유틸리티 | Jackson JSON 직렬화, MapStruct DTO 매핑, Lombok |
| **보안** | OAuth2/JWT | 사용자 인증 — Access Token (15분) + Refresh Token (7일) |
| | 인증/인가 | Role: `ROLE_USER`, `ROLE_INSTRUCTOR`, `ROLE_ADMIN` |
| | 데이터 암호화 | 민감 정보(건강 조건) AES-256 at-rest 암호화 |
| **Open Telemetry** | Metric | Micrometer → Prometheus → Grafana |
| | Logging | SLF4J + Logback → ELK Stack |
| | E2E Trace | Spring Cloud Sleuth + Zipkin — 매칭 요청 전 구간 추적 |

---

### 2-2. 배치 (Batch)

| 분류 | 구성 요소 | 상세 |
|------|-----------|------|
| **작업 유형** | E-E-A-T 스키마 빌드 | `poses_database.json` (2700+) + FYT100 PDF → enriched JSON 생성 |
| | 포즈 DB 인리치먼트 | Python 파이프라인 → benefits/contraindications/geo_keywords 자동 추출 |
| | 강사 신뢰점수 업데이트 | 리뷰 집계 + 수업 이력 → `instructor_trust_score` 재산출 (일 1회) |
| **I/O** | JSON Reader/Writer | Spring Batch `FlatFileItemReader` / `JsonFileItemWriter` |
| | PDF OCR | FYT100 세션 PDF → Apache PDFBox → 큐잉 스크립트 텍스트 추출 |
| | 이미지 최적화 | 포즈 이미지 WebP 변환 + `search.yogaman.club/api/pose-images/` 업로드 |
| **실행 및 제어** | Schema.org JSON-LD 생성 | `SchemaOrgService.buildHowTo()` → `/glossary/:pose/` 페이지 JSON-LD 파일 생성 |
| | Typesense 인덱스 갱신 | 신규/수정 포즈 → Typesense Admin API → 검색 인덱스 동기화 |
| | Mindbody 스케줄 동기화 | 스튜디오 시간표 → DB 갱신 (30분 주기) |
| | 트리거 관리 | Spring `@Scheduled` + Quartz (크론 표현식) |
| **Foundation** | 오류/장애 관리 | 배치 실패 시 `JobExecutionListener` → Slack 알림 |
| | 설정/구성 관리 | `application-batch.yml` + Job 파라미터 관리 |

---

### 2-3. AEO/GEO 엔진 (센터컷 대응)

| 분류 | 구성 요소 | 상세 |
|------|-----------|------|
| **AI 검색 최적화** | Schema.org 마크업 | `HowTo`, `Course`, `DefinedTerm`, `FAQPage` JSON-LD 자동 생성 |
| | Perplexity/SearchGPT | `geo_keywords` + `aeo_summary` → AI 엔진 인용 소스 등록 |
| | Gemini Knowledge Panel | `Course` + `DefinedTerm` JSON-LD → Featured Snippet 획득 |
| | ChatGPT Actions | `/api/v1/match` OpenAPI spec → GPT Action 등록 가능 구조 |
| **실행 및 제어** | 인용 추적 | Google Search Console API → AI 인용 횟수 모니터링 |
| | A/B 스키마 테스트 | HowTo vs. DefinedTerm 마크업 효과 비교 |
| | 랜딩 페이지 생성 | `/glossary/:pose/` Jekyll 정적 페이지 + JSON-LD 삽입 자동화 |

---

## 3. 운영 (Operations)

| 관리 영역 | 구성 요소 | 상세 |
|-----------|-----------|------|
| **시스템 관리** | 통합 관리 환경 | 온라인/배치/AEO 환경 통합 제어 |
| | 사용자 관리 | 수련자 / 강사 / 스튜디오 어드민 계정 관리 |
| | 인증/인가 관리 | JWT 발급 현황, 세션 만료 정책 |
| **온라인 관리** | 매칭 현황 모니터링 | 실시간 매칭 요청 수, 평균 응답 시간, Kill-Switch 발동 건수 |
| | API 성능 관리 | Endpoint별 P95/P99 지연 시간, 오류율 대시보드 |
| | Studio 연동 관리 | Mindbody/1club 동기화 상태, 슬롯 오류 알림 |
| | 온라인 로그 관리 | 매칭 요청/응답 로그 — ELK Stack |
| **배치 관리** | 스키마 빌드 현황 | E-E-A-T 인리치먼트 진행률, 실패 포즈 목록 |
| | 인덱스 동기화 상태 | Typesense 인덱스 최신화 시각, 불일치 건수 |
| | 배치 실행 이력 | Spring Batch JobRepository → 작업별 성공/실패 이력 |
| **AEO/GEO 관리** | AI 인용 현황 | Perplexity/SearchGPT/Gemini 인용 횟수 주간 리포트 |
| | Schema.org 유효성 | Google Rich Results Test API → 오류 스키마 즉시 알림 |
| | Featured Snippet 추적 | 타깃 키워드별 노출 순위 변화 추적 |
| **신뢰 모니터링** | Trust Score 대시보드 | 강사별 `instructor_trust_score` 변동 추이 |
| | 리뷰/평점 관리 | 이상 리뷰 감지 (평점 급변 알림) |
| | Kill-Switch 감사 | CRITICAL 금기사항 발동 로그 — 안전 감사용 |
| **분산 트랜잭션** | 예약 전환 추적 | 매칭 요청 → 세션 예약 완료 전환율 (목표 > 30%) |
| | 외부 API 장애 복구 | Mindbody/Instagram API 장애 시 Circuit Breaker (Resilience4j) |
| | 트랜잭션 대시보드 | Zipkin → 매칭 요청 전 구간 분산 추적 |
| **모니터링/관제** | OpenTelemetry | Prometheus + Grafana — 전 구성 요소 메트릭 통합 |
| | 시스템 상태 알림 | PagerDuty / Slack Webhook — P1 장애 즉시 알림 |
| | AI 인용 증감 알림 | 인용 횟수 전주 대비 -20% 이하 → 자동 알림 |

---

## 주요 기능

### 개발 환경

- **E-E-A-T 기반 도메인 모델 자동화**
  - 2700+ 포즈 DB → Python 파이프라인 → benefits/contraindications 자동 추출
  - 설계 스키마 ↔ Java 엔티티 양방향 동기화 (MapStruct + Flyway)

- **개발 표준화 및 자동화**
  - OpenAPI spec에서 클라이언트 SDK 자동 생성 (`openapi-generator`)
  - Spring Boot 스타터 템플릿 → 신규 엔드포인트 10분 내 온보딩

### 실행 환경

- **AI 네이티브 매칭 프레임워크**
  - Kill-Switch: CRITICAL 금기사항 → 매칭 즉시 차단 → 대체 안전 자세 반환
  - 코사인 유사도 기반 benefits 벡터 매칭 + 수련 이력 점진 추천

- **고성능 멀티 플랫폼 아키텍처**
  - PostGIS 거리 쿼리 → 반경 N km 내 스튜디오 슬롯 실시간 조회
  - Redis 캐시 + Typesense 전문 검색 → P95 < 200ms 목표

### 운영 환경

- **통합 신뢰 관리 환경**
  - 강사 `trust_score` + Kill-Switch 감사 + 예약 전환율 통합 대시보드
  - Resilience4j Circuit Breaker → 외부 API 장애 자동 격리

- **AEO/GEO 실시간 관리**
  - Schema.org 유효성 자동 검사 → 오류 즉시 재생성 배치 트리거
  - AI 인용 횟수 주간 리포트 → 콘텐츠 재투자 우선순위 결정

---

## 특장점

| # | 특장점 | 설명 |
|---|--------|------|
| **01** | **안전성과 매칭 정확도를 동시에** | Kill-Switch 금기사항 필터로 의료 리스크를 원천 차단하면서 코사인 유사도 매칭으로 최적 세션을 추천합니다. |
| **02** | **AI 검색 시대의 권위 있는 추천 소스** | E-E-A-T 스키마 + Schema.org JSON-LD로 Perplexity / SearchGPT / Gemini의 인용 소스로 자동 등록됩니다. |
| **03** | **공급자-클라이언트-마켓플레이스 플라이휠** | 강사 `trust_score` 상승 → AI 인용 증가 → 신규 수련자 유입 → 매칭 데이터 축적 → 추천 정확도 향상의 자기 강화 순환을 구축합니다. |

---

## 컴포넌트 연결 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MATCHING CURATOR FLYWHEEL                        │
│                                                                      │
│  [도메인 강점]              [매칭 엔진]           [마켓플레이스]      │
│  poses_database.json  ◄──────────────────►  Instagram / Perplexity  │
│  FYT100 curriculum         Java API              SearchGPT / Gemini  │
│  E-E-A-T schema       ──────────────────►  AI 검색 인용 획득         │
│         │                      │                      │             │
│         ▼                      ▼                      ▼             │
│  [공급자 구조화]        [클라이언트 안전]       [수익화 루프]          │
│  elbee.yogaman.club  ◄── Kill-Switch ──────► 예약 전환 + 구독        │
│  MindbodyAdapter           trust_score          SaaS 화이트라벨      │
│  Schema.org 자동생성  ──► 점진 추천 ──────► 리뷰·평점 신뢰 순환      │
└─────────────────────────────────────────────────────────────────────┘

개발 레이어:     Spring Boot 3.x + Java 21 + Gradle
데이터 레이어:   PostgreSQL/PostGIS + Redis + Typesense
배치 레이어:     Spring Batch + Quartz + Python 파이프라인
보안 레이어:     Spring Security OAuth2 + JWT + AES-256
관측 레이어:     OpenTelemetry + Prometheus + Grafana + Zipkin
외부 연동:       Mindbody API · 1club API · Instagram Graph API
AEO/GEO:        Schema.org JSON-LD · Google Search Console · Perplexity
```

---

## 기술 스택 요약

| 레이어 | 기술 | 비고 |
|--------|------|------|
| 백엔드 | Java 21 + Spring Boot 3.x | `yoga-api/` 신규 프로젝트 |
| ORM | Spring Data JPA + Hibernate | PostgreSQL Dialect |
| DB | PostgreSQL 16 + PostGIS | 위치 기반 스튜디오 쿼리 |
| 캐시 | Redis 7 | 매칭 결과 캐시 (TTL 5분) |
| 검색 | Typesense | 포즈명 / geo_keywords 전문 검색 |
| 배치 | Spring Batch 5 + Quartz | E-E-A-T 빌드, 인덱스 갱신 |
| 마이그레이션 | Flyway | `db/migration/V*.sql` |
| 보안 | Spring Security OAuth2 + JWT | AES-256 민감 데이터 암호화 |
| 관측 | Micrometer + Prometheus + Grafana + Zipkin | OpenTelemetry 수집 |
| 프론트엔드 | Jekyll (GitHub Pages) | `_data/*.yml` 포즈 카드 유지 |
| 레거시 | Python/Flask + Typesense | `rag_pipeline/api/search_api.py` 유지 |
| 외부 API | Mindbody, 1club, Instagram Graph | Studio 어댑터 패턴 |
| AEO/GEO | Schema.org JSON-LD, Google Rich Results | HowTo / Course / DefinedTerm |
