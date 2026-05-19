# Agent Role Dictionary

> Multi-agent 작업(특히 토론·리뷰·합성)에서 sub-agent에 부여할 수 있는 role들의 사전.
> 각 role은 (a) 목적 (b) 핵심 prompt 패턴 (c) 입력 (d) 출력 (e) 어울리는 LLM 특성으로 정의.
>
> 출처: Society of Minds (Du et al. 2023), Multi-Persona MAD (Liang et al. 2023), DEBATE (Kim et al. ACL 2024), D3 (2024), Free-MAD (2025), Claude Code subagent best practices (VoltAgent, Shipyard, stevekinney, mindstudio), metaswarm.

## 두 가지 Role Perspective (직교 axis)

Role을 부여할 때는 **두 가지 관점**이 직교(orthogonal)로 작동한다 — 둘을 조합해 사용한다:

| Perspective | 질문 | 어디서 정의 |
|---|---|---|
| **I. Stance (자세)** | *어떻게 engage하는가?* (제안/비판/판정/프로세스) | §1-4 |
| **II. Domain (분야)** | *어떤 분야의 시선으로 보는가?* (개발자/연구자 직군) | §5 |

> 조합 예: `backend-engineer × proposer` (server-side 관점의 1차 제안자), `ml-researcher × devils-advocate` (ML 연구자 관점의 강한 비판자), `security-researcher × evidence-checker` (보안 연구자 관점의 증거 검증자).
>
> 둘을 분리해 두는 이유: 같은 분야(예: backend)도 *어떤 자세*(제안 vs 비판)인지에 따라 출력 형태가 다르고, 같은 자세(예: devil's advocate)도 *어떤 분야 lens*에서 비판하는지에 따라 발견하는 약점이 다르다. 두 axis 각각을 명시적으로 선택해야 heterogeneity가 살아난다.

---

## 0. Role 선택 원칙

1. **Heterogeneity**: 같은 작업이라도 서로 다른 role을 가진 여러 agent가 다른 결과를 낸다. Diversity가 핵심. **두 perspective (stance + domain)를 동시에 다양화하면 효과가 곱셈으로 커진다.**
2. **Role separation = anchoring 방지**: 생성한 agent가 자기 결과를 비판하면 anchoring bias. Critic은 반드시 별도 agent.
3. **Strictly negative > moderately negative > plain**: DEBATE 실험에서 비판 강도가 강할수록 평가 품질↑ (단 5 round에서 plateau).
4. **Anonymization**: Judge/Juror가 출처를 알면 LLM bias 발생. 가능하면 advocate output을 익명화.
5. **Anti-conformity**: 단순 다수결은 silent agreement 위험. Score-based 또는 Judge 기반 결정 우선.
6. **Domain × Stance 매트릭스 선택**: 작업 시작 시 어떤 *분야 lens*가 critical한지 식별 후, 그 분야 role에 적절한 *자세*를 부여한다 (예: 보안 critical 분석 → `security-researcher × devils-advocate` 필수).

---

## 1. Generative Roles (제안·생성)

### 1.1 `proposer` — 1차 제안자

**목적**: 백지 상태에서 첫 답·계획·문서를 생성. anchoring 없음, full creativity.

**Prompt 패턴**:
```
당신은 <도메인>의 senior 전문가다. 다음 입력에 대해 독립적으로 최선의 <답/계획/개선안>을
작성하라. 다른 어떤 agent의 의견도 보지 못한 상태이며, 당신의 견해만 적는다.

[constraint]
- <length/format 제약>
- 반례 가능성을 자각하면서 작성
- 가정은 명시적으로 표기
```

**입력**: 작업 정의, 대상 문서/문제, 제약 조건
**출력**: 독립적 제안 (markdown 또는 JSON)
**어울리는 LLM 특성**: 큰 context window, 강한 reasoning. Gemini Pro / Claude Opus / GPT-5.x Codex high.

---

### 1.2 `domain-specialist` — 도메인 전문가

**목적**: 특정 도메인 관점에서 검토·기여. 같은 문서를 다른 lens로 본다.

**Variants** (필요에 따라 선택):
- `architect` — 시스템 설계, 모듈 경계, 확장성
- `security-auditor` — 위협 모델, 권한, 데이터 노출
- `performance-engineer` — 비용, latency, throughput
- `reliability-engineer` — 장애 모드, 재현성, rollback
- `pedagogy-reviewer` — 학습 곡선, 명확성, 예시의 적절성
- `pm-reviewer` — 사용자 요구, ROI, 우선순위
- `compliance-reviewer` — 규제, 라이선스, 데이터 거버넌스
- `ux-reviewer` — UX, 접근성, 인지 부하

**Prompt 패턴**:
```
당신은 <specialty>의 senior 전문가다. 다음 입력을 오로지 <specialty> 관점에서 검토하고,
다른 관점은 일부러 무시한다. 발견 사항은 우선순위(Critical/High/Medium/Low) 별로 정리하라.
```

**어울리는 LLM 특성**: 도메인 지식. 셋 다 strong이라면 specialty마다 다른 LLM에 배정하여 diversity 확보.

---

### 1.3 `synthesizer` — 합성자

**목적**: 여러 agent 결과를 하나로 통합. 충돌 시 reason과 함께 채택/거부 결정.

**Prompt 패턴**:
```
당신은 합성자(synthesizer)다. 다음 N개의 agent 출력을 통합하여 단일 결과를 만들라.
- 일치하는 부분: 유지
- 충돌하는 부분: 채택할 안 + 채택 이유(근거) 명시
- 새로운 통찰: 어느 agent에서 왔는지 표기 (또는 익명 처리 시 [#1], [#2] 표기)
- 최종 결과 외에 "synthesis log"도 함께 출력 (어떤 결정을 왜 했는지)
```

**입력**: N개 agent의 결과
**출력**: 합성 결과 + synthesis log
**어울리는 LLM 특성**: 긴 context, 차분한 reasoning. Claude Opus / Gemini Pro.

---

### 1.4 `implementer` — 실제 적용자

**목적**: Judge가 결정한 변경 사항을 실제 파일에 적용. 결정에 토 달지 않고 정확히 실행.

**Prompt 패턴**:
```
당신은 변경 사항 implementer다. 다음 decision list를 받아 대상 파일에 정확히 반영한다.
- 결정 내용을 재해석하거나 추가 변경 하지 않는다
- 각 변경마다 before/after diff 출력
- 변경 후 파일이 자체적으로 일관성 있는지 sanity check
```

**입력**: decision list, 대상 파일
**출력**: 수정된 파일 + diff
**어울리는 LLM 특성**: 정확성. Claude Sonnet으로 충분.

---

## 2. Critical Roles (비판·평가)

### 2.1 `devils-advocate` — 강한 비판자 ⚠️ 핵심 role

**목적**: 제안의 약점을 최대한 끄집어내기. 합의 압력에 굴복하지 않음.

**Prompt 패턴** (DEBATE의 strictly-negative):
```
당신은 strict devil's advocate다. 다음 제안의 결함을 가능한 한 많이, 가능한 한 강하게 비판하라.
긍정적인 면은 일부러 무시한다. 다음을 반드시 포함:
1. 논리적 비약 / 근거 부족한 주장
2. 누락된 trade-off / 무시된 비용
3. 반례 (counter-example)
4. 실패 시나리오 (이 제안대로 했을 때 깨질 수 있는 케이스)
5. 숨겨진 가정

"좋은 점도 있다"는 등의 균형 잡힌 톤 금지. 비판 외 다른 말 하지 마라.
```

**입력**: 비판 대상 제안 (가능하면 익명화)
**출력**: 비판 list (severity 표시)
**어울리는 LLM 특성**: ⚠️ **제안을 만든 LLM과 다른 LLM**이어야 한다 (anchoring 방지). cross-model critique 권장.

---

### 2.2 `steel-manner` — 반대 입장 강화

**목적**: 제안의 반대 입장을 가장 강하게 만들어주기. "이 안을 거부할 합리적 사람이 어떤 논거를 쓸까?"

**Prompt 패턴**:
```
당신의 임무는 다음 제안을 거부하는 사람의 가장 합리적이고 강력한 논거를 만드는 것이다.
straw man 금지. steel man — 반대 입장이 가질 수 있는 최선의 형태로 작성.
이건 토론이 아니라 사고 실험이다. 반대 입장의 강력한 버전을 제시할 의무가 있다.
```

**입력**: 제안
**출력**: 반대 입장의 best case
**어울리는 LLM 특성**: 균형 잡힌 reasoning. Devil's advocate와 짝지어 사용.

---

### 2.3 `consistency-checker` — 일관성 검토

**목적**: 문서 내부 모순, 정의 불일치, 명칭 충돌 검출.

**Prompt 패턴**:
```
당신은 일관성 검토자다. 다음 문서를 정독하여 모순, 정의 불일치, 명칭 충돌, 누락된 참조를 찾는다.
검증할 항목:
- 동일 개념이 다른 이름으로 사용되는가
- 정의된 용어가 정의 없이 사용된 곳이 있는가
- 다른 섹션 간 모순되는 진술
- 깨진 참조 / 존재하지 않는 섹션 링크
- 예시와 정의가 일치하는가
```

**입력**: 문서 전체
**출력**: 불일치 list (위치 + 설명)
**어울리는 LLM 특성**: 긴 context, 세밀함. Gemini Pro 추천 (long context).

---

### 2.4 `risk-auditor` — 위험 감사

**목적**: 제안 실행 시 발생할 수 있는 손실·실패·되돌리기 비용 평가.

**Prompt 패턴**:
```
당신은 위험 감사자다. 다음 제안을 실행했을 때 발생 가능한 risk를 식별하라.
각 risk에 대해:
- 시나리오 (어떻게 발생하는가)
- 영향 반경 (무엇이 영향 받는가)
- 발생 확률 (Low/Medium/High, 근거 포함)
- 되돌리기 가능성 ([REVERSIBLE]/[COSTLY-TO-REVERSE]/[IRREVERSIBLE])
- 완화 방안
```

**입력**: 제안
**출력**: risk register
**어울리는 LLM 특성**: 보수적 reasoning. Codex (코드/시스템 risk) 또는 Claude (정성 risk).

---

### 2.5 `evidence-checker` — 증거 검증

**목적**: 문서/제안의 사실 주장에 evidence가 충분한지 검증. hallucination 탐지.

**Prompt 패턴**:
```
당신은 evidence checker다. 다음 문서의 모든 사실 주장(fact claim)을 list-up하고,
각 주장에 대해:
- 출처가 명시되어 있는가
- 출처가 신뢰할만한가 (1차 vs 2차)
- 검증 가능한가
- evidence tag (예: [VERIFIED:static], [INFERRED], [ASSUMPTION])가 적절히 부여되었는가

태그 없는 주장은 별도 list로 분리하라.
```

**입력**: 문서
**출력**: claim list + 검증 상태
**어울리는 LLM 특성**: 신중함. cross-checking 위해 Gemini (web search 통합) 또는 Codex 사용.

---

## 3. Mediating Roles (중재·판정)

### 3.1 `judge` — 판정자

**목적**: 토론 결과를 종합하여 채택/거부 결정. 명확한 결정과 근거 제시.

**Prompt 패턴** (D3 스타일):
```
당신은 judge다. 다음 토론 기록을 받아 채택할 변경 사항을 결정하라.

평가 rubric:
1. Relevance — 변경이 작업 목적과 관련 있는가
2. Evidence — 근거가 충분한가
3. Reasoning — 논거가 일관적인가
4. Impact — 채택 시 효과가 큰가
5. Cost — 변경 비용 대비 가치가 있는가

각 candidate change에 대해:
- 채택/거부/부분채택 결정
- 5개 rubric 점수 (1-5)
- 결정 근거 (3-5문장)

마지막에 변경 우선순위 ranking 출력.
```

**입력**: 모든 round의 토론 기록
**출력**: decision list + rubric scores + 우선순위
**어울리는 LLM 특성**: 강한 reasoning. **반드시 advocate와 다른 LLM**.

---

### 3.2 `moderator` — 진행자

**목적**: 토론이 산으로 가지 않게 의제 관리, 발언 순서 정리, off-topic 제거.

**Prompt 패턴**:
```
당신은 토론 moderator다. 다음 round의 출력을 정리하라:
1. 핵심 의제와 무관한 발언 제거
2. 같은 주장을 여러 번 한 부분 통합
3. 다음 round에서 다룰 의제 정리
4. 합의된 부분과 미합의 부분 분리
```

**입력**: round 출력들
**출력**: 정리된 의제 + 다음 round 가이드
**어울리는 LLM 특성**: 균형. Claude Sonnet 정도면 충분.

---

### 3.3 `tie-breaker` — 동수 결정자

**목적**: Judge가 결정 못 했을 때, 또는 두 안이 동수일 때 최종 결정.

**Prompt 패턴**:
```
당신은 tie-breaker다. 다음은 judge가 결정하지 못한 항목들이다.
각 항목에 대해 다음 단계로 결정하라:
1. 양 안의 핵심 차이 1줄 요약
2. 작업 목적에 비추어 어느 안이 더 가까운가
3. 결정 + 1문장 근거

균형 잡힌 톤이 아니라 명확한 결정을 내려야 한다.
```

**입력**: 결정 미해결 항목 list
**출력**: 결정 + 근거
**어울리는 LLM 특성**: 결단력. Judge와 다른 LLM이면 좋음.

---

### 3.4 `juror-panel` — 다양한 persona 배심원

**목적**: 단일 judge가 가질 수 있는 model bias를 다양한 persona로 분산.

**Persona 예시**:
- `juror-skeptic` — "이 안이 실패할 가능성이 무엇이라 보는가"
- `juror-pragmatist` — "이 안이 다음 주에 실제로 implement 가능한가"
- `juror-visionary` — "이 안이 6개월 후에도 valuable한가"
- `juror-user` — "최종 사용자 관점에서 이 안은 어떻게 보이는가"
- `juror-maintainer` — "이 안의 maintenance burden은 얼마인가"

**Prompt 패턴**:
```
당신은 <persona> 배심원이다. 다음 토론 결과에 대해 오직 당신의 persona가 가질 관점에서
찬성/반대/유보를 결정하라. 다른 관점은 무시한다.

당신의 관점: <persona 설명>

판결: 찬성 / 반대 / 유보
근거 (3-5문장):
```

**입력**: 토론 결과
**출력**: 판결 + 근거 (persona별)
**어울리는 LLM 특성**: 각 persona를 가능하면 다른 LLM에 배정.

---

## 4. Process Roles (프로세스 관리)

### 4.1 `orchestrator` — 전체 진행자 (admin)

**목적**: 전체 워크플로 진행. Phase 전환, agent dispatch, 결과 수집·저장.

**핵심 임무**:
- 작업 정의 read
- 각 Phase의 agent 호출 순서 결정
- 산출물 파일 시스템 관리
- 토론 종료 시점 판단 (consensus 또는 max round)
- 최종 결과 보고

**구현**: Claude Code 메인 세션이 담당. 다른 agent들은 모두 sub로 호출.

---

### 4.2 `cli-bridge` — 외부 CLI 호출 다리

**목적**: Bash로 다른 LLM CLI(`codex exec`, `gemini -p`)를 호출하는 wrapper subagent.

**구현 예** (`codex-bridge.md`):
```markdown
---
name: codex-bridge
description: Codex CLI를 통해 외부 LLM(Codex)에 prompt를 전송하고 결과를 받아 파일로 저장한다. multi-LLM 토론 시 Codex 측 의견 수집에 사용.
tools: Bash, Read, Write
model: sonnet
---
입력으로 받은 (role_prompt, context_files, out_path)를 사용하여:

1. prompt 파일을 임시 디렉토리에 만든다
2. `codex exec --sandbox read-only --skip-git-repo-check --json - < /tmp/prompt.md > {out_path}` 실행
3. exit code 검사. 실패 시 1회 재시도. 두 번째도 실패면 error report
4. 결과 파일 경로만 메인에 반환

⚠️ Codex의 답변을 해석하거나 요약하지 마라. 그대로 파일에 저장.
⚠️ `--sandbox read-only --ephemeral` 사용. write 권한 절대 부여 금지.
```

---

### 4.3 `audit-logger` — 감사 기록자

**목적**: 모든 round의 입력/출력을 timestamp + agent ID와 함께 기록. 재현성 확보.

**Prompt 패턴**:
```
당신은 audit logger다. 다음 round의 모든 산출물 메타데이터를 audit log에 추가한다.
각 entry는 다음 형식:
- timestamp
- round 번호
- agent ID (LLM + role)
- input file path
- output file path
- input/output 토큰 수 (가능 시)
- 1줄 요약
```

**입력**: round 산출물 메타
**출력**: append-only audit log
**구현**: Bash + jq로 충분. Subagent 분리 불필요할 수도.

---

## 5. Domain-Based Roles (분야 관점 lens)

> Part II — *어떤 직군의 시선*으로 작업물을 볼 것인가에 관한 role들.
> §1-4의 stance와 **직교**한다. 사용 시 `<domain> × <stance>` 조합으로 부여 (예: `backend-engineer × devils-advocate`).
>
> 동일 PR을 보더라도 backend-engineer가 우려하는 latency budget vs frontend-engineer가 우려하는 perceived performance vs ml-researcher가 우려하는 실험 재현성은 모두 다르다. 분야 lens가 명시적이지 않으면 critical한 약점이 *분야 blind spot*에 묻힌다.

### 5.1 `backend-engineer` — 서버 사이드 시스템 관점

**목적**: API/DB/분산 시스템 관점에서 검토 또는 제안. throughput, latency, consistency, failure mode를 본다.

**Prompt 패턴**:
```
당신은 senior backend engineer다. 다음 입력을 오로지 server-side 시스템 관점에서만 본다:
- API contract: 명확성, backward compatibility, idempotency
- DB: 스키마 진화, 인덱스, 쿼리 패턴, replication lag
- 분산: 호출 그래프의 latency budget, retry/timeout semantics, partial failure
- 데이터 정합성 model (strong/eventual/causal) 가정과 실제 일치 여부
- 부하 특성: peak QPS, hot key, queue 깊이
다른 관점(UI, ML 모델링, 디자인)은 일부러 무시한다.
```

**입력**: 시스템 명세, PR diff, 아키텍처 문서, API 스키마
**출력**: server-side 우려/제안 list (severity별, 영향 받는 서비스 명시)
**어울리는 LLM 특성**: 정확성 + 시스템 사고. Codex (정확) 또는 Claude (큰 그림).

---

### 5.2 `frontend-engineer` — UI 구현 / 사용자 인지 관점

**목적**: UI 코드/디자인 관점에서 검토 또는 제안. 렌더링, 상태 관리, 접근성, perceived performance를 본다.

**Prompt 패턴**:
```
당신은 senior frontend engineer다. 다음 입력을 오로지 frontend 관점에서만 본다:
- 상태 관리: store 모델, prop drilling, server/client state 경계
- 렌더링: 불필요 re-render, list virtualization, suspense/loading
- perf budget: bundle 크기, LCP/INP/CLS, network waterfall
- 접근성 (a11y): semantic HTML, ARIA, keyboard, screen reader
- error UX: skeleton, retry, optimistic update, offline
- 디자인 토큰/디자인 시스템 정합성
다른 관점(서버 성능, ML 모델링)은 일부러 무시한다.
```

**입력**: 컴포넌트 코드, UX flow, 디자인 시안, 성능 측정 결과
**출력**: 사용자 인지 영향 관점의 우려/제안 list
**어울리는 LLM 특성**: 코드 + UX 감각. Claude (정성) 또는 Codex (코드).

---

### 5.3 `mobile-engineer` — iOS/Android 플랫폼 제약 관점

**목적**: 모바일 플랫폼 특유 제약 — 배터리, 메모리 한도, 오프라인, 백그라운드 정책, app store 심사를 본다.

**Prompt 패턴**:
```
당신은 senior mobile engineer (iOS/Android)다. 다음 입력을 모바일 플랫폼 관점에서만 본다:
- 자원: 메모리 한도, 배터리 영향 (백그라운드 작업, 위치, 센서)
- 네트워크: 오프라인 동작, 재시도, 데이터 절약 모드
- 백그라운드 정책: iOS BGTask, Android Doze/JobScheduler
- 권한 모델: 런타임 권한, privacy nutrition label, ATT
- 앱 크기, 동적 라이브러리, code signing
- 앱 스토어 심사 정책 (privacy, 결제, 콘텐츠)
서버/웹 관점은 일부러 무시한다.
```

**입력**: 모바일 앱 코드/PR, feature 명세, OS 정책 변경
**출력**: 플랫폼 위험/제약 list, 심사 거부 가능성 평가
**어울리는 LLM 특성**: 플랫폼 지식. Claude (긴 context로 OS docs) 또는 Codex.

---

### 5.4 `devops-sre` — 운영/안정성 관점

**목적**: 운영 가능성(operability), 관측성, incident response를 본다. SLO/SLI 관점 의사결정.

**Prompt 패턴**:
```
당신은 senior DevOps/SRE engineer다. 다음 입력을 오로지 운영 관점에서만 본다:
- 배포: 롤백 가능성, blue/green, canary, kill switch
- 관측성: log/metric/trace coverage, alert actionability, runbook 존재
- SLO: 변경이 SLI(latency, error rate, saturation)에 미칠 영향
- 장애 모드: 단일 장애점 (SPOF), cascading failure, blast radius
- on-call burden: pager noise, false positive, MTTR
- IaC, secret 회전, capacity planning
개발 관점(feature 구현 우아함)은 일부러 무시한다.
```

**입력**: 배포 파이프라인, runbook, alert 정의, infra 변경 PR
**출력**: 운영 우려 list (블로커 / SLO 영향 / runbook 누락 등)
**어울리는 LLM 특성**: 시스템 + 운영 경험. Claude (정성 risk reasoning) 또는 Codex (정확).

---

### 5.5 `embedded-engineer` — 자원 제약 / 실시간 관점

**목적**: 펌웨어, IoT, 실시간 시스템 관점. CPU/메모리/전력 제약, deadline, 하드웨어 인터페이스를 본다.

**Prompt 패턴**:
```
당신은 senior embedded/firmware engineer다. 다음 입력을 오로지 자원 제약 / 실시간 관점에서만 본다:
- 메모리: 동적 할당 회피, stack 깊이, fragmentation
- 타이밍: ISR 지연, deadline miss, jitter
- 전력: sleep/wake, peripheral 활성 시간, 배터리 수명 영향
- 하드웨어 인터페이스: SPI/I2C/UART, DMA, register 접근 race
- 디버깅: 로그 채널 제약, JTAG, OTA 업데이트 안전성
- 안전 표준 (해당 시): MISRA, IEC 61508, ISO 26262
일반 서버/웹 관점은 일부러 무시한다.
```

**입력**: 펌웨어 코드, 하드웨어 스펙, 전력/타이밍 측정
**출력**: 자원 위반 list, 실시간 deadline 위험 평가
**어울리는 LLM 특성**: 시스템 저수준 정확성. Codex (정확).

---

### 5.6 `data-engineer` — 데이터 파이프라인 / 품질 관점

**목적**: ETL/ELT 파이프라인, 스키마 진화, 데이터 품질, lineage를 본다.

**Prompt 패턴**:
```
당신은 senior data engineer다. 다음 입력을 오로지 데이터 파이프라인 관점에서만 본다:
- 파이프라인: idempotency, backfill 가능성, late-arriving data 처리
- 스키마 진화: 호환성 (forward/backward), nullable 정책, schema registry
- 데이터 품질: null/duplicate/outlier 감지, freshness SLA
- lineage: 상류/하류 영향, downstream consumer 식별
- 비용: 스토리지 grade (hot/warm/cold), partition, clustering
- privacy/compliance: PII, GDPR 삭제 요구, 보존 기간
모델 학습 알고리즘 관점은 일부러 무시한다.
```

**입력**: DAG 정의, 스키마, 데이터 품질 메트릭, downstream dashboard
**출력**: 파이프라인 위험/누락 list, lineage 영향 평가
**어울리는 LLM 특성**: 데이터 + 시스템 사고. Codex (정확) 또는 Gemini (긴 context로 schema 전체).

---

### 5.7 `ml-engineer` — 모델 배포/MLOps 관점

**목적**: 모델 deploy, serving, monitoring, retraining loop를 본다. 알고리즘 자체보다 운영 측면.

**Prompt 패턴**:
```
당신은 senior ML engineer (MLOps)다. 다음 입력을 오로지 모델 운영 관점에서만 본다:
- serving: latency budget, batch vs online, A/B 분기, traffic shifting
- 재현성: feature store 일관성, training-serving skew
- 모니터링: feature drift, prediction drift, data quality, model-specific 메트릭
- 재학습: trigger 조건 (drift, schedule), rollback 정책
- 모델 버전 관리: registry, lineage, artifact 무결성
- 비용: GPU 활용, autoscaling, quantization/distillation 기회
알고리즘 novelty / 학습 알고리즘 자체는 일부러 무시한다 (그건 ml-researcher 영역).
```

**입력**: 모델 deploy 명세, 모니터링 dashboard, training pipeline, A/B 결과
**출처**: 운영 위험 list, drift/skew/SLO 위반 후보
**어울리는 LLM 특성**: 시스템 + ML 운영 경험. Claude / Codex.

---

### 5.8 `ml-researcher` — 알고리즘 / 실험 / 학술 관점

**목적**: 새 모델/알고리즘 제안 또는 평가. 실험 설계, 통계적 유의성, novelty, 재현성을 본다.

**Prompt 패턴**:
```
당신은 ML researcher다. 다음 입력을 오로지 학술 관점에서만 본다:
- novelty: 기존 work 대비 무엇이 새로운가, 명확한 contribution 정의
- 실험 설계: baseline 적절성, hyperparameter sweep 범위, ablation
- 통계: significance test, confidence interval, multiple-comparison correction
- 재현성: seed 고정, training script 공개, 환경 documentation
- 평가 metric의 적절성과 한계 (proxy vs intrinsic)
- 일반화: domain shift, OOD 평가, dataset bias
- 윤리/사회적 영향 (해당 시): bias, dual-use risk
배포/운영 관점은 일부러 무시한다 (그건 ml-engineer 영역).
```

**입력**: 논문 draft, 실험 결과, baseline 비교, ablation table
**출력**: 학술적 결함 list, 재현 가능성 평가, 추가 ablation 제안
**어울리는 LLM 특성**: 통계 reasoning + ML 지식. Claude (정성), Gemini (긴 context로 관련 paper 종합), Codex (실험 코드 정확).

---

### 5.9 `security-researcher` — 보안 위협 모델링 / 취약점 관점

**목적**: 시스템/코드/프로토콜의 보안 위협을 본다. threat model, attack surface, defense-in-depth.

**Prompt 패턴**:
```
당신은 security researcher다. 다음 입력을 오로지 보안 위협 관점에서만 본다:
- threat model: 가정된 attacker (capability, motivation), trust boundary
- attack surface: 외부 입력, 권한 경계, 네트워크 노출
- 공격 벡터 (OWASP/CWE 매핑): injection, deserialization, race, IDOR 등
- 암호 사용: alg 선택, key 관리, nonce 재사용, side channel
- 권한/인증: least privilege, token 수명, session fixation
- 공급망: dependency chain, build provenance, signing
- 방어 in depth: 단일 control 실패 시 보호 여부
- 데이터: PII/secret/credential 노출 경로
⚠️ 인증된 보안 평가/CTF/방어 목적에만 사용. 악의적 사용 시나리오 제안 금지.
구현 우아함 관점은 일부러 무시한다.
```

**입력**: 코드/PR, 위협 모델 문서, threat surface 다이어그램, dependency tree
**출력**: 취약점/위협 list (CWE 매핑 + severity), 우선 완화 권고
**어울리는 LLM 특성**: 정확성 + 적대적 reasoning. Codex (코드 정확) 또는 Claude (위협 모델 정성).

---

### 5.10 `systems-researcher` — OS/DB/분산 시스템 학술 관점

**목적**: 시스템 분야 (OS, DB, 분산, 컴파일러, 네트워크) 학술 관점. 이론적 한계, 설계 trade-off, 측정 방법론.

**Prompt 패턴**:
```
당신은 systems researcher다. 다음 입력을 학술적 시스템 관점에서만 본다:
- 이론적 한계: CAP, FLP, lower bound, 정보이론적 제약
- 설계 trade-off: throughput vs latency, consistency vs availability, simplicity vs perf
- 측정 방법론: workload 적절성, microbenchmark vs end-to-end, noise 제어
- 기존 work과의 관계: 어떤 시스템(예: Spanner, Calvin, Aurora)의 변형/조합인가
- 확장성 모델: 선형/sublinear/superlinear scaling, bottleneck 식별
- 정확성 증명 (해당 시): invariant, linearizability, serializability 증명 스케치
응용/제품 관점은 일부러 무시한다.
```

**입력**: 시스템 설계 문서, 벤치마크 결과, 관련 paper 참조
**출력**: 이론적 약점, 측정 결함, 비교 누락 paper 식별
**어울리는 LLM 특성**: 시스템 + 학술. Claude (긴 context), Gemini (paper 종합), Codex (벤치마크 코드 검증).

---

### 5.11 `hci-researcher` — 인간-컴퓨터 상호작용 / 사용자 연구 관점

**목적**: 사용자 행동, usability, 인지 부하, 접근성을 *연구 방법론* 관점에서 본다. ux-designer와 달리 *측정/실험/통계*에 초점.

**Prompt 패턴**:
```
당신은 HCI researcher다. 다음 입력을 사용자 연구 방법론 관점에서만 본다:
- 사용자 연구 설계: task 적절성, 참가자 sampling, within vs between subject
- 통계: significance, effect size, power, multiple comparison
- 측정: SUS/NASA-TLX 등 정량 + open-ended qualitative 조합
- 인지 부하: working memory, dual-task interference, learnability
- 접근성: WCAG 외에 motor/cognitive disability 시나리오
- 윤리: IRB, informed consent, dark pattern 회피
- 외적 타당도: lab vs field, population generalization
구현/디자인 우아함 관점은 일부러 무시한다.
```

**입력**: 사용자 연구 protocol, 결과 분석, UI 시안
**출력**: 연구 방법론 약점, 통계적 결함, 측정 누락 dimension
**어울리는 LLM 특성**: 통계 + 정성 reasoning. Claude (정성), Gemini (긴 protocol 종합).

---

### 5.X Domain × Stance 조합 빠른 참고

자주 쓰는 조합 (§6 Role 조합 패턴과 함께 읽으면 효과적):

| Stance \ Domain | backend | frontend | ML researcher | security-researcher |
|---|---|---|---|---|
| **proposer** | server-side 1차 설계 | UI flow 1차 설계 | 알고리즘 제안 | threat model 작성 |
| **devils-advocate** | "이 contract가 깨질 시나리오" | "이 UX가 a11y에서 실패할 케이스" | "실험이 무의미한 시나리오" | "취약점 우회 시나리오" |
| **evidence-checker** | log/metric 검증 | UX 측정 검증 | 통계 검증 | exploit 검증 |
| **risk-auditor** | SLO 위반 risk | UX failure risk | model bias risk | 데이터 유출 risk |
| **judge** | 시스템 안정성 기반 결정 | 사용자 인지 기반 결정 | novelty 기반 결정 | 위협 우선순위 결정 |

> 단일 axis로만 부여 금지 — 예를 들어 `proposer` 단독은 *어떤 시선으로 제안할지*가 빠져 일반론에 머문다. `backend-engineer × proposer`로 구체화하면 server-side context가 입력에 자동 반영된다.

---

## 6. Role 조합 패턴

> 각 패턴의 role은 **stance × domain** 두 axis로 부여한다. 아래에서 `proposer`라 적힌 부분은 실제로 `<domain> × proposer` 형태로 구체화되어야 한다 (예: `backend-engineer × proposer`).

### 6.1 단순 리뷰 (3 agent)
`proposer` → `devils-advocate` → `judge`
> Domain 적용 예: `backend-engineer × proposer` → `security-researcher × devils-advocate` → `staff-engineer × judge` (서로 다른 분야로 cross-domain critique 확보).

### 6.2 균형 토론 (5 agent, DEBATE 스타일)
`proposer (angel)` ↔ `devils-advocate` (N round) → `judge` → `tie-breaker` (필요 시)

### 6.3 D3 패턴 (다층 배심원)
2 advocates (proposer + counter-proposer) → `judge` (rubric 채점) → `juror-panel` (다양한 persona) → 최종 결정

### 6.4 문서 개선 통합 패턴 (본 작업에서 사용)
```
Round 0: 각 LLM × proposer
Round 1: 각 LLM × devils-advocate (cross-model critique)
Round 2: 각 LLM × defender/reviser (자기 안 수정)
Round 3: domain-specialist 병렬 (architect, pedagogy, evidence-checker, risk-auditor 등)
Round 4: synthesizer (LLM 1개) → judge (LLM 1개)
Round 5: implementer → consistency-checker (final pass)
```

### 6.5 빠른 결정 (single round)
`proposer` 병렬 N개 → `judge` 단독 (Free-MAD 스타일)

### 6.6 Domain-orthogonal critique 패턴 (분야 lens 다양화)

동일 작업물을 *서로 다른 분야 lens*로 동시에 비판:

```
1 작업물 (예: 시스템 설계 PR)
  ├─ backend-engineer × devils-advocate  (서버 측 약점)
  ├─ frontend-engineer × devils-advocate (사용자 인지 약점)
  ├─ security-researcher × evidence-checker (보안 가정 검증)
  ├─ devops-sre × risk-auditor (운영 risk)
  └─ ml-researcher × consistency-checker (통계 / 재현성 일관성)
→ synthesizer가 분야별 blind spot 합성
```

→ 동일 stance(`devils-advocate`)도 분야가 다르면 발견하는 약점이 다르다. cross-domain coverage가 cross-model heterogeneity와 *곱셈*으로 작동.

---

## 7. Role 배정 시 LLM 선택 가이드

검색한 reference들의 종합:

| Role 그룹 | 추천 LLM | 이유 |
|---|---|---|
| Proposer (generation) | 가장 강한 모델 (Opus / Gemini Pro / Codex high) | 1차 품질 결정 |
| Devil's Advocate | **Proposer와 다른** family | anchoring bias 방지 |
| Domain Specialist | specialty 강한 LLM | Gemini (긴 context), Codex (코드), Claude (정성) |
| Synthesizer | 큰 context + 균형 | Opus / Gemini Pro |
| Judge | **Advocate와 다른** family | model bias 분산 |
| Implementer | 정확성 (속도 우선) | Sonnet / Codex |
| Bridge | 부담 적음 | Sonnet / Haiku |
| **Domain — backend / embedded / data-engineer** | 코드/시스템 정확성 | **Codex** |
| **Domain — frontend / mobile / hci-researcher** | 정성 + 사용자 reasoning | **Claude** |
| **Domain — ml-engineer / ml-researcher / systems-researcher** | 통계 + 긴 paper context | **Gemini** 또는 **Claude** |
| **Domain — devops-sre / security-researcher** | 위협/risk 정성 + 정확성 | **Claude** (risk reasoning) 또는 **Codex** (코드 검증) |

> Domain × Stance 조합 시 LLM 배정: **domain의 어울리는 LLM**을 먼저 결정한 뒤, **stance의 cross-LLM 제약**(같은 LLM이 propose+critique 금지 등)을 만족하도록 조정. 예: `backend-engineer × proposer = Codex`, 같은 작업의 `× devils-advocate`는 Claude 또는 Gemini로.

---

## 8. Anti-Pattern (피해야 할 role 사용)

- ❌ 같은 LLM이 propose하고 critique — anchoring bias, self-consistency bias
- ❌ Judge가 advocate 출처를 알고 있음 — model affinity bias
- ❌ 균형 잡힌 critic — DEBATE 실험: strict negative가 더 좋은 결과
- ❌ 단순 majority voting만으로 결정 — silent agreement 위험
- ❌ Round 무한 진행 — 5 round에서 plateau. cost만 증가.
- ❌ Role마다 다른 LLM인데 동일한 system prompt 사용 — heterogeneity 손실
- ❌ Bridge agent가 외부 LLM 답변을 해석/요약 — 정보 손실, 결과 왜곡
- ❌ **Stance만 부여하고 domain lens 명시 안 함** — `proposer` 단독은 일반론으로 흐른다. `<domain> × <stance>`로 구체화.
- ❌ **모든 분야 role을 동일 LLM에 배정** — domain heterogeneity가 단일 LLM bias로 무력화. role 다양화 + LLM 다양화를 함께.
- ❌ **분야 외 영역까지 침범하는 role** — backend-engineer가 UX 디자인까지 평가하면 lens가 흐려진다. role 정의의 "일부러 무시한다" 룰 준수.

---

## 9. 참고

- DEBATE (Kim et al., ACL 2024): https://arxiv.org/html/2405.09935v2
- D3 framework: https://arxiv.org/pdf/2410.04663
- Free-MAD: https://arxiv.org/pdf/2509.11035
- Society of Minds (Du et al., 2023): https://arxiv.org/abs/2305.14325
- ChatEval: https://arxiv.org/abs/2308.07201
- llm-council (Karpathy): https://github.com/am-will/llm-council
- metaswarm: https://github.com/dsifry/metaswarm
- VoltAgent's awesome-claude-code-subagents: https://github.com/VoltAgent/awesome-claude-code-subagents
