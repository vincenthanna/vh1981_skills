# Optimized Prompt Composer

> **무엇**: rough request + prompt component library → 실행 가능한 optimized prompt를 만드는 메타 orchestrator. 이 파일 자체가 조합용 prompt다.
> **용도**: Claude / Claude Code 메인 세션의 prompt로 붙여 Phase 1→7로 prompt를 조립·평가할 때 사용.
> **시리즈 위치**: composer 본체(Phase 1~7 전체 진행). 아래 component들을 호출.
>
> **시리즈 구성** (모두 같이 사용 — 파일 path는 `prompts/prompt-composer-system/` 기준 상대 경로):
>
> **조합 인프라 — `builder/` 디렉토리**:
> 1. `builder/task-spec-template.md` — Phase 1 입력 형식
> 2. `builder/prompt-component-router.md` — Phase 2 routing 로직
> 3. `builder/context-injection-patterns.md` — Phase 3 context 주입 패턴
> 4. `builder/prompt-evaluation-rubric.md` — Phase 5, 7 평가 기준
> 12. **`builder/optimized-prompt-composer.md`** ← 이 파일 (orchestrator)
>
> **컴포넌트 — `components/` 디렉토리**:
> 5. `components/multi-agent-analysis-template.md` — 가장 자주 활성화하는 component (multi-topic 분석)
> 6. `components/agent-role-dictionary.md` — role 정의 카탈로그
> 7. `components/code-review-rubric.md` — PR/diff 평가 (Review task)
> 8. `components/experiment-design-template.md` — 실험 설계·실행·분석 (Analysis + ml-researcher lens)
> 9. `components/rfc-writing-template.md` — RFC/ADR/design doc 작성 (Generation + team audience)
> 10. `components/autonomous-optimization-loop.md` — 측정가능 지표의 자동 반복 최적화 (Analysis + 탐색, REVERSIBLE)
> 11. `components/speckit-spec-generation.md` — speckit(github/spec-kit) 기반 spec/plan/tasks 생성 (Generation + planning/SDD, REVERSIBLE; rfc-writing-template과 상호 배타)

---

## 사용법

### 방법 A — Claude.ai / 일반 chat
이 파일 전체를 system / 첫 user prompt로 붙여넣고, rough request를 이어서 적는다.

### 방법 B — Claude Code SKILL.md로 등록
이 파일을 `.claude/skills/prompt-composer/SKILL.md`로 저장.
frontmatter는 §0 참고. 이후 "이 작업을 위한 prompt를 만들어줘" 같은 자연어로 trigger.

### 방법 C — 메인 세션에서 partial 호출
필요한 phase만 발췌 (예: Phase 1만 — spec 추출만) 후 자체 사용.

---

## §0. Skill frontmatter (방법 B 사용 시)

```yaml
---
name: prompt-composer
description: >
  Rough request를 받아 prompt component library에서 적절한 것들을 선택하고 조합하여
  optimized prompt를 생성한다. 동일 task의 반복 / multi-topic 평가 / 외부 보고 대상
  task에서 활성화. "이 작업을 위한 prompt 만들어줘", "여러 옵션 평가하고 싶어",
  "task 위한 component 조합해줘", "이 분석 prompt 최적화해줘" 같은 요청에 trigger.
---
```

---

## §1. Composer가 수행하는 7 phase

```
Phase 1: Intake          — rough request → Task Spec 추출
Phase 2: Routing         — component 선택 + bypass 판단
Phase 3: Context         — 주입할 context source 식별
Phase 4: Assembly        — composed prompt 작성
Phase 5: Pre-validation  — composed prompt 자체 검증
Phase 6: Execution       — composed prompt 실행 (또는 사용자에게 반환)
Phase 7: Post-eval       — 결과 평가 + 개선 loop
```

**각 phase 사이에 명시적 gate (G1-G6).** 이전 phase 미통과 시 다음으로 진행 금지.
(Gate 매핑: G1 Intake→Routing, G2 Routing→Context, G3 Context→Assembly, G4 Assembly→Pre-validation, G5 Pre-validation→Execution, G6 Post-eval Loop 종료. **Phase 6 Execution 뒤 별도 phase gate 없음** — lifecycle 메타 평가(`prompt-evaluation-rubric.md §5`)는 phase gate가 아닌 분기 cycle. ⚠ G7은 존재하지 않음 — eval-rubric §7 표 SSOT와 일치.)

