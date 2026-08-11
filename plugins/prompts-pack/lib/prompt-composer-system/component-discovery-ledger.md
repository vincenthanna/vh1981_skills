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
| RFL-001 | `review-reflector` (agent role 추가) | proposed | role (agent-role-dictionary §2 신규) | finding *발행 전* 자기검토 pass(진짜 결함이냐 / severity 적정 / line anchor 정확 / actionable / nit pruning) 부재 — evidence-checker는 *출처*만 검증, anchoring 금지는 anti-pattern 선언뿐 | 4(alibaba OSS; 개념 INFERRED) | 2026-06-07 | 2026-06-07 |
| RUL-001 | `code-review-custom-rule-layer` (rubric §9) | built | rubric-§ enhancement | code-review-rubric=고정 8축뿐 — 파일패턴-스코프 repo-local 룰 + override 우선순위(CLI>project>global>embedded) 부재. context-injection은 *사실* 주입이라 별개 | 4(alibaba OSS; schema VERIFIED) | 2026-06-07 | 2026-06-07 |
| CSC-001 | `code-review-changeset-scoping` (rubric §10) | built | rubric-§ enhancement (methodology) | rubric trigger만 "1000+LOC/5+파일" — *어떻게 분할·번들하나* 방법론 부재(인터페이스+구현 / 스키마+마이그레이션 / 코드+테스트 / i18n 쌍; cross-cutting invariant 가시성) | 4(alibaba OSS; 예시 VERIFIED·알고리즘 INFERRED) | 2026-06-07 | 2026-06-07 |

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

### RFL-001 — `review-reflector` (agent role)

- **gap**: 리뷰 finding을 *발행 전* 검증하는 자기검토 pass가 라이브러리에 없음. `agent-role-dictionary §2.5 evidence-checker`는 *주장에 출처가 있나*만 보고, §0 anchoring 금지는 "별도 critic 써라" 선언뿐 — *이 finding을 굳이 올릴 가치/severity 적정성/line anchor 정확성/actionability*를 검토하는 role은 없음.
- **정의유형**: role (stance, `agent-role-dictionary §2 Critical Roles` 신규). 코드뿐 아니라 모든 리뷰에 재사용 → 분석 컨텐츠 layer 유지(System Invariant④ 부합).
- **devils-advocate 통과**: "evidence-checker로 충분" 반론 → evidence-checker=fact-claim 출처 검증, reflector=finding *선별·심각도·위치·actionable* 검증. 기능 분리. LLM 코드리뷰 최대 실패모드(false positive)를 정면으로 침. 생존.
- **출처**:
  - `[VERIFIED:webfetch tier4 https://github.com/alibaba/open-code-review accessed:2026-06-07]` "Reflection 모듈 — content accuracy 개선" + "Positioning 모듈 — location accuracy"가 독립 시스템으로 존재(설계 thesis).
  - `[INFERRED]` 모듈 *메커니즘*은 미공개 — 제안 role의 절차는 모듈 *이름·목적* + 일반 LLM-review best practice에서 역설계. approve run에서 원본 prompt/소스 심층 read로 격상 필요.
- **빌드 시 참고**: agent-role-dictionary §2(Critical) 신규 role + §5.X/§6 조합표 cross-ref + router는 code-review-rubric 분기에 reflector 추가 검토. Positioning(line anchor)은 별도 role 아닌 reflector 절차에 흡수 권장.

### RUL-001 — `code-review-custom-rule-layer` (built 2026-06-07 — 1줄 축약)

`code-review-rubric.md §9 Custom rule layer`로 빌드. 파일패턴-스코프 repo-local 규칙 + 4계층 우선순위(인라인>project>global>embedded, first-match) + `{path,rule}` schema + §4 hard floor 불가침. 출처 `[VERIFIED:webfetch tier4 README-described @2026-06-07]`(rule.json 파일 미독립 fetch — 블라인드 리뷰 B-3 반영해 tag 격하). 블라인드 독립 채점(general-purpose agent) → 3 blocking(§5 template 확장, evidence tag 격하) + 5 non-blocking 전부 반영 후 commit.

