# Prompt Component Router

> Task Spec을 받아 어떤 component를 어떤 조합으로 활성화할지 결정하는 routing logic.
>
> **참고 영향**: Anthropic Skills의 description-based auto-loading (Claude가 SKILL.md를 자동 선택하는 메커니즘), DSPy의 module selection.
>
> **시리즈 위치**: composer Phase 2에서 호출. 입력은 `task-spec-template.md`로 작성된 spec.

---

## 0. Routing 원칙

1. **Spec-driven** — Task Spec 없이 routing 금지. spec이 모호하면 router도 모호한 답을 낸다.
2. **Bypass 우선** — 적합 case 매트릭스(§3)에서 BYPASS면 composition 대신 direct prompting.
3. **Cap on count** — 1 composition에 component 4개 초과 활성화 금지. 더 필요하면 task 분할.
4. **Log rationale** — 어느 component를 *왜* 선택했는지 반드시 한 줄 로그 (§4).
5. **Bias caution** — "익숙한" component 자동 선택 금지. spec → component mapping 표(§2) 기반.

---

## 1. Component Catalog (메타데이터)

각 component의 trigger / input / output / cost / 충돌 정보를 한 곳에서 관리.

| Component | Trigger signals | Inputs | Outputs | Cost (rough tokens) | 충돌 가능 component |
|---|---|---|---|---|---|
| `task-spec-template.md` | 항상 (composition input) | rough request | structured spec | Low (~300) | — |
| `prompt-component-router.md` | (이 문서) — composer 내부에서 | spec | selected components + log | Low (~500) | — |
| `multi-agent-analysis-template.md` | topic ≥ 3, 동일 criteria로 비교, decision output | topic list, criteria, baseline | ranked decision + matrix | High (full=30k, 발췌=3-5k) | direct-prompting bypass |
| `agent-role-dictionary.md` | role 다양화 필요, critique/judge 단계, multi-perspective 검토 | role names list (stance × domain) | role prompts | Medium (per-role 200-400) | — |
| `context-injection-patterns.md` | 프로젝트 / user 맥락이 결정에 영향 | context sources list | injection plan | Low (~500) | — |
| `prompt-evaluation-rubric.md` | 산출물 품질 보장 필요, irreversible 권고 | composed prompt + output | pass/fail + improvement list | Low (~500) | — |
| `code-review-rubric.md` | spec.B=Review + spec.H에 PR/diff + spec.L=security-researcher/backend-engineer/frontend-engineer | diff + 변경 파일 list | 8축 점수 + 차단 결정 + reviewer comment draft | Low (~600 발췌 / ~2.5k full) | `multi-agent-analysis-template` (over-scope) |
| `experiment-design-template.md` | spec.B=Analysis + spec.L=ml/systems/hci-researcher + 실험/baseline 키워드 | research question + dataset + baseline 후보 | 실험 protocol + ablation + 결과 분석 + 재현 manifest | Medium (~2k 발췌 / ~12k full) | `multi-agent-analysis-template`(대안 비교 vs 가설 검증), `code-review-rubric` (영역 다름) |
| `rfc-writing-template.md` | spec.B=Generation + spec.F=team/external + RFC/ADR/design doc 키워드 | 결정 대상 + motivation + stakeholder list | RFC markdown + stakeholder feedback log + decision status | Medium (~1.5k 발췌 / ~10k full) | `experiment-design-template`(영역 다름 — 실험 vs 설계 문서) |
| `optimized-prompt-composer.md` | 메인 orchestrator — 본인 | spec + components + context | optimized prompt | Medium (~2k) | — |

### 1.1 Catalog 메타 (의무)

각 row는 다음 메타를 유지:
- `last_modified`: component 파일의 git mtime — composer가 stale catalog 감지에 사용
- `version`: semantic version (호환성 깨지는 변경 시 major↑)
- `owner`: 유지보수 책임자 (team 공유 시)

---

## 2. Routing decision tree