---

## §2. Phase 1 — Intake

### Input
- Rough request (사용자의 자연어 요청)
- (선택) 기존 spec 파일이 있으면 path

### Action
1. `task-spec-template.md`의 A-E 필수 필드를 rough request에서 추출 시도.
2. 모호하면 사용자에게 단답형 질문 (max 3개, ask_user_input_v0 또는 자연어):
   - "Output Type이 Decision / Analysis / Generation / Review / Transformation 중 무엇입니까?"
   - "주요 평가 기준 또는 success criteria 2-3개를 알려주세요"
   - "산출물 audience는 누구입니까?"
3. Spec을 `.specs/<task-id>.md`로 저장 (단, dry-run 모드면 chat에 markdown으로만).
4. task-id는 kebab-case, 한글 가능 (예: `qwen-glm-gemma-eval`, `seal-onprem-cleanup`).

### Gate G1 (Intake → Routing)
- [ ] Spec A-E 5개 필수 필드 채워짐
- [ ] Purpose가 한 문장 + 단일 goal
- [ ] Success criteria가 측정 가능 (체크리스트 형태 권장)

**미통과** → 사용자에게 spec 보강 요청. composition 진행 금지.

---

## §3. Phase 2 — Routing

### Input
- Task Spec (Phase 1 결과)
- Component Catalog (`prompt-component-router.md` §1)

### Action
1. router decision tree (router §2) 적용 — 자동 실행:
   - spec.B → 후보 component 결정
   - spec.C topic count → multi-agent-template 활성/비활성
   - spec.G Reversibility → eval-rubric / judge persona 결정
   - spec.L Domain Lens → role-dict 활성화 list
   - spec.K Multi-LLM 신호 → pattern 6.8.X 결정
2. Bypass 조건 (router §3) 평가. **Bypass면 §3.x 분기로**.
3. Routing log 작성 (router §4 format) — `.specs/<task-id>.log`에 append.
4. Selected component의 estimated cost 합산, spec.D 예산과 대조.

### Bypass 분기 (§3.x)
Bypass 결정 시:
1. 사용자에게 알림: "이 task는 composition이 부적합합니다. 이유: <reason>."
2. 대안 제시: direct prompt 예시 또는 더 단순한 워크플로 권고.
3. 사용자가 "그래도 진행" 선택하면 cap 2 components로 minimal composition.
4. 그 외 → composition 종료.

### Gate G2 (Routing → Context)
- [ ] Routing log가 작성됨
- [ ] Selected component 수 ≤ 4
- [ ] 예산 위반 없음 (또는 사용자가 위반 인지하고 진행 결정)
- [ ] Bypass 시 사용자 알림 완료

---

## §4. Phase 3 — Context Identification

### Input
- Task Spec (특히 H. Prior Context, I. Environment, F. Audience)
- 가용 context sources (CLAUDE.md, memory, baseline, etc)

### Action
1. `context-injection-patterns.md` §1 표 기반으로 context source 식별.
2. 각 source에 대해 4 patterns 중 하나 결정 (Header / Body / Reference / Memory).
3. Redaction 필요 항목 미리 mark (context-injection §3).
4. **Context manifest 작성**:

```markdown
## Context Manifest
| Source | Pattern | Redaction | Where in composed |
|---|---|---|---|
| CLAUDE.md (project conventions) | Header | No | §2 of composed |
| spec.F audience | Header | No | §1 of composed |
| baseline.md | Reference | No | §5 - path only |
| env vars list | Reference | Yes (이름만) | §5 |
| memory durable pattern: <X> | Body | No | §4.x |
```

### Gate G3 (Context → Assembly)
- [ ] 모든 활성 context source가 manifest에 있음
- [ ] Redaction 필요 항목이 mark됨
- [ ] 큰 source는 Reference로 분류 (token 절약)
- [ ] User preference는 spec 명시된 것만 (자동 추론 금지)

---

## §5. Phase 4 — Assembly

### Input
- Spec + Routing log + Context Manifest

### Action
Composed prompt를 다음 layout으로 작성:

