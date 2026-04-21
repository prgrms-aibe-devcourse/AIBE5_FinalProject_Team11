# MATCHING SYSTEM ROADMAP

## 목표

`aiegoo/yoga`의 요가 세션 매칭 시스템을 AI 기반 권위 추천 엔진으로 확장합니다.
핵심 목표는 다음과 같습니다:

> 참고: 첫 단계에서 데이터 소스는 `yoga` 리포지토리의 읽기 전용 파일을 참조합니다.
> `aeogeo` 리포지토리에서는 해당 `yoga` 파일을 직접 수정하지 않습니다.
- E-E-A-T 기반 포즈/세션 데이터 모델 구축
- Java Spring Boot 백엔드로 매칭 API 전환
- Schema.org JSON-LD로 AEO/GEO 검색 인용 확보
- 스튜디오/수업 예약 API 통합 및 위치 기반 매칭
- 신뢰 기반 수익화 경로 설계

## 현재 상태 (2026-04-21)

### Phase 1 ✅ 완료
- `scripts/enrich_poses.py`, `schemas/pose_eat_schema.json`, `data/poses/poses_eat_schema.json`

### Phase 2 🔄 진행 중
- `yoga-api/` Spring Boot 스캐폴딩 완료
- JPA 엔티티 + Flyway 마이그레이션 완료
- `MatchService` kill-switch 점수 산출 로직 구현 완료
- `SchemaOrgService` HowTo JSON-LD 빌더 구현 완료
- `Dockerfile` + `docker-compose.yml` 추가 (로컬 Java 없이 실행 가능)

### 남은 Phase 2 작업
- `session/`, `studio/` 패키지 스켈레톤 생성
- `/api/v1/match` 통합 테스트 작성
- DB 인제스트: `generate_pose_insert_sql.py` 실행 후 Flyway 적용

### 빌드 환경 이슈 (로컬)
- **Java 17 JDK 미설치** — `bash yoga-api/setup.sh` 로 설치 (sudo 필요)
- 또는 Docker로 바로 실행: `cd yoga-api && docker compose up --build`

---

## Phase 1 — 데이터 권위화: E-E-A-T 포즈 스키마

### 핵심 목표
- `poses_database.json` 기반 E-E-A-T 포즈 스키마 설계
- `benefits`, `contraindications`, `kill_switch`, `geo_keywords` 포함
- `pose` 및 `session`의 Schema.org `HowTo`, `Course` JSON-LD 자동 생성 준비

### 산출물
- `Pose` E-E-A-T JSON 스키마
- `Contraindication` severity / kill_switch 체계
- 포즈 데이터 enrichment 스크립트
- 초기 `pose` JSON-LD 엔드포인트 설계
- `schemas/pose_eat_schema.json`에 명세된 포즈 스키마 상세 정의

### 스키마 세부 사항
- `pose_id`: 고유 식별자 (`trikonasana_001`)
- `canonical_name`, `common_name`: 표준 명칭 및 일반 명칭
- `difficulty_rank`: 1~5 난이도 등급
- `anatomical_focus`: 해부학적 초점 부위 목록
- `educational_metadata`: 강사 큐잉, 계보 출처, FYT100 세션 참조, AEO 요약
- `matching_logic.benefits`: 태그/가중치 기반 benefit 목록
- `matching_logic.contraindications`: condition, severity, kill_switch, instruction
- `geo_keywords`: AI 검색 및 discovery를 위한 키워드 집합
- `schema_org`: Schema.org `HowTo` JSON-LD 객체

### 우선 작업
1. `../yoga/references/2700-asanas/json/poses_database.json`에서 읽기 전용 데이터 분석
2. `poses_database.json` → 확장 스키마 자동 변환 스크립트 작성
3. 기존 Jekyll 포즈/세션 데이터 구조를 반영한 스키마 문서화
4. 초기 `API /api/v1/poses/{id}.jsonld` 요구 사항 정의

---

## Phase 2 — Java Spring Boot 매칭 엔진 구축

### 핵심 목표
- `yoga-api/` Java 프로젝트 생성
- Spring Boot, Spring Data JPA, PostgreSQL, SpringDoc/OpenAPI 구성
- `MatchService`에 Kill-Switch 안전 매칭 로직 구현
- `PoseController`, `MatchController`, `StudioController` 설계

