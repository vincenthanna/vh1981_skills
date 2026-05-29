# Speckit Spec Generation

> **무엇**: `github/spec-kit`(이하 speckit) CLI와 그 agent slash command 세트를 활용해 task의 spec/plan/tasks 등 **구조화 산출물**을 생성·갱신하는 component.
> **용도**: spec.B=Generation에서 코드 작성 *직전*에 기계 처리 가능한 spec(`specs/<feature>/spec.md|plan.md|tasks.md`)을 만들고 곧바로 `/speckit.implement`에 이어붙이고 싶을 때.
> **시리즈 위치**: composer Phase 2~5 — router decision tree §2 `Generation` 분기 하위, spec.A에 "spec / plan / tasks / SDD / spec-driven / speckit" 키워드 + spec.G=REVERSIBLE일 때 활성화. `rfc-writing-template`과 **상호 배타** (자유 형식 vs 구조화 spec).
>
> 산출물: `specs/<feature>/{spec,plan,tasks}.md` + (선택) `.specify/memory/constitution.md` 의 path 목록 + 각 산출물의 게이트 통과 결과.
> 출처: `[VERIFIED:webfetch https://github.com/github/spec-kit @2026-05-26]`
> Changelog: 1.0 초안.

---

## 0. Router 등록 metadata

| 항목 | 값 |
|---|---|
| component name | `speckit-spec-generation.md` |
| trigger signals | spec.B = Generation **AND** spec.A에 `spec / plan / tasks / SDD / spec-driven / speckit` 키워드 **AND** spec.G = REVERSIBLE |
| inputs | feature description(자연어), 기존 `specs/<feature>/spec.md`(선택 — 갱신 모드), repo root 경로 |
| outputs | `specs/<feature>/spec.md` / `plan.md` / `tasks.md`(선택) 의 path 목록 + 각 산출물에 대한 G0–G5 통과 표 |
| cost (rough tokens) | Low (~1.5k 발췌 / ~5–6k full; speckit slash command 호출 자체는 사용자 세션 비용) |
| 충돌 가능 component | `rfc-writing-template.md`(자유 형식 vs 구조화 spec — **상호 배타**, 동시 활성 금지) |
| version | 1.0 |
| owner | prompt-composer-system 유지자 |
| layer | **domain content (planning / SDD)** — CLAUDE.md "조합 인프라(5) / 분석 컨텐츠(2) / domain content" 3축 분류. router §1.1 metadata 정의 참조. |

---

## 1. 사용 시점 / 비사용 시점

### 1.1 사용 시점
- spec.B = Generation **AND** 구현 직전 단계 **AND** 결과물이 다른 agent/도구가 입력으로 받을 `spec.md / plan.md / tasks.md` 여야 함.
- speckit의 `/speckit.implement`로 곧바로 연결할 의도가 있는 경우.
- feature 1개당 산출물 1세트 (다중 feature는 후보별로 본 component를 1회씩 — self_upgrade "1회 1대상" 정신).

### 1.2 비사용 시점 (bypass)
- 자유 형식 설계 합의 문서가 목적 → `rfc-writing-template`.
- 1회성 코드 변경 → bypass, direct prompt.
- speckit 미설치 + 사용자가 설치 거부 → bypass + 사용자에게 사유 보고 후 종료.

---

## 2. 작업 모델 — speckit surface

`[VERIFIED:webfetch https://github.com/github/spec-kit @2026-05-26]`

### 2.1 CLI 진입점
- 이름: `specify` (패키지명 `specify-cli`).
- 설치 (사용자 환경 mutation — 본 component는 **문서화만, 실행 금지**):
  - 1순위 (README 권장): `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z` — `@vX.Y.Z`는 릴리스 태그.
  - 2순위 `[ASSUMPTION pipx alternative — README 본문 미확인, 검증방법: webfetch README 재확인]`: `pipx install --spec git+https://github.com/github/spec-kit.git specify-cli`.
- CLI 서브커맨드(README 기준): `init <project>`, `check`, `integration list`, `extension search/add`, `preset search/add`. **로컬 설치 버전에 따라 `init`/`check` 만 노출되는 경우 있음** — 항상 `specify --help`로 실측.

