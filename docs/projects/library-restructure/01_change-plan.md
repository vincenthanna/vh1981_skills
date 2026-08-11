# Component 라이브러리 재구성 변경 계획

이 문서는 `prompts/prompt-composer-system/components/`의 component들을 composer 경유 없이도 호출할 수 있게 만드는 변경 계획이다. 결론은 component를 "더 범용적으로" 고쳐 쓰는 것이 아니라, **입구를 composer 하나에서 둘로 늘리고 composer를 라이브러리의 정문에서 소비자 중 하나로 강등**하는 것이다. Phase 1은 완료했고 배포 경계가 확정됐다. 다음 할 일은 Phase 2의 code-review SSOT 통합이며, 그 전에 승인이 필요한 변경이 하나 있다.

승인 대기 항목은 PR 리뷰 진입점의 위치다. 라이브러리와 같은 plugin 안에 있어야 참조가 가능하므로 `plugins/vh1981/skills/pr-review/`에서 `plugins/prompts-pack/skills/pr-review/`로 옮긴다. 나머지 대기 중인 결정은 `/pr-audit`과 새 진입점을 합칠지 분리할지, 62KB `multi-agent-analysis-template.md`를 어디까지 쪼갤지 두 가지다. 각 항목의 제안 기본값은 "대기 중인 결정" 절에 있다.

## 문제 정의

component 라이브러리가 닫혀 있다. `prompts/prompt-composer-system/` 내부와 `plugins/prompts-pack/commands/build_prompt.md`를 제외하면, component를 참조하는 실행 경로가 repo 안에 존재하지 않는다.

원인은 두 가지다. 첫째, component의 trigger가 `spec.B = Review`, `spec.L = security-researcher` 처럼 **Task Spec 필드로만 기술**돼 있어서 Phase 1(spec 작성)과 Phase 2(router)를 통과하지 않으면 도달할 수 없다. 둘째, composer가 3세션 프로토콜(compose, execute, evaluate를 각각 다른 conversation에서 수행)이라 보상이 세션 전환 2번 뒤에 온다. `prompts/prompt-composer-system/CLAUDE.md`의 Invariant 1이 이 분리를 강제한다.

실사용 데이터가 이를 뒷받침한다.

```
.specs/  (2026-05-21 ~ 2026-07-24)
  task-id 6개, 그중 .result.md 존재 1개
```

compose에서 evaluate까지 루프가 닫힌 것은 1건이다. 나머지 5건은 composed prompt를 만든 뒤 실행 단계로 이어지지 않았다.

가장 뚜렷한 증상은 code-review 자산의 분열이다. 서로를 참조하지 않는 세 자산이 같은 일을 한다.

| 파일 | 규모 | 도달 방법 | 내용 |
|---|---|---|---|
| `plugins/prompts-pack/agents/code-reviewer.md` | 255줄 | Agent 도구 자동 라우팅 | 근거 기반 검증, 고위험 리뷰 강제 |
| `plugins/prompts-pack/commands/pr-audit.md` | 40줄 | `/pr-audit` | 3단계 체크리스트 |
| `prompts/prompt-composer-system/components/code-review-rubric.md` | 21KB | composer Phase 2 경유만 | 8축 rubric, §9 repo-local 규칙, §10 changeset 번들링 |

가장 상세한 rubric이 가장 도달하기 어려운 위치에 있다.

## 목표 상태

repo를 4개 레이어로 정리하고, L1이 L2와 L3 양쪽에서 도달 가능하게 만든다.

| 레이어 | 내용 | 현재 | 목표 |
|---|---|---|---|
| L0 지식 | `prompts/ai-reference/`, `baseline.md`, `commit_rules.md` | 직접 참조 가능 | 유지 |
| L1 component | `components/*.md` (rubric, role-dict, template) | composer 경유만 | 직접 입구 추가 |
| L2 실행 | skills, commands | 직접 호출 가능 | L1을 소비하도록 연결 |
| L3 오케스트레이터 | composer, `/fsd`, multi-agent-template | L1 독점 소비 | 소비자 중 하나로 강등 |

각 component는 입구 두 개를 갖는다. **직접 입구**는 Task Spec 없이 지금 이 세션에서 구체적 대상에 건다. **조합 입구**는 component 3개 이상이 얽힌 task일 때만 composer가 같은 파일로 라우팅한다. 파일은 하나이고 래퍼는 얇게 유지해 내용 중복을 만들지 않는다.

## 대기 중인 결정

**D1. component 라이브러리의 배포 경계 (결정됨)**

