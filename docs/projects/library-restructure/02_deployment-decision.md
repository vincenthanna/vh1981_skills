# 배포 경계 결정 — component 라이브러리의 위치와 참조 방식

Phase 1의 목표였던 배포 경계를 실측으로 확정했다. 결론은 component 라이브러리를 `plugins/prompts-pack/lib/prompt-composer-system/`으로 옮기고, 라이브러리를 소비하는 진입점도 같은 plugin 안에 두는 것이다. 근거는 `${CLAUDE_PLUGIN_ROOT}`가 자신을 포함한 plugin의 루트로만 해석되므로 **plugin을 가로지르는 파일 참조 수단이 존재하지 않는다**는 점이다. 이 결정 때문에 원래 계획에서 `plugins/vh1981/skills/pr-review/`에 두려던 PR 리뷰 진입점이 `plugins/prompts-pack/skills/pr-review/`로 바뀐다. 이 변경은 사용자 승인 대기 중이다.

부수적으로 두 가지 결함을 확인했다. `/build_prompt`는 설치본에서 동작하지 않으며, 이 머신의 설치본은 2026-05-29 기준 vh1981 1.3.0으로 현재 선언된 1.5.0보다 낡았다.

## 확정된 사실

설치 경로는 두 개이고 내용이 다르다. plugin이 실제로 실행되는 위치는 cache이며, 여기에는 plugin 디렉토리 안의 것만 들어간다.

| 경로 | 내용 | component 포함 |
|---|---|---|
| `~/.claude/plugins/marketplaces/vh1981_skills/` | repo 전체 clone | 포함 |
| `~/.claude/plugins/cache/vh1981_skills/vh1981/1.3.0/` | `plugins/vh1981/` 하위만 | 미포함 |
| `~/.claude/plugins/cache/vh1981_skills/prompts-pack/0.1.0/` | `plugins/prompts-pack/` 하위만 | 미포함 |

marketplace clone에 repo 전체가 있지만 이 경로를 가리키는 변수가 없고 marketplace 이름에 의존하므로 참조 대상으로 쓸 수 없다.

plugin 디렉토리는 하위 구조를 가리지 않고 통째로 복사된다. `claude-mem` 설치본이 `modes/`, `ui/`, `scripts/`, `package.json`처럼 표준이 아닌 항목을 그대로 담고 있고, `devlog` skill의 `commands/`, `reference/`, `templates/` 하위 디렉토리도 모두 복사돼 있다. 따라서 plugin 안이라면 `lib/` 같은 임의 디렉토리를 써도 배포된다.

## 참조 방식 실측

probe plugin을 만들어 `claude -p --plugin-dir`로 4개 메커니즘을 실행 검증했다. 실험 파일은 `scratchpad/plugtest/testplug/`에 있다.

| 메커니즘 | 결과 |
|---|---|
| 형제 skill 상대 참조 `../lib-a/components/probe.md` | 동작 |
| SKILL.md 본문의 `${CLAUDE_PLUGIN_ROOT}/lib/probe2.md` | 동작 |
| command의 `@${CLAUDE_PLUGIN_ROOT}/lib/probe2.md` | 동작 |
| command의 repo 상대 경로 `@prompts/prompt-composer-system/trigger.md` | 미동작 |

마지막 항목은 1차 시도에서 위양성이 나왔다. "첨부됐는가"만 물었을 때 모델이 `ATTACHED`라고 답했으나, 첨부 파일의 첫 줄을 그대로 인용하라고 요구하자 `NOT_ATTACHED`가 나왔다. 존재하지 않는 경로를 넣은 대조군도 `NOT_ATTACHED`를 반환해 판정이 일관됐다.

plugin을 가로지르는 참조는 시험하지 않았다. 다른 plugin의 루트를 지칭하는 변수가 정의돼 있지 않으므로 하드코딩된 절대 경로 외에 수단이 없고, 절대 경로는 설치 위치에 따라 달라지므로 후보에서 제외했다.

## 결정

**D1은 결정됨.** `prompts/prompt-composer-system/` 전체를 `plugins/prompts-pack/lib/prompt-composer-system/`으로 옮기고, 원래 위치에는 심볼릭 링크를 남긴다. 근거는 세 가지다.

첫째, 디렉토리를 통째로 옮기면 component가 `../builder/prompt-component-router.md`를 참조하는 기존 상대 경로가 그대로 유지된다. `builder/`와 `components/`가 양쪽 위치에서 형제 관계를 유지하기 때문이다.

