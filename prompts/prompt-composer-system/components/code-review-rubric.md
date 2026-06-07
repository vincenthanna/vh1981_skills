# Code Review Rubric

> **무엇**: Code change(PR/patch/commit series)를 architect×review, security-researcher×evidence-checker lens로 평가하는 rubric.
> **용도**: PR 채택/차단 결정, 추가 검증 요구, reviewer feedback comment의 1차 자료로 사용.
> **시리즈 위치**: composer Phase 4 (Assembly)에서 component로 활성화, Phase 5/7 자체 채점에도 활용. `../builder/prompt-evaluation-rubric.md`(=composed prompt 평가)와 별개로 본 rubric은 *코드 변경*을 평가.

---

## 0. Router 등록 metadata

`../builder/prompt-component-router.md §1` 표에 등록될 정보:

| 항목 | 값 |
|---|---|
| component name | `code-review-rubric.md` |
| trigger signals | spec.B = Review, spec.H 에 PR/commit/diff 경로 존재, spec.L 에 `security-researcher` / `backend-engineer` / `frontend-engineer` 등 코드 도메인 lens (role-dict §5 실재 lens). (+ repo-local 리뷰 규칙 파일 존재 → §9; changeset 1000+LOC 또는 5+파일 cross-cutting → §10) |
| inputs | diff (unified or git format), 변경 대상 파일 경로 list, (선택) PR description / 이슈 link, (선택) repo-local 규칙 파일 (§9) |
| outputs | 8축 점수 + axis별 발견 사항 + 차단 조건 통과 여부 + reviewer comment draft + (해당 시) 적용된 repo-local rule 출처 + bundle 분할 plan |
| cost (rough tokens) | Low-Medium (~600 발췌 / ~3k full; §10 분할 시 bundle 수에 비례) |
| 충돌 가능 component | `multi-agent-analysis-template.md` (multi-topic 비교가 아닌 단일 변경 평가, 함께 쓰면 over-scoping) |
| version | 1.1 |
| owner | prompt-composer-system 유지자 |
| layer | **domain content (review)** — CLAUDE.md "조합 인프라(5) / 분석 컨텐츠(2) / domain content" 3축 분류. router §1.1 metadata 정의 참조. |

> **trigger 분기 추가** (router §2 decision tree): step 2에서 `spec.B = Review` 분기 시 `role-dictionary(devils-advocate + evidence-checker)` 대신 또는 추가로 이 rubric을 활성화.

---

## 1. 사용 시점 / 비사용 시점

### 1.1 사용 시점

- PR / patch / commit series 가 사용자 결정의 핵심 산출물.
- 변경이 다음 중 1개 이상 해당:
  - 외부 API contract 변경
  - 보안 surface 변경 (auth, crypto, network, secret 처리)
  - DB 스키마 migration
  - 분산 시스템 invariant 변경 (consistency, ordering, idempotency)
  - 1000+ LOC 변경 또는 5+ 파일 cross-cutting → **§10 스코핑/번들링으로 분할 리뷰**
- Reviewer가 *왜 통과/차단*인지 evidence-backed 근거를 남겨야 할 때.

### 1.2 비사용 시점 (bypass)

- 단순 typo / formatter / dependency version bump → direct review.
- prototyping 코드 (장기 운영 의도 없음, throwaway 명시).
- 본인 작성한 코드 self-review만 — anchoring bias. 별도 reviewer 또는 LLM critic 필수 (`agent-role-dictionary.md §0 anchoring 방지`).
- spec.G = `[REVERSIBLE]` + 변경 < 50 LOC + test 자동 통과 → 가벼운 spot-check 충분.

---

## 2. 평가 축 정의 (8축)

각 축은 *무엇을 보는가*와 *어디서 근거를 찾는가*를 명시.

> repo-local 컨벤션 규칙이 있으면 **§9 custom rule layer**로 해당 축의 통과 임계를 강화·추가한다 (8축은 embedded 기본층).