```
1. Task Spec 작성 완료?
   ├─ No → "task-spec-template만 활성화, 사용자에게 spec 보강 요청"
   └─ Yes → 2

2. spec.B Output Type = ?
   ├─ Decision (multi-topic) → multi-agent-template 후보 → 3으로
   ├─ Analysis →
   │    ├─ multi-topic 비교 → multi-agent-template → 3으로
   │    └─ spec.L=ml/systems/hci-researcher + 가설/baseline 의도 → experiment-design-template → 5
   ├─ Generation / Transformation →
   │    ├─ spec.F=team/external + RFC/ADR/design doc 의도 → rfc-writing-template + role-dict(pedagogy-reviewer×proposer, consistency-checker) → 5
   │    └─ 기본 → role-dictionary만 (proposer + domain lens) → 5
   ├─ Review →
   │    ├─ spec.H에 PR/diff/commit → code-review-rubric + role-dict(architect, security-researcher) → 5
   │    └─ 기본 → role-dictionary (devils-advocate + evidence-checker) → 5
   └─ Mixed → ❌ task 분할 권고 (composition abort)

3. spec.C topic_count = ?
   ├─ 1     → BYPASS multi-agent-template, direct prompt + role-dictionary (§3)
   ├─ 2     → BYPASS (template §0.5 warning 신호) → single-agent 권장
   ├─ 3-10  → multi-agent-template 활성화 → 4
   └─ 10+   → multi-agent-template + Large N 처리 (template §6.2) → 4

4. spec.G Reversibility = ?
   ├─ REVERSIBLE          → eval-rubric optional (시간 압박 시 skip)
   ├─ COSTLY-TO-REVERSE   → eval-rubric 필수, multi-LLM 검토 후보
   └─ IRREVERSIBLE        → eval-rubric 필수 + judge persona 추가 (role-dict §3.1)

5. spec.L Domain Lens 명시?
   ├─ Yes → role-dictionary §5의 해당 domain × 적절 stance 활성화
   └─ No  → router가 spec.A Purpose에서 inference
            → log에 inference 근거 명시
            → high-stakes(spec.G=COSTLY/IRREVERSIBLE)이면 사용자 확인 권장

6. spec.H Prior Context 있음?
   ├─ Yes → context-injection-patterns 활성화
   └─ No  → skip (over-injection 방지)

7. spec.K Multi-LLM 신호 1건 이상?
   ├─ Yes → multi-LLM 활성화 추가 (multi-agent-template §6.8 pattern 선택)
   └─ No  → claude single-LLM (default)
```

---

## 3. Bypass conditions (composition 안 함)

다음 중 하나라도 해당하면 composition 자체를 skip:

| 조건 | 이유 | 대안 |
|---|---|---|
| Scale.topic_count = 1 + Output = Decision | multi-agent 가치 없음 | direct prompt + role 1-2개 |
| 1회성 ad-hoc | 메타 step 비용 > task | direct prompt |
| spec.K + spec.G 모두 미명시 + Confidence=Low | routing 정보 부족 | spec 보강 후 재시도 |
| 토큰 예산 < 10k 추정 | composition만으로 예산 초과 | direct prompt |
| spec.B = Mixed | composition 결과 일관 없음 | task 분할 |
| Task가 *코드 작성 한정* | Anthropic의 코딩 스킬이 더 적합 | Claude Code 직접 사용 |

> Bypass는 실패가 아니다. composition은 *도구*이지 *목적*이 아니다. (multi-agent template §0.5 Warning signs 참조)

---

## 4. Routing log format (의무)

composition 시작 시 다음 형식으로 한 줄 로그를 `.specs/<task-id>.log`에 append:

```
[ROUTING <timestamp>] task=<task-id>
- input spec: <spec_path> @ <spec git hash if any>
- selected components: [<comp1@version>, <comp2@version>, ...]
- bypass: <none | reason>
- domain lens: <list> (source: <spec.L | inferred from purpose>)
- token estimate: <est> / cap <cap>
- multi-LLM: <off | pattern §6.8.X>
- rationale: <한 줄, 왜 이 조합인지>
```

