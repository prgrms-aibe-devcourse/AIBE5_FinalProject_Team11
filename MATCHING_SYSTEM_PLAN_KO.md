# 요가 세션 매칭 시스템 개발 계획 v2 (한국어)

> **기준일:** 2026년 4월 20일  
> **대상 저장소:** `aiegoo/yoga` (GitHub Pages + Java Spring Boot API)  
> **목표:** 전문 요가 강사 교육 지식베이스를 AEO/GEO 최적화된 권위 있는 추천 엔진으로 확장  
> **핵심 변경:** 백엔드 엔진 Python/Flask → **Java Spring Boot**, E-E-A-T 기반 포즈 스키마 도입

---

## 개요 (Overview)

본 시스템은 세 개의 앵커 포인트 — **도메인 강점**, **공급자 구조**, **마켓플레이스** — 를 연결하여 요가 수련자와 최적 강사/세션을 매칭하는 AI 기반 추천 인프라를 구축합니다.

---

### 1. 요가 도메인 강점 지표 (Domain Strength Metrics)

요가 데이터를 단순 콘텐츠가 아닌 **측정 가능한 도메인 자산**으로 재정의합니다.

| 레벨 | 지표 | 측정 방식 |
|------|------|-----------|
| **포즈(Pose)** | 난이도 등급, 계보(Lineage) 출처, 해부학적 초점 부위 수, Drishti·Bandha 정밀도, 금기사항 심각도 | `difficulty_rank` 1–5, `anatomical_focus[]` 배열 길이, `kill_switch` 불리언 |
| **시퀀스(Sequence)** | 빈야사 카운트 완성도, 전환 복잡도, 호흡–동작 동기화율, 점진적 부하 패턴 | Ashtanga structured JSON의 `vinyasa_count`, FYT100 큐잉 스크립트 분석 |
| **도메인(Domain)** | 계보 권위(Iyengar/Ashtanga/Vinyasa), 교사 자격(FYT100/200), 치료 근거 기반 태깅 수, 교육 자료 커버리지 | `lineage_source` depth, FYT100 `session_ref` 연결 밀도, E-E-A-T 점수 |

이 지표들은 `poses_database.json` (2,700+ asanas) + `AshtangaYoga_data.json` + FYT100 세션 이력을 **weighted enrichment 파이프라인**으로 통합하여 산출합니다. 도메인 강점 지표가 높을수록 AI 검색 엔진의 인용 확률이 올라가며, 매칭 알고리즘의 precision도 함께 향상됩니다.

---

### 2. 공급자 재구조화 필요성 (Provider — Content & Marketing Restructuring)

현재 요가 강사·스튜디오·학교는 전문 지식을 가지고 있으나, **디지털 가시성 구조**가 분산되어 있어 AI 시대의 검색·추천 흐름에서 이탈되고 있습니다.

**대표 사례 — `elbee.yogaman.club` (본 저장소 운영자):**

| 현재 상태 | 문제 | 목표 상태 |
|-----------|------|-----------|
| FYT100 커리큘럼 + 큐잉 스크립트 + 포즈 라이브러리를 GitHub 레포에 관리 | Schema.org 마크업 없음 → AI 검색 인용 불가 | `/glossary/:pose/` 페이지에 HowTo JSON-LD 자동 생성 |
| PDF·OCR 데이터가 Git LFS에 분산 저장 | 수강생 검색 경로가 없음 → 이탈률 높음 | 수강생 intake form → 매칭 결과 → 예약 전환 funnnel |
| 인스타그램·오프라인 구전에 의존한 신규 학생 유입 | AI 플랫폼에서 강사 권위 신호 없음 | E-E-A-T 메타데이터 + 강사 trust_score → AI 인용 획득 |
| 스튜디오별 시간표가 별도 채널에 파편화 | 1club/Mindbody API 미연동 → 실시간 예약 불가 | Java Studio Adapter → `/api/v1/studios/{id}/schedule` |

**확장 대상 공급자 유형:**

- **개인 강사:** `elbee.yogaman.club`처럼 서브도메인 + GitHub 레포 조합으로 개인 브랜드 운영  
- **소규모 스튜디오:** Mindbody·1club 등록은 되어 있으나 SEO/AEO 구조 없음  
- **요가 학교(YTT 기관):** FYT100/200 같은 교육 과정 자료가 내부에만 존재; Structure Data로 공개 전환 시 신뢰도 급상승 가능  

---

### 3. 마켓플레이스 현황 (Marketplace — Instagram & AI-Driven Platforms)

공급자와 클라이언트가 동시에 존재하는 플랫폼은 크게 두 레이어로 구분됩니다.

#### 3-1. 비주얼·소셜 레이어 (Instagram 중심)

| 채널 | 공급자 활용 | 클라이언트 활용 | 현재 갭 |
|------|-------------|-----------------|---------|
| Instagram Reels | 포즈 데모, 큐잉 클립 | 포즈 발견, 강사 팔로우 | 게시물이 매칭 시스템과 미연결 → 조회수가 예약으로 전환 안됨 |
| Instagram Stories | 클래스 공지, 할인 | 일정 확인 | 임시적·소멸성; 구조화 데이터 없음 |
| Hashtag Discovery | `#ashtanga` `#vinysayoga` | 클래스 검색 | AI 크롤러가 인스타그램 해시태그를 Schema.org 대체물로 읽지 못함 |