`prompts/prompt-composer-system/` 전체를 `plugins/prompts-pack/lib/prompt-composer-system/`으로 옮기고 원래 위치에 심볼릭 링크를 남긴다. 라이브러리를 참조하는 skill, command, agent는 라이브러리와 같은 plugin 안에 두어야 한다. 근거는 `${CLAUDE_PLUGIN_ROOT}`가 자신을 포함한 plugin의 루트로만 해석돼 plugin을 가로지르는 참조 수단이 없다는 것이다. 실측 근거와 참조 방식 4종의 검증 결과는 `02_deployment-decision.md`에 있다.

**D2. `/pr-audit`과 새 PR 리뷰 입구의 관계 (미결)**

제안 기본값은 분리 유지다. `/pr-audit`은 branch 전체 commit 감사라는 고유 목적이 있고, 새 입구는 단일 PR의 8축 rubric 평가를 담당한다. 둘 다 rubric 파일을 SSOT로 참조하되 진입 조건이 다르다. 통합하면 커맨드 하나가 두 워크플로를 분기해야 해서 description 기반 자동 라우팅이 부정확해진다.

**D3. `multi-agent-analysis-template.md` 분할 범위 (미결)**

이 파일은 1150줄이며 subagent 정의 파일, 출력 템플릿, 실전 시나리오가 한 파일에 연결돼 있다. 제안 기본값은 전면 분할이 아니라 상위 라우터와 온디맨드 섹션 분리다. `plugins/vh1981/skills/devlog/`가 이미 검증된 구조(`SKILL.md` 라우터 + `commands/*.md` + `reference/*.md` + `templates/*.md`)를 보여준다.

## 실행 원칙

`self_upgrade.md`의 불변 규칙을 이 계획에도 적용한다. 1회 실행은 대상 1개로 제한하고, 변경마다 사람 승인을 받으며, diff는 리뷰 가능한 크기로 유지한다. 따라서 아래 Phase들은 한 세션에 몰아서 수행하지 않고 Phase 단위로 나눠 커밋한다.

각 Phase는 독립적으로 배포 가능하다. Phase 2까지만 하고 멈춰도 code-review SSOT 통합이라는 실익이 남는다.

## Phase 1 — 배포 경계 확정 (완료)

목표: component 라이브러리를 plugin으로 배포하는 방식을 실제 설치로 검증해 확정한다.

결과는 `02_deployment-decision.md`에 기록했다. probe plugin을 만들어 `claude -p --plugin-dir`로 참조 방식 4종을 실행 검증했고, 형제 skill 상대 참조와 `${CLAUDE_PLUGIN_ROOT}` 참조가 skill 본문과 command의 `@` 첨부 양쪽에서 동작하는 것을 확인했다. repo 상대 경로 참조는 동작하지 않는다.

완료 기준 충족 여부: 충족. 다만 검증 수단은 `/plugin install`이 아니라 `--plugin-dir` 기반 headless 실행이며, 배포 복사 동작은 기존 설치본의 cache 내용으로 확인했다.

## Phase 1b — 라이브러리 이전 (완료)

목표: 라이브러리 실체를 plugin 안으로 옮겨 설치본에서 도달 가능하게 만들고, 이전으로 깨지는 참조를 함께 고친다.

변경 파일:

```
plugins/prompts-pack/lib/prompt-composer-system/   (신규 — 기존 19개 파일 전체 이전)
prompts/prompt-composer-system                      (심볼릭 링크로 대체)
plugins/prompts-pack/commands/build_prompt.md       (@ 경로를 CLAUDE_PLUGIN_ROOT 기준으로)
lib/.../trigger.md, trigger-prompts.md              (라이브러리 위치 안내를 자기 상대 경로로)
lib/.../audit-composer-system.md                    (25곳 경로 치환)
lib/.../component-discovery-{collect,approve}.md    (각 6곳 경로 치환)
lib/.../builder/optimized-prompt-composer.md        (시리즈 구성 경로 기준 문구)
```

수행한 작업:

- `git mv`로 디렉토리 전체를 옮겼다. `builder/`와 `components/`가 형제 관계를 유지해 component의 `../builder/prompt-component-router.md` 참조가 그대로 살아 있다.
- `prompts/prompt-composer-system`을 심볼릭 링크로 만들었다. 방향은 기존 `prompts/agents`, `prompts/commands` 선례와 같다.
- `trigger.md`가 component 위치를 repo 상대경로로 안내하고 있었다. 이 파일이 `/build_prompt`로 첨부되는 본문이므로 설치본에서 composer가 라이브러리를 찾지 못한다. 자기 파일 기준 상대 위치 안내로 바꾸고 `trigger-prompts.md` A-1과 A-2 정본도 동기화했다.
- 유지보수 도구의 경로를 실체 경로로 치환했다. git의 경로 필터링이 심볼릭 링크를 따라가지 않아 `audit-composer-system.md`의 G5 검사(`git status --short`)가 구경로에서 삭제로만 보고됐기 때문이다.