예시:
```
[ROUTING 2026-05-19T14:30] task=qwen-glm-gemma-eval
- input spec: .specs/qwen-glm-gemma-eval.md @ 3a7f9c
- selected components: [task-spec@1.0, multi-agent-template@1.2, role-dict@1.1(ml-researcher×proposer; ml-researcher×devils-advocate; devops-sre×risk-auditor), eval-rubric@1.0]
- bypass: none
- domain lens: [ml-researcher, devops-sre] (source: spec.L)
- token estimate: 28k / cap 50k
- multi-LLM: off (spec.K 모두 false)
- rationale: 3 model 후보 + decision output + A100 환경 제약 + 한국어 품질 — domain lens 두 개로 cross-coverage, irreversible 아니라 multi-LLM 불필요.
```

---

## 5. Failure modes (router-side)

router가 만들 수 있는 실패와 방지책:

- **Over-selection**: 모든 component 활성화 → token blowup. **§0 cap 4개 강제**.
- **Under-selection**: 핵심 component 누락 → 품질 저하. **spec.E echo**를 routing log에 포함하여 post-eval에서 비교.
- **Wrong domain lens**: spec.L 없을 때 inference 오류. **inference 근거를 log에 적고**, composer 단계에서 사용자 확인 권장 (high-stakes일 때).
- **Stale catalog**: catalog가 component 변경을 못 따라감. **§1.1 last_modified를 routing 직전 확인**.
- **Selection bias**: LLM이 "익숙한" component만 자동 선택. **§2 decision tree를 explicit하게 따르고, 분기에서 벗어난 선택은 log에 사유 명시 의무**.

---

## 6. Catalog 업데이트 절차

새 component 추가 시:
1. §1 표에 row 추가 (trigger / input / output / cost / 충돌 / version / owner)
2. §2 decision tree에 분기 추가 (해당 시)
3. §3 bypass condition 재검토 (새 component가 bypass를 무력화하지 않는지)
4. `optimized-prompt-composer.md`의 component reference 추가
5. 기존 spec들로 회귀 테스트 — 같은 spec에서 routing 결과가 의도대로 바뀌는지 확인

---

## 7. 빠른 참고 표 — spec → component 자동 매핑

```
B=Decision + C.topic=3-10 + G=REVERSIBLE
→ [task-spec, multi-agent-template, role-dict(proposer+devils-advocate), eval-rubric optional]

B=Decision + C.topic=3-10 + G=IRREVERSIBLE
→ [task-spec, multi-agent-template, role-dict(proposer+devils-advocate+judge), eval-rubric mandatory]
  + multi-LLM 활성화 검토

B=Generation + C.topic=1 + spec.L=ml-researcher
→ [task-spec, role-dict(ml-researcher×proposer + consistency-checker)]
  multi-agent-template BYPASS

B=Review + spec.H에 prior PR/문서 있음
→ [task-spec, role-dict(devils-advocate + evidence-checker), context-injection, eval-rubric]

B=Review + spec.H에 diff/PR + spec.L=security-researcher/backend-engineer/frontend-engineer
→ [task-spec, code-review-rubric, role-dict(architect + security-researcher×evidence-checker), context-injection]

B=Analysis + spec.L=ml-researcher + 가설/baseline/ablation 의도
→ [task-spec, experiment-design-template, role-dict(ml-researcher×proposer + ml-researcher×devils-advocate), eval-rubric]
  multi-agent-template은 *후보 선정* 단계에서만 (sequential, 가설 검증 시 BYPASS)

B=Generation + spec.F=team/external + RFC/ADR/design doc 의도
→ [task-spec, rfc-writing-template, role-dict(pedagogy-reviewer×proposer + consistency-checker), context-injection]

B=Mixed
→ ABORT, sub-task 분리 요청
```