| 축 ID | 축 이름 | Lens | 무엇을 보는가 | 근거 위치 |
|---|---|---|---|---|
| **A1** | Correctness | architect | 변경이 의도된 동작을 정확히 구현하는가 (logic, edge case, off-by-one) | diff + 기존 동작 명세 / test |
| **A2** | Security | security-researcher | 위협 모델, attack surface, data exposure, secret handling | diff + threat model (없으면 inference + `[ASSUMPTION]`) |
| **A3** | Maintainability | architect | 변경이 코드베이스의 미래 변경을 쉽게 / 어렵게 만드는가 | 코드 구조, naming, 추상화 layer |
| **A4** | Test quality | architect | 변경에 대응하는 test가 (a) 존재 (b) failing-case cover (c) flaky 아닌가 | test 파일 + CI 결과 |
| **A5** | Performance | architect | latency / memory / I/O / DB query pattern 변화 | 측정 결과 (없으면 정성 reasoning + `[INFERRED]`) |
| **A6** | Documentation | architect (pedagogy 보조) | API doc / commit message / inline 주석 / CHANGELOG | 변경 사항 description |
| **A7** | Design fit | architect | 변경이 기존 아키텍처 결과 정합 / 부분 위반 / 전면 재설계 신호 | 인접 파일 / 모듈 경계 |
| **A8** | Evidence quality | evidence-checker | 위 7축 평가 자체의 근거가 어디서 왔는가 | reviewer note + 외부 reference |

> **A8 의 메타-성격**: 다른 7축은 코드를 본다. A8 는 *reviewer가 그 평가를 어디서 얻었는지* 본다. 후속 reviewer가 검증 가능해야 함.

---

## 3. 채점 rubric (각 축 1-5)

| 점수 | A1 Correctness | A2 Security | A3 Maintainability | A4 Test quality |
|---|---|---|---|---|
| **5** | 모든 edge case cover, 명세와 정확히 일치 | 위협 모델 명시 + 신규 attack vector 0 + 기존 vector 닫힘 | 변경이 미래 작업 더 쉽게 (예: 추상화 정리, 죽은 코드 제거) | 변경된 모든 분기에 test 추가 + edge case cover |
| **4** | 핵심 path 정확, 일부 edge case 미커버 (명시됨) | 위협 모델 인지 + 신규 vector 0 | 변경이 기존 수준 유지 | 변경 path test 추가 (edge 일부 누락) |
| **3** | 정상 path만 검증됨 | 위협 모델 미명시이나 의심점 0 | 일부 추상화 누수 (justified) | test 부분 존재 |
| **2** | logic bug 의심 1건 이상 | 신규 attack vector 1건 이상 (mitigation 명시) | 추상화 손상 + future refactor 강제 | 핵심 path 미커버 |
| **1** | logic bug 확인 / 명세 위반 | 명백한 vulnerability 도입 | 변경이 코드베이스 악화 | test 누락 + 변경 검증 불가 |

| 점수 | A5 Performance | A6 Documentation | A7 Design fit | A8 Evidence quality |
|---|---|---|---|---|
| **5** | 측정 결과 첨부 + 영향 0 또는 개선 | API doc + CHANGELOG + 의도 명시 commit | 기존 아키텍처 강화 | 모든 평가에 `[VERIFIED:static <path:line>]` 또는 외부 인용 |
| **4** | 정성 reasoning + 추정 영향 < 10% | doc 핵심 부분 update | 기존 결 따름 | 평가의 80%+ evidence-tagged |
| **3** | 영향 분석 1줄 명시 | doc 변경 없음 (변경 안 영향) | local optimum, global 영향 미평가 | 평가의 50%+ evidence-tagged |
| **2** | 영향 분석 누락 + 의심점 | doc stale 위험 | 아키텍처 인접 위반 (justified) | 평가 대부분 reviewer 인상 |
| **1** | 명백한 regression 의심 | API 변경했는데 doc 미반영 | 아키텍처 무시 / 우회 | evidence 없음 |

> **사용법**: 각 축에 1-5 점수 부여, 8축 평균 + 최저 축 함께 기록.

---

## 4. 통과 / 차단 / 조건부 통과

### 4.1 통과 (merge 권장)

- **평균 ≥ 4.0 AND 모든 축 ≥ 3** AND
- A2 (Security) ≥ 4 (보안 변경 포함 시) AND
- A4 (Test quality) ≥ 3

### 4.2 조건부 통과 (reviewer comment로 fixes 요구 후 재검토)

- **평균 3.0-4.0** 또는 일부 축 = 2 (단, A2/A4 ≥ 3)
- 차단되지 않은 fix request를 PR description에 explicit 표기
- 재검토 시 변경된 축만 재채점

### 4.3 차단 (merge 금지, 재작업 요구)