```markdown
# [Composed Prompt: <task-id>]

## 1. Role & Tone
당신은 <role from spec.F or default>. 응답 언어: <language from spec.D>.
<additional tone from manifest>

## 2. Project Context
<header-injected context, redacted>

## 3. Task

### 3.1 Purpose
<spec.A — 그대로>

### 3.2 Output Specification
- Type: <spec.B>
- Form: <spec.D format>
- Length / Scale: <spec.C>
- Reversibility (해당 시): <spec.G>

### 3.3 Constraints
<spec.D constraints, spec.J confidence required>

## 4. Activated Components

### 4.1 <Component_1>
출처: `<file_path>` § <발췌한 § 번호와 이름>

<핵심 패턴 발췌 — 본문 전체 복사 금지>

### 4.2 <Component_2>
...

(필요 시 §4.3, §4.4 — cap 4)

## 5. Run-specific Context (Reference)
- baseline: `<path>`  ← 읽지 못하면 즉시 abort, 분석 진행 금지
- prior: `<path>`
- env vars (redacted names only): [<name1>, <name2>]

## 6. Output Gates

실행 종료 조건:
- [ ] <spec.E 항목 1>
- [ ] <spec.E 항목 2>
- [ ] (해당 시) evidence tag 룰 준수 — multi-agent-template §2.1
- [ ] reversibility 명시 (action 권고일 때)
- [ ] (해당 시) counter-argument 포함

## 7. Routing Log (참조)
```
<routing log block 그대로 echo>
```
```

### Component 발췌 룰 (중요)

- **한 component에서 본문 전체 복사 금지.** 핵심 § 만 발췌 (예: 입력 contract / workflow / gates).
- **발췌 부분에 원본 path + § 명시** — 사용자가 deeper read 가능하도록.
- **모순 발견 시**: §1 (Role) 또는 §6 (Output Gates)에서 우선순위 결정.
- **failure-mode fallback 절도 함께 발췌** — 각 component의 "도구/Read 실패 시 abort·회귀" 절(예: multi-agent §3.1 abort-on-fetch-fail, autonomous §3 measure 실패 revert, code-review §9.6/§10.4-3 fallback)을 발췌에서 누락하지 말 것. (누락 시 eval-rubric §2.4 Missing fallback smell — 반복 audit 발견 B6.)
- **메인 component 1개 + 부속 component 1-3개** 구조 권장 (예: multi-agent-template이 메인, role-dict가 부속).

### 발췌 가이드 (자주 쓰는 §)

- `multi-agent-template.md`: §2 (framework), §3.1 (topic-analyst 입력 contract), §4 (workflow), §7 (gates), §8 (anti-patterns)
- `agent-role-dictionary.md`: §0.2 (선택 원칙), §5 (해당 domain), §6 (조합 패턴 1개)
- `task-spec-template.md`: 발췌 안 함 (Phase 1에서 이미 사용)
- `code-review-rubric.md`: §2 (8축 정의), §3 (채점), §4 (통과/차단 조건). spec.B=Review 일 때. (repo-local 규칙 있으면 §9 custom rule layer, 대형 changeset이면 §10 스코핑/번들링 추가 발췌.)
- `experiment-design-template.md`: §3 (Step 0-6 절차) 중 task에 필요한 step만, §4 (Quality Gates). spec.L=ml-researcher 일 때.
- `rfc-writing-template.md`: §3 (Step 0-6 절차), §4 (Quality Gates). spec.F=team/external + design doc 의도일 때. ADR 변형은 §1.3 참조.
- `autonomous-optimization-loop.md`: §3 (Step 0-5 절차), §4 (Quality Gates), §6 (anti-patterns). 단일 스칼라 지표 자동 반복 최적화 + spec.G=REVERSIBLE 일 때. experiment-design과 순차(탐색→검증).
- `speckit-spec-generation.md`: §2 (CLI/slash surface), §3 (Step 0–5), §4 (Quality Gates SSOT), §6 (anti-patterns). spec.B=Generation + spec.A에 spec/plan/tasks/SDD/spec-driven/speckit 키워드 + spec.G=REVERSIBLE 일 때. `rfc-writing-template`과 상호 배타.

### 산출물 저장 (필수)

composed prompt는 **항상 markdown 파일로 저장**한다 — bypass 없는 불변 규칙.