### 산출물
- ✅ `Pose.java`, `Benefit.java`, `Contraindication.java`, `EducationalMetadata.java`
- ✅ `MatchService`, `MatchController`, `MatchResult` 모델
- ✅ `SchemaOrgService` JSON-LD 생성기 (HowTo, 실제 포즈 데이터 매핑)
- ✅ `application.yml` 및 Flyway migration (`V1__create_pose_tables.sql`)
- ✅ `Dockerfile` + `docker-compose.yml` (로컬 Java 없이 실행 가능)
- ⬜ `session/`, `studio/` 패키지 스캐폴딩
- ⬜ 통합 테스트

### 우선 작업
1. ✅ Spring Initializr 기반 `yoga-api/` 프로젝트 스캐폴딩
2. ✅ JPA 엔티티 및 DB 마이그레이션 설계
3. ✅ `MatchService` score/kill-switch 로직 구현
4. ⬜ `/api/v1/match` 통합 테스트 작성
5. ⬜ `session/`, `studio/` 패키지 생성 (Phase 4 사전 작업)

### 빌드 방법
```bash
# Option A: 로컬 (Java 17 + Maven 필요)
bash setup.sh      # 최초 1회 — Java 17 JDK + Maven 설치 (sudo 필요)
mvn spring-boot:run

# Option B: Docker (Java 불필요)
docker compose up --build
```

---

## Phase 3 — AEO/GEO 최적화와 구조화 데이터

### 핵심 목표
- AI 검색 엔진이 인용할 수 있는 구조화 데이터 노출
- `/glossary/:pose/` 랜딩 페이지 및 JSON-LD 자동 생성
- 문제-해결 중심 semantic cluster 전략 적용

### 산출물
- 포즈/세션 JSON-LD 템플릿
- Jekyll `poses` 컬렉션 + `/glossary/:pose/` 자동 생성
- `pose`/`session` semantic cluster 목록
- AI 검색 타겟 키워드 매핑

### 우선 작업
1. `SchemaOrgService`가 `HowTo`, `Course` JSON-LD 생성하도록 구현
2. Jekyll `poses` 컬렉션 퍼머링크 설정
3. 대표 문제 클러스터 5개 선정 및 콘텐츠 매핑
4. Google Rich Results / AI 검색 인덱싱 검증

---

## Phase 4 — 스튜디오 API 통합 및 위치 기반 매칭

### 핵심 목표
- Mindbody / OneClub 등 스튜디오 예약 API 연결
- 위치 기반 `nearby` 스튜디오 검색
- 스튜디오 availability + 세션 매칭 통합

### 산출물
- `StudioAdapter` 인터페이스 및 어댑터 구현
- `StudioController` `/studios/nearby` API
- PostGIS 또는 Haversine 기반 거리 계산
- Live booking/availability 통합 패턴

### 우선 작업
1. `StudioAdapter` 패턴 설계
2. Mindbody/OneClub 샘플 어댑터 작성
3. 위치 기반 스튜디오 검색 API 설계
4. 예약 전환 플로우 시나리오 정리

---

## Phase 5 — 신뢰 기반 수익화 및 파트너 온보딩

### 핵심 목표
- 스튜디오/강사 대상 매칭 SaaS 제안
- AEO/GEO 노출 기반 가치 증명
- Pilot → Value Proof → Paid Tier 로 확장

### 산출물
- 파트너 온보딩 플랜
- 매칭 전환율 리포트 템플릿
- 월간/엔터프라이즈 과금 모델
- White-label Java API 제안서

### 우선 작업
1. 서울 3개 스튜디오 대상 Pilot 제안 만들기
2. 매칭 결과/전환율 리포트 포맷 정의
3. `yoga-api` 서비스의 핵심 KPI 목록 설정
4. 수익화 서비스 상품화 시나리오 작성

---

## 즉시 실행 가능한 첫 단계
1. `yoga-api/` Java 프로젝트 생성
2. `Pose` 엔티티 및 JSON-LD 출력을 위한 초기 스키마 작성
3. `references/2700-asanas/json/poses_database.json`로부터 오픈 포즈 데이터 enrichment 시작
4. `/api/v1/poses/{id}.jsonld` 및 `/api/v1/match` 엔드포인트 우선 구현

---

## 기대 효과
- AI 검색/챗봇에서 `yogaman.club`과 `elbee.yogaman.club`의 인용 소스 채택 가능성 증가
- 안전 중심 Kill-Switch 매칭으로 신뢰성과 전환율 개선
- 스튜디오/강사 콘텐츠를 AI 시대에 맞는 권위 자산으로 변환
- 장기적으로 매칭 SaaS 및 예약 마켓플레이스 수익화 기반 확보
