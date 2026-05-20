# Autonomous Optimization Loop

> 측정 가능한 단일 스칼라 지표를 가진 태스크를 **고정 예산 · 단일 변수 · keep-or-revert**로 에이전트가 무인 반복 개선하게 만드는 워크플로우 template.
>
> 산출물: slot 정의 → baseline → 반복 trial 로그 → best config + 학습 요약.
>
> 출처 아이디어: karpathy/autoresearch `program.md` (ML 학습 코드 야간 자율 최적화)를 도메인 무관 형태로 추상화. `[ASSUMPTION canonical URL: https://github.com/karpathy/autoresearch 검증 방법: web fetch + tier=community 확인]`
>
> **시리즈 위치**: composer Phase 4 (Assembly)에서 활성화. `experiment-design-template.md`가 단일 *가설의 통계적 검증*이라면, 본 template은 측정가능 지표의 *자동 탐색 최적화*. 둘은 순차 결합 — 본 template으로 best config 발견 → experiment-template으로 그 효과를 검증.

---

## 0. Router 등록 metadata

| 항목 | 값 |
|---|---|
| component name | `autonomous-optimization-loop.md` |
| trigger signals | spec.B = Analysis + 목표가 단일 스칼라 지표 minimize/maximize + 측정 자동화 가능 + 반복 탐색 의도 + spec.G = REVERSIBLE |
| inputs | objective metric + direction, editable/frozen surface, 1회 budget, measure command, stop condition |
| outputs | 누적 trial 로그 (results.tsv) + best commit + baseline 대비 개선 요약 + 학습 메모 |
| cost (rough tokens) | Medium (~1.5k 발췌 / ~9k full) — 단, 실제 비용은 trial 횟수 × measure 비용이 지배적 |
| 충돌 가능 component | `experiment-design-template.md` (탐색 vs 검증 — 동시 활성 시 over-scope, 순차 사용), `multi-agent-analysis-template.md` (자동 탐색 vs 대안 비교 결정) |
| version | 1.0 |
| owner | prompt-composer-system 유지자 |

> **trigger 분기**: router §2 step 2에서 `B = Analysis` AND 목표가 *측정가능 스칼라의 자동 반복 개선*이면 본 template 활성화. `B = Analysis` 이지만 *단일 가설 검증*이면 `experiment-design-template`. 자동 탐색으로 best config를 찾은 뒤 그 효과를 정식 검증하려면 본 template → experiment-template *순차*.

---

## 1. 사용 시점 / 비사용 시점

### 1.1 사용 시점

- 목표가 **단일 스칼라 지표**로 환원된다 (`minimize`/`maximize`가 명확).
- 1회 시도(수정→측정)가 **유한·재현 가능한 예산**(wall-clock 또는 비용) 안에서 끝나고, 시도 간 예산이 동일해 **공정 비교** 가능.
- 변경 효과를 **사람 판단 없이 자동 측정**할 수 있다 (measure command + 파싱 1단계).
- 변경을 **commit/revert로 되돌릴 수 있는** 버전관리 환경 (spec.G = REVERSIBLE).
- 사람 부재 시 다음 시도를 자율 결정해도 되는 **위임 권한**이 있다.

### 1.2 비사용 시점 (bypass)

- 측정이 주관적이거나 사람 리뷰가 필수 → `verify` 스킬 / `code-review-rubric.md`.
- 1회 측정이 비싸거나 비결정적이라 공정 비교 불가, 또는 통계적 검증이 목표 → `experiment-design-template.md`.
- 다수 *대안 설계*를 동일 기준으로 비교·선정 (탐색이 아니라 의사결정) → `multi-agent-analysis-template.md`.
- 되돌릴 수 없는 부수효과(외부 배포, 데이터 변경, 과금)를 동반하는 변경 (spec.G = COSTLY/IRREVERSIBLE) — 본 template 차단.
- 지표가 사용자 결정에 영향 없는 지식 만족용 — overhead 큼.

---

## 2. 작업 모델 (Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│ Optimizer (메인 세션 — 무인 루프)                            │
│  phases: setup → (modify → measure → judge → log) × N        │
│  - 단일 변수 가설 1개 선정 (proposer 자세)                   │
│  - editable_surface 수정 + commit                            │
│  - measure_command 실행 (고정 budget)                        │
│  - 지표 파싱 + best 대비 keep/revert 판정                    │
│  - results_log append + 학습 메모                            │
└─────────────────────────────────────────────────────────────┘
        │ (proposer 자세로 다음 시도 설계)        ▲ devils-advocate / risk-auditor 자세로 review
        ▼                                         │
