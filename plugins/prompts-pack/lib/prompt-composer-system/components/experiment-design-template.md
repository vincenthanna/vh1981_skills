# Experiment Design Template

> **무엇**: ML/systems/HCI 실험을 ml-researcher×proposer + ml-researcher×devils-advocate lens로 설계·실행·분석하는 워크플로우 template.
> **용도**: 단일 가설을 통계적으로 검증해야 할 때 활성화.
> **시리즈 위치**: composer Phase 4 (Assembly). `multi-agent-analysis-template.md`가 다수 *대안* 비교라면 본 template은 단일 *가설* 검증 — 둘 다 켜면 over-scoping이므로 분리 사용.
>
> 산출물: research question → hypothesis → 실험 protocol → 결과 분석 → 재현 가능한 write-up.

---

## 0. Router 등록 metadata

| 항목 | 값 |
|---|---|
| component name | `experiment-design-template.md` |
| trigger signals | spec.B = Analysis + spec.L = `ml-researcher` (또는 `systems-researcher`/`hci-researcher`) + 실험/baseline/ablation 키워드 |
| inputs | research question, 가용 dataset/환경, 비교 baseline 후보, 측정 metric 후보 |
| outputs | 실험 protocol 문서 + ablation table + 결과 분석 + 재현 manifest |
| cost (rough tokens) | Medium (~2k 발췌 / ~12k full) |
| 충돌 가능 component | `multi-agent-analysis-template.md` (대안 비교 vs 가설 검증 — 둘 다 활성 시 over-scope), `code-review-rubric.md` (영역 다름) |
| version | 1.0 |
| owner | prompt-composer-system 유지자 |
| layer | **domain content (analysis / 가설 검증)** — CLAUDE.md "조합 인프라(5) / 분석 컨텐츠(2) / domain content" 3축 분류. router §1.1 metadata 정의 참조. |

> **trigger 분기**: router §2 step 2에서 `B = Analysis` AND `L 1순위 = ml/systems/hci-researcher` 인 경우 본 template 활성화. spec.C topic_count 가 N개 baseline 비교이면 multi-agent-template과 본 template *순차* 사용 (multi-agent로 후보 선정 → 본 template으로 검증).

---

## 1. 사용 시점 / 비사용 시점

### 1.1 사용 시점

- 검증할 **단일 hypothesis**가 있고 측정 가능한 결과 도출 필요.
- 결과를 *논문 / 외부 보고 / repro 가능한 형태*로 남겨야 함.
- 다음 중 1개 이상 해당:
  - ML 모델 변경의 효과 검증 (architecture, training data, hyperparameter)
  - 시스템 변경의 throughput/latency 측정
  - 새 UI 패턴의 usability 측정 (HCI)
- spec.J Confidence Required ≥ Medium.

### 1.2 비사용 시점 (bypass)

- 빠른 prototype 검증 — 정성적 inspection으로 충분, 통계 없이 진행.
- 다수 후보 비교 (5개 모델 중 1개 채택 등) → `multi-agent-analysis-template.md` 사용 후 winner 만 본 template으로 검증.
- 결과가 *사용자 결정*에 영향 없음 (지식 만족 only) — overhead 큼.
- Pilot study without IRB / 데이터 동의 부재 (HCI) — 윤리 차단.

---

## 2. 작업 모델 (Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│ Researcher (메인 세션)                                       │
│  phases: design → execute → analyze → write-up               │
│  - hypothesis 정의 + falsifiability 검증                     │
│  - baseline / ablation 결정                                  │
│  - 실험 실행 (또는 dispatch)                                 │
│  - 결과 종합 + 재현 manifest 작성                            │
└─────────────────────────────────────────────────────────────┘
        │ (proposer 자세로 design)                ▲ devils-advocate 자세로 review
        ▼                                         │
┌──────────────────────────────────────────────────────────┐
│  Hypothesis devil's advocate (별도 LLM 또는 reviewer)    │
│  (agent role: ml-researcher × devils-advocate)           │
│  - 실험이 무의미한 시나리오 가설 생성                     │
│  - 측정 metric의 proxy / intrinsic 한계 지적              │
│  - confound / leak 후보 식별                              │
└──────────────────────────────────────────────────────────┘
```

> **Lens 분리 원칙** (`agent-role-dictionary.md §0`): proposer는 실험을 *설계*하고, devil's advocate는 *깨는 시나리오*를 생성. 같은 사람/LLM이 둘 다 하면 anchoring — 별도 agent로 분리.

---

## 3. 절차 (Step 0 ~ Step 6)

### Step 0 — Research question 정의

산출물: `.experiments/<exp-id>/00_question.md`

```markdown
## Research question
<한 문장으로 — "X가 Y에 어떤 영향을 미치는가?" 형태>