**연결 전략:** Instagram 콘텐츠 → 구조화된 `/glossary/:pose/` 랜딩 페이지로 링크 → Schema.org HowTo 마크업이 AI 플랫폼에 인덱싱.

#### 3-2. AI 주도 플랫폼 레이어

| 플랫폼 | 역할 | 최적화 방식 |
|--------|------|-------------|
| **Perplexity / SearchGPT** | "요통에 좋은 요가 자세 추천" 쿼리 응답 | Schema.org HowTo + `geo_keywords` → 인용 소스 등록 |
| **Gemini (Google AI)** | Knowledge Panel + 리치 결과 | `Course`, `DefinedTerm`, `FAQPage` JSON-LD → Featured Snippet |
| **Mindbody / 1club** | 스튜디오 예약 마켓플레이스 | Java Studio Adapter → 실시간 슬롯 동기화 |
| **YouTube (AI caption)** | 요가 튜토리얼 검색 | 동영상 스크립트 큐잉 스크립트와 연동 → 관련 랜딩 페이지 링크 |
| **ChatGPT 플러그인 / Actions** | 대화형 포즈 추천 | `/api/v1/match` OpenAPI spec → GPT Action으로 등록 가능 |

---

### 4. 클라이언트/사용자 니즈 (Client & User Needs)

수련자는 단순히 "요가 클래스"를 찾는 것이 아닌, 아래의 다층적 니즈를 가집니다.

| 니즈 유형 | 구체적 요구 | 본 시스템의 응답 |
|-----------|-------------|-----------------|
| **안전(Safety)** | 허리 디스크·무릎 부상·혈압 문제 등 신체 조건에 맞는 클래스 | Kill-Switch contraindication 필터 → 위험 포즈 포함 세션 제외 |
| **목표(Goal)** | 유연성 향상, 스트레스 해소, 근력 강화, 체중 감량, 수면 질 개선 | `benefits[].weight` 벡터 유사도 매칭 |
| **레벨(Level)** | 완전 초보자부터 고급 수련자까지 맞는 강도 탐색 | `difficulty_rank` 필터 + 수련 이력 기반 점진 추천 |
| **접근성(Access)** | 시간대·위치·온라인/오프라인·가격대 | Studio Adapter → PostGIS 거리 쿼리 + Mindbody 슬롯 매칭 |
| **신뢰(Trust)** | "이 강사는 검증된 자격을 가지고 있는가?" | `instructor_trust_score` + 계보 출처 + FYT100 certification ref |
| **발견(Discovery)** | 인스타그램이나 AI 검색으로 우연히 만난 포즈를 수업으로 연결 | `/glossary/:pose/` 랜딩 → 관련 세션 추천 CTA |

---

### 5. 세 앵커 포인트의 시너지 연결 구조 (Synergy Architecture)

