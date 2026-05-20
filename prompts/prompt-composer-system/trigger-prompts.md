# Trigger Prompts — 시스템 가동용 입력

> **무엇**: optimized-prompt-composer 시스템을 실제로 돌리기 위한 entry prompt 모음. *어떻게 시동을 거는가*만 다룬다(component 라이브러리는 별도).
> **용도**: composer를 step-by-step 또는 auto 모드로 시동할 때 복사해 쓸 입력을 고를 때 참조.
> **시리즈 위치**: composer 진입점(entry). 라이브러리 component가 아니라 시동 입력.
>
> **Changelog**:
> - v1.1 (2026-05-19): 방법 A에 `auto` 모드 추가. step-by-step (default) 외에 논스톱 자동 진행 모드.

---

## 입력 형태 선택 가이드

| 상황 | 추천 방법 | 비용 |
|---|---|---|
| 처음 한두 번 시험, 단계별로 보고 싶음 | **방법 A-1 (step-by-step)** | claude.ai 1회용 paste |
| 익숙해진 후 빠르게 돌리고 싶음 | **방법 A-2 (auto)** | claude.ai 1회용 paste (논스톱) |
| 같은 패턴 6주 이상 반복 예정 | **방법 B** | Claude Code skill 영구 설치 |
| 이미 작성한 prompt를 검증만 하고 싶음 | **방법 C-5** | Phase 5 단독 |
| spec만 깔끔히 추출하고 prompt는 직접 작성 | **방법 C-1** | Phase 1 단독 |
| Router의 결정만 보고 싶음 | **방법 C-2** | Phase 2 단독 |

---

## 방법 A — Claude.ai / Claude Code chat에서 1회용 사용

### 절차
1. 새 conversation 시작 (또는 Claude Code 세션)
2. 컴포넌트 파일 위치 확인:
   - claude.ai라면: 7개 md 파일을 attach 또는 paste
   - Claude Code라면: `prompts/prompt-composer-system/` 디렉터리에서 Read tool로 읽음
3. 아래 두 모드 중 하나 선택해서 trigger paste

### A-1. Step-by-step 모드 (보수적, 단계별 확인)

```
너는 지금부터 optimized-prompt-composer로 동작한다.
컴포넌트 파일들을 라이브러리로 사용해 (claude.ai: 첨부 파일 / Claude Code: prompts/prompt-composer-system/ 디렉터리).

[Rough request]
<여기에 실제 요청 자연어로>

[실행 규칙 — step-by-step]
1. Phase 1 (Intake)부터 시작. A-E 추출 후 모호한 필드만 단답형 질문 최대 3개로 보강.
2. G1 통과 후 작성된 Task Spec을 markdown으로 보여주고 내 확인 대기.
3. Phase 2 (Routing) — decision tree 통과 경로 + routing log + selected components 표시 후 확인 대기.
4. Phase 3-4 (Context + Assembly) — composed prompt를 markdown 코드블록으로 출력.
5. Phase 5 (Pre-validation) — P1~P7 결과 표 형태.
6. Phase 6 (Execution) — 별도 지시 있을 때까지 prompt만 출력하고 대기.
7. Phase 7 — (실행 후) 5축 rubric 점수 + 개선 권고.

규칙:
- 각 gate 통과/실패를 명시적으로 보고.
- Bypass 적합 케이스면 §3에서 먼저 권고하고 사용자 결정 대기.
- 컴포넌트 발췌는 §-숫자 ref로 명시 (예: "multi-agent-template §2.1 발췌").
```

**언제 쓰나**: 처음 시도, 작동 방식 학습 중, 각 phase 결과를 검토하며 가고 싶을 때, high-stakes task로 매 단계 통제하고 싶을 때.

### A-2. Auto 모드 (빠른 진행, 필수 질문만)

