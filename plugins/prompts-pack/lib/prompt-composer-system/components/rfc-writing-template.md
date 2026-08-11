# RFC / Design Doc Writing Template

> **무엇**: RFC/ADR/design doc 같은 팀·외부 audience 대상 설계 문서를 pedagogy-reviewer×proposer + consistency-checker lens로 작성하는 워크플로우 template.
> **용도**: 설계 결정을 문서화하고 이해당사자 합의를 끌어내야 할 때 활성화.
> **시리즈 위치**: composer Phase 4 (Assembly). `experiment-design-template.md`가 *실험 검증*이라면 본 template은 *설계 문서화 + 합의*.
>
> 산출물: motivation → alternatives → design → tradeoffs → rollout → stakeholder feedback → final document.

---

## 0. Router 등록 metadata

| 항목 | 값 |
|---|---|
| component name | `rfc-writing-template.md` |
| trigger signals | spec.B = Generation + spec.F = team/external audience + RFC/ADR/design doc/spec 키워드 |
| inputs | 결정 대상 (변경/도입/폐기), motivation, 영향 받는 stakeholder list, prior 관련 결정 |
| outputs | RFC markdown (또는 ADR — 짧은 변형), stakeholder feedback log, decision status |
| cost (rough tokens) | Medium (~1.5k 발췌 / ~10k full) |
| 충돌 가능 component | `experiment-design-template.md` (영역 다름 — 실험 vs 설계 문서화. 함께 쓰면 over-scope) |
| version | 1.0 |
| owner | prompt-composer-system 유지자 |
| layer | **domain content (generation / 자유 형식 설계 문서)** — CLAUDE.md "조합 인프라(5) / 분석 컨텐츠(2) / domain content" 3축 분류. router §1.1 metadata 정의 참조. |

> **trigger 분기**: router §2 step 2에서 `B = Generation` AND `F = 외부/팀` AND 결정 영향 범위 ≥ 다수 → 본 template 활성화. 1인 노트/메모는 bypass.

---

## 1. 사용 시점 / 비사용 시점

### 1.1 사용 시점

- 다음 중 1개 이상 해당하는 결정:
  - 1주일 이상 영향, 5명 이상의 engineer가 코드 영역 공유
  - API 외부 노출 / 호환성 변경
  - infra / 보안 / 데이터 정책 변경
  - 신규 시스템 도입 / 폐기 / migration
- 외부 audience (다른 팀, OSS 기여자, 클라이언트) 가 후속 이해 필요.
- spec.G = `[COSTLY-TO-REVERSE]` 또는 `[IRREVERSIBLE]`.

### 1.2 비사용 시점 (bypass)

- 단일 PR 으로 끝나는 변경 (PR description 으로 충분).
- 실험적 prototype — RFC 작성 비용 > prototype 비용.
- 의사결정자가 1명 + 영향 범위 본인만.
- 긴급 incident 대응 (postmortem 으로 사후 작성).

### 1.3 ADR 변형 사용

ADR (Architecture Decision Record) 은 RFC의 단축 변형:
- 결정 1개 + 1-2 페이지.
- §2 Step 0/1/2/4 만 사용 (Step 3 tradeoffs는 inline, Step 5 stakeholder review는 lightweight).
- 적합 시점: 작은 결정 + 후속 reference 가 필요할 때.

---

## 2. 작업 모델 (Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│ Author (메인 세션)                                            │
│  phases: motivate → propose → critique → revise → finalize    │
│  - 학습자/외부 reader 입장에서 명확성 우선                    │
│  - 모든 정의/참조의 정합성 의무                               │
└─────────────────────────────────────────────────────────────┘
        │ (pedagogy-reviewer × proposer 자세)
        ▼
┌──────────────────────────────────────────────────────────┐
│  Consistency-checker (별도 LLM 또는 reviewer)            │
│  (agent role: §1.2 consistency-checker)                  │
│  - 정의/명칭/참조 일관성 검토                             │
│  - 깨진 참조, 미정의 용어, 모순 진술 식별                 │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│  Stakeholder reviewer panel (사람)                       │
│  - 영향 받는 팀 / OSS 기여자 / 의사결정자                 │
│  - 결정 권한과 review 기한 명시                           │
└──────────────────────────────────────────────────────────┘
```

> **Lens 분리** (`agent-role-dictionary.md §0`): author 가 자신의 RFC를 자기가 정합성 검토하면 anchoring. consistency-checker는 별도 agent.

---

## 3. 절차 (Step 0 ~ Step 6)

### Step 0 — Motivation + scope

산출물: `<rfc-id>.md` 상단 섹션.

```markdown
# RFC: <Title> (RFC-<n>)