완료 기준 충족 여부: 충족. 타 repo cwd에서 `--plugin-dir`로 prompts-pack을 로드해 `@${CLAUDE_PLUGIN_ROOT}/lib/prompt-composer-system/trigger.md`가 `trigger.md`의 첫 줄을 그대로 첨부하는 것을 확인했다. composer 자체 무결성 검사 6종(G0 파일수 19, 표준 머리말, layer 필드, rfc↔speckit 상호배타 3 hit, S5 12행, audit 미등록 0)도 새 위치에서 모두 통과한다.

## Phase 2 — code-review SSOT 통합

목표: 분열된 code-review 자산 3개를 `code-review-rubric.md` 하나를 SSOT로 삼는 구조로 합치고, composer 없이 호출되는 첫 직접 입구를 만든다.

변경 파일:

```
plugins/prompts-pack/skills/pr-review/SKILL.md      (신규 — D-승인 대기)
plugins/prompts-pack/commands/pr-audit.md           (수정 — rubric 포인터 추가)
plugins/prompts-pack/agents/code-reviewer.md        (수정 — rubric 포인터 추가)
plugins/prompts-pack/lib/prompt-composer-system/components/code-review-rubric.md  (수정 — §0 standalone 메타)
.claude-plugin/marketplace.json                     (수정 — skill 목록)
plugins/prompts-pack/.claude-plugin/plugin.json     (수정 — description, version)
```

작업 내용:

- `.specs/pr-review-skill.composed.md`가 2026-07-24에 작성됐으나 실행되지 않은 상태다. 이 composed prompt를 fresh 세션에서 실행해 SKILL.md 초안을 만든다. composer의 Invariant 1을 지키는 실행이며, 동시에 composer가 실제로 잘하는 일이 무엇인지 확인하는 사례가 된다.
- `.specs/pr-review-skill.md`의 성공 기준 5개 rule이 초안에 보존됐는지 대조한다. 연동 확인, 치명 문제 한정, field 검증 완화, 주목적 commit 검토, LFS skip이 그것이다.
- SKILL.md는 rubric 내용을 재서술하지 않고 파일 경로로 참조한다. 재서술하면 drift가 발생한다.
- `pr-audit.md`와 `code-reviewer.md`는 기존 체크리스트를 유지하되, 고위험 리뷰에서 8축 rubric을 읽으라는 한 줄 포인터를 넣는다. 세 자산의 역할 경계를 각 파일 머리말에 명시한다.

완료 기준: `/pr-review <PR URL>` 한 번으로 rubric 8축이 적용된 리뷰가 나오고, Task Spec 작성이나 composer 기동이 필요하지 않다.

## Phase 3 — component 라우팅 해제

목표: 모든 component의 `§0 Router 등록 metadata`에 자연어 description과 standalone 가능 여부를 추가해 Task Spec 없이도 선택 가능하게 만든다.

변경 파일:

```
prompts/prompt-composer-system/components/agent-role-dictionary.md
prompts/prompt-composer-system/components/autonomous-optimization-loop.md
prompts/prompt-composer-system/components/code-review-rubric.md
prompts/prompt-composer-system/components/experiment-design-template.md
prompts/prompt-composer-system/components/multi-agent-analysis-template.md
prompts/prompt-composer-system/components/rfc-writing-template.md
prompts/prompt-composer-system/components/speckit-spec-generation.md
prompts/prompt-composer-system/CLAUDE.md          (규약에 신규 필드 추가)
prompts/prompt-composer-system/builder/prompt-component-router.md  (§1 catalog 동기화)
```

작업 내용:

- `§0` 표에 `standalone` 필드를 추가한다. 값은 `yes`(직접 입구 있음), `no`(composer 전용), `planned`(직접 입구 예정) 중 하나로 한다.
- `§0` 표에 `description` 필드를 추가한다. SKILL.md frontmatter의 description처럼 자연어 트리거 문구를 쓴다. 기존 `trigger signals` 필드는 spec 기반 라우팅용으로 그대로 둔다. 두 필드는 대상 독자가 다르다.
- `CLAUDE.md`의 "새 문서 추가 체크리스트"에 신규 필드 2개를 반영한다.
- `prompt-component-router.md §1` catalog 표를 동기화한다. 이 표가 component 메타의 SSOT라고 `§1.1`이 규정하고 있으므로 갱신을 빠뜨리면 stale 상태가 된다.

완료 기준: component 7개 전부에 `standalone`과 `description` 필드가 있고, router `§1` catalog와 값이 일치한다.

## Phase 4 — monolith 분할

목표: 대형 component를 devlog skill이 쓰는 progressive disclosure 구조로 쪼개 직접 입구와 composer 발췌 양쪽의 토큰 비용을 낮춘다.