세 앵커(도메인 강점 · 공급자 · 마켓플레이스)는 독립적으로 작동할 경우 각자 한계를 가집니다. 매칭 시스템은 **연결 레이어**로서 이 세 축의 가치를 증폭시킵니다.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SYNERGY FLYWHEEL                             │
│                                                                      │
│  [도메인 강점]          [매칭 엔진]          [마켓플레이스]           │
│  poses_database.json  ◄─────────────►  Instagram / Perplexity       │
│  FYT100 curriculum        Java API         SearchGPT / Gemini        │
│  E-E-A-T schema       ─────────────►  AI 검색 인용 획득              │
│         │                   │                    │                   │
│         ▼                   ▼                    ▼                   │
│  [공급자 재구조화]    [클라이언트 니즈]    [수익화 루프]              │
│  elbee.yogaman.club  ◄─ Kill-Switch ──►  예약 전환 + 구독            │
│  스튜디오 어댑터          매칭 점수         SaaS 화이트라벨            │
│  Schema.org 자동생성 ──► trust_score ──►  리뷰·평점 신뢰 순환        │
└──────────────────────────────────────────────────────────────────────┘
```

**플라이휠 작동 원리:**
1. **도메인 강점** → E-E-A-T 스키마로 변환 → AI 플랫폼이 본 repo를 권위 소스로 인용
2. **인용 증가** → 신규 클라이언트 유입 → 매칭 데이터 축적 → 추천 정확도 향상
3. **매칭 정확도 향상** → 클라이언트 전환율 상승 → 공급자(`elbee.yogaman.club`, 파트너 스튜디오)의 수익 증가
4. **공급자 수익 증가** → 콘텐츠 재투자(큐잉 스크립트, OCR 데이터) → 도메인 강점 재강화
5. 이 순환이 반복될수록 **경쟁 장벽(moat)** 이 높아지며, 후발 플랫폼이 복제하기 어려운 **전문성 데이터 자산**이 축적됩니다.

---

## 핵심 전략: AEO + GEO 권위 확보

2026년 AI 검색(Gemini, SearchGPT, Perplexity)은 단순한 키워드 매칭이 아닌 **E-E-A-T** 신호를 기준으로 콘텐츠를 평가합니다.

| E-E-A-T 요소 | 이 앱에서의 구현 방식 |
|---|---|
| **Experience (경험)** | FYT100/FYT200 수업 이력 + 실제 큐잉 스크립트 연결 |
| **Expertise (전문성)** | 해부학적 초점 + 강사 큐 우선순위 + 계보(Lineage) 태그 |
| **Authoritativeness (권위)** | Schema.org HowTo/Course 마크업 + Iyengar/Ashtanga 계보 출처 |
| **Trustworthiness (신뢰)** | 금기사항(Contraindication) 심각도 등급 + 임상 안전 지침 |

---

## 0. 현황 파악 (As-Is)

| 자산 | 파일 경로 | 현재 상태 |
|------|-----------|-----------|
| 포즈 DB (일반) | `_data/yoga_poses.yml` | sanskrit/english/image 3개 필드만 존재 |
| 포즈 DB (아쉬탕가) | `_data/ashtanga_poses.yml` | category/series/source 추가됨 |
| 포즈 DB (빈야사) | `_data/vinyasa_poses.yml` | key/image만 존재 |
| 퀴즈 카드 | `_data/yoga_quiz.yml`, `ashtanga_quiz.yml`, `vinyasa_quiz.yml` | type/question/answer/options 구조 |
| 수업 이력 | `_data/freepass.yml` | duration/hours/format 있음 |
| 검색 API | `rag_pipeline/api/search_api.py` | Flask, Typesense, `/api/search` 운영 중 (레거시 유지) |
| 이미지 서버 | `search.yogaman.club/api/pose-images/` | 아쉬탕가·빈야사 이미지 서빙 중 |
| 참고 자료 | `references/2700-asanas/json/poses_database.json` | drishti/modification/alt_name 포함, enrichment 소스 |

**핵심 갭 (Gap):**  
benefits / contraindications / E-E-A-T 메타데이터 / Schema.org 마크업이 **없음** → AI 검색 인용 불가, 매칭 알고리즘 구동 불가.

**백엔드 전환:**  
기존 Python/Flask → **Java Spring Boot 3.x** (이유: JVM 성능, Jackson JSON 직렬화, Spring Security, OpenAPI 자동 문서화, Schema.org JSON-LD 생성 용이)

---

## 1단계: E-E-A-T 기반 포즈 스키마 설계 (Phase 1 — Authoritative Data Schema)

### 1-1. 전문가 수준 포즈 JSON 스키마

AEO/GEO에서 AI 엔진이 인용하려면 포즈 데이터가 **단순 검색 가능**이 아니라 **권위 있는 의미론적 구조**를 가져야 합니다. 아래는 본 저장소의 FYT100 교육 지식베이스와 통합되는 확장 스키마입니다.

```json
{
  "pose_id": "trikonasana_001",
  "canonical_name": "Trikonasana",
  "common_name": "Triangle Pose",
  "difficulty_rank": 2,
  "anatomical_focus": ["Hamstrings", "Lateral Spine", "Obliques", "IT Band"],
  "educational_metadata": {
    "instructor_cue_priority": "앞쪽 엉덩이를 미세 조정하여 천장관절(SI joint)을 보호하세요.",
    "lineage_source": "Iyengar / Hatha",
    "fyt100_session_ref": "FYT100/session-06",
    "aeo_summary": "Trikonasana는 척추 측굴과 하체 안정성을 증진하는 기본 서서하는 자세입니다. 해부학적으로 장경인대와 측면 척추 근육에 작용하며, Iyengar 전통에서 정렬 원칙의 핵심 자세입니다."
  },
  "matching_logic": {
    "benefits": [
      {"tag": "Spinal_Mobility",     "weight": 0.9},
      {"tag": "Hip_Opening",         "weight": 0.7},
      {"tag": "Digestion_Support",   "weight": 0.4},
      {"tag": "Anxiety_Relief",      "weight": 0.6},
      {"tag": "IT_Band_Release",     "weight": 0.8}
    ],
    "contraindications": [
      {
        "condition": "Low_Blood_Pressure",
        "severity": "CAUTION",
        "kill_switch": false,
        "instruction": "어지럼증 방지를 위해 천천히 일어서세요."
      },
      {
        "condition": "Acute_Back_Injury",
        "severity": "CRITICAL",
        "kill_switch": true,
        "instruction": "깊은 측굴을 피하세요. 벽 지지 변형 자세만 허용됩니다."
      },
      {
        "condition": "Neck_Injury",
        "severity": "CAUTION",
        "kill_switch": false,
        "instruction": "시선은 중립 방향으로 유지하고 위쪽을 바라보지 마세요."
      }
    ]
  },
  "geo_keywords": [
    "척추측만증 요가",
    "엉덩이 열기 자세",
    "초보자 서서하는 요가 자세",
    "허리 통증 완화 요가",
    "yoga for scoliosis",
    "how to do Triangle Pose safely",
    "standing yoga poses for hip flexibility"
  ],
  "schema_org": {
    "@type": "HowTo",
    "name": "How to Do Triangle Pose (Trikonasana)",
    "description": "Step-by-step guide to Triangle Pose with safety cues from FYT100-certified instructors.",
    "educationalLevel": "Beginner to Intermediate",
    "teaches": "Spinal lateral flexion, hip stability, lower body strengthening"
  }
}
```

### 1-2. 금기사항 심각도 등급 체계

| 등급 | 코드 | Kill-Switch | 동작 |
|------|------|-------------|------|
| 임상 주의 | `CAUTION` | false | 수정 자세 제안 + 경고 표시 |
| 임상 금지 | `CRITICAL` | **true** | 매칭 점수 즉시 0점 + 대체 자세 추천 |
| 의사 상담 필요 | `MEDICAL_CLEARANCE` | **true** | 세션 완전 차단 + 전문의 상담 안내 |

### 1-3. 데이터 마이그레이션 전략

`references/2700-asanas/json/poses_database.json` (기존 보유) + FYT100 세션 PDF 내용을 사용해 반자동 enrichment를 진행합니다.

```
Step 1: Python 스크립트로 poses_database.json → JSON 스키마 초안 생성
Step 2: FYT100 세션 자료(session-06~15)에서 임상 큐잉 노트 추출
Step 3: 강사 검토 → CRITICAL/CAUTION 등급 수동 확인
Step 4: Java API의 PostgreSQL DB에 최종 ingest
Step 5: Jekyll _data/*.yml은 프리뷰/플래시카드용으로 유지 (가벼운 버전)
```

---

## 2단계: Java Spring Boot API 아키텍처 (Phase 2 — Backend Engine)

### 2-1. 프로젝트 구조

```
yoga-api/                          # 신규 Java 프로젝트 (별도 디렉토리)
├── src/main/java/club/yogaman/api/
│   ├── YogaApiApplication.java
│   ├── pose/
│   │   ├── PoseController.java       # GET /api/v1/poses/{id}
│   │   ├── PoseService.java
│   │   ├── PoseRepository.java       # Spring Data JPA
│   │   └── model/
│   │       ├── Pose.java             # JPA Entity
│   │       ├── Benefit.java
│   │       ├── Contraindication.java
│   │       └── EducationalMetadata.java
│   ├── matching/
│   │   ├── MatchController.java      # POST /api/v1/match
│   │   ├── MatchService.java         # Kill-Switch 로직 포함
│   │   ├── MatchScore.java           # 점수 산출 도메인 객체
│   │   └── UserProfile.java          # 요청 DTO
│   ├── session/
│   │   ├── SessionController.java    # GET /api/v1/sessions
│   │   └── SessionService.java
│   ├── studio/
│   │   ├── StudioController.java     # GET /api/v1/studios/nearby
│   │   ├── MindbodyAdapter.java      # 외부 API 어댑터
│   │   └── OneClubAdapter.java
│   └── seo/
│       └── SchemaOrgService.java     # JSON-LD 생성 서비스
├── src/main/resources/
│   ├── application.yml
│   └── db/migration/                 # Flyway 마이그레이션
└── pom.xml
```

### 2-2. 핵심 Java 클래스 설계

**Pose 엔티티 (E-E-A-T 스키마 반영)**

```java
// pose/model/Pose.java
@Entity
@Table(name = "poses")
public class Pose {

    @Id
    private String poseId;          // "trikonasana_001"
    private String canonicalName;   // "Trikonasana"
    private String commonName;      // "Triangle Pose"
    private int difficultyRank;     // 1-5

    @ElementCollection
    private List<String> anatomicalFocus;

    @Embedded
    private EducationalMetadata educationalMetadata;

    @OneToMany(cascade = CascadeType.ALL)
    private List<Benefit> benefits;

    @OneToMany(cascade = CascadeType.ALL)
    private List<Contraindication> contraindications;

    @ElementCollection
    private List<String> geoKeywords;

    // Schema.org JSON-LD 자동 생성용
    @Transient
    public String toSchemaOrgJsonLd() {
        return SchemaOrgService.buildHowTo(this);
    }
}

@Embeddable
public class EducationalMetadata {
    private String instructorCuePriority;  // 강사 큐 우선순위
    private String lineageSource;          // "Iyengar / Hatha"
    private String fyt100SessionRef;       // "FYT100/session-06"
    @Column(length = 1000)
    private String aeoSummary;             // AI 엔진 인용용 요약
}

@Entity
public class Contraindication {
    @Id @GeneratedValue
    private Long id;
    private String condition;           // "Acute_Back_Injury"

    @Enumerated(EnumType.STRING)
    private Severity severity;          // CAUTION | CRITICAL | MEDICAL_CLEARANCE

    private boolean killSwitch;         // true면 매칭 즉시 차단
    private String safetyInstruction;   // 안전 지침 텍스트

    public enum Severity { CAUTION, CRITICAL, MEDICAL_CLEARANCE }
}
```

**Kill-Switch 매칭 서비스**

```java
// matching/MatchService.java
@Service
public class MatchService {

    // health_flag → 금지 contraindication 코드 매핑 (설정 파일로 외부화 가능)
    private static final Map<String, Set<String>> KILL_SWITCH_MAP = Map.of(
        "HIGH_BLOOD_PRESSURE",  Set.of("INVERSIONS", "INTENSE_BACKBEND"),
        "KNEE_INJURY",          Set.of("FULL_LOTUS", "HERO_POSE", "DEEP_SQUAT"),
        "GLAUCOMA",             Set.of("INVERSIONS", "EXTENDED_FORWARD_FOLD"),
        "PREGNANCY_LATE",       Set.of("DEEP_TWISTS", "PRONE_POSES", "CORE_INTENSIVE"),
        "DISC_HERNIATION",      Set.of("DEEP_FORWARD_FOLD", "LOADED_SPINAL_FLEXION"),
        "WRIST_INJURY",         Set.of("ARM_BALANCE", "CHATURANGA", "DOWNWARD_DOG")
    );

    public MatchResult computeScore(UserProfile user, Session session) {
        List<String> triggered = new ArrayList<>();

        // 1. Kill-Switch 우선 검사
        for (String flag : user.getHealthFlags()) {
            Set<String> forbidden = KILL_SWITCH_MAP.getOrDefault(flag, Set.of());
            session.getContraindications().stream()
                .filter(c -> c.isKillSwitch() && forbidden.contains(c.getCondition()))
                .forEach(c -> triggered.add(flag + " → " + c.getCondition()));
        }

        if (!triggered.isEmpty()) {
            return MatchResult.blocked(session.getSessionId(), triggered);
        }

        // 2. 가중 점수 산출
        double sBenefit = computeBenefitScore(user, session);   // 0.40
        double sGoal    = computeGoalScore(user, session);      // 0.25
        double sLevel   = computeLevelScore(user, session);     // 0.20
        double sTime    = computeTimeScore(user, session);      // 0.15

        // 3. 강사 신뢰 보정 계수 (±10%)
        double trustBonus = (session.getInstructorTrustScore() - 3.0) / 20.0;

        double baseScore = 0.40*sBenefit + 0.25*sGoal + 0.20*sLevel + 0.15*sTime;
        double finalScore = baseScore * (1 + trustBonus);

        return MatchResult.scored(session.getSessionId(),
            Math.min(1.0, finalScore), sBenefit, sGoal, sLevel, sTime);
    }
}
```

**매칭 API 컨트롤러**

```java
// matching/MatchController.java
@RestController
@RequestMapping("/api/v1")
public class MatchController {

    @PostMapping("/match")
    public ResponseEntity<MatchResponse> match(@Valid @RequestBody UserProfile profile) {
        List<MatchResult> results = matchService.matchSessions(profile);
        List<MatchResult> recommendations = results.stream()
            .filter(r -> !r.isBlocked())
            .sorted(Comparator.comparingDouble(MatchResult::getScore).reversed())
            .limit(profile.getTopK())
            .collect(Collectors.toList());

        return ResponseEntity.ok(new MatchResponse(recommendations,
            results.stream().filter(MatchResult::isBlocked).collect(Collectors.toList())));
    }

    @GetMapping("/poses/{id}.jsonld")
    public ResponseEntity<String> getPoseSchemaOrg(@PathVariable String id) {
        // GEO: /api/v1/poses/trikonasana_001.jsonld → Schema.org HowTo JSON-LD 반환
        String jsonLd = schemaOrgService.buildPoseJsonLd(poseService.findById(id));
        return ResponseEntity.ok()
            .contentType(MediaType.valueOf("application/ld+json"))
            .body(jsonLd);
    }
}
```

### 2-3. application.yml 설정

```yaml
# yoga-api/src/main/resources/application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/yogadb
    username: ${DB_USER}
    password: ${DB_PASS}
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
  flyway:
    enabled: true

yoga:
  typesense:
    host: http://search.yogaman.club
    api-key: ${TYPESENSE_API_KEY}
  studio:
    mindbody-api-key: ${MINDBODY_API_KEY}
    oneclub-api-key: ${ONECLUB_API_KEY}
  geo:
    enable-jsonld: true
    schema-base-url: "https://yogaman.club"

server:
  port: 8080

springdoc:
  api-docs:
    path: /api/v1/openapi.json   # OpenAPI 자동 문서
```

### 2-4. docker-compose.yml 확장 (기존 파일 통합)

```yaml
# rag_pipeline/docker-compose.yml에 추가
  yoga-java-api:
    build:
      context: ./yoga-api
      dockerfile: Dockerfile
    container_name: yoga-java-api
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      DB_USER: ${DB_USER}
      DB_PASS: ${DB_PASS}
      TYPESENSE_API_KEY: ${TYPESENSE_API_KEY}
      MINDBODY_API_KEY: ${MINDBODY_API_KEY}
      ONECLUB_API_KEY: ${ONECLUB_API_KEY}
    depends_on:
      - postgres
      - typesense
    networks:
      - yoga-network

  postgres:
    image: postgres:16-alpine
    container_name: yoga-postgres
    environment:
      POSTGRES_DB: yogadb
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - yoga-network
```

---

## 3단계: AEO/GEO 최적화 전략 (Phase 3 — Answer & Generative Engine Optimization)

### 3-1. Schema.org 구조화 데이터 자동 생성

Java `SchemaOrgService`가 각 포즈·세션 엔드포인트에서 JSON-LD를 자동 생성합니다.

**포즈 페이지 예시 (Jekyll + JSON-LD 인젝션)**

```html
<!-- _includes/pose_jsonld.html -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{{ pose.common_name }} ({{ pose.canonical_name }}) 수행 방법",
  "description": "{{ pose.educational_metadata.aeo_summary }}",
  "educationalLevel": "{{ pose.difficulty_rank | difficulty_to_label }}",
  "teaches": {{ pose.anatomical_focus | jsonify }},
  "provider": {
    "@type": "EducationalOrganization",
    "name": "YogaMan FYT100 Instructor Program",
    "url": "https://yogaman.club"
  },
  "hasPart": [
    {% for benefit in pose.matching_logic.benefits %}
    {
      "@type": "HowToStep",
      "name": "{{ benefit.tag }}",
      "text": "이 자세는 {{ benefit.tag | humanize }}에 효과적입니다 (강도: {{ benefit.weight }})."
    }{% unless forloop.last %},{% endunless %}
    {% endfor %}
  ]
}
</script>
```

**세션 페이지 (Course 스키마)**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "{{ session.title }}",
  "description": "{{ session.aeo_summary }}",
  "provider": {
    "@type": "Organization",
    "name": "YogaMan Studio"
  },
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "in-person",
    "duration": "PT{{ session.duration_min }}M",
    "instructor": {
      "@type": "Person",
      "name": "{{ session.instructor_name }}",
      "hasCredential": {{ session.instructor_certifications | jsonify }}
    }
  }
}
</script>
```

### 3-2. 시맨틱 클러스터 (Semantic Clusters) 전략

AI 엔진은 "요가 앱"이라는 단일 키워드보다 **문제-해결 클러스터**를 선호합니다.

| 문제 클러스터 | 타겟 GEO 키워드 | 콘텐츠 전략 |
|---|---|---|
| **테크넥 (거북목)** | "목 통증 요가", "재택근무 요가 루틴", "yoga for text neck" | 15분 요법 세션 페이지 + 포즈 3개 조합 |
| **L4-L5 디스크** | "허리 디스크 요가", "척추 감압 자세" | 강사 임상 노트 포함된 세션 페이지 |
| **불안 완화** | "불안 해소 요가", "미주신경 자극 호흡" | 리스토레이티브 세션 + 과학적 근거 인용 |
| **산전 요가** | "임산부 요가 안전", "prenatal yoga contraindications" | Kill-Switch 적용 세션만 표시 |
| **아쉬탕가 입문** | "아쉬탕가 프라이머리 시리즈 초보자" | FYT100 교육 자료 연결 |

### 3-3. 요가 용어 사전 (Yoga Glossary) — AEO 핵심 전략

> "각 포즈에 독립적인 랜딩 페이지를 부여하면 AI 엔진은 고품질 정의를 색인합니다."

```
/glossary/trikonasana/        → Trikonasana 상세 페이지 (JSON-LD HowTo + aeo_summary)
/glossary/surya-namaskar/     → 태양경배 시퀀스 페이지 (JSON-LD HowToSection)
/glossary/pranayama/          → 호흡법 개요 (JSON-LD DefinedTerm)
```

Jekyll `_poses/` 컬렉션 (기존 보유)을 활용해 자동 생성합니다.

```yaml
# _config.yml에 추가
collections:
  poses:
    output: true
    permalink: /glossary/:name/
```

### 3-4. "강사 인더루프" 신뢰 신호

AI 엔진이 순수 AI 생성 콘텐츠를 강등시키는 추세에 대응합니다.

- **FYT100 수업 노트 직접 인용:** "강사 [Name]이 Session 6에서 SI 관절 보호를 위해 강조한 미세정렬"
- **임상 근거 태그:** `fyt100_session_ref: "FYT100/session-06"` → 기존 `FYT100/session-06/notes/` PDF와 연결
- **강사 자격 표시:** Schema.org `hasCredential` 필드에 FYT200, Ashtanga Authorization 등 표기

---

## 4단계: 스튜디오 API 통합 + 위치 기반 매칭 (Phase 4 — Studio Integration)

### 4-1. Java 어댑터 패턴

```java
// studio/StudioAdapter.java
public interface StudioAdapter {
    List<AvailableClass> getAvailability(String studioId, LocalDate date);
    String createBooking(String classId, String userId);
}

// studio/MindbodyAdapter.java
@Component
public class MindbodyAdapter implements StudioAdapter {
    private final RestTemplate restTemplate;
    private final String apiKey;

    @Override
    public List<AvailableClass> getAvailability(String studioId, LocalDate date) {
        String url = "https://api.mindbodyonline.com/public/v6/class/classes";
        HttpHeaders headers = new HttpHeaders();
        headers.set("API-Key", apiKey);
        // ... 응답 매핑
    }
}
```

### 4-2. 위치 기반 스튜디오 매칭 (GEO "Near Me" 대응)

```java
// studio/StudioController.java
@GetMapping("/studios/nearby")
public List<StudioResult> findNearby(
    @RequestParam double lat,
    @RequestParam double lng,
    @RequestParam(defaultValue = "5") double radiusKm,
    @RequestParam(required = false) String therapyCertification
) {
    // PostGIS or Haversine 공식으로 거리 계산
    // therapyCertification 필터: "prenatal", "back_therapy", "sports_recovery"
}
```

---

## 5단계: 신뢰 기반 마케팅 + SaaS 수익화 (Phase 5)

### 5-1. 스튜디오 온보딩 제안

| 단계 | 내용 | 기간 |
|------|------|------|
| **Pilot** | 서울 3곳 무료 API 연동 + 매칭 전환율 리포트 | 1개월 |
| **Value Proof** | 매칭 → 예약 전환율 리포트 + GEO 노출 횟수 제공 | 2개월 |
| **Paid Tier** | "Smart Lead Matching" SaaS — 월 ₩150,000/스튜디오 | 3개월~ |
| **Enterprise** | White-label Java API + 스튜디오 자체 브랜드 | 6개월~ |

---

## 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Pages (Jekyll)                    │
│  /glossary/:pose  /match  /sessions  /studios               │
│  Schema.org JSON-LD 포함  ←──── AEO/GEO 인덱싱              │
└──────────────────┬──────────────────────────────────────────┘
                   │ fetch POST /api/v1/match
                   ▼
┌──────────────────────────────────────────────────────────────┐
│          Java Spring Boot API (search.yogaman.club:8080)     │
│                                                              │
│  MatchController  →  MatchService (Kill-Switch)              │
│  PoseController   →  SchemaOrgService (JSON-LD)              │
│  StudioController →  MindbodyAdapter / OneClubAdapter        │
└───────┬──────────────────────┬───────────────────────────────┘
        │                      │
        ▼                      ▼
┌──────────────┐    ┌──────────────────────┐
│  PostgreSQL  │    │  Typesense (기존)    │
│  Pose/Session│    │  전문 검색 인덱스    │
│  E-E-A-T DB  │    │  (Python API 공존)  │
└──────────────┘    └──────────────────────┘
```

## 즉시 실행 가능한 첫 번째 액션 (이번 주)

1. **`yoga-api/` 디렉토리 생성** — Spring Initializr로 `spring-boot-starter-web`, `spring-boot-starter-data-jpa`, `postgresql`, `springdoc-openapi` 포함 프로젝트 생성
2. **`Pose.java` 엔티티 작성** — 위 스키마 기반 JPA 엔티티 + Flyway 마이그레이션 SQL
3. **`scripts/enrich_poses.py` 실행** — `references/2700-asanas/json/poses_database.json`에서 benefits/contraindications 초안 추출 → PostgreSQL ingest
4. **`/api/v1/poses/{id}.jsonld` 엔드포인트** — Schema.org JSON-LD 첫 배포 → Google Rich Results Test 검증

> **기대 효과:** 위 4가지 완료 시 Perplexity/ChatGPT가 "Trikonasana 효능" 검색에서 `yogaman.club`을 인용 소스로 채택할 수 있는 구조적 기반이 완성됩니다.

---

## 사용자 여정 스토리보드: "Smart Flow" (User Journey Storyboard)

> 이 스토리보드는 일반적인 검색 방식에서 **AI 기반·안전 우선 매칭**으로 전환되는 핵심 사용 흐름을 시각화합니다.  
> 각 씬(Scene)은 시스템 아키텍처의 특정 레이어와 직접 연결됩니다.

---

### Scene 1: 바이오-디지털 온보딩 (Bio-Digital Onboarding)

**화면:** 사용자(Sarah)가 앱을 열면 "Level 선택" 같은 일반적 화면 대신, 현재 신체 상태를 묻는 인간 중심 인터페이스가 나타납니다.

**사용자 액션:** Sarah가 프로필을 설정합니다.
- ✅ "만성 허리 통증 (Chronic Lower Back Pain)"
- ✅ "중급 경험 (Intermediate)"
- ✅ "30분 가용 시간"

**시스템 로직:**

```
사용자 프로필 입력
        │
        ▼
[MatchService.java] — KILL_SWITCH_MAP 조회
        │
        ├── condition: "Low_Back_Pain" + severity: CRITICAL
        │       → 깊은 전굴(Forward Fold) 세션 즉시 필터링
        │
        └── benefits[].tag: "Spinal_Traction" + weight ≥ 0.7
                → 우선 추천 세션 목록 생성
```

> **데이터 소스:** `FYT100/session-*/` 큐잉 스크립트의 해부학적 주석 + `poses_database.json`의 `contraindications[].kill_switch` 필드가 이 로직을 구동합니다.

---

### Scene 2: AEO/GEO 음성 검색 발견 (Voice-First Discovery)

**화면:** Sarah는 앱을 직접 검색하지 않습니다. AI 어시스턴트(Gemini/Siri)에게 묻습니다.

> *"Find me a yoga session that helps with sciatica but doesn't strain my wrists."*

**AEO 작동 메커니즘:**

| 단계 | 처리 내용 |
|------|-----------|
| AI 어시스턴트가 쿼리 분석 | `sciatica` → `geo_keywords[]`에 "척추신경통 요가", "wrist-free yoga" 포함 포즈/세션 검색 |
| Schema.org 인덱싱 | `/api/v1/poses/{id}.jsonld`의 `HowTo` 마크업이 권위 있는 답변 소스로 채택 |
| AI 응답 생성 | *"I've found a 'Wrist-Free Lumbar Release' session designed by \[Your Brand\]'s senior educators."* |

**결과:** 광고비 없이 **고의도(High-Intent) 사용자**가 자연어로 유입됩니다. 이것이 AEO 전략의 핵심 ROI입니다.

---

### Scene 3: 인터랙티브 세션 + 마켓 연결 (Interactive Session & Market Bridge)

**화면:** Sarah가 영상 세션을 시작합니다. 특정 포즈 실행 중 "Expert Note" 오버레이가 나타납니다.

> *"뒤쪽 무릎을 살짝 구부려 천장관절(SI joint)을 보호하세요."*

**포즈 메타데이터 연동:**

```json
{
  "pose_id": "trikonasana_001",
  "educational_metadata": {
    "instructor_cue_priority": "앞쪽 엉덩이를 미세 조정하여 SI joint를 보호하세요.",
    "fyt100_session_ref": "FYT100/session-06"
  },
  "matching_logic": {
    "benefits": [{"tag": "Spinal_Mobility", "weight": 0.9}]
  }
}
```

> Sarah의 프로필 목표("허리 통증")와 포즈의 `benefits[].tag` 벡터가 일치 → 실시간 코칭 메시지 트리거.

**마켓 통합 배지:**

```
┌─────────────────────────────────────────────────┐
│  💡 이 스타일이 마음에 드셨나요?                    │
│  강사 'Marco'가 내일 오후 6시 'Downtown Yoga'에서  │
│  동일 시퀀스를 라이브로 진행합니다.                  │
│  [예약하기 →]   (Studio Adapter API 연동)         │
└─────────────────────────────────────────────────┘
```

---

### Scene 4: 피드백 루프 + 가중치 업데이트 (Biometric Feedback Loop)

**화면:** 세션 종료 후 간단한 체크인:

> *"허리 상태가 어떻게 느껴지시나요? [좋아짐 / 그대로 / 나빠짐]"*

**Sarah 선택: "좋아짐 (Better)"**

**매칭 로직 업데이트:**

$$w_{\text{new}} = w_{\text{old}} + \alpha \cdot \text{feedback\_score}$$

```java
// MatchService.java — 피드백 반영
benefitWeight = benefitWeight + (LEARNING_RATE * feedbackScore);
sessionHistoryRepo.save(new SessionFeedback(userId, sessionId, "BETTER", benefitWeight));
```

**공유 가능한 Progress Insight 자동 생성:**

> *"30분 하타 요가로 인지된 허리 긴장도가 40% 감소했습니다."*  
> → Schema.org `Review` 타입으로 직렬화 → AI 플랫폼의 **사용자 경험(E-E-A-T Experience)** 신호로 축적

---

### Scene 5: 스튜디오 핸드오프 + 수익화 모델 (Studio Hand-off & Monetization)

**화면:** Sarah가 "스튜디오 예약" 버튼을 클릭합니다.

**동의 기반 프로필 전송:**

```
Sarah의 "Smart Profile" (허가 후 전송)
├── physical_conditions: ["Low_Back_Pain"]
├── contraindications: ["Deep_Forward_Fold", "Wrist_Loading"]
├── preferred_style: "Hatha / Gentle"
├── session_history: 12 sessions, avg_feedback: 4.3/5
└── trust_score: 87 (FYT100-certified 강사 추천 기반)
```

**스튜디오 강사가 수신하는 "AI-Ready 학생" 정보:**

> *"Sarah는 허리 부상이 있으며, 손목 로딩 자세는 피해야 합니다. 전 12회 세션에서 척추 견인 시퀀스에 긍정적 반응을 보였습니다."*

**수익화 구조 (이중 모델):**

| 모델 | 대상 | 과금 방식 | 전략적 가치 |
|------|------|-----------|-------------|
| **Direct Marketplace** | 사용자 Sarah | 예약 건당 수수료 (5–15%) | 즉각적 거래 수익, 스케일 확장성 |
| **SaaS Lead Gen** | 스튜디오/강사 | 월정액 구독 (기본/프로/엔터프라이즈) | "AI-Ready 학생" 공급 = 스튜디오 전환율↑ |

**플라이휠 완성:**

```
Sarah의 긍정 피드백
        │
        ▼