**상태**: Draft / Review / Accepted / Rejected / Superseded by <ref>
**작성자**: <이름>
**작성일**: <YYYY-MM-DD>
**리뷰 기한**: <YYYY-MM-DD>
**영향 받는 시스템 / 팀**: <list>

## 1. Motivation
- 현재 무엇이 문제인가? (관찰 가능한 사실)
- 왜 *지금* 다뤄야 하는가? (시급성)
- 본 RFC가 *답할 질문* 1-2개 (한 문장씩)

## 2. Scope
- in-scope: <list>
- out-of-scope: <list — 명시적 제외>
- non-goal: <자주 오해될 수 있는 인접 문제와의 경계>
```

**Gate**: G0 (조건·실패 처리는 §4 SSOT).

### Step 1 — Alternatives considered

산출물: `## 3. Alternatives considered`

```markdown
## 3. Alternatives considered

### Alt-A: <이름>
- 설명 (2-3 줄)
- Pros: <list>
- Cons: <list>
- 평가: <왜 채택 안 함 또는 채택 후보>

### Alt-B: <이름>
...

### Alt-Z: Do nothing (status quo)
- Pros: <list>
- Cons: <list>
- 평가: <왜 부족한가>
```

> **"Do nothing" 의무** — 현 상태 유지의 cost를 명시하지 않으면 RFC 전체가 *change for change's sake* 인지 검증 불가.

**Gate**: G1 (조건·실패 처리는 §4 SSOT).

### Step 2 — Proposed design

산출물: `## 4. Proposed design`

```markdown
## 4. Proposed design

### 4.1 개요
<채택안의 핵심 아이디어 1-2 단락>

### 4.2 상세 design
<아키텍처 / API / 데이터 모델 / 흐름>

[그림 / 다이어그램 위치]
- mermaid 또는 ASCII 권장. 외부 image 의존 최소.

### 4.3 핵심 결정 (Decisions)
| Decision | 선택 | 근거 | 대안 |
|---|---|---|---|
| D1: <이름> | <선택> | <근거 + reference> | <Alt-X §3> |
| D2: ... | ... | ... | ... |

### 4.4 정의 (이 RFC에서 도입하는 새 용어)
- **<용어>**: <정의>
- **<용어 2>**: <정의>
```

**Gate**: G2 (조건·실패 처리는 §4 SSOT).

### Step 3 — Tradeoffs / drawbacks / open questions

산출물: `## 5. Tradeoffs / 6. Open questions`

```markdown
## 5. Tradeoffs / drawbacks

### 5.1 명시적 tradeoffs
- 채택안이 *희생하는 것* + 그 cost 추정
- 예: "X를 위해 Y를 포기. Y는 ~6개월 후 별도 해결 예상."

### 5.2 Devil's advocate review
- 채택안을 *깨는* alternative 가설: <list>
- 실패 시나리오: <list>
- 가장 회피하고 싶은 비판 + 답변

## 6. Open questions
- 본 RFC가 *답하지 않는* 질문 (후속 RFC 또는 회의 필요)
- 검증 필요한 가정 `[ASSUMPTION]` + 검증 방법
```

> Devil's advocate review 는 본인이 아닌 별도 reviewer 의 input 의무 — anchoring 방지.

**Gate**: G3 (조건·실패 처리는 §4 SSOT).

### Step 4 — Rollout plan

산출물: `## 7. Rollout plan`

```markdown
## 7. Rollout plan

### 7.1 Migration path
- Phase 1: <한 줄>
- Phase 2: ...
- 각 phase의 reversibility: `[REVERSIBLE]` / `[COSTLY-TO-REVERSE]` / `[IRREVERSIBLE]`

### 7.2 Backward compatibility
- 기존 사용자 / API consumer 영향: <영향 list>
- 호환성 기간: <deprecation timeline>

### 7.3 Rollback plan
- 단계별 rollback procedure
- rollback 한계 (어느 단계 이후 rollback 불가)

### 7.4 Success metrics
- 무엇을 보면 "rollout 성공"이라고 판단?
- 측정 가능 metric (가능하면 dashboard URL 또는 query)
```

**Gate**: G4 (조건·실패 처리는 §4 SSOT).

### Step 5 — Stakeholder review

산출물: `## 8. Stakeholder review log`

```markdown
## 8. Stakeholder review log

### 8.1 Reviewer assignment
| Reviewer | 영역 | review 기한 | 결정 권한 |
|---|---|---|---|
| <이름/팀> | <어떤 측면> | <YYYY-MM-DD> | approver / consulted / informed |

### 8.2 Feedback round 1 (date: <YYYY-MM-DD>)
- <reviewer>: <feedback 요약>
  - author response: <accept / partial / reject + 근거>
  - 반영 위치: <§X.Y>

### 8.3 Consistency-check log (별도 agent)
- 정의되지 않은 용어 사용: <list>
- 깨진 참조: <list>
- 모순 진술: <list>
- 결과: <0건 / N건 (수정 완료) / N건 (미해결)>
```