### 2.2 Agent slash commands (실제 spec/plan/tasks 작업의 본체)
- 핵심: `/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`.
- 선택: `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`, `/speckit.taskstoissues`.
- ⚠️ slash command는 **Claude Code 등 에이전트 세션 내부에서 사용자가 입력**해야 동작. `specify init`은 템플릿·constitution을 부트스트랩하는 1회성 작업이고, 실제 산출물은 slash command가 만든다. 본 component는 slash command를 *직접 호출하지 않는다* — 사용자에게 안내만 한다.

### 2.3 표준 산출물 경로
```
.specify/
├── memory/constitution.md       ← /speckit.constitution 산출
├── scripts/bash/                ← 템플릿 스크립트
└── templates/
specs/<feature-name>/
├── spec.md                      ← /speckit.specify
├── plan.md                      ← /speckit.plan
├── tasks.md                     ← /speckit.tasks
├── data-model.md                ← /speckit.plan 부속
├── quickstart.md
├── research.md
└── contracts/
```

---

## 3. 절차 (Step 0 ~ Step 5)

> 각 Step의 통과 조건과 실패 처리는 §4 SSOT 표를 참조 (조건 중복 금지 — drift 방지).

### Step 0 — Detect
- read-only 명령으로 speckit 설치 여부 + 사용 가능 서브커맨드 실측:
  ```bash
  which specify || echo "not installed"
  specify --help 2>&1 | head -30
  ```
- **Gate**: G0 (조건·실패 처리는 §4 SSOT).

### Step 1 — (필요 시) Install 안내
- 미설치 시 §2.1의 1·2순위 명령을 **문서로만 제시**. 본 component는 실행하지 않는다.
- 사용자가 거부하면 bypass로 전환 후 종료.
- **Gate**: G1 (조건·실패 처리는 §4 SSOT).

### Step 2 — Bootstrap 점검 / 기존 spec 식별
- 현재 repo에 `.specify/` 디렉토리 존재 여부 확인. 없으면 사용자에게 `specify init <project>` 실행을 안내(별도 디렉토리 권장).
- 입력의 "기존 `specs/<feature>/spec.md`(선택)"가 주어지면 *갱신 모드*로 진입 — feature 디렉토리·필수 섹션을 미리 확인하고 어느 부분을 보강할지 사용자와 합의.
- **Gate**: G2 (조건·실패 처리는 §4 SSOT).

### Step 3 — `/speckit.specify` 실행 안내 + 산출물 검증
- spec.A Purpose를 1–2 paragraph 자연어로 정리해 사용자에게 `/speckit.specify <description>` 입력 안내.
- 사용자 실행 후 `specs/<feature>/spec.md` 생성 확인. 모호한 부분 있으면 `/speckit.clarify` 권장.
- 산출물 path + 필수 섹션(존재 여부)을 표로 출력.
- **Gate**: G3 (조건·실패 처리는 §4 SSOT).

### Step 4 — (선택) `/speckit.plan` → `/speckit.tasks`
- spec.md G3 통과 후에만 `/speckit.plan` 안내. plan G4 통과 후에만 `/speckit.tasks` 안내. 단계 우회 금지.
- (선택) `/speckit.analyze`로 cross-artifact 일관성 1회 점검 권장.
- **Gate**: G4 (조건·실패 처리는 §4 SSOT).

### Step 5 — (선택) composer 재연결 / 종료
- 생성된 spec.md를 `../builder/task-spec-template.md`에 다시 매핑할지 결정. 매핑이 합당하면 1단락 가이드 첨부 후 composer Phase 1로 안내. 그렇지 않으면 `/speckit.implement`로 사용자가 직접 이행, 본 component 종료.
- 종료 시 outputs(산출물 path 목록 + G0–G5 통과 표)을 한 메시지로 정리.
- **Gate**: G5 (조건·실패 처리는 §4 SSOT).

---

## 4. Quality Gates (G0 ~ G5) — SSOT

> 이 표가 Gate 정의의 **단일 출처(SSOT)**다. §3 각 Step은 해당 Gate를 포인터로만 참조한다.

