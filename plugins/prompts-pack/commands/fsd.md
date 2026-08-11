Full Self-Development — 기능 목표를 조사·계획해 격리된 git worktree + 자기완결적 handoff 문서로 만들어, 새 세션이 끝까지(개발 → 리뷰 → 검증 → PR) 실행할 수 있게 인계한다. 구현은 하지 않는다.

## 목표 (rough goal)

$ARGUMENTS

## fsd란

fsd는 자율 개발 루프의 **계획 + 인계(handoff) 절반**이다. 기능을 **구현하지 않는다**. 산출물은 두 가지다:

1. 새 티켓 branch 위의 **격리된 git worktree**
2. 그 worktree 안의 **자기완결적 handoff 문서**

이 두 가지가 있으면 *새* 세션이 handoff 문서 하나만으로 **개발 → 리뷰 → 검증 → PR**을 추가 컨텍스트 없이 끝까지 수행할 수 있다.

```
/fsd <목표>              →  조사 + 결정 + worktree + handoff 문서   ─┐
                                                                     ├─ 기능마다 반복 가능
새 세션에서 handoff 실행  →  개발 → 리뷰 → 검증 → PR                ─┘
```

**분리 자체가 핵심이다.** 계획 세션에는 무거운 조사·결정 컨텍스트가 쌓이고, 실행 세션은 깨끗한 컨텍스트 창을 원한다. 모든 결정을 durable한 handoff에 고정하고 작업을 worktree로 격리하면, 실행 세션은 신선하면서도 완전히 브리핑된 상태로 시작한다 — 다음 기능에 대해 루프를 다시 돌려도 컨텍스트가 오염되지 않는다.

## 사용 / 비사용 기준

- **사용**: 사소하지 않은 변경을 조사·계획해 자율 실행 준비까지 마치고 싶을 때. "계획하고 인계해줘", "이 세션의 흐름을 반복하자" 같은 요청.
- **비사용**: 한 파일짜리 사소한 수정, 순수 질문, 사용자가 지금 이 세션에서 *바로* 구현하길 원할 때. fsd는 의도적으로 구현의 상류(upstream)에 있다.

## 시작 전 — repo 규약 감지

fsd는 repo-agnostic이지만, handoff는 *현재* repo의 규약을 따라야 한다. repo 루트 `CLAUDE.md`(그리고 `~/.claude/CLAUDE.md`)를 읽고 다음을 추출한다:

- **이슈 키/티켓 규약**(예: `PII`)과 branch/commit prefix 규약
- **PR base branch**(예: `main` — release branch를 금지하는 repo가 많다. 지켜라.)
- 전역보다 우선하는 **repo-local skill**(흔히 `commit`, `pr`, `dev`, `test`, `stage`, `prod`, 그리고 리뷰용 skill). handoff의 워크플로 순서는 *이들을* 참조해야 한다.
- **worktree 디렉토리** 규약(흔히 `.claude/worktrees/<TICKET>`)
- **툴체인** 규칙(예: `bun`/`uv` 강제, `npm`/`pip` 금지)과 **검증** 커맨드(`tsc`/`lint`, `py_compile`/`pytest`)

규약이 명시돼 있지 않으면 뻔한 기본값을 골라 그 사실을 handoff에 남긴다. 검증할 수 없는 티켓 번호를 지어내지 마라 — 기존 최신 티켓 branch에서 다음 번호를 유도하고 잠정(provisional)임을 표시한다.

## 파이프라인 (순서대로 실행)

### 1 — main을 remote와 동기화

`git fetch origin` 후 로컬 default branch == `origin/<default>`인지 확인한다. 뒤처져 있으면 fast-forward. HEAD vs remote를 보고한다. 낡은 main 위에 세운 계획은 즉시 썩는다 — 이 단계는 협상 불가.

### 2 — 코드 인덱스/그래프 갱신 (repo에 도구가 있을 때)

