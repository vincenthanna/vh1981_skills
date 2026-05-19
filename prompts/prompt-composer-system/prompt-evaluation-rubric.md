# Prompt Evaluation Rubric

> Composed prompt(실행 전) + 실행 결과(실행 후) **양쪽**을 평가하는 rubric.
>
> **Pre-execution**: 실행해도 되는가? **Post-execution**: 결과를 채택 가능한가?
>
> **시리즈 위치**: composer Phase 5(pre)와 Phase 7(post)에서 호출.

---

## 0. 두 단계 평가의 이유

대부분의 prompt 시스템은 *output*만 평가한다. 그러나 composition 시스템에서는 *input prompt 자체*도 평가 대상이다 — 잘못 조합된 prompt를 실행하면 token도 낭비되고 결과도 silent failure로 끝난다.

- **Pre-execution (실행 전, ~1분)**: composed prompt가 spec.E를 다룰 가능성을 가졌는가? 모순/누락은 없는가?
- **Post-execution**: 실제 산출물이 spec.E를 충족했는가? 어떤 component가 부족했는가?

두 단계의 결과는 component 자체의 개선 loop로 환류한다 (§4).

---

## 1. Pre-execution Checklist

composer Phase 5에서 적용. composed prompt가 다음 7항목을 통과해야 실행 허용.

| ID | 항목 | 통과 조건 | 실패 시 | Severity |
|---|---|---|---|---|
| P1 | spec coverage | composed prompt가 spec A-E 모두 다룸 (텍스트 grep으로 키워드 확인) | 누락 부분 보강 | **Blocking** |
| P2 | output 형식 명시 | 출력 schema / 길이 / 언어 명시됨 | composer §6 output spec에 추가 | **Blocking** |
| P3 | gate / 종료 조건 | 무엇을 만들면 "끝"인지 명시됨 | gate criteria 추가 | **Blocking** |
| P4 | 충돌 없음 | header 톤/언어와 body component 지시가 모순 없음 | 우선순위 명시 (header 우선) | **Blocking** |
| P5 | 민감정보 redacted | secret 정규식 grep 통과 (context-injection §3.1) | re-redact 후 재검사 | **Blocking** |
| P6 | 토큰 예산 내 | rough estimate (lines × 4) < spec.D 예산 | component 축소 / 발췌 | Warning |
| P7 | bypass 재검토 | composition이 정말 direct보다 나은가? | bypass로 전환 | Warning |

**P1-P5는 blocking** (1개라도 fail → 실행 금지). **P6-P7은 warning** (사용자 확인 후 진행 가능).

### 1.1 P1 spec coverage 자동 검사

```python
# pseudocode
spec_keywords = extract_keywords(spec.A, spec.B, spec.E)
for kw in spec_keywords:
    if kw not in composed_prompt:
        fail(f"P1: '{kw}' not covered")
```

키워드 매칭은 fuzzy하게 (lemma 또는 synonym 허용). 절대 grep 100% 매칭은 false negative 많음.

### 1.2 P3 gate 명시 확인

다음 표현 중 1개라도 있어야 통과:
- "다음을 모두 만족하면 종료" / "다음 조건을 충족"
- "출력 종료 조건"
- "출력 후 자체 검토 항목"
- multi-agent template의 G0-G4 gate 참조

---

## 2. Composition smell tests

Pre-execution에서 다음 패턴이 보이면 composition 재작업 신호:

### 2.1 Redundancy
같은 instruction이 여러 component에서 반복.
**예**: "사실 주장에 evidence tag 부착" 가 component A의 §2와 B의 §3에 같이 등장.
**조치**: 1곳으로 consolidate, 다른 곳은 reference.

### 2.2 Contradictions
한 component는 "정성 분석 의무" 다른 곳은 "정성 분석 금지" 같은 모순.
**조치**: composer §1 Role에서 우선순위 결정, 또는 task 재정의.

### 2.3 Vague gates
"충분히 좋으면 종료" 같은 모호한 종료 조건.
**조치**: 측정 가능한 조건으로 sharpen (체크리스트 형태).

### 2.4 Missing fallback
도구 실패 / context 부족 시 무엇을 할지 명시 없음.
**조치**: "X가 실패하면 abort, 메인에 보고" 한 줄 추가.

### 2.5 Anchoring 누출
"우선 가설" 같은 anchoring 표현이 spec → component까지 흘러감 (multi-agent template C-021 violation).
**조치**: spec에 anchoring 단어가 있으면 제거 후 재composition.

### 2.6 Over-scoping
spec은 1 topic인데 multi-agent template이 활성화됨 (router bypass 실패).
**조치**: router 재실행, bypass 분기 적용 확인.

---

## 3. Post-execution Rubric (5축 채점)

산출물을 5축으로 1-5 채점. 각 축은 spec과 산출물의 함수.