```
너는 지금부터 optimized-prompt-composer로 동작한다.
컴포넌트 파일들을 라이브러리로 사용해 (claude.ai: 첨부 파일 / Claude Code: prompts/prompt-composer-system/ 디렉터리).

[Rough request]
<여기에 실제 요청 자연어로>

[실행 모드 — auto]
Phase 1 → 7을 중간 확인 없이 논스톱으로 진행하고, 한 응답 안에 누적 출력한다.

다음 4가지 경우에만 멈추고 사용자 입력 대기:
(a) Phase 1: A-E 필드 추출 모호 시 보강 질문 (max 3개)
(b) Gate G1~G6 실패 시: 사유 보고 후 stop
(c) Phase 2: bypass 조건 충족 시: 권고 후 사용자 결정 대기
(d) Phase 6: 외부 도구 호출 / 파일 작성 권한 / 외부 API 호출 필요 시

형식:
- "## Phase N — <이름>" 헤더로 각 phase 시작
- Gate 결과 한 줄로 명시: "✓ G<N> 통과" 또는 "✗ G<N> 실패: <사유>"
- 컴포넌트 발췌는 §-숫자 ref 명시 (예: "multi-agent-template §2.1 발췌")
- 모든 phase를 한 응답 안에 누적, phase별 응답 분리 금지

⚠️ Self-evaluation 주의:
Phase 6과 Phase 7이 같은 세션에서 실행되면 Phase 7 점수에 self-eval bias 가능.
- Phase 7의 5축 점수 옆에 "[self-eval 경고]" 표시.
- spec.G == [IRREVERSIBLE] 이거나 spec.J == High이면 Phase 6 직전에 (d) trigger로 자동 stop하고 "별도 세션 실행 권고" 안내.
```

**언제 쓰나**: 시스템 작동 방식 익숙해진 후, Generation task (산출물 작성), 낮은-중간 stakes task, 한 응답으로 끝까지 보고 싶을 때.

**언제 쓰면 안 되나**:
- spec.G = [IRREVERSIBLE] task — 매 phase 검토가 안전. step-by-step 권고
- 처음 돌려보는 새 task pattern — 어디서 막히는지 모름. step-by-step 권고
- spec.J = High confidence required — 자동 진행은 부적합

### 첫 응답 신호
어느 모드든 첫 응답은 반드시 다음 형태로 시작:
```
## Phase 1 — Intake
자동 추출 결과:
A. Purpose: ...
B. Output Type: ...
...
```

이 형태가 아니면 trigger 실패. 메시지를 다시 paste하거나 컴포넌트 파일이 attached/readable한지 확인.

---

## 방법 B — Claude Code skill로 영구 설치 (반복 사용)

### 설치 (1회만)

```bash
# project root에서
mkdir -p .claude/skills/prompt-composer/refs

# 1) SKILL.md 생성 — frontmatter + composer 본문
cat > .claude/skills/prompt-composer/SKILL.md << 'FRONTMATTER'
---
name: prompt-composer
description: Rough request를 받아 prompt component library에서 적절한 것들을 선택·조합하여 optimized prompt를 생성한다. 동일 task의 반복 / multi-topic 평가 / 외부 보고 대상 task에서 활성화. "이 작업을 위한 prompt 만들어줘", "여러 옵션 평가하고 싶어", "task 위한 component 조합해줘", "이 분석 prompt 최적화해줘" 같은 요청에 trigger.
---

FRONTMATTER

cat optimized-prompt-composer.md >> .claude/skills/prompt-composer/SKILL.md

# 2) 나머지 6개 reference 파일 복사
cp task-spec-template.md \
   prompt-component-router.md \
   context-injection-patterns.md \
   prompt-evaluation-rubric.md \
   multi-agent-analysis-template.md \
   agent-role-dictionary.md \
   .claude/skills/prompt-composer/refs/

# 3) 운영 룰 + reference 경로 append
cat >> .claude/skills/prompt-composer/SKILL.md << 'EOF'

---
## Reference files location
세부 컴포넌트는 `refs/` 디렉터리:
- `refs/task-spec-template.md`
- `refs/prompt-component-router.md`
- `refs/context-injection-patterns.md`
- `refs/prompt-evaluation-rubric.md`
- `refs/multi-agent-analysis-template.md`
- `refs/agent-role-dictionary.md`

Phase 진행 중 해당 컴포넌트의 룰이 필요하면 위 경로를 Read.

## Default 실행 모드
별도 지시 없으면 auto 모드 (trigger-prompts.md 방법 A-2와 동일 규칙):
- Phase 1→7 논스톱, (a)~(d) 케이스만 중단
- spec.G=[IRREVERSIBLE] 또는 spec.J=High이면 자동으로 step-by-step으로 전환

명시적으로 step-by-step 원하면 trigger에 "step-by-step 모드로 진행" 추가.
EOF
```