- 저장 경로: `.specs/<task-id>.composed.md` (task-id는 Phase 1에서 정한 kebab-case).
- 저장 시점: Phase 4에서 작성 직후 1차 저장. Phase 5 pre-validation이 Phase 4로 회귀시켜 수정하면 **최종 통과본으로 덮어쓰기**(파일은 항상 최신 통과본을 반영).
- **회귀 이력 보존 (B4)**: 덮어쓰기 *직전* 통과 못 한 버전을 `.specs/<task-id>.composed.iter-<N>.md`로 스냅샷 보존(append-only, N=1,2,…). 최신본은 `.specs/<task-id>.composed.md` 유지. `.specs/`는 gitignore이므로 이력은 **로컬 전용**(git 추적 안 함) — 회귀 원인 분석/diff 용. (정책 선택지: 본 iter-suffix 방식이 기본. log diff 첨부 또는 미보존도 가능 — 유지자 결정으로 변경 가능한 *reversible 정책*.)
- 저장 수단: Claude Code는 Write 도구로 직접 기록. claude.ai/chat 등 파일 쓰기가 불가한 환경이면 markdown 블록으로 출력 + "이 내용을 `.specs/<task-id>.composed.md`로 저장하라"고 명시 안내 (저장 책임을 사용자에게 위임하되 경로·파일명 고정).
- 파일 내용: §1~§7 전체 composed prompt + 말미에 routing log(§7) 포함. 별도 routing log는 기존대로 `.specs/<task-id>.log`에도 유지.
- 저장에 실패하면 그 사실을 산출물에 명시하고 Gate G4 미통과로 처리.

### Gate G4 (Assembly → Pre-validation)
- [ ] composed prompt가 §1-§7 모두 있음
- [ ] 발췌 출처 명시됨
- [ ] 모순 해소됨 (또는 우선순위 명시)
- [ ] §4 component 수 ≤ 4
- [ ] spec.E의 각 success criterion이 §6 Output Gates에 grep 단위로 echo됨 (criterion 1개라도 §6에서 누락 시 회귀 — under-selection 방지, router §5 failure mode)
- [ ] composed prompt가 `.specs/<task-id>.composed.md`로 저장됨 (또는 파일 쓰기 불가 환경에서 경로 지정 저장 안내 완료)

---

## §6. Phase 5 — Pre-validation

### Input
- Composed prompt

### Action
1. `prompt-evaluation-rubric.md` §1 Pre-execution Checklist 7항목 적용.
2. §2 Composition smell tests 6항목 적용.
3. **P1-P5 blocking 항목 1개라도 실패 → Phase 4로 회귀** 후 수정.
4. P6-P7 warning → 사용자에게 확인 메시지.

### Smell test 자동 수행

- 모든 component 발췌 부분을 한 cardinal text로 concat한 후:
  - Redundancy 검출: 같은 문장 또는 같은 의미의 반복
  - Contradictions: 부정문 vs 긍정문 매칭
  - "우선 가설" 같은 anchoring 단어 grep

### Gate G5 (Pre-validation → Execution)
- [ ] P1-P5 모두 통과
- [ ] Smell test 통과 (또는 사용자 수용)
- [ ] Token estimate 최종 cap 내

---

## §7. Phase 6 — Execution

### Mode A: Claude Code 메인 세션에서 직접 실행
composed prompt를 다음 user message로 발송.
- multi-agent-template이 활성화되어 있다면 subagent dispatch 이어짐.
- run-id 디렉토리(`.analysis/<run-id>/`)는 spec.id 기준으로 생성.

### Mode B: 사용자에게 markdown으로 반환
composed prompt를 markdown block으로 반환. 사용자가 별도 환경에서 실행.
- routing log + context manifest도 함께 전달.

### Mode C: API 호출
composed prompt를 system + user messages로 분할:
- §1-§2 → system message
- §3-§7 → user message
- API 호출 (Anthropic API), 결과 받음.

각 mode에서 **routing log + context manifest를 함께 보존** (`.specs/<task-id>.log`). composed prompt 자체는 Phase 4에서 이미 `.specs/<task-id>.composed.md`로 저장됨 — 실행은 이 파일을 입력으로 삼는다.