## 왜 중요한가
<현재 알려진 것 + 본 실험이 줄 새 정보>

## 측정 가능성 (falsifiability check)
- 이 질문은 measurable 결과로 답할 수 있는가? <yes/no + 이유>
- 어떤 결과가 나오면 "yes / no / inconclusive" 인가?
```

**Gate**: G0 (조건·실패 처리는 §4 SSOT).

### Step 1 — Baseline 선정

산출물: `.experiments/<exp-id>/01_baselines.md`

```markdown
## Baseline list

| Baseline | 선정 이유 | 출처 (paper / repo) | 평가 시점 |
|---|---|---|---|
| B1: <이름> | <왜 비교 대상> | <citation 또는 path> | <date / version> |
| B2: ... | ... | ... | ... |

## 비교 fair-ness check
- 같은 dataset / 같은 환경 / 같은 metric 사용? <yes/no + 차이 명시>
- baseline 구현의 *원본 저자 결과*와 본 구현의 차이는? <reproduction gap>
```

**Anti-pattern**: weak baseline 선택 (자기 안이 잘 보이도록). `agent-role-dictionary §5.8 ml-researcher` "baseline 적절성" 룰 위반.

**Gate**: G1 (조건·실패 처리는 §4 SSOT).

### Step 2 — Hypothesis + 측정 metric 결정

산출물: `.experiments/<exp-id>/02_hypothesis.md`

```markdown
## Primary hypothesis (H1)
<단일 가설 — "intervention X가 metric M을 Δ만큼 개선"

## Null hypothesis (H0)
<반대 가정>

## 측정 metric

### Primary metric (1개)
- 이름: <metric>
- 정의: <수식 / 측정 방법>
- 한계: <proxy인지 / intrinsic인지 / known confound>

### Secondary metric (선택, ≤ 3)
- ...

### 측정 단위
- sample size: <N>
- statistical test: <t-test / Wilcoxon / bootstrap CI / ...>
- significance threshold: <α = 0.05 또는 prior-justified value>
- effect size: <기대값 + 어떻게 정당화되었나>

## Devil's advocate review (별도 agent)
- 이 metric으로 H1이 *true*인데 *측정 실패*할 시나리오는?
- 이 metric으로 H1이 *false*인데 *유의*하게 나올 시나리오는?
- confound 후보 list: <data leak / spurious correlation / population shift / ...>
```

**Gate**: G2 (조건·실패 처리는 §4 SSOT).

### Step 3 — Ablation 설계

산출물: `.experiments/<exp-id>/03_ablation.md`

```markdown
## Ablation matrix

| 조건 | intervention 활성 | confound 변수 | 예상 결과 |
|---|---|---|---|
| C0 (baseline) | ✗ | controlled | metric = baseline 값 |
| C1 (intervention) | ✓ | controlled | metric = baseline + Δ |
| C2 (ablation: X 제거) | partial | controlled | <if X 핵심이면 baseline 근접> |
| C3 (sanity: random) | random | uncontrolled | <random 수준> |

## Coverage check
- 모든 핵심 구성 요소가 ablation 변수로 등장? <yes/no>
- 각 ablation 의 *예상 결과*가 명시? (post-hoc rationalization 차단)
```

**Gate**: G3 (조건·실패 처리는 §4 SSOT).

### Step 4 — 실험 실행

산출물: `.experiments/<exp-id>/04_runs/`

```
04_runs/
├── manifest.json       # 실행 환경 (commit hash, seed, hw, sw versions)
├── C0/result.json
├── C1/result.json
├── C2/result.json
└── C3/result.json
```

manifest.json 의무 필드:
```json
{
  "exp_id": "<id>",
  "code_commit": "<git sha>",
  "data_version": "<dataset version>",
  "hardware": "<gpu type / cpu / mem>",
  "software": {"python": "...", "pytorch": "...", ...},
  "seed": [<seed list, 최소 3개>],
  "run_dates": ["<ISO>"],
  "conditions_run": ["C0", "C1", "C2", "C3"]
}
```

**Gate**: G4 (조건·실패 처리는 §4 SSOT).

### Step 5 — 결과 분석

산출물: `.experiments/<exp-id>/05_analysis.md`

```markdown
## Result table

| 조건 | Primary metric (mean ± CI) | Secondary | p-value vs C0 | Effect size |
|---|---|---|---|---|
| C0 | <값> ± <CI> | ... | — | — |
| C1 | <값> ± <CI> | ... | <p> | <Cohen's d / 등> |
| C2 | ... | ... | ... | ... |