| Gate | 조건 | 실패 시 처리 |
|---|---|---|
| **G0** | Step 0 — `specify --help`가 종료코드 0 + `init` 서브커맨드 출력에 존재 | 미설치로 판정 → G1으로 |
| **G1** | Step 1 — 설치 명령은 **문서화만**(본 component가 직접 실행 0건) + 사용자가 설치 의사 명시(yes/no) | 사용자 거부 → bypass + 사유 보고 후 종료 |
| **G2** | Step 2 — `.specify/` 존재 OR 사용자에게 `specify init` 실행 안내 완료. 갱신 모드면 기존 `specs/<feature>/spec.md` 경로 확인 + 사용자 동의 | bootstrap 재안내 또는 갱신/신규 결정 재확인 |
| **G3** | Step 3 — `specs/<feature>/spec.md` 파일 존재 + 사용자가 내용 확인 완료 + (필요시) `/speckit.clarify` 통과 | spec 재작성 또는 clarify 추가 round |
| **G4** | Step 4 — plan.md / tasks.md 생성한 경우 각 단계 사이 사용자 확인 게이트 통과 + (선택) `/speckit.analyze` 결과 critical 0건 | plan→tasks 진행 중단, 이전 산출물 보강 |
| **G5** | Step 5 — 산출물 path 목록 + 각 Gate 통과 결과 출력 완료 + Reversibility 명시(신규 디렉토리=REVERSIBLE / 기존 파일 덮어쓰기=COSTLY-TO-REVERSE) | 출력 보강 후 재제출 |

---

## 5. 산출물 디렉토리 구조

`/speckit.specify` 등 slash command가 만드는 표준 경로(§2.3) 그대로 유지. 본 component가 별도 디렉토리를 강제하지 않는다.

> commit 정책: speckit 산출물(`specs/<feature>/*.md`)은 사용자가 통상 PR 단위로 commit. 본 component는 commit을 직접 수행하지 않는다.

---

## 6. Anti-patterns

- ❌ **사용자 동의 없이 speckit 임의 설치** — 환경 mutation. G1 차단.
- ❌ **`rfc-writing-template`과 동시 활성화** — 자유 형식과 구조화 spec 중복 작성, over-scoping. router §2 분기에서 키워드 명시적 분리.
- ❌ **spec 직후 plan/tasks skip하고 바로 `/speckit.implement`** — 단계 우회. G4 차단.
- ❌ **slash command를 본 component가 직접 호출 시도** — slash command는 사용자 에이전트 세션 입력 이벤트. 본 component는 *안내만*.
- ❌ **기존 `specs/<feature>/spec.md` 무단 덮어쓰기** — COSTLY-TO-REVERSE. G2에서 갱신 동의 필수.

---

## 7. 시나리오 (Mini E2E)

> 시나리오: "새 CLI 기능 `vh1981 export` 추가 — spec → plan → tasks → implement."

1. **Step 0/G0**: `which specify` → 설치됨. `specify --help` → `init/check`만 노출(로컬 버전). G0 통과.
2. **Step 2/G2**: 현재 repo에 `.specify/` 없음 → 사용자에게 별도 워크 디렉토리에서 `specify init export-feature` 실행 안내. 사용자 완료 보고 후 G2 통과.
3. **Step 3/G3**: 사용자가 `spec.A` Purpose를 2-paragraph로 정리한 description으로 `/speckit.specify` 실행. `specs/export-feature/spec.md` 생성 확인. clarify 1 round 후 G3 통과.
4. **Step 4/G4**: 사용자가 `/speckit.plan` → `plan.md` + `data-model.md` 생성. `/speckit.analyze` critical 0건. 이어서 `/speckit.tasks` → `tasks.md`. G4 통과.
5. **Step 5/G5**: 산출물 path 3건 + G0–G4 통과표 + Reversibility=REVERSIBLE(신규 디렉토리) 출력 후 종료. 사용자가 `/speckit.implement` 또는 composer 재연결 결정.

---

## 8. 참고

- speckit upstream: `https://github.com/github/spec-kit` `[VERIFIED:webfetch @2026-05-26]`
- 인접 component(영역 다름, 상호 배타): `components/rfc-writing-template.md`
- 본 component 거버넌스: repo root `self_upgrade.md` (1회 1대상, 사람 승인 게이트), changelog: `self_upgrade-changelog.md`
- 본 component 등록 ledger: `component-discovery-ledger.md` (id=`SKIT-001`)
