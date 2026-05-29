# prompt-composer-system — 디렉토리 규약

이 디렉토리(하위 `components/` 포함)의 모든 `*.md` 문서는 **표준 머리말(standard header)** 로 시작한다.
새 문서를 추가하거나 기존 문서를 편집할 때 아래 규약을 반드시 따른다.

## 표준 머리말 형식

`# 제목` 바로 다음에 `>` 블록인용으로 3개 필드를 순서대로 둔다.

```
# <제목>

> **무엇**: 이 문서가 하는 일 (1줄)
> **용도**: 언제·누가·왜 쓰는가 (1줄)
> **시리즈 위치**: composer Phase N에서 호출 / 진입점(entry) / 독립
>
> (선택) 산출물·출처·참고 영향·Changelog 등 보조 정보는 빈 `>` 줄 뒤에 이어 둔다.

---
```

## 규칙

- **무엇 / 용도 / 시리즈 위치** 3필드는 필수. 순서·라벨을 그대로 쓴다.
- 각 필드는 가급적 1줄. 길어지면 보조 줄로 내린다.
- 보조 정보(산출물, 출처, 참고 영향, Changelog 등)는 3필드 **아래**에 빈 `>` 줄로 구분해 유지한다. 기존 보조 정보는 지우지 않는다.
- 머리말 블록 다음에는 `---` 구분선을 둔다.
- `trigger.md`처럼 통째로 복사해 쓰는 prompt 파일도 머리말을 붙이되, "아래 구분선부터가 복사 본문"임을 명시한다.

## 새 문서 추가 체크리스트

1. `# 제목` + 표준 3필드 머리말 작성 (이 규약대로)
2. component라면 `## 0. Router 등록 metadata` 섹션 포함 — `prompt-component-router.md`가 인식하도록
3. `시리즈 위치` 필드에 어느 Phase에서 호출되는지 명시
4. 필요 시 `builder/optimized-prompt-composer.md`의 시리즈 구성 목록에 추가

---

# Prompt Composer System — 프로젝트 컨텍스트 (요약)

> 전체 설계 인계 문서는 claude.ai 진행분 기준. 아래는 이 디렉토리에서 작업할 때 반드시 지켜야 할 핵심만 간추린 것. (v1.2, 2026-05-19)

## What this is

Rough request를 받아 prompt component library의 컴포넌트들을 골라 조합·검증·실행하는 메타 orchestration system. 동일 task가 반복되거나 multi-topic 평가 / 외부 보고 / irreversible 결정이 걸린 task에서만 활성화. 단순 ad-hoc 질의는 bypass. 참고 ancestor: DSPy(declarative composition), Anthropic Skills(folder-based + description routing).

## ⚠️ System Invariants — 위반 금지

이 시스템이 *정상* 동작하기 위한 불변식. 어기면 system guarantee가 깨짐.

1. **Compose / Execute / Evaluate 세션 분리** — prompt 생성(Phase 1-5)과 실행(Phase 6)은 **반드시 다른 conversation**에서. 위반 시 ① self-eval bias(점수 1-2점 부풀림) ② context contamination(fresh-start 가정 붕괴 → role priming 무효) ③ tool 환경 불일치(simulation 전락). smoke test 예외만 같은 세션 허용하되 production 사용 금지. → `trigger-prompts.md` A-2(compose) / C-6(execute) / C-7(evaluate).
2. **G1 (Intake gate) 면제 불가** — Phase 1 종료 시 A-E 5필수 필드 충족 + Purpose 단일 goal(compound 분리) + Success Criteria 측정 가능, 셋 다 우회 금지. 면제하면 garbage routing 직결.
3. **컴포넌트 발췌만 인용, 전체 복사 금지** — 조합 prompt에 component 본문 전체 복사 금지, `§-숫자` ref로만 발췌. (토큰 비용 + anchoring 방지 + 무관 룰 오염 방지)
4. **레이어 분리 유지** — 컴포넌트는 3축 중 하나로 명시 분류: ① 조합 인프라(5개) ② 분석 컨텐츠(2개: multi-agent-template, agent-role-dictionary) ③ domain content(rfc-writing / experiment-design / code-review-rubric / autonomous-optimization-loop / speckit-spec-generation 등 도메인 특화). 다른 layer를 섞지 말 것 — 분석 룰(evidence tagging, reversibility 등)은 기존 2개에 유지. 같은 layer 안에서 *상호 배타* 표시된 component(예: rfc-writing-template ↔ speckit-spec-generation)는 동시 활성 금지. 각 component §0 metadata의 `layer` 필드와 router §1.1 정의가 SSOT.