**Gate**: G5 (조건·실패 처리는 §4 SSOT).

### Step 6 — Final + Glossary + Status

산출물: 문서 마지막 + 별도 status update.

```markdown
## 9. Glossary
<§4.4의 새 용어 + 본문에서 사용된 모호 가능 용어>

## 10. References
- 관련 RFC / ADR / paper / docs (각각 [VERIFIED:*] tag)

## 11. Revision history
| Date | Version | Change | Author |
|---|---|---|---|
| <date> | 0.1 | Initial draft | <name> |
| <date> | 0.2 | Address reviewer X feedback | <name> |
| <date> | 1.0 | Accepted | <name> |
```

**Gate**: G6 (조건·실패 처리는 §4 SSOT).

---

## 4. Quality Gates (G0 ~ G6 통합) — SSOT

> 이 표가 Gate 정의의 **단일 출처(SSOT)**다. §3 각 Step은 해당 Gate를 포인터로만 참조한다 (조건 중복 금지 — drift 방지).

| Gate | 조건 | 실패 시 처리 |
|---|---|---|
| **G0** | Step 0 — motivation 사실 기반 + scope/out/non-goal 3종 + 질문 1-2개 | motivation 재작성 |
| **G1** | Step 1 — 대안 ≥ 3 (Do nothing 포함) + Pros/Cons/평가 | 대안 추가 검토 |
| **G2** | Step 2 — design 추적 가능 + 정의 표 + 외부 의존 tagged | design 보강 |
| **G3** | Step 3 — tradeoffs ≥ 2 + devils-advocate review (별도) + open q 검증 방법 | tradeoffs/review 보강 |
| **G4** | Step 4 — migration reversibility + backward compat + rollback + success metric | rollout 재설계 |
| **G5** | Step 5 — approver ≥ 1 + consistency-check Critical 0 + feedback response | review 추가 round |
| **G6** | Step 6 — glossary 정합 + references tagged + status 명시 | finalization 보강 |

---

## 5. 산출물 디렉토리 구조

```
docs/rfcs/<rfc-id>/
├── <rfc-id>.md            # 본 RFC 본문 (Step 0~6 통합)
├── alternatives/          # (선택) 대안별 상세 분석
│   ├── alt-a.md
│   └── alt-b.md
├── diagrams/              # (선택) 다이어그램 source (mermaid / draw.io)
│   └── overview.mmd
└── reviews/               # stakeholder feedback raw
    ├── reviewer-A-round1.md
    └── consistency-check.md
```

ADR 변형:
```
docs/adrs/
├── 0001-<title>.md
├── 0002-<title>.md
└── ...
```

> commit 정책: RFC 본문은 PR로 review 후 commit. accepted 상태 변경은 별도 PR (revision history 누적).

---

## 6. Anti-patterns

- ❌ **Motivation이 vague** — "더 좋게 만들기 위해" 같은 표현. G0 차단. *관찰 가능한 사실* + tag.
- ❌ **"Do nothing" 대안 누락** — status quo 의 cost 미평가. G1 차단.
- ❌ **Tradeoffs 섹션이 "단점 없음"** — 모든 결정은 something 희생. G3 차단.
- ❌ **본인이 본인 RFC 의 consistency-check** — anchoring. 별도 agent (`§1.2 consistency-checker`) 또는 reviewer.
- ❌ **Stakeholder review 없이 self-approve** — G5 차단. approver ≥ 1 명시 의무.
- ❌ **새 용어 정의 전 사용** — pedagogy-reviewer lens 위반. §4.4 정의 표 → 본문 사용 순서.
- ❌ **Rollback 없는 IRREVERSIBLE rollout** — Step 4 + spec.G 매트릭스 위반. PoC 또는 canary 의무.
- ❌ **Open question 을 답 없이 닫음** — "나중에 결정" 표현 금지. *검증 방법* 또는 *후속 RFC* 로 escalate.
- ❌ **외부 reference 의 access date 누락** — 6개월 후 stale 가능. `[VERIFIED:webfetch <tier> <URL> accessed:<date>]` 의무.
- ❌ **Revision history 미관리** — accepted 후 silent edit. 변경은 별도 PR + revision row 추가.
- ❌ **Status 미명시** — Draft 인지 Accepted 인지 모르면 후속 reader 가 의사결정 단계 추적 불가.

---

## 7. 시나리오 예시 — Mini RFC

### 시나리오: 신규 internal API gateway 도입 결정