repo가 코드 그래프/인덱스 도구(원본 환경에서는 `graphify`)를 쓴다면 갱신하고(`graphify update .` 등), 리포트의 빌드 기준 commit == `git rev-parse HEAD`인지 확인한 뒤에만 신뢰한다. 새 worktree에는 그래프가 없을 수 있다 — 같은 방법으로 bootstrap한다. 이후 모든 조사 agent가 이 그래프에 의존한다. 도구가 없는 repo라면 이 단계는 생략하고 이후 조사에서 일반 탐색(Glob/Grep/LSP)을 쓴다.

### 3 — 운영 모델 채택

명시적으로 선언하고 실행 내내 유지한다:

- **팀리드 모드**: 너는 모니터링·리뷰·할당만 한다. 조사·구현을 인라인으로 하지 **않는다** — **subagent를 spawn**한다. 한 커맨드짜리 사소한 조회만 인라인 허용.
- **합의 프로토콜 (코드 변경)**: 동일한 프롬프트로 **병렬 subagent 5개**를 spawn하고, **≥3/5** 다수 접근을 채택하거나 최선 요소를 합성한 뒤, 근거를 보고하고, 그 후에만 적용한다. (실제 발동은 실행 세션에서지만, handoff가 이를 지시해야 한다.)
- **그래프-우선 주입 (그래프 도구가 있을 때 필수)**: 그래프 규칙은 위임 과정에서 **살아남지 않는다**. spawn하는 **모든** subagent 프롬프트에 다음 한 줄을 넣어라: *"광범위한 grep/rg/glob 전에 코드 그래프를 먼저 질의하고 그래프 리포트를 읽어라. grep은 정확 문자열 탐색의 fallback으로만 쓴다. file:line을 인용하라."*
- **Ultracode**: ultracode가 켜져 있으면 조사(그리고 handoff에 담길 이후 phase들)를 **Workflow** 도구로 구동한다 — fan-out, 적대적 검증, 합성 — phase 사이에는 네가 루프에 남는다.

### 4 — 조사 (위임, 절대 인라인 금지)

목표를 독립적인 차원으로 분해한다(보통: 현재 아키텍처/데이터 모델, 변경할 서브시스템, 통합 지점, 배포/런타임, 테스트·검증, 그리고 fetch할 외부 문서). **병렬 조사 agent**로 fan-out하고 structured output을 받는다(각각 그래프-우선 주입 포함). 그다음 **적대적 검증자(adversarial verifier)** 를 돌려 인용된 파일을 다시 읽어 핵심(load-bearing) 주장을 확인하고 **정확한 구현 anchor(file:line)를 고정**한다. `Workflow` 도구를 우선하고, 안 되면 병렬 `Explore`/`general-purpose` agent를 spawn한다.

의외의 결과는 실패가 아니라 발견으로 취급하라 — 예컨대 참조하려던 문서/API가 못 쓰는 것으로 판명되면, 그것은 숨길 막다른 길이 아니라 문서화할 가치가 있는 *부정적 결과(negative result)*다.

### 5 — 진짜 갈림길만 질문

`AskUserQuestion`은 **무엇을 만들지가 바뀌면서** 코드/기본값으로 해소할 수 없는 결정에만 쓴다(scope, 키 설계, 위험한 트레이드오프, 요청 속의 낡은 전제). 답변은 handoff에 **DECIDED**로 굳힌다. 유추할 수 있는 것은 묻지 마라. 질문을 찔끔찔끔 흘리지 말고 한 번에 배치로 묻는다.

### 6 — 티켓 + worktree

repo의 이슈 트래커 skill(예: `/jira`)로 티켓 + branch + worktree를 만든다.

- **branch는 repo가 요구하는 PR base branch 기준으로**(대개 `main`) 만든다. repo가 달리 말하지 않는 한 release branch가 아니다.
- **이슈 트래커 MCP/CLI가 없을 때의 fallback**(headless 실행에서 흔함): 그래도 `origin/<base>` 기준으로 `<worktree-dir>/<TICKET>`에 worktree를 만든다. 티켓 번호는 기존 최신 티켓 branch의 다음 번호를 쓰되 잠정임을 표시하고, 사용자가 UI에서 직접 만들 수 있도록 바로 붙여넣을 티켓 본문(팀 언어)을 handoff 안에 넣는다.