변경 파일:

```
prompts/prompt-composer-system/components/agent-role-dictionary.md          (34KB, 분할 대상)
prompts/prompt-composer-system/components/multi-agent-analysis-template.md  (62KB, 분할 대상)
```

작업 내용:

- `agent-role-dictionary.md`를 상위 라우터와 role 그룹별 파일로 나눈다. 현재 `§1` Generative, `§2` Critical, `§3` Mediating, `§4` Process, `§5` Domain-Based가 이미 그룹 경계 역할을 하고 있다. `§5` Domain-Based Roles가 384줄부터 653줄까지로 가장 크므로 우선 분리 후보다.
- `multi-agent-analysis-template.md`는 D3 결정에 따른다. 제안 기본값을 채택하면 subagent 정의(`§3`), 출력 템플릿, 실전 시나리오(`§9`), 부록 A를 별도 파일로 빼고 본문에는 라우터만 남긴다.
- 기존 `§-숫자` 앵커를 유지한다. composer의 발췌 참조와 `audit-composer-system.md`의 grep 기반 자기 진단이 이 앵커에 의존한다.

완료 기준: 분할 후 `audit-composer-system.md`를 실행해 `§3.1` 파일 존재 검사와 `S5` grep 검사가 통과한다.

## Phase 5 — composer 범위 재정의

목표: composer의 광고된 용도를 실제로 값을 낸 용도로 좁혀, per-task 프롬프트 생성기라는 기대를 제거한다.

변경 파일:

```
prompts/prompt-composer-system/CLAUDE.md            ("What this is" 절)
prompts/prompt-composer-system/trigger.md
prompts/prompt-composer-system/trigger-prompts.md   (A-2 정본 — trigger.md와 동기화 필수)
plugins/prompts-pack/commands/build_prompt.md
README.md
```

작업 내용:

- `.specs/`의 6건 중 값을 낸 3건이 `pr-review-skill`, `speckit-spec-generation-component`, `composer-system-audit`이다. 셋 다 새 component나 skill을 저작한 경우다. composer의 용도를 **component 팩토리**로 재정의하고, 1회성 task 프롬프트 생성은 bypass 대상임을 명시한다.
- `router §3` bypass 조건 표에 항목을 추가한다. 직접 입구가 있는 component 1개로 해결되는 task는 composition을 건너뛴다.
- `trigger.md`는 `trigger-prompts.md` A-2의 paste-ready 사본이다. `CLAUDE.md`가 정본 수정 시 동기화를 요구하므로 두 파일을 함께 고친다.
- README의 `/build_prompt` 설명을 바뀐 용도에 맞춘다.

완료 기준: `CLAUDE.md`와 `trigger.md`와 README가 같은 용도를 서술하고, `trigger.md`와 `trigger-prompts.md` A-2 본문이 일치한다.

## Phase 6 — 문서 정합

목표: 레이어 구조와 신규 입구를 README와 marketplace 매니페스트에 반영해 외부에서 설치했을 때 무엇이 있는지 알 수 있게 한다.

변경 파일:

```
README.md
.claude-plugin/marketplace.json
plugins/vh1981/.claude-plugin/plugin.json
plugins/prompts-pack/.claude-plugin/plugin.json
```

작업 내용:

- README에 L0부터 L3까지의 레이어 구조와 각 레이어의 진입 방법을 절로 추가한다. 현재 README는 plugin과 skill 목록만 나열하고 있어서 component 라이브러리의 존재가 드러나지 않는다.
- marketplace.json과 plugin.json의 description에 신규 skill을 반영하고 version을 올린다.
- Phase 1에서 배포 경계가 바뀌었다면 README의 디렉토리 구조 코드블록을 갱신한다.

완료 기준: README만 읽고 component 라이브러리를 직접 입구로 호출하는 방법을 알 수 있다.

Phase 3 이후의 변경 파일 목록은 `prompts/prompt-composer-system/` 경로로 적혀 있다. Phase 1b 이후 이 경로는 심볼릭 링크가 되며 repo 안에서는 그대로 유효하다.

## 검증하지 않은 가정

아래 항목은 실행으로 확인하지 않았다. 미검증 상태다.

- `.specs/pr-review-skill.composed.md`가 현재 repo 상태에서 그대로 실행 가능한지 확인하지 않았다. 2026-07-24 작성 이후 skill 디렉토리 구조가 바뀌었고, 진입점 위치도 `prompts-pack`으로 바뀐다.
- component `§0` 표에 필드를 추가했을 때 `audit-composer-system.md`의 자기 진단이 통과하는지 확인하지 않았다.
- 심볼릭 링크된 디렉토리 아래의 `CLAUDE.md`가 자동 로드되는지 확인하지 않았다. Phase 1b의 확인 항목이다.