**Step 0**:
- Motivation: 5개 backend service 가 각자 auth / rate limit 구현 중복. `[VERIFIED:static services/*/auth/*]`. 2명 engineer-month 의 중복 작업이 분기마다 발생 `[INFERRED ← 최근 6개월 PR 분석]`.
- Scope: 5개 service 의 auth/rate-limit 통합. 단일 gateway 도입.
- Out-of-scope: service mesh 도입 (별도 RFC), 외부 partner API (다른 보안 모델).
- Non-goal: micro-service 분해 정책 변경.

**Step 1**: 대안 = (A) 단일 API gateway (Kong/Envoy), (B) shared library (각 service에 import), (C) sidecar (Istio 등 service mesh subset), (Z) Do nothing.

**Step 2**: 채택 = A. design 상세 — gateway가 auth 검증, rate-limit, request log. service들은 health check만. D1=Kong vs Envoy 비교 (Envoy 선택, 근거: 사내 Envoy 운영 경험).

**Step 3**: tradeoffs — gateway가 SPOF (HA 구성으로 mitigate). Latency +5ms 추정 `[INFERRED]`. Devils-advocate review: "Gateway 자체의 보안 surface 가 5 service 모두 동시 영향" — mitigation: gateway팀 별도 보안 검토.

**Step 4**: Phase 1 = 1 service migrate (canary, `[REVERSIBLE]`). Phase 2 = 5 service 전체 (`[COSTLY-TO-REVERSE]`). rollback = service-by-service revert. success metric = "중복 auth 코드 0 lines + p99 latency Δ < 10ms".

**Step 5**: Reviewers = backend team lead (approver), SRE (consulted), security team (consulted). Consistency-check: "API gateway"와 "service gateway"가 혼용 → "API gateway" 로 통일.

**Step 6**: Status = Accepted. Revision = 0.1 (draft), 0.2 (security review 반영), 1.0 (accept).

---

## 8. 참고

### 8.1 내부 (라이브러리 내)

- `agent-role-dictionary.md` §1.2 `pedagogy-reviewer` (학습자 명확성), `consistency-checker` (정의/참조 정합) — 본 template의 lens 출처. `[VERIFIED:static prompts/prompt-composer-system/agent-role-dictionary.md:57,160]`
- `multi-agent-analysis-template.md` §2.2 reversibility tagging — 본 template Step 4 rollout 의 tag 출처. `[VERIFIED:static prompts/prompt-composer-system/multi-agent-analysis-template.md]`
- `experiment-design-template.md` — 본 RFC의 *결정을 검증하기 위한 실험* 이 필요하면 sequential 사용. `[VERIFIED:static prompts/prompt-composer-system/experiment-design-template.md]`

### 8.2 외부 (RFC/ADR/design doc 형식 영향)

- IETF RFC 7991, "The 'xml2rfc' Vocabulary Used in IETF" (2016) — 본 template은 매우 단순화한 변형. Step 0~2의 상태(Draft/Review/Accepted/Rejected/Superseded) 모델의 출처. `[ASSUMPTION canonical URL: https://www.rfc-editor.org/rfc/rfc7991.html 검증 방법: web fetch + tier=official(IETF) 확인]`
- Michael Nygard, "Documenting Architecture Decisions" (Relevant blog, 2011) — ADR 원형. §1.3 ADR 변형의 출처. `[ASSUMPTION canonical URL: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions 또는 https://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions 검증 방법: web fetch + tier=community(개인 블로그) 확인. 원본 도메인 변경 가능 — Wayback Machine 대안.]`
- Rust RFC 프로세스 — public repo PR-driven RFC + numbered RFC + tracking issue 패턴. Step 5 stakeholder review log의 영향. `[ASSUMPTION canonical URL: https://github.com/rust-lang/rfcs 검증 방법: web fetch + tier=official(Rust 공식) 확인]`
- Google Design Doc convention — TL;DR 도입, alternatives 의무, "Non-goals" 명시 패턴. Step 0 scope/out/non-goal 3종의 출처. `[ASSUMPTION 산업 공유 자료 (구체 URL 없음) 검증 방법: 공개 컨퍼런스 talk 또는 책 "Software Engineering at Google" 참조]`
- GitLab Blueprint format — handbook의 공개 design doc 템플릿. `[ASSUMPTION canonical URL: https://about.gitlab.com/handbook/engineering/architecture/ 검증 방법: web fetch + tier=vendor 확인]`

> ⚠️ 외부 reference의 URL은 라이브러리 작성 시점(2026-05-19)에 web fetch 미수행. 일부 도메인(Relevant blog 등)은 archive 가능성. 첫 운영 시 composer Phase 5 P5 단계 또는 `evidence-checker` role에서 `[VERIFIED:webfetch <tier> <URL> accessed:<date>]`로 격상 의무. URL 무효화 발견 시 Wayback Machine archive로 대체.