## Hypothesis verdict
- H1: <accept / reject / inconclusive>
- 근거: <p-value + effect size + CI 해석>
- 다중 비교 보정 적용: <Bonferroni / FDR / 등 + α 조정 결과>

## Devil's advocate review
- 결과를 *깨는* alternative 가설: <list>
- 각각의 가능성과 추가 검증 필요 여부

## Confound / leak 후보 재검토
- Step 2 에서 식별된 confound 가 controlled 됐나 사후 확인
- 새로 발견된 leak: <list>
```

**Gate**: G5 (조건·실패 처리는 §4 SSOT).

### Step 6 — Write-up + 재현 manifest

산출물: `.experiments/<exp-id>/06_writeup.md` + `99_repro.md`

```markdown
# 06_writeup.md

## TL;DR
<2-3 줄: question + 답 + 한계>

## 1. Question + motivation
## 2. Method (baselines + intervention + ablation)
## 3. Results (table + 그래프 reference)
## 4. Discussion (limitation + threat to validity + 다음 작업)
## 5. Reproduction
- 위치: `.experiments/<exp-id>/`
- 1-line repro: `<commands>`

# 99_repro.md

## Step-by-step repro
1. `git checkout <commit>`
2. `<setup commands>`
3. `<run commands>`
4. expected output: <hash 또는 metric range>
```

**Gate**: G6 (조건·실패 처리는 §4 SSOT).

---

## 4. Quality Gates (G0 ~ G6 통합) — SSOT

> 이 표가 Gate 정의의 **단일 출처(SSOT)**다. §3 각 Step은 해당 Gate를 포인터로만 참조한다 (조건 중복 금지 — drift 방지).

| Gate | 조건 | 실패 시 처리 |
|---|---|---|
| **G0** | Step 0 — question 단일 + falsifiable + 사용자 결정 영향 명시 | Step 0 재작성 |
| **G1** | Step 1 — baseline 의 fair-ness check + reproduction gap 명시 | weak baseline 교체 |
| **G2** | Step 2 — primary metric 1개 + statistical test 선택 정당화 + devils-advocate review | metric / test 재선정 |
| **G3** | Step 3 — ablation ≥ 2 + 예상 결과 사전 명시 | post-hoc 단정 차단, ablation 추가 |
| **G4** | Step 4 — manifest 완전 + seed ≥ 3 + 환경 동일 | 재실행 |
| **G5** | Step 5 — mean + CI + p + effect size 4종 + devils-advocate review + 다중 비교 보정 | 분석 재실행 |
| **G6** | Step 6 — TL;DR + limitation + repro 가능 | writeup 보강 |

---

## 5. 산출물 디렉토리 구조

```
.experiments/<exp-id>/
├── 00_question.md
├── 01_baselines.md
├── 02_hypothesis.md
├── 03_ablation.md
├── 04_runs/
│   ├── manifest.json
│   ├── C0/result.json
│   ├── C1/result.json
│   ├── C2/result.json
│   └── C3/result.json
├── 05_analysis.md
├── 06_writeup.md
└── 99_repro.md
```

> commit 정책: `manifest.json` 의 `code_commit` / `data_version` 은 의무 commit. `04_runs/*/result.json` 은 외부 보고 대상이면 commit, 내부 스냅샷이면 .gitignore.

---

## 6. Anti-patterns

- ❌ **Weak baseline** — 자기 안이 잘 보이도록 약한 baseline. `agent-role-dictionary §5.8` 위반. 1순위 baseline은 *공식 SOTA* 또는 *팀 prior best*.
- ❌ **Post-hoc rationalization** — Step 3 의 *예상 결과 사전 명시* 가 없으면 결과 보고 "이게 사실 의도였어" 식 합리화 가능. G3 가 차단.
- ❌ **Single-seed run** — random seed 1개로 결과 보고. variance 추정 불가. G4 차단.
- ❌ **Primary metric 다중 선택** — "primary metric 3개"는 사실상 fishing. 1개로 commit, 나머지는 secondary.
- ❌ **Confound check skip** — Step 2 devils-advocate review에서 confound 식별 후 Step 5 사후 재검토 누락. silent failure.
- ❌ **Devil's advocate를 본인이 수행** — anchoring. 별도 LLM/사람.
- ❌ **Effect size 없이 p-value만 보고** — statistical significance ≠ practical significance. 둘 다 의무.
- ❌ **Repro 어려운 hw 의존** — "A100 1대에서만 돌아감" 가능하지만 manifest 에 명시 의무. third-party 가 modify 가능한 형태로.
- ❌ **HCI 윤리 step 누락** — 사용자 연구이면 IRB / informed consent / data retention 정책 명시. (HCI domain만 해당)

---

## 7. 시나리오 예시 — Mini run

### 시나리오: LLM에 step-by-step prompting을 추가하면 reasoning accuracy 가 개선되는가?

**Step 0**: question = "GSM8K math problem 에서 step-by-step prompting이 zero-shot 대비 accuracy 를 5%+ 개선하는가?" Falsifiable (accuracy 가 측정 가능, Δ < 5% 이면 reject).

**Step 1**: baseline = (a) zero-shot prompting, (b) 5-shot example prompting (no step-by-step). 둘 다 동일 model로.

**Step 2**: H1 = step-by-step Δ ≥ 5%, H0 = Δ < 5%. metric = exact-match accuracy on GSM8K test (1319 samples). test = paired bootstrap CI (95%). devils-advocate: "step-by-step이 단순히 token 수를 늘려 hallucination 감소시키는 confound" 식별.

**Step 3**: ablation = (C0) zero-shot, (C1) step-by-step, (C2) "verbose output" (token 수만 늘림 — confound 분리), (C3) random output (sanity).

**Step 4**: manifest 작성 + 3 seed + 동일 model/temperature.

**Step 5**: 결과 — C0=18%, C1=35%, C2=22%, C3=2%. C1-C0=17% (CI 14-20%, p<0.001, Cohen's d=0.8). C2 effect로 confound 부분 설명 (verbose 만으로 4% 개선) → 실제 step-by-step 효과는 ~13%. **H1 accept** (Δ ≥ 5%).

**Step 6**: writeup 의 limitation = "GSM8K 한정, math reasoning 만, smaller model 효과 다를 수 있음".

---

## 8. 참고

### 8.1 내부 (라이브러리 내)

- `agent-role-dictionary.md` §5.8 `ml-researcher`, §5.10 `systems-researcher`, §5.11 `hci-researcher` — 본 template의 lens 출처. `[VERIFIED:static prompts/prompt-composer-system/agent-role-dictionary.md:548,596,618]`
- `multi-agent-analysis-template.md` §2.1 evidence tagging, §2.3 confidence — 본 template의 G2/G5 결과 보고 형식의 기반. `[VERIFIED:static prompts/prompt-composer-system/multi-agent-analysis-template.md]`
- `../builder/prompt-evaluation-rubric.md` §5 메타 평가 — 본 template으로 실행한 실험들의 누적 품질을 분기별 검토. `[VERIFIED:static prompts/prompt-composer-system/builder/prompt-evaluation-rubric.md]`

### 8.2 외부 (도메인별)

#### ML
- Andrej Karpathy, "A Recipe for Training Neural Networks" (2019) — 본 template의 baseline-first / single-seed 금지 / repro manifest 원칙의 영감. `[ASSUMPTION canonical URL: http://karpathy.github.io/2019/04/25/recipe/ 검증 방법: web fetch + tier=community(개인 블로그) 확인]`
- HuggingFace "Evaluate" library / Eval card spec — primary/secondary metric 분리 및 measurement metadata의 산업 표준. `[ASSUMPTION canonical URL: https://huggingface.co/docs/evaluate/ 검증 방법: web fetch + tier=vendor 확인]`

#### Systems
- USENIX / SOSP / OSDI "Artifact Evaluation" 가이드라인 — Step 4 manifest.json / Step 6 repro 의 산업 패턴 (DOI + functional/reproduced badge). `[ASSUMPTION canonical URL: https://sysartifacts.github.io/ 또는 USENIX AE 사이트 검증 방법: web fetch + tier=community 확인]`

#### HCI
- Lazar, Feng, Hochheiser, *Research Methods in Human-Computer Interaction* (Wiley, 2nd ed. 2017) — Step 0 falsifiability / Step 2 statistical test 정당화 / Step 5 confound 처리의 교과서. `[ASSUMPTION ISBN: 978-0128053904 검증 방법: 출판사 사이트 또는 Google Books 확인 tier=official]`
- ACM SIGCHI Research Ethics — Step 0의 IRB / informed consent 의무 (HCI domain). `[ASSUMPTION canonical URL: https://sigchi.org/community/ethics/ 검증 방법: web fetch + tier=official 확인]`

> ⚠️ 외부 reference의 URL/ISBN은 라이브러리 작성 시점(2026-05-19)에 web fetch 미수행. 첫 운영 시 composer Phase 5 P5 단계 또는 `evidence-checker` role에서 `[VERIFIED:webfetch <tier> <URL> accessed:<date>]`로 격상 의무.