### 사용 — 자연어 trigger

skill description의 trigger phrase 중 하나를 포함하면 자동 활성화:

```
이 작업을 위한 optimized prompt 만들어줘: <요청>
prompt-composer 돌려서 <요청>
<task>를 위한 prompt를 컴포넌트 조합으로 만들어줘
여러 옵션 평가하는 prompt 만들어줘
이 분석 prompt 최적화해줘
```

명시적으로 호출하고 싶으면:
```
.claude/skills/prompt-composer 활성화해서 다음 task 진행: <요청>
```

step-by-step 강제:
```
prompt-composer로 다음 task 진행, step-by-step 모드: <요청>
```

### Skill이 작동하는지 확인
첫 응답이 "## Phase 1 — Intake" 형태로 시작하지 않으면 skill 자동 trigger 실패. `claude` CLI에서 `/skills list`로 등록 확인.

---

## 방법 C — 단일 phase 사용 (가장 가벼운 방식)

### C-1. Phase 1만 — Task Spec 추출 단독

```
[task-spec-template.md attach]

위 template을 사용해 아래 rough request에서 Task Spec을 추출해.

규칙:
- A-E 필수 필드는 무조건 채울 것. rough request에서 추출 불가하면 단답형 질문으로 보강.
- 보강 질문은 최대 3개 (선택지 형태 우선).
- F-J 권장 필드는 rough request에서 자연스럽게 추출되면 채우고, 안 되면 비워둘 것.
- K-L은 explicit 신호 있을 때만.
- 마지막에 self-check(§5) 결과 표시.

[Rough request]
<요청>
```

### C-2. Phase 2만 — 이미 작성된 spec의 routing 결정

```
[prompt-component-router.md + 본인 spec 파일 attach]

위 router를 사용해 첨부된 spec에 대한 routing 결정만 수행.

출력:
1. Decision tree 경로 — 어느 노드를 어떤 spec 필드 기준으로 통과했는지
2. Selected components list (version 포함)
3. Estimated cost (full vs 발췌)
4. Bypass 적합 여부 평가 + 사유
5. Routing log (router §4 format)

여기서 멈춤. Phase 3 이후는 진행하지 않음.
```

### C-3. Phase 3만 — context injection plan 작성

```
[context-injection-patterns.md attach + spec attach]

위 patterns 문서를 사용해 첨부된 spec에 대한 context injection plan을 작성.

출력:
- Context source 식별 (§1의 7-source taxonomy 매핑)
- Source별 injection pattern 결정 (Header/Body/Reference/Memory)
- Redaction 필요 항목 list + sanity check 결과
- 최종 context manifest (§4 format)
```

### C-4. Phase 4만 — composed prompt 조립 (이미 routing/context plan 있을 때)

```
[composer.md §6 + 결정된 components + context manifest attach]

위 §6 layout (§1~§7)을 따라서 composed prompt를 조립.

규칙:
- 각 component 발췌는 §-숫자 ref로 명시
- 전체 본문 복사 금지, 발췌만
- 최종 prompt를 markdown 코드블록 하나로 출력
```

### C-5. Phase 5만 — 누군가 작성한 prompt의 사전 검증