### CSC-001 — `code-review-changeset-scoping` (built 2026-06-07 — 1줄 축약)

`code-review-rubric.md §10 대형 changeset 스코핑 & 번들링`으로 빌드. 번들 휴리스틱 표(인터페이스+구현/스키마+마이그레이션/코드+테스트/호출자+피호출자/i18n 쌍/경로 유사도) + cross-cutting pass + 비분해 changeset 단일-bundle fallback. 출처 `[VERIFIED:webfetch tier4 @2026-06-07]` divide-and-conquer + i18n 예시 / 일반 알고리즘 `[INFERRED]`(비공개). RUL-001과 동일 파일이라 1 commit으로 묶어 반영.

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

[COLLECT 2026-06-07] task=component-discovery (manual, source=github.com/alibaba/open-code-review)
- existing components baseline: 7 (agent-role-dictionary, multi-agent-analysis-template, code-review-rubric, experiment-design-template, rfc-writing-template, autonomous-optimization-loop, speckit-spec-generation)
- searched: alibaba/open-code-review (tier4 vendor OSS) — webfetch repo page + raw README
- appended: RFL-001, RUL-001, CSC-001 (all proposed)
- considered/rejected (devils-advocate 탈락): 결함 taxonomy 체크리스트(NPE/race/injection/leak) — rubric A1+A2+security-researcher CWE로 이미 커버, redundant; deterministic÷agent 분리는 *insight*(infra 변경은 Invariant④로 비권장, ledger 미등재)
- dedup: 기존 RCA/EVAL/CTX/LRA/SKIT와 의미 중복 0 (RUL-001 ≠ CTX-001: CTX는 infra-layer 신규였고 RUL은 rubric §확장)
- evidence note: rule.json schema(RUL-001)만 VERIFIED, reflection/positioning 메커니즘은 미공개라 RFL-001/CSC-001 일부 INFERRED → approve run에서 원본 prompt/소스 심층 read로 격상 필요
- note: RUL-001·CSC-001은 같은 파일(code-review-rubric.md) §확장 → approve 시 묶어 검토 권장. commit은 사람 위임.

[APPROVE 2026-06-07] task=component-discovery-approve (RUL-001 + CSC-001, batch)
- input: ledger proposed 3건 (RFL-001 / RUL-001 / CSC-001)
- 사람 게이트 #1 (batch 심사): RUL-001 승인, CSC-001 승인, RFL-001 **보류**(proposed 유지 — 다음 batch)
- build 단위: 둘 다 code-review-rubric.md §확장 → self_upgrade "1회1대상"의 대상=code-review-rubric.md 1파일, §9+§10 1 commit (no new file → 컴포넌트 수 7 유지, CLAUDE.md 무변경)
- selected agents: [agent-role-dictionary(proposer §1.1 + evidence-checker §2.5 + consistency-checker §2.3 + devils-advocate §2.1), prompt-evaluation-rubric(§1 P1-P7 + §2 smell)]
- evidence: RUL-001 schema=`[VERIFIED README-described]`(rule.json 미독립 fetch), CSC-001 divide-and-conquer+i18n 예시=`[VERIFIED]` / 일반 알고리즘=`[INFERRED]`(docs 404·비공개)
- blind review: general-purpose agent(별도 세션, self_upgrade §B4 fallback L2), 블라인드. 결과 DO-NOT-MERGE-AS-IS → 3 blocking(B-1/B-2 §5 template 미확장, B-3 schema evidence 과claim) + 5 non-blocking. 전부 수정 후 재적용.
- built: code-review-rubric.md §9(custom rule layer) + §10(changeset 스코핑/번들링), §0 metadata v1.0→1.1, §1.1/§2/§5 보강
- integrated: router §1 catalog row + §2 Review 분기 note, composer §5 발췌 가이드. (새 분기/새 component 아님 → §7 매핑·CLAUDE.md 무변경)
- status: RUL-001 = built, CSC-001 = built, RFL-001 = proposed(보류)
```
