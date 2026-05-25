# Component Discovery Ledger

> **무엇**: 외부 prompt 생태계 발굴의 공유 상태 파일(SSOT). `collect`가 후보를 append만, `approve`가 status를 갱신.
> **용도**: 주기적 component 발굴을 2단으로 분리 — 무인 `collect`는 후보만 적재(파일 생성 0), 사람은 `approve`로 batch 승인. 중복·재기각 방지.
> **시리즈 위치**: 독립 데이터 파일. `component-discovery-collect.md`(쓰기: append)와 `component-discovery-approve.md`(쓰기: status/build)가 공유. composer Phase 밖.
>
> **불변 규칙**: component 파일 생성 / router·composer 갱신 / library mutation은 **approve + 사람 승인 이후에만**. collect는 이 파일에 행 추가만.

---

## 0. 상태(status) 정의

| status | 의미 | 다음 run 동작 |
|---|---|---|
| `proposed` | collect가 새로 발굴, 미심사 | approve가 사람에게 제시 |
| `considered` | 과거 평가했으나 현재 gap 아님(중복/불필요) | **재발굴 skip** (collect dedup 대상) |
| `approved` | 사람이 승인, 빌드 대기 | approve가 component 빌드 |
| `built` | component 생성 + router/composer 반영 완료 | skip (이미 라이브러리에 존재) |
| `rejected` | 사람이 영구 기각 | **재발굴 skip** (collect dedup 대상) |

> collect는 신규 topic이 어느 행과도 의미상 중복이면 append하지 않는다(noise 방지). 새 정보가 생기면 기존 행 `비고`에 1줄만.

---

## 1. 후보 인덱스

| id | topic (component 후보명) | status | 정의유형 | gap 요약 | 출처 tier | 발굴일 | 갱신일 |
|---|---|---|---|---|---|---|---|
| RCA-001 | `root-cause-analysis-template` | proposed | template | spec.B=Analysis의 *진단*(원인 미상) 분기 공백 — 기존은 비교/가설검증/스칼라최적화만 | 2(Anthropic)+3(arXiv×3) | 2026-05-22 | 2026-05-22 |
| EVAL-001 | `eval-design-template` | considered | template | prompt-evaluation-rubric(조합 prompt 평가)와 표면 중복 — 재심 전 차별화 근거 필요 | 2(Anthropic) | 2026-05-22 | 2026-05-22 |
| CTX-001 | `context-engineering-patterns` | considered | infra | 조합 인프라 레이어 — System Invariant④(레이어 분리) 위반 위험 | 2(Anthropic) | 2026-05-22 | 2026-05-22 |
| LRA-001 | `long-running-agent-harness` | considered | template | `autonomous-optimization-loop`와 기능 중첩 | 2(Anthropic) | 2026-05-22 | 2026-05-22 |
| SKIT-001 | `speckit-spec-generation` | built | domain content | spec.B=Generation에서 코드 작성 직전 *기계 처리 가능한 spec/plan/tasks* 산출 부재 — rfc-writing은 자유 형식, 구조화 spec 분기 공백 | 1(github/spec-kit) | 2026-05-26 | 2026-05-26 |

---

## 2. 후보 상세 (proposed / approved 만 유지 — built/rejected 시 1줄로 축약)

### RCA-001 — `root-cause-analysis-template`

- **gap**: spec.B=Analysis 3 sub-branch(multi-agent 비교 / experiment 가설검증 / autonomous 스칼라최적화) 어디에도 "원인 미상 증상 진단"이 없음. `bug-fix`는 스킬 레이어(다른 층), 구조화 진단 방법론 부재.
- **정의유형**: template (experiment-design의 형제 — 진단 vs 검증).
- **devils-advocate 통과**: "experiment-design/bug-fix로 충분" 반론 → experiment는 *기존 가설 검증*, bug-fix는 스킬. 진단 분기는 공백. 생존.
- **출처**:
  - `[VERIFIED:webfetch tier3 https://arxiv.org/abs/2403.16362 accessed:2026-05-22]` AgentFL: comprehension→navigation→confirmation
  - `[VERIFIED:webfetch tier3 https://arxiv.org/abs/2512.06749 accessed:2026-05-22]` DoVer: intervention-driven hypothesis validation
  - `[VERIFIED:websearch tier3 https://arxiv.org/html/2602.06875]` TraceCoder: 정보수집→가설형성→수정 (html 전문 fetch 격상 권장)
  - `[VERIFIED:websearch tier2 https://www.anthropic.com/engineering/multi-agent-research-system]` 프로덕션 트레이싱 RCA
- **빌드 시 참고**: 2026-05-22 세션에 전문 draft + router(§1/§2/§7)·composer 통합 diff안이 작성됨(approve run에서 재생성·재검증). `[self-eval 경고]` — 블라인드 독립 채점 미수행.

### SKIT-001 — `speckit-spec-generation` (built 2026-05-26 — 1줄 축약)

`components/speckit-spec-generation.md`로 빌드 완료. spec.B=Generation + spec.A에 spec/plan/tasks/SDD/spec-driven/speckit 키워드 + spec.G=REVERSIBLE 분기. `rfc-writing-template`과 상호 배타. 출처 `[VERIFIED:webfetch https://github.com/github/spec-kit @2026-05-26]`. 블라인드 독립 채점 1회(general-purpose agent) PASS-with-fixes → §4 SSOT 표화 + 설치 명령 버전 태그 + token cost 현실화 fix 반영 후 commit.

---

## 3. Run 로그 (collect/approve append)

```
[COLLECT 2026-05-22] seeded from session discovery run (external-prompt-component-discovery)
- existing components baseline: 6 (agent-role-dictionary, multi-agent-analysis-template, code-review-rubric, experiment-design-template, rfc-writing-template, autonomous-optimization-loop)
- appended: RCA-001 (proposed)
- considered(skip 등록): EVAL-001, CTX-001, LRA-001
- search whitelist: anthropic.com, github.com/anthropics, arxiv
- note: 이 시드는 사람 세션 발굴분. 이후 무인 collect run이 이 형식으로 append.

[APPROVE 2026-05-26] task=speckit-spec-generation-component (single-candidate direct submission)
- input: composed prompt at .specs/speckit-spec-generation-component.composed.md
- gap analysis: 6 existing components 모두 planning/SDD 분기 미충족 (rfc는 자유 형식, 구조화 spec 부재)
- selected agents: [agent-role-dictionary(proposer §1.1 + consistency-checker §2.3 + evidence-checker §2.5 + devils-advocate §2.1), prompt-evaluation-rubric(§1+§2), context-injection-patterns]
- evidence: [VERIFIED:webfetch https://github.com/github/spec-kit @2026-05-26] (tier 1)
- blind review: general-purpose agent, P1-P7 + smell, PASS-with-fixes → §4 SSOT 표화, 설치 명령에 @vX.Y.Z 명시, pipx [ASSUMPTION] 격하, cost Low로 현실화, layer 필드 router §1.1과 동시 정의
- built: components/speckit-spec-generation.md
- integrated: router §1/§1.1/§2/§7, composer 머리말/§5, CLAUDE.md Invariant ④/컴포넌트 라이브러리, ledger §1/§2/§3
- status: SKIT-001 = built
```