### 7 — handoff 작성

`<worktree>/.claude/handoffs/<TICKET>-HANDOFF.md`를 쓴다. 이것이 새 실행 세션이 소비할 산출물이다. 아래 "handoff 문서 템플릿"을 뼈대로 모든 섹션을 채운다. handoff는 반드시:

- **"STEP 0 — 어떤 작업보다 먼저"로 시작**하고, 그 안에서 순서대로 (a) 팀리드/agent-orchestration 운영 모델의 인지·채택, (b) 코드 그래프 갱신 + 신선도 확인을 강제한다. 이로써 모든 실행 세션이 네가 방금 확립한 것과 같은 규율 상태로 재진입한다.
- repo-local skill을 사용해 **개발 워크플로 순서를 내장**한다:
  `개발 (구현, phased, 5-agent 합의) → 리뷰 → 로컬 스택 기동 → 테스트 게이트 → /commit → /pr` — repo에 해당 skill(`/review-orchestrator`, `/dev`, `/test` 등)이 있으면 그 이름을 그대로 쓰고, 없으면 동등한 절차로 대체해 명시한다.
- 다음을 담는다: 목표; 조사 결과(file:line); **DECIDED vs OPEN**으로 나눈 설계; 검증자가 확인한 구현 **anchor**; **phased 계획**(phase당 ≤ ~5 파일, 코드 phase마다 5-agent 합의, phase 사이 검증); 추가할 **테스트** + **완료 전 검증 게이트**; 남은 미결 결정/리스크; 최상단에 **실행 진입점 한 줄**.
- 문서 언어는 팀 규약을 따른다(이 repo 기준: 한글. 티켓 본문·사용자 노출 문자열 등 DATA도 팀 언어로).

## 완료 시 보고

파이프라인이 끝나면 사용자에게 압축된 상태를 보고한다: 동기화된 HEAD, 그래프 신선도, worktree 경로 + branch, handoff 경로, 티켓(또는 잠정 번호와 그 이유), 그리고 실행 진입 커맨드 한 줄. **부정적 조사 결과는 눈에 띄게 앞세워라** — 지금 잡아낸 잘못된 전제가 실행 세션 전체를 구한다.

## fsd 자기 출력 검증

완료 선언 전에 확인한다: (1) worktree가 존재하고 올바른 branch 기반인가, (2) handoff 파일이 존재하고 STEP 0 섹션 + 워크플로 순서 + DECIDED/OPEN 설계 + anchor를 담고 있는가, (3) handoff가 참조하는 repo-local skill이 실제로 그 worktree에 존재하는가. fsd는 코드를 만들지 않으므로 컴파일할 것이 없다 — 기준은 **차가운(cold) 세션이 너에게 아무것도 묻지 않고 handoff를 실행할 수 있는가**다.

---

## Handoff 문서 템플릿

모든 섹션을 채운다. 괄호 안 가이드 문구는 지운다. 목표: 차가운 세션이 계획자에게 아무것도 묻지 않고 이 문서만으로 실행을 끝낼 수 있어야 한다.

````markdown
# <TICKET> — <기능 한 줄 제목>

> **진입점:** 이 worktree 안의 새 세션에서 `.claude/handoffs/<TICKET>-HANDOFF.md`를 읽고 실행하라.
> 이 문서는 자기완결적이며 이 작업의 유일한 기준(authoritative)이다. **개발 → 리뷰 → 검증 → PR**을 끝까지 수행하라.
> 구현은 계획 세션에서 의도적으로 미뤄졌다 — OPEN 표시가 없는 모든 것은 이미 결정된 사항이다.

| | |
|---|---|
| **티켓** | <TICKET> (트래커에 없으면 생성 — 문서 끝의 본문 사용) |
| **Branch / worktree** | `<TICKET>` @ `<worktree 경로>`, `origin/<base>` 기반 |
| **PR base** | `<base branch>` |
| **Scope** | <범위에 포함되는 서비스/디렉토리> |