### 실행 실패 분기 (B3 — mode별 fallback)

실행이 실패하면 *조용히 종료하지 말고* mode별로 다음을 따른다:

- **Mode A (메인 세션 직접 실행) 실패** (subagent dispatch 오류 / tool 실패 / 도중 abort): 실패 지점과 사유를 `.specs/<task-id>.log`에 기록 → composed prompt 결함이면 **Phase 4로 회귀**(발췌·gate 수정), 환경/도구 문제면 사용자에 보고 후 재시도. run-id 디렉토리는 보존(부분 산출 분석용).
- **Mode B (사용자 paste 반환) 실패** (사용자가 결과를 다음 turn에 안 붙여넣음 / 실행 환경 부재): 누락을 1회 안내하고 대기. 사용자가 별도 환경에서 못 돌리면 Mode A 또는 Mode C 전환 권고.
- **Mode C (API 호출) 실패** (rate limit / 토큰 초과 / API 오류): 오류 코드와 함께 `.specs/<task-id>.log`에 기록 → 토큰 초과면 component 발췌 축소 후 재호출, 일시 오류면 backoff 재시도, 영속 오류면 Mode A 폴백.

> 공통: 실행 실패는 **G6 채택이 아니다.** 실패 사유를 로그에 남기고 위 분기 중 하나로 명시 전환한다 (silent failure 금지 — eval-rubric §2.4).

---

## §8. Phase 7 — Post-evaluation

### Input
- Execution 산출물 (Mode A이면 disk의 `.analysis/<run-id>/`, Mode B이면 사용자가 다음 turn에 붙여넣음)

### Action
1. `prompt-evaluation-rubric.md` §3 Post-execution Rubric 적용 (5축 채점).
2. 각 축 점수를 `.specs/<task-id>.log`에 append.
3. 평균과 최저 축 점수 둘 다 확인:
   - **평균 ≥ 4.0 AND 모든 축 ≥ 3.0** → 채택, 종료.
   - **평균 3.0-4.0** → 부족 축에 대해 §4 개선 loop. 최대 2 iteration.
   - **평균 < 3.0** → composition 재검토, Phase 1 또는 2로 회귀.

### 개선 loop (rubric §4 mapping)

| 부족 축 | 1순위 수정 |
|---|---|
| Relevance | task-spec.A 재작성 → Phase 1 재시작 |
| Evidence | role-dict의 evidence-checker 추가 → Phase 2 재실행 |
| Reasoning | role-dict의 devils-advocate 추가 → Phase 2 |
| Completeness | spec.E 보강 → Phase 1 |
| Actionability | composer §6 output spec 보강 → Phase 4 |

### Gate G6 (Loop 종료)
- [ ] 평균 ≥ 4.0 AND 모든 축 ≥ 3 → 채택
- [ ] 사용자가 현재 결과를 명시적으로 채택 → 채택
- [ ] iteration count = 2 도달 → **명시적 abandon**, bypass로 전환 또는 task 재정의

---

## §9. 메타 — Composer 자체 사용 시 주의

- **Composer ≠ 만능 도구**: spec이 모호하거나 1회성 task에서는 composer를 거치지 말 것. router의 bypass 분기를 신뢰.
- **Component drift 방지**: component가 업데이트되면 composer의 발췌 부분도 재검토. router catalog의 last-modified를 매번 확인.
- **Self-application 제한**: 이 composer 파일 자체를 composer가 다루는 component로 등록하지 말 것 (재귀 위험).
- **로그 보존**: routing log + post-eval 점수를 `.specs/<task-id>.log`에 누적하여 §10 메타 평가에 활용.
- **민감정보**: composer 출력(composed prompt)도 context에 준하는 redaction 검사 대상. Phase 5 P5에서 확인.
- **PR 권고 trace**: composer의 routing log ID + post-eval 점수를 PR description에 기재 (multi-agent template §10.1 PR 템플릿과 같은 결).

---

## §10. Lifecycle 관리

### Week 0 — 시범 운영
- 5개 component를 작은 task 1-2개에 적용
- Routing 정확성 수동 검증 (Phase 2의 결정이 expected인지)
- Phase 7 점수가 적어도 평균 3.5 이상인지