매칭 가중치 정밀화 → 더 나은 추천
        │
        ▼
스튜디오 전환율 상승 → SaaS 구독 유지
        │
        ▼
스튜디오가 세션 데이터 추가 제공 → 도메인 강점↑
        │
        ▼
AI 플랫폼 인용 증가 → 신규 Sarah 유입
```

---

### 사용 사례 가치 요약 (Use Case Value Summary)

| 사용 사례 | 기술 드라이버 | 사용자 혜택 | 시스템 연결 포인트 |
|-----------|---------------|-------------|-------------------|
| **Pain-Point 진입** | Expert Knowledge Base + Kill-Switch | 첫 순간부터 안전과 신뢰 | `MatchService.KILL_SWITCH_MAP` |
| **음성 우선 검색** | AEO/GEO Strategy + Schema.org | 자연어로 발견됨 | `SchemaOrgService.java` + `geo_keywords[]` |
| **미세 조정 코칭** | JSON Pose Metadata | 실시간 강사급 큐잉 | `educational_metadata.instructor_cue_priority` |
| **스튜디오 연결** | Studio Adapter API + Smart Profile | 홈에서 커뮤니티로 seamless 전환 | `MindbodyAdapter` / `OneClubAdapter` |
| **피드백 학습** | 가중치 업데이트 + Progress Insight | 수련이 쌓일수록 추천 정밀화 | `benefitWeight` 학습률($\alpha$) 루프 |

---

### Scene 5 구현 전략: 이중 수익화 상세 설계

> **결정:** Direct Marketplace(예약 수수료) + SaaS Lead Gen(스튜디오 구독)을 **동시 운영**합니다.

**티어 구조:**

```
Free Tier
├── 사용자: 매칭 추천 무제한, 세션 미리보기
└── 스튜디오: 월 5건 AI-Ready 리드 무료 수신

Pro Tier (₩29,000/월 · 스튜디오)
├── AI-Ready 학생 무제한 수신
├── Smart Profile 전체 열람
└── 강사 신뢰 배지(Trust Badge) 발급

Enterprise Tier (맞춤 견적 · YTT 학교)
├── 화이트라벨 매칭 위젯 (`elbee.yogaman.club` 임베드)
├── FYT100/200 수료생 데이터 우선 매칭
└── Schema.org Co-Author 크레딧 → AI 인용 공동 수혜
```