```
[prompt-evaluation-rubric.md + 검증할 prompt attach]

위 rubric의 사전 체크리스트로 첨부된 prompt를 평가.

출력 형식:
| 항목 | 통과/실패 | 사유 | Fix 권고 |
|---|---|---|---|
| P1 ... | ... | ... | ... |
| ... | ... | ... | ... |

P1~P5 중 하나라도 실패면 prompt 사용 금지 권고.
P6~P7은 warning으로만 표시.
```

### C-7. Phase 7만 — 실행 결과 사후 평가

```
[prompt-evaluation-rubric.md + spec.E (Success Criteria) + 실행 결과 attach]

위 rubric §3의 5축으로 실행 결과를 평가.

출력:
- 5축 점수 (Relevance / Evidence / Reasoning / Completeness / Actionability) 각 1-5
- 가장 약한 축 식별
- §4 improvement loop의 어느 component를 수정해야 하는지 mapping
- 다음 iteration 권고 (있다면)
```

---

## 모드 선택 결정 트리

```
이번 task 처음 돌리는 패턴인가?
├─ Yes → step-by-step (A-1)
└─ No
    └─ spec.G == [IRREVERSIBLE] 또는 spec.J == High?
        ├─ Yes → step-by-step (A-1)
        └─ No
            └─ Output Type이 Generation/Transformation/Review인가?
                ├─ Yes → auto (A-2) — self-eval bias 영향 적음
                └─ No (Decision/Analysis)
                    └─ 시간 여유 있나?
                        ├─ Yes → step-by-step (A-1)
                        └─ No → auto (A-2) + Phase 7 결과 재검토 의무
```

---

## 흔한 실수 방지

### ❌ Trigger 메시지에 "Phase 1부터" 명시 빠뜨림
composer가 sometimes Phase 2부터 시작하려고 함. 명시적으로 "Phase 1 (Intake)부터 시작" 적을 것.

### ❌ 컴포넌트 파일 첨부 누락
방법 A에서 7개 중 하나라도 빠지면 composer가 발췌 단계에서 막힘. 특히 multi-agent-template / agent-role-dictionary는 분석/결정 task에서 빠지면 안 됨.

### ❌ Rough request에 compound goal
"X 결정하고 Y도 작성해줘" → Phase 1 G1에서 무조건 차단됨. trigger 전에 두 task로 분리하든가, Phase 1이 분리 권고할 때 수용.

### ❌ Skill description의 trigger phrase를 안 쓰고 호출
방법 B에서 description에 없는 표현으로 호출하면 자동 trigger 실패 가능. 명시적 호출 (`.claude/skills/prompt-composer 활성화`)로 강제하는 게 안전.

### ❌ Phase 4 출력을 다시 Phase 4에 넣음
composed prompt를 받고 그대로 composer에 다시 넣는 재귀 호출은 의미 없음. composed prompt는 *별도 conversation*에서 실행해야 evaluation이 fair.

### ❌ Auto 모드를 high-stakes task에 사용
spec.G = [IRREVERSIBLE] 또는 외부 보고 대상 task에서 auto 모드로 돌리면 단계별 검토 기회 잃음. 위 결정 트리 참조.

---

## Quick reference

| 입력 시점 | 가장 짧은 trigger |
|---|---|
| 처음 시도 (방법 A-1) | "너는 optimized-prompt-composer로 동작한다. step-by-step 모드, Phase 1부터 시작. Rough request: <요청>" |
| 익숙해진 후 (방법 A-2) | "너는 optimized-prompt-composer로 동작한다. auto 모드, Phase 1→7 논스톱. Rough request: <요청>" |
| Claude Code skill 등록 후 (방법 B) | "이 작업을 위한 optimized prompt 만들어줘: <요청>" (default auto) |
| Spec만 추출 (C-1) | "위 task-spec-template으로 A-E 추출해. 모호하면 질문 3개 이내. Rough request: <요청>" |
| Prompt 검증만 (C-5) | "위 rubric으로 첨부 prompt P1~P7 평가, 표 형태로." |