| 축 | 의미 | 1점 (실패) | 3점 (보통) | 5점 (우수) |
|---|---|---|---|---|
| **Relevance** | spec.A purpose 충실도 | 목적 빗나감 | 부분 충족 | 직접 답함 |
| **Evidence** | 사실 주장의 근거 | tag 없거나 false | 일부 tag, 일부 검증 가능 | 모두 [VERIFIED:*] |
| **Reasoning** | 논리 일관성 | 모순/비약 | 결론 도달 가능 | 모든 step 정당화 |
| **Completeness** | spec.E success criteria | < 절반 | 핵심 충족, 부속 누락 | 모두 충족 |
| **Actionability** | 다음 step이 명확한가 | 추상적 | step 식별 가능 | reversibility + 실행계획 명시 |

### 3.1 점수별 처리

- **평균 ≥ 4.0** → 채택, 종료.
- **3.0 ≤ 평균 < 4.0** → 부분 채택 + 미흡 축 재실행 (§4 개선 loop).
- **평균 < 3.0** → 채택 거부, composition 재작업 (Phase 1 또는 2로 회귀).

### 3.2 spec.G와 결합

- `[IRREVERSIBLE]` 권고 + Confidence-축 < 4 → 자동 PoC 요구 (multi-agent template §2.3.1 매트릭스).
- `[COSTLY-TO-REVERSE]` + Evidence-축 < 4 → 추가 검증 의무.

---

## 4. 개선 loop — 부족 축 → 수정 대상 mapping

산출물이 부족한 축을 보고 어떤 component를 수정할지 결정:

| 부족 축 | 1순위 수정 대상 | 2순위 |
|---|---|---|
| **Relevance** | task-spec.A 재작성 (purpose sharpen) | router의 component 선택 재검토 |
| **Evidence** | role-dict의 `evidence-checker` 추가 | multi-agent-template §2.1 evidence tagging 강조 |
| **Reasoning** | role-dict의 `devils-advocate` 추가 | `consistency-checker` 추가 |
| **Completeness** | spec.E 재작성 (criteria 보강) | composer §6 output spec에서 echo |
| **Actionability** | composer §6에 reversibility + 실행계획 필드 명시 | role-dict의 `judge` 추가 |

iteration cap: 2회. 그래도 부족하면 Phase 1로 회귀하거나 bypass 전환.

---

## 5. 메타 평가 (시스템 자체, 3개월 주기)

누적 사용 결과를 검토하여 시스템 자체를 개선:

### 5.1 측정 metric

```
- Bypass 비율 = bypassed_count / total_request_count
- Re-composition 비율 = re_run_count / total_composition_count
- Post-eval 평균 점수 (5축 평균의 평균)
- Component별 활성화 빈도
- spec → routing 의도 일치율 (수동 sampling)
```

### 5.2 해석 가이드

- **Bypass 비율 < 10%** → over-routing 의심 (composition을 너무 자주 강행)
- **Bypass 비율 > 70%** → composition이 거의 안 쓰임 (시스템 무용지물 의심)
- **Re-composition 비율 > 30%** → 1차 composition 품질 낮음 → router 또는 spec template 개선
- **평균 점수 trend 우하향** → drift 의심 (component가 stale 또는 spec quality 저하)
- **저빈도 component (< 5% 활성화)** → 삭제 또는 trigger 재설계 후보

### 5.3 개선 행동

- 메타 평가 결과를 `.meta-eval/<quarter>.md`로 저장
- 시정 조치는 component의 version↑ (catalog §1.1)으로 표시
- 큰 변경(major 버전 bump)이면 기존 spec으로 회귀 테스트

---

## 6. Anti-patterns

- ❌ **Post-eval 점수만 보고 평균 ≥ 4 통과** — 5축 모두 ≥ 3인지 함께 확인. 한 축 1점이면 평균 4여도 fail.
- ❌ **Pre-eval skip하고 일단 실행** — token 낭비. P1-P5는 의무.
- ❌ **Smell test를 LLM에게 self-eval로 시킴** — 본인이 만든 prompt를 본인이 검토하면 anchoring. 별도 role(devils-advocate 또는 consistency-checker) 호출.
- ❌ **개선 loop 무한 진행** — cap 2회 엄수. 그래도 안 되면 task 재정의.
- ❌ **메타 평가 안 함** — 시스템 drift가 누적되어 silent quality 저하.

---

## 7. Gate 표 (composer phase와 매핑)

| Composer Phase | 이 rubric에서 호출하는 부분 | Gate ID |
|---|---|---|
| Phase 5 (Pre-validation) | §1 P1-P7 + §2 smell tests | G5 |
| Phase 7 (Post-eval) | §3 5축 채점 | G6 |
| Lifecycle (분기별) | §5 메타 평가 | (분기 cycle) |

각 gate 통과 기준은 composer 본문 참조.