## STEP 0 — 어떤 작업보다 먼저 (필수, 이 순서대로)

### 0.1 — 운영 모델 인지·채택
(팀리드 모드: 모니터링/리뷰/할당만, subagent spawn, 인라인 구현 금지;
 코드 변경은 병렬 subagent 5개 합의 ≥3/5; 모든 subagent 프롬프트에 "코드 그래프 먼저 질의" 주입;
 phased 실행 phase당 ≤5 파일; 시니어-완벽주의 기준; ultracode 시 Workflow 도구.)

### 0.2 — 코드 그래프 갱신 (도구가 있는 repo만)
그래프 갱신 후 리포트의 빌드 기준 commit == `git rev-parse HEAD` 확인. 새 worktree에 그래프가 없으면
bootstrap. 그래프 산출물 디렉토리는 절대 commit하지 않는다.

> 0.1 + 0.2 완료 후에만 진행한다.

## 개발 워크플로 — 필수 순서
개발 (구현, phased, 코드 phase마다 5-agent 합의)
  → 리뷰            (repo 리뷰 skill이 있으면 사용; 다수 리뷰어 합의 blocker는 코드 대조 검증 후 수정)
  → 로컬 스택 기동   (repo의 `/dev` 등)
  → 테스트 게이트    (repo의 `/test <tier>` 등; PASS 기준 = 게이트 exit 0)
  → /commit         (원자적 Conventional Commits, [<TICKET>] prefix)
  → /pr             (팀 언어 설명, 시각적 diff)
repo-local skill을 쓰고, 전역/플러그인 변형을 쓰지 마라. PR base = <base>.

## 1. 목표
<문제 + 원하는 최종 상태를 평이하게>

## 2. 핵심 발견 / 의외의 결과
<부정적 결과, 요청 속의 낡은 전제, 접근을 바꾸는 모든 것 — 크게 드러내라>

## 3. 현재 아키텍처 (조사 결과, file:line 검증됨)
<현재 상태: 데이터 모델, 변경할 서브시스템, 통합 지점, 배포/런타임 — file:line 포함>

## 4. 설계 (DECIDED vs OPEN)
<무엇을 만들 것인가. 각 결정에 DECIDED(근거/결정 주체 포함) 또는 OPEN(해결 필요)을 표시.
 AskUserQuestion 답변은 DECIDED로 굳혀 넣는다.>

## 5. 구현 anchor (검증자가 확인한 file:line)
<각 변경이 걸리는 정확한 함수/라인 범위; 커버되지 않은 경로도 명시>

## 6. Phased 계획 (phase당 ≤ ~5 파일 · 코드 phase마다 5-agent 합의 · phase 사이 검증)
<Phase 1..N, 각 phase가 건드리는 파일과 그 phase의 수용 기준>

## 7. 테스트 & 검증
<`/test <tier>`가 무엇을 돌리고 PASS 기준은 무엇인지; 이 기능에 필요한 NEW 커버리지;
 /commit 전에 통과해야 하는 완료-전-검증 게이트(repo에 따라 tsc/lint 또는 py_compile/pytest)>

## 8. 미결 결정 / 리스크
<남은 갈림길 + 합리적 기본값; 실행 중 사용자에게 표면화할 사항>

## 9. 티켓 본문 (<TICKET> 생성용 — 팀 언어)
<바로 붙여넣을 수 있는 트래커 설명: 목표 / 배경 / Action Items. 계획 세션이 트래커에
 프로그램적으로 접근하지 못했을 때 사용>

---
*commit `<hash>` 기준 N-agent 조사 workflow로 생성. file:line 참조는 그 commit에 대해 검증자가
확인함 — HEAD가 이동했다면 그래프 갱신 후 재확인할 것.*
````

---

> 출처: 외부 `fsd`(Full Self-Development) skill(SKILL.md + references/handoff-template.md)을 한글 번역·이식. 원본의 특정 환경 종속 요소(graphify, `/jira`, `/goal`, `/review-orchestrator` 등)는 "repo 규약 감지" 원칙에 따라 일반화했다.