다음 중 1개라도 해당:
- A1 (Correctness) = 1 (logic bug 확인)
- A2 (Security) ≤ 2 (vulnerability 도입 또는 mitigation 부재)
- A8 (Evidence quality) = 1 (평가 자체가 근거 없음 → 평가 무효)
- 평균 < 3.0

### 4.4 spec.G와 결합

| spec.G | 추가 조건 |
|---|---|
| `[REVERSIBLE]` | 위 표 그대로 |
| `[COSTLY-TO-REVERSE]` | A1, A4 모두 ≥ 4 의무 |
| `[IRREVERSIBLE]` | A1, A2, A4, A7 모두 ≥ 4 의무 + PoC / canary plan 필수 |

---

## 5. Reviewer comment draft 형식

본 rubric의 출력은 마지막에 다음 형태의 comment draft 1개를 생성:

```markdown
### Review summary

- 평균: <X>/5
- 최저 축: <Axn> = <점수>
- 결정: 통과 / 조건부 통과 / 차단

### 축별 발견

**A1 Correctness (<점수>)**: <1-3 line 발견 + `[VERIFIED:static <path:line>]`>
**A2 Security (<점수>)**: <위협 + mitigation 권고 + 근거>
... (8축)

### 차단 / 조건부 fix list (있는 경우)

- [ ] <항목 1> — <근거 path:line> — <fix 권고>
- [ ] <항목 2> ...

### Author 자기검증 요청 (선택)

- [ ] <A8 evidence 부족 항목>에 대해 author가 추가 검증

### 적용된 repo-local rule (§9, 해당 시)

- <layer/path> → <rule 요약> → <영향 축/차단 조건>  (예: `project .review-rules.json` `auth/**` → A2 임계 ≥4)

### Bundle별 발견 / cross-cutting (§10, 대형 changeset 시)

- **Bundle <이름>** (<파일 목록>): <축별 발견 요약>
- **Cross-cutting** (bundle 경계 넘는 invariant): <발견 + 근거>
```

이 draft는 PR comment에 그대로 paste 가능한 markdown. 단, *자동 게시 금지* — reviewer가 1회 검토 후 게시.
§9 적용 시 "적용된 repo-local rule" 절, §10 적용 시 "Bundle별 발견 / cross-cutting" 절을 포함한다(미적용 시 생략).

---

## 6. 적용 예시 — Mini E2E

### 예시 입력

- spec.A: "auth middleware 신규 PR 검토"
- spec.B: Review
- spec.G: `[COSTLY-TO-REVERSE]` (auth 변경은 rollback 시 사용자 강제 logout)
- spec.H: `feature/jwt-rotation`, base `main`, 3 파일 변경 / +180 -45 LOC
- spec.L: security-researcher (1순위), backend-engineer (2순위)

### 평가 흐름

1. Composer가 routing에서 `code-review-rubric` 활성화 (spec.B=Review).
2. 본 rubric §2 8축 + §3 채점.
3. spec.G=`[COSTLY-TO-REVERSE]` → §4.4 적용, A1/A4 ≥ 4 의무.
4. 평가 결과 (가상):
   - A1=4, A2=3 (위협 모델 누락), A3=4, A4=3 (refresh token rotation test 없음), A5=4, A6=3, A7=4, A8=4.
   - 평균 = 3.6
   - 판정 분기:
     - §4.1 통과 조건의 "보안 변경 시 A2 ≥ 4" 인데 A2=3 → **통과 불가**.
     - spec.G=`[COSTLY-TO-REVERSE]`의 §4.4 추가 조건(A1·A4 ≥ 4)에서 A4=3 → **미충족**.
     - 평균 3.6 + A2/A4 ≥ 3 이므로 §4.2 **조건부 통과**로 분류. 단 위 두 미충족 항목(A2 위협 모델, A4 rotation test)은 **차단성 필수 fix**.
5. 결정: **조건부 통과 (차단성 fix 2건) — 위협 모델 보강(A2 → ≥4) + refresh rotation test 추가(A4 → ≥4) 후 재검토. 두 fix 전에는 merge 금지.**

### 출력 sample (요약)

```markdown
### Review summary
- 평균: 3.6/5
- 최저 축: A2 (Security) = 3
- 결정: 조건부 통과 (차단성 fix 2건, merge 전 필수)

### 차단성 fix list (merge 전 필수)
- [ ] auth/middleware.py: refresh token rotation 시나리오의 위협 모델 명시 (A2 → ≥4)
- [ ] tests/auth/test_jwt_rotation.py: rotation race condition test 추가 (A4 → ≥4)
```

---

## 7. Anti-patterns

- ❌ **본인이 자기 PR을 본 rubric으로 채점** — `agent-role-dictionary §0` anchoring 위반. 별도 reviewer (사람 또는 LLM critic) 사용.
- ❌ **8축 평균만 보고 통과 결정** — §4.1 의 "모든 축 ≥ 3" 조건 확인. 평균 4여도 A2=1 이면 차단.
- ❌ **A8 (Evidence quality) skip** — "코드 보면 알지" 식 평가는 후속 reviewer가 검증 불가. 모든 평가에 `[VERIFIED:static <path:line>]` 또는 `[INFERRED <근거 chain>]` 부착 의무.
- ❌ **draft comment 자동 게시** — §5 draft 는 paste-ready 일 뿐, reviewer 1회 검토 의무.
- ❌ **`[COSTLY-TO-REVERSE]` PR 에 §4.4 조건 무시** — auth/migration/billing 변경은 spec.G 추가 조건 의무. 시간 압박 시 PoC 부분 분리 권고.
- ❌ **multi-agent-template과 동시 활성화** — 본 rubric은 단일 변경 평가. 다수 PR 비교는 multi-agent로 별도.
- ❌ **차단 결정 후 즉시 close** — author가 fix 가능한 형태로 차단. close는 별도 의사결정.

---

## 8. 참고

### 8.1 내부 (라이브러리 내)

- `../builder/prompt-evaluation-rubric.md` — composed prompt 자체의 5축 평가 (Phase 5/7). 본 rubric과 영역 다름. `[VERIFIED:static prompts/prompt-composer-system/builder/prompt-evaluation-rubric.md]`
- `agent-role-dictionary.md` §1.2 `architect`, §5.9 `security-researcher`, §2.5 `evidence-checker` — 본 rubric의 lens 출처. `[VERIFIED:static prompts/prompt-composer-system/agent-role-dictionary.md:57,571,202]`
- `multi-agent-analysis-template.md` §2.1 evidence tagging, §2.2 reversibility — A8 / §4.4 조건의 원칙. `[VERIFIED:static prompts/prompt-composer-system/multi-agent-analysis-template.md]`

### 8.2 외부 (axes 선정 영향)

- Conventional Comments — Reviewer comment 분류 규약 (blocking / nitpick / suggestion 등). §5 reviewer comment draft 형식의 영감. `[ASSUMPTION canonical URL: https://conventionalcomments.org 검증 방법: web fetch + tier=community 확인]`
- Google Engineering Practices — "Code Review Developer Guide" 공개 자료 (How to do a code review / Speed of Code Reviews / Code review standards). 본 rubric의 8축 분리 원칙(A1 Correctness, A4 Test, A7 Design fit 등)의 영감. `[ASSUMPTION canonical URL: https://google.github.io/eng-practices/review/ 검증 방법: web fetch + tier=vendor 확인]`
- "Best Kept Secrets of Peer Code Review" (SmartBear) — 코드 리뷰 best practice에 대한 산업 가이드 (line-by-line ≤ 400 LOC, ≤ 60 min 등 measurable threshold 권고). `[ASSUMPTION canonical URL: smartbear.com/learn/code-review/ 검증 방법: web fetch + tier=vendor 확인]`

> ⚠️ 외부 reference의 URL은 라이브러리 작성 시점(2026-05-19)에 web fetch 미수행. 첫 운영 시 composer Phase 5 P5 단계 또는 `evidence-checker` role에서 `[VERIFIED:webfetch <tier> <URL> accessed:<date> version:<v>]`로 격상 의무.

> **§ 배치 참고**: §9·§10은 §8(참고) *뒤에* 추가됐다 — 기존 §1~§8 번호와 cross-ref(§4.3/§5/§8.2 등)를 깨지 않기 위한 의도적 선택(no-renumber). 참고 절이 마지막이 아닌 점은 알려진 경미한 양식 편차. (출처: alibaba/open-code-review `[VERIFIED:webfetch tier4 https://github.com/alibaba/open-code-review accessed:2026-06-07]`에서 착안, v1.1 추가.)

---

## 9. Custom rule layer (repo-local 규칙 계층)

> v1.1 추가. §2의 8축(embedded 기본층) 위에 repo 고유 컨벤션 규칙을 우선순위로 얹는 *추가 강화층*. 8축을 대체하지 않는다.

### 9.1 왜 필요한가

§2의 8축은 **범용 embedded 기본층**이다. 그러나 repo마다 고유 컨벤션이 있다 — `auth/**`는 위협 모델 필수, `migrations/`는 reversible 필수, `*mapper*.xml`은 SQLi 점검. 이를 매 리뷰 instruction에 수동 주입하면 (a) 누락 (b) reviewer마다 drift. → **선언적 규칙 파일로 SSOT화**하고 8축 위에 얹는다.

> `context-injection-patterns.md`(Phase 3)가 일반 context 주입을 제공하지만, §9는 그 위에 *구조화 schema(`.review-rules.json`) + 우선순위 체인*을 얹는 점이 다르다(ad-hoc 주입 ≠ 패턴-스코프 규칙 + precedence).

### 9.2 우선순위 계층 (높은 쪽 우선, layer당 first-match)

`[VERIFIED:webfetch tier4 README-described https://raw.githubusercontent.com/alibaba/open-code-review/main/README.md accessed:2026-06-07]` open-code-review 4계층 rule chain 착안 (단, rule-processing 구현은 비공개 — README 기술 기준):

| 우선순위 | layer | 위치 | 비고 |
|---|---|---|---|
| 1 (최우선) | 호출 인라인 규칙 | spec/CLI에서 직접 준 rule | 1회성 override |
| 2 | 프로젝트 규칙 | `<repo>/.review-rules.json`(또는 기존 컨벤션 파일) | 팀 공유 SSOT |
| 3 | 사용자/전역 규칙 | `~/.review-rules.json` | 개인 기본 |
| 4 (기본) | embedded | 본 rubric §2 8축 | 항상 존재 |

> layer당 첫 매칭 path가 이긴다(first-match). `[VERIFIED README-stated, 구현 미검증]` — 상위 layer가 매칭되면 하위 동일 path 규칙은 무시.

### 9.3 규칙 형식 (path glob → rule text)

`[VERIFIED:webfetch tier4 README-described — `rule.json` 파일 미독립 fetch]` schema(`{path, rule}`, `**` 재귀 glob + `{a,b}` brace 확장):

```json
{
  "rules": [
    { "path": "auth/**/*.{py,go}", "rule": "신규/변경 엔드포인트는 위협 모델 명시 — A2 Security 통과 임계를 ≥4로 강제" },
    { "path": "**/migrations/*",   "rule": "down-migration 존재 + reversible 확인 — 없으면 §4.3 차단" },
    { "path": "**/*mapper*.xml",   "rule": "SQL injection / 파라미터 오류 / 미닫힘 태그 점검 (A2)" }
  ]
}
```

### 9.4 규칙 ↔ 8축 매핑 `[INFERRED]`

custom rule은 8축을 **대체하지 않고 강화/추가**한다. 각 rule은 둘 중 하나로 해석:

- (a) **임계 상향**: 특정 축의 통과 점수를 올림 (예: `A2 ≥ 4 강제`).
- (b) **신규 차단 조건**: §4.3 차단 목록에 rule-derived 항목 추가 (예: down-migration 없음 → 차단).

충돌 시: §9.2 우선순위 + **"더 엄격한 쪽 우선"**(보수적). reviewer가 1줄 근거로 판정.

> **§4 hard floor 불가침**: custom rule은 §4의 hard floor(예: A2 ≤ 2 → 무조건 차단, A8 = 1 → 평가 무효)를 *낮추지 못한다* — 오직 추가·상향만 가능. 상위 layer가 더 느슨해도 §4 floor는 그대로 적용.

### 9.5 적용 절차

1. 변경 파일 경로 각각을 규칙 path와 매칭(layer 1→4, first-match).
2. 매칭된 rule을 해당 축 평가에 주입(임계 상향 또는 차단 조건).
3. **§5의 "적용된 repo-local rule" 절**에 어느 rule이 어디서(layer/path) 적용됐는지 출처 명시.

### 9.6 Anti-patterns

- ❌ 규칙 파일을 못 읽었는데 "규칙 없음"으로 진행 → **abort 또는 embedded(§2)만 사용임을 §5에 명시**(silent 누락 금지).
- ❌ rule 텍스트만 믿고 8축 평가 skip — custom rule은 *추가층*, 8축은 항상 평가.
- ❌ rule이 8축/§4 floor와 모순될 때 임의 선택 — §9.2 우선순위 + §9.4 hard floor 불가침 따름.
- ❌ rule path가 광범위(`**/*`)해 모든 파일에 무차별 적용 → 과적용, scope 좁힌 path 권고.

---

## 10. 대형 changeset 스코핑 & 파일 번들링

> v1.1 추가. §1.1의 "1000+LOC / 5+파일" 트리거에 대응하는 *분할 방법론*. 동시성/병렬 실행 tooling은 범위 밖.

### 10.1 왜 필요한가

§1.1은 `1000+ LOC / 5+ 파일`을 *사용 시점*으로만 명시하고 **어떻게 분할하나**는 비움. 대형 changeset을 한 컨텍스트에 통째로 넣으면 (a) 컨텍스트 한도 초과 (b) 후반 파일 attention 저하 (c) **파일 간(cross-file) 결함 누락**. → 관련 파일을 **리뷰 단위(bundle)**로 묶어 분할하고, bundle별 평가 후 cross-cutting 합산.

### 10.2 번들 휴리스틱 (관련 파일을 한 단위로)

`[VERIFIED:webfetch tier4 https://github.com/alibaba/open-code-review accessed:2026-06-07]` divide-and-conquer 파일 번들링 + i18n 쌍 예시. 그 외 휴리스틱은 `[INFERRED]`(일반 알고리즘 비공개) + 일반 코드리뷰 관행:

| 번들 유형 | 묶는 파일 | 이유 |
|---|---|---|
| 인터페이스+구현 | `*.proto`+생성물 / interface+impl | 계약과 구현을 함께 봐야 정합 판정 |
| 스키마+마이그레이션 | model/entity + migration | 스키마 변경의 reversible·정합 |
| 코드+테스트 | `src/foo` + 대응 `test/foo` | A4 Test quality를 같은 단위에서 |
| 호출자+피호출자 | API 시그니처 변경 + 호출부 | backward-compat·누락 호출부 |
| i18n/설정 쌍 | `message_en.*`+`message_zh.*` | 키 누락·불일치 (open-code-review 예시 `[VERIFIED]`) |
| 파일명/경로 유사도 | 같은 디렉토리·유사 stem | 응집된 변경 단위 |

> 한 bundle은 한 컨텍스트에서 독립 리뷰 가능한 크기로(§8.2 SmartBear ≤400 LOC 권고와 정합).

### 10.3 cross-cutting invariant 보존 (분할의 핵심 위험 방어) `[INFERRED]`

분할은 **파일 간 결함을 못 보게** 만들 수 있다. 방어:

1. **분할 전** — changeset 전체의 *cross-cutting 관심사 목록* 작성: 공유 상태/락, API contract, 트랜잭션 경계, 보안 surface, 전역 invariant. 각 bundle 리뷰 시 이 목록을 헤더로 주입.
2. **분할 후** — bundle별 finding을 모은 뒤 **cross-cutting pass**: bundle 경계를 넘는 가정(예: bundle A가 bundle B의 lock/ordering을 가정) 확인. 이 pass 없이는 §4 판정 금지.

### 10.4 적용 절차

1. trigger 확인(§1.1: 1000+LOC 또는 5+파일 cross-cutting).
2. cross-cutting 관심사 목록 작성(§10.3-1).
3. §10.2 휴리스틱으로 partition → bundle 목록. **깨끗한 partition을 못 찾으면 단일 bundle로 처리하되 §10.3 cross-cutting pass는 필수.**
4. bundle별 §2 8축 + (해당 시) §9 custom rule 평가.
5. §10.3-2 cross-cutting pass.
6. **§5의 "Bundle별 발견 / cross-cutting" 절**에 bundle별 발견 + cross-cutting 통합 발견 기재.

### 10.5 Anti-patterns

- ❌ 토큰 채우려 **무관 파일**을 한 bundle에 — bundle 응집 깨짐.
- ❌ cross-cutting 목록 없이 분할 → 파일 간 결함 누락(분할의 최대 실패모드).
- ❌ bundle을 완전 독립이라 가정하고 cross-cutting pass skip.
- ❌ partition 안 되는 changeset을 무리하게 쪼갬 → §10.4-3 단일 bundle fallback 사용.
- ❌ **동시성/병렬 실행 엔진** 세부(타임아웃·worker 수)를 여기서 규정 — 본 §는 *분할 방법론*만, 실행 tooling은 범위 밖.