둘째, 심볼릭 링크의 방향이 이 repo의 기존 선례와 같다. `prompts/agents`와 `prompts/commands`가 이미 `plugins/prompts-pack/` 아래 실체를 가리키고 있고, git은 이를 mode `120000`으로 저장한다. 실체가 plugin 안에 있어야 배포되고, 링크는 repo 안에서만 쓰이므로 배포 경로에 링크가 끼어들지 않는다.

셋째, 라이브러리를 소비하는 자산 3개가 모두 `prompts-pack`에 있다. `commands/build_prompt.md`, `commands/pr-audit.md`, `agents/code-reviewer.md`가 그것이다.

**소비자 배치 규칙.** 라이브러리를 참조하는 skill, command, agent는 라이브러리와 같은 plugin 안에 두어야 한다. plugin을 가로지르는 참조 수단이 없기 때문이다.

## 승인이 필요한 변경

PR 리뷰 진입점의 위치가 바뀐다. `.specs/pr-review-skill.md`의 D 제약은 `plugins/vh1981/skills/<name>/SKILL.md`를 규정하고 있으나, 이 위치에서는 `code-review-rubric.md`를 참조할 수 없다.

| 항목 | 기존 계획 | 변경안 |
|---|---|---|
| PR 리뷰 진입점 | `plugins/vh1981/skills/pr-review/` | `plugins/prompts-pack/skills/pr-review/` |
| 근거 | 2026-07-24 spec의 repo 규약 | 라이브러리와 동일 plugin 요구 |

`prompts-pack`에는 현재 `skills/` 디렉토리가 없다. probe 실험에서 `skills/`와 `commands/`를 함께 가진 plugin이 정상 동작하는 것을 확인했으므로 추가에 문제가 없다.

## 함께 발견한 결함

**`/build_prompt`가 설치본에서 동작하지 않는다.** `plugins/prompts-pack/commands/build_prompt.md`가 `@prompts/prompt-composer-system/trigger.md`를 repo 상대 경로로 참조한다. 이 경로는 사용자의 작업 repo를 기준으로 해석되므로 vh1981_skills가 아닌 곳에서는 파일이 없다. 위 실측 표의 마지막 항목이 이 경우다. 라이브러리 이전 후 `@${CLAUDE_PLUGIN_ROOT}/lib/prompt-composer-system/trigger.md`로 고치면 해결된다.

**설치본이 낡았다.** 이 머신의 vh1981 설치본은 1.3.0이고 `installedAt`이 2026-05-29이며 `gitCommitSha`가 `f86cc2a`다. 현재 `marketplace.json`은 1.5.0을 선언한다. 그 결과 `md-tidy`, `md-to-html` skill과 `devlog`의 `commands/update.md`, `commands/upload.md`가 설치본에 없다. Phase 2 검증 전에 `/plugin marketplace update`가 필요하다.

## 이전 후 확인한 심볼릭 링크의 한계

파일 읽기는 링크를 따라간다. `ls prompts/prompt-composer-system/*.md`가 이전 전과 같은 19개를 반환한다.

git의 경로 필터링은 링크를 따라가지 않는다. `git status --short prompts/prompt-composer-system/`이 구경로 파일들을 삭제(`D`)로 보고하고 새 위치의 변경을 보여주지 않는다. 이 때문에 `audit-composer-system.md`의 G5 검사와 `component-discovery-collect.md`의 ledger `git add`가 깨졌고, 두 파일과 `component-discovery-approve.md`의 경로 37곳을 실체 경로로 치환했다.

`CLAUDE.md`는 실체 경로에서 정상 자동 로드된다. 이전 후 `plugins/prompts-pack/lib/prompt-composer-system/` 아래 파일을 편집할 때 자동 로드되는 것을 확인했다.

## 미검증 항목

- 심볼릭 링크가 plugin 디렉토리 **안**에 있을 때 cache 복사가 이를 따라가는지 확인하지 않았다. 위 결정은 링크를 plugin 바깥에만 두므로 이 동작에 의존하지 않는다.
- 심볼릭 링크 경유(`prompts/prompt-composer-system/`)로 파일을 편집할 때 `CLAUDE.md`가 자동 로드되는지 확인하지 않았다. 실체 경로가 정본이므로 편집은 실체 경로로 하면 된다.
- component 안의 `[VERIFIED:static prompts/...]` 출처 표기는 구경로 그대로 두었다. 검증 시점의 기록이며 링크로 계속 읽히므로 깨지지 않는다.