### 3개월 — 1차 메타 평가
- `prompt-evaluation-rubric.md` §5 메타 평가 적용
- Bypass 비율 / re-composition 비율 / 평균 점수 분석
- Low-usage component 정리, high-conflict pair 수정
- Component version bump 필요한 항목 식별

### 6개월 — 구조 재검토
- spec.E 누적 결과로 component 재작성 vs 분리 결정
- 새 도메인 lens 추가 필요성 검토 (agent-role-dictionary §5 확장)

### 1년 — 표준화
- composer 자체를 SKILL 형태로 표준화하여 팀(DeepingSource 등) 공유
- Skills 시장에 공개 가능 여부 검토 (agentskills.io 표준)

---

## §11. 참고

- **DSPy** (Stanford NLP, 2024+): declarative composition framework. 본 composer는 DSPy의 Signature/Module/Optimizer 개념을 markdown-based로 단순화한 형태. Compilation 기반 최적화는 본 시스템 범위 외 (manual composition).
- **Anthropic Skills** (2025+): SKILL.md folder-based component. 본 composer는 skill 등록 호환 (§0 frontmatter). Anthropic 내부 운영 사례 (수백 개의 skill, 9-category framework)를 design philosophy로 반영.
- **multi-agent-analysis-template.md / agent-role-dictionary.md**: 이 composer가 가장 자주 활성화하는 두 component. 두 파일의 evidence tagging / reversibility / confidence 룰을 composed prompt에도 자동 전파.
- **code-review-rubric.md / experiment-design-template.md / rfc-writing-template.md / autonomous-optimization-loop.md**: 도메인 특화 컴포넌트. 각각 Review / Analysis(가설 검증) / Generation(설계 문서) / Analysis(자동 탐색 최적화) 분기에서 활성화. router catalog §1 표에 등록되어 있어 spec.B/L/F/G 신호로 자동 매핑. optimization-loop은 experiment-design과 탐색→검증 순차 관계.
- **agentskills.io**: skills의 open standard. composer의 §0 frontmatter는 이 표준 호환을 시도.

---

## §12. 사용 예시 — Mini E2E

> 시나리오: "Qwen / GLM / Gemma 중 A100 40GB에 PRIMARY로 적합한 모델 결정"

### Phase 1 → spec 추출
```markdown
A. Purpose: A100 40GB에서 PRIMARY로 사용할 LLM 모델 1개 결정 (FALLBACK 1개 부수)
B. Output: Decision
C. Scale: 3 topic (Qwen / GLM / Gemma 후보군)
D. 시간 1일, 한국어 markdown, VRAM 40GB 제약
E. 성공: 채택 모델의 (a) VRAM 적합도 (b) 한국어 품질 점수 (c) throughput 측정 계획 명시
G. Reversibility: [REVERSIBLE] (재학습 없이 교체 가능)
L. Domain: ml-researcher (1순위), devops-sre (2순위)
```

### Phase 2 → Routing log
```
[ROUTING 2026-05-19T15:00] task=qwen-glm-gemma-a100-eval
- selected: [task-spec, multi-agent-template, role-dict(ml-researcher×proposer; devils-advocate; devops-sre×risk-auditor), eval-rubric]
- bypass: none
- domain lens: [ml-researcher, devops-sre] (spec.L)
- token est: 26k / cap 50k
- multi-LLM: off (spec.K all false)
- rationale: 3 topic + decision + reversible → multi-agent-template fit, 2 domain lens로 cross-coverage.
```

### Phase 4 → Assembly 결과 (요약)
- §1 Role: 한국어, ml-researcher 톤
- §3 Task: spec echo
- §4: multi-agent-template §2 framework + §4 workflow 발췌, role-dict §5.8 ml-researcher + §5.4 devops-sre 발췌, §2.1 evidence-tagging 강조
- §6 Gates: spec.E echo

### Phase 5 → Pre-validation
P1-P5 통과, P6 26k이므로 OK, P7 bypass 재검토 — 3 topic 비교는 composition value 있음, 진행.

### Phase 6 → Execution
multi-agent-template의 workflow가 실행되면서 baseline-collector → topic-analyst × 3 → synthesis 진행.

### Phase 7 → Post-eval
산출물 5축 채점, 평균 4.2, Evidence 축 5점, Actionability 4점 → 채택.