## Mandatory safeguards (Invariant 외 추가 보호)

1. Bypass mode — 단순 요청은 조합 단계 건너뛰고 직접 prompt
2. Pre-execution validation gate — 조합 후 실행 전 P1~P5 blocking
3. 컴포넌트 ≤4개 cap — 과적층 방지
4. Routing rationale 로깅 — 컴포넌트 선택 사유 추적

## v1.2 default flow

```
[Conversation 1: Compose]  A-2 (compose-only auto) → composed prompt artifact (.composed.md) **필수 저장**
        ↓ 저장 완료
[Conversation 2: Execute]  fresh context + 필요 tool → C-6 + artifact → task result (.result.md)
        ↓
[Conversation 3: Evaluate] (또는 Conv 2 이어서) C-7 + spec.E + result → 5축 점수 + 개선 권고
        ↓ iteration 필요 시: 점수 낮은 축 → 수정할 component 결정 → Conv 1 재실행
```

- A-2 = compose-only auto (default), A-3 = full-auto smoke test (warning, production 금지)
- artifact 저장: composed prompt는 `.specs/<task-id>.composed.md`로 **항상 저장**(필수, bypass 없음 — composer §5 Phase 4 / Gate G4). `.result.md`(실행 결과) / `.log`(routing log + 점수)는 해당 단계에서 저장.

## 컴포넌트 라이브러리

- **조합 인프라(5) — `builder/` 디렉토리**: `builder/optimized-prompt-composer.md`(7-phase orchestrator, 메인 진입점), `builder/task-spec-template.md`(Phase 1), `builder/prompt-component-router.md`(Phase 2), `builder/context-injection-patterns.md`(Phase 3), `builder/prompt-evaluation-rubric.md`(Phase 5/7)
- **분석 컨텐츠(2)**: `multi-agent-analysis-template.md`(다각도 평가), `agent-role-dictionary.md`(stance × domain 카탈로그)
- **domain content(도메인 특화)**: `code-review-rubric.md`(Review/PR), `experiment-design-template.md`(Analysis/가설 검증), `rfc-writing-template.md`(Generation/자유 형식 설계 문서), `autonomous-optimization-loop.md`(Analysis/스칼라 자동 탐색), `speckit-spec-generation.md`(Generation/구조화 spec — rfc-writing과 상호 배타)
- **인터페이스**: `trigger-prompts.md`(시동 입력, v1.2: 3 mode + C-6/C-7)
- **라이브러리 성장(component 발굴 2단 파이프라인)**: `component-discovery-collect.md`(stage 1 — 외부 발굴→ledger append, 무인 주기 구동 가능) → `component-discovery-approve.md`(stage 2 — 사람 batch 승인→component 생성·router/composer 반영·commit), 공유 상태 `component-discovery-ledger.md`. 거버넌스는 `self_upgrade.md` 준수. 조합 인프라/분석 컨텐츠 레이어와 별개(component를 *만드는* 메타 도구이지 routable component 아님 — router catalog 미등록).
- **진단 도구 (build 흐름과 분리, router 미등록)**: `audit-composer-system.md`(prompt-composer-system 자체를 정기 진단; composer Phase 밖에서 독립 실행). composer build 흐름(Phase 1-5)에서 호출 금지. router §1/§2/§7/composer 시리즈 목록에 *등록 금지*.