┌──────────────────────────────────────────────────────────┐
│  Gaming / overfit auditor (별도 LLM 또는 reviewer)       │
│  (agent role: systems-researcher × devils-advocate       │
│   또는 risk-auditor — domain에 따라 ml-researcher)       │
│  - 지표가 eval에 overfit / 측정 코드 우회로 gaming?       │
│  - frozen_surface 침범 여부 감사                          │
│  - 개선이 노이즈 수준인지 (tie-breaker 적용 정당)         │
│  - 숨은 비용(VRAM/복잡도/가독성) 누락 여부                │
└──────────────────────────────────────────────────────────┘
```

> **Lens 분리 원칙** (`agent-role-dictionary.md §0`): proposer는 최적화 가설을 *생성*하고, devil's advocate/risk-auditor는 *gaming·overfit·scope 침범*을 감사. 같은 세션이 둘 다 하면 자기 변경에 anchoring — 주기적(예: 10 trial마다 또는 종료 시) 별도 agent로 감사. 무인 단발 루프이면 종료 시 1회 감사 의무.

---

## 3. 절차 (Step 0 ~ Step 5)

### Step 0 — Slot 정의 (루프 진입 전 1회)

산출물: `.optimize/<run-id>/00_slots.yaml`

이 블록만 채우면 루프가 작동한다. 미완성 채로 시작 금지.

```yaml
objective_metric:   # 예: "p95 latency (ms)" — 단일 스칼라
direction:          # minimize | maximize
editable_surface:   # 수정 가능 범위. 예: "src/model/train.py 단일 파일"
frozen_surface:     # 절대 수정 금지. 예: "데이터 준비/평가 코드, 의존성, 측정 스크립트"
budget_per_run:     # 1회 시도의 고정 예산. 예: "wall-clock 5분" / "$0.20"
measure_command:    # 지표 산출 단일 명령. 예: "uv run train.py > run.log 2>&1"
metric_parse:       # run.log 에서 지표 추출. 예: "grep 'val_bpb' run.log | tail -1"
results_log:        # 누적 기록 파일. 예: ".optimize/<run-id>/results.tsv"
stop_condition:     # 종료 조건. 예: "사람이 중단할 때까지" / "50 trial" / "지표<0.9" / "30회 연속 미개선"
tie_breakers:       # 동률/근소차 2차 기준. 예: "코드 단순성 > 메모리 > 가독성"
```

**G0 통과 조건**: 10개 slot 모두 채워짐 + `objective_metric` 단일 스칼라 + `measure_command`가 부수효과 없는 측정만 수행 + `editable_surface ∩ frozen_surface = ∅`.

### Step 1 — Baseline 확보

산출물: `.optimize/<run-id>/results.tsv` (header + baseline 행), baseline commit

1. `editable_surface` / `frozen_surface` / `measure_command` 관련 파일을 모두 읽는다.
2. 전용 작업 브랜치 생성 — `autoloop/<topic>-<date>`.
3. `measure_command`를 **수정 없이 1회 실행**해 baseline 지표 산출. 실행 자체 실패 시 거기서 멈추고 보고.
4. `results.tsv`를 header와 함께 초기화, baseline 행 기록, baseline commit (`baseline: <metric>=<value>`).

`results.tsv` 권장 컬럼:
```
iter	timestamp	metric	delta_vs_best	kept	commit	idea_summary	notes
```

**G1 통과 조건**: baseline measure가 성공적으로 1회 재현 + baseline 값 기록 + baseline commit 존재.

### Step 2 — 단일 변수 trial

각 iteration:

```
1. 가설 1개 선정 (single variable — 무엇이 효과를 냈는지 귀속 가능해야 함)
2. editable_surface 수정 + commit (1 commit = 1 가설)
3. measure_command 실행 (고정 budget — 자체 timeout 권장)
4. metric_parse 로 지표 추출
5. results.tsv 에 1행 append (성공/실패 모두)
```

**G2 통과 조건**: 한 iteration에 변경 변수 1개 + 변경이 commit으로 격리 + measure가 budget 내 종료(timeout 시 실패 기록).

### Step 3 — keep / revert 판정

```
- direction 기준 best 대비 개선 → keep (best 갱신)
- 악화/동률 → git reset --hard <best_commit> 로 롤백
- 근소차(노이즈 수준) → tie_breakers 로 판정
- 비정상값(NaN/crash/0) → 결과 기록하되 미채택 + 원인 1줄 메모
```

**G3 통과 조건**: 판정이 `direction` + `tie_breakers`에 따라 객관적 — "느낌상 좋아 보임" 채택 금지. "0.001 개선 위해 20줄 hacky 코드"는 tie_breaker(단순성)로 기각.

### Step 4 — 로그 + 다음 가설

- 채택 여부와 무관하게 **모든 trial을 results.tsv에 기록** (실패는 탐색 공간을 좁히는 정보).
- 학습 1줄 메모 → 다음 가설 선정. `stop_condition` 미달이면 Step 2로.

**G4 통과 조건**: 실패 trial 누락 없음 + `frozen_surface` 침범 0건 (측정 코드 수정으로 지표 개선 = 부정행위) + `run.log`는 채택 trial만 보존.

### Step 5 — 종료 + 감사 + 요약

산출물: `.optimize/<run-id>/05_summary.md`

`stop_condition` 도달 시:
1. **gaming/overfit 감사** (별도 lens, §2): 지표가 eval에 overfit 됐는지, measure 우회 없었는지, frozen_surface 무결한지 확인.
2. best 대비 baseline 개선 요약 테이블 작성.
3. 유효/무효 방향 3~5줄 학습 요약 (다음 세션 출발점).

요약 테이블:

| 항목 | baseline | best | 개선폭 | best commit |
|---|---|---|---|---|
| `<objective_metric>` | … | … | … | `<sha>` |

**G5 통과 조건**: gaming/overfit 감사 1회 완료 + best commit 명시 + 학습 요약 ≥ 3항목 + best가 baseline 대비 실제 개선(아니면 "개선 없음"을 명시).

---

## 4. Quality Gates (G0 ~ G5 통합)

| Gate | 조건 | 실패 시 처리 |
|---|---|---|
| **G0** | Step 0 — slot 10개 완비 + 단일 스칼라 + 부수효과 없는 measure + surface 분리 | slot 재정의, 루프 진입 차단 |
| **G1** | Step 1 — baseline 재현 + 값 기록 + commit | measure 환경 수정 후 재시도 |
| **G2** | Step 2 — 단일 변수 + commit 격리 + budget 내 종료 | 변경 분할, timeout 설정 |
| **G3** | Step 3 — `direction`+`tie_breakers` 기반 객관 판정 | 주관 채택 롤백, 기준 재적용 |
| **G4** | Step 4 — 실패 포함 전 trial 기록 + frozen_surface 무결 | 누락 보강, 침범 trial 무효화 |
| **G5** | Step 5 — gaming/overfit 감사 + best 요약 + 학습 ≥ 3 | 감사 수행, 요약 보강 |

---

## 5. 산출물 디렉토리 구조

```
.optimize/<run-id>/
├── 00_slots.yaml       # Step 0 — 10 slot 정의
├── results.tsv         # Step 1-4 — 누적 trial 로그 (성공/실패 모두)
├── run.log             # 최근(채택) trial 의 raw 측정 로그
└── 05_summary.md       # Step 5 — best 요약 + 감사 + 학습
```

> commit 정책: `00_slots.yaml` / `05_summary.md` / `results.tsv`는 외부 보고 대상이면 commit. trial별 코드 변경은 작업 브랜치의 commit 이력에 자연히 남으므로 best commit sha만 요약에 인용. `run.log`는 대용량이면 .gitignore.

---

## 6. Anti-patterns

- ❌ **Metric gaming** — measure/eval 코드를 수정해 지표를 개선. `frozen_surface` 침범. G4 차단, G5 감사 재확인.
- ❌ **Multi-variable trial** — 한 iteration에 여러 변경 → 효과 귀속 불가. G2 차단. 1 commit = 1 가설.
- ❌ **Eval overfit** — 동일 측정셋에 과적합해 일반화 실패. G5 감사에서 held-out/재측정으로 확인.
- ❌ **노이즈 채택** — 측정 분산 내 차이를 개선으로 오인. `tie_breakers` + (비결정적이면) 다회 측정으로 방어. 비결정 측정은 애초에 §1.2 bypass.
- ❌ **사람에게 매 trial 확인 요청** — 무인 위임이 전제. `stop_condition` 전엔 멈추지 않는다.
- ❌ **깨진 접근 과디버깅** — 근본적으로 깨진 가설을 2회 이상 붙들기. 빠르게 롤백 후 다른 가설로.
- ❌ **실패 trial 미기록** — 실패도 탐색 공간 정보. G4 차단.
- ❌ **숨은 비용 무시** — 지표만 보고 복잡도/메모리/가독성 폭증 방치. `tie_breakers`에 2차 비용 명시 의무.
- ❌ **부수효과 measure** — measure_command에 배포/과금/데이터변경 포함. G0 차단.

---

## 7. 시나리오 예시 — Mini run

### 시나리오: 추론 서버 p95 latency 를 야간에 자동 최적화

**Step 0 (slots)**: `objective_metric=p95 latency(ms)`, `direction=minimize`, `editable_surface="serving/config.yaml + serving/batcher.py"`, `frozen_surface="모델 가중치, 벤치 스크립트, 데이터"`, `budget_per_run="고정 부하 90초 벤치"`, `measure_command="python bench.py --dur 90 > run.log"`, `metric_parse="grep 'p95_ms' run.log | tail -1"`, `stop_condition="40 trial 또는 20회 연속 미개선"`, `tie_breakers="처리량 유지 > 코드 단순성"`.

**Step 1**: baseline 벤치 1회 → p95 = 210ms 기록 + commit.

**Step 2-4 (반복)**:
- trial 1: max_batch 8→16. p95 195ms → keep.
- trial 2: timeout 5ms→10ms. p95 240ms → revert.
- trial 3: dynamic batching 도입. p95 168ms → keep.
- trial 4: prefetch thread +2. p95 167ms (Δ<1, 노이즈) + 코드 복잡↑ → tie_breaker(단순성)로 revert.
- … (frozen_surface인 벤치 스크립트는 한 번도 수정 안 함)

**Step 5**: best = trial 3 (p95 168ms, baseline 대비 -20%). gaming 감사 — 벤치 스크립트/부하 무결 확인, 처리량 baseline 유지 확인. 학습: "batch size↑·dynamic batching이 주효, timeout·prefetch는 무효". → 이후 이 config를 `experiment-design-template`로 정식 부하 분포에서 검증.

---

## 8. 참고

### 8.1 내부 (라이브러리 내)

- `experiment-design-template.md` §3 (Step 0-6), §4 (Gates) — 본 template으로 찾은 best config를 *순차*로 통계 검증할 때 연결. 탐색(본 template) vs 검증(experiment) 경계. `[VERIFIED:static prompts/prompt-composer-system/components/experiment-design-template.md]`
- `agent-role-dictionary.md` §0 (lens 분리), §5.8 `ml-researcher`, §5.10 `systems-researcher` — §2 감사 lens 출처. `[ASSUMPTION 위치: prompts/prompt-composer-system/agent-role-dictionary.md §5 검증 방법: grep ml-researcher/systems-researcher 확인]`
- `multi-agent-analysis-template.md` — 자동 탐색(본 template) vs 대안 비교 결정(multi-agent)의 경계. `[VERIFIED:static prompts/prompt-composer-system/components/multi-agent-analysis-template.md]`
- `verify` 스킬 — 변경이 사람 기준으로 의도대로 동작하는지 검증(주관) vs 본 template의 자동 스칼라 최적화. `[VERIFIED:static prompts/commands/verify.md]`

### 8.2 외부

- karpathy/autoresearch `program.md` — 본 template의 고정 budget / single-file scope / keep-or-revert / NEVER-STOP 자율 루프 원형. `[ASSUMPTION canonical URL: https://github.com/karpathy/autoresearch 검증 방법: web fetch + tier=community(개인 repo) 확인]`
- Andrej Karpathy, "A Recipe for Training Neural Networks" (2019) — single-variable / baseline-first 원칙의 영감. `[ASSUMPTION canonical URL: http://karpathy.github.io/2019/04/25/recipe/ 검증 방법: web fetch + tier=community 확인]`

> ⚠️ 외부 reference의 URL은 라이브러리 작성 시점(2026-05-20)에 web fetch 미수행(autoresearch repo는 본 세션 fetch 확인). 첫 운영 시 composer Phase 5 또는 `evidence-checker` role에서 `[VERIFIED:webfetch <tier> <URL> accessed:<date>]`로 격상 의무.

---

## 부록 A. 무인 실행 안전장치

- measure_command에 자체 timeout — 행(hang) 시 해당 trial 실패 처리.
- 외부 비용/배포가 발생하는 명령은 measure에서 제외 (부수효과 없는 측정만).
- N회 연속 미개선 시 자동 종료 가드를 `stop_condition`에 포함.
- 디스크/로그 관리: `run.log`는 매 trial 덮어쓰고 채택 trial만 보존.
- 비결정적 측정이면 본 template 부적합 (§1.2) — 굳이 쓰면 trial당 다회 측정 + 평균/CI로 노이즈 방어.
