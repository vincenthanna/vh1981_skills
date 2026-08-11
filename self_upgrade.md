# self_upgrade — 프롬프트 자가 개선 오케스트레이터

> 짧은 명령("자가 개선을 해라")으로 이 repo의 프롬프트/스킬을 **조금씩, 측정 가능하게, 롤백 가능하게** 개선한다.
>
> 핵심 원칙: 이 프롬프트는 새 능력을 만들지 않는다. 이미 있는 부품을 잇는다.
> - 지식 소스: `prompts/ai-reference/` (anthropic 공식 repo 큐레이션, 갱신 절차는 `META.md §6`)
> - 적합도 함수: `plugins/prompts-pack/lib/prompt-composer-system/builder/prompt-evaluation-rubric.md` (pre/post 평가)
> - 개선 단계: `plugins/prompts-pack/commands/improve-prompt.md`
> - 버전/롤백: git

---

## 0. 실행 모드

명령 형태:

- `자가 개선` 또는 `self_upgrade` → 아래 **모드 선택**을 묻고 진행
- `self_upgrade A` → Loop A(지식 갱신)만
- `self_upgrade B <대상 프롬프트 경로>` → Loop B(프롬프트 개선)만, 대상 1개
- `self_upgrade full <대상 프롬프트 경로>` → A 먼저, 그 결과를 근거로 B

**불변 규칙 (모든 모드 공통):**

1. **1회 실행 = 대상 프롬프트 1개.** 여러 파일을 한 번에 갈아엎지 않는다.
2. **모든 변경은 출처를 인용한다.** 출처 없는 "개선"은 금지. 오픈 웹보다 `ai-reference` 같은 큐레이션 소스를 우선한다.
3. **파일 적용 전 반드시 사람 승인.** diff + eval 점수 + 출처를 보여주고 멈춘다 (§3 게이트).
4. **self-eval 편향을 표기한다.** 같은 세션에서 개선·평가하면 점수 옆에 `[self-eval 경고]`.
5. **작은 diff.** 1회 실행의 변경은 리뷰 가능한 크기로. 구조 전면 재작성이 필요하면 그 사실만 보고하고 멈춘다.

---

## Loop A — 지식 갱신 (저위험)

목적: `ai-reference/`를 공식 소스의 최신 상태로 동기화. 창의적 재작성이 아니라 **sync**.

### A1. 소스 화이트리스트

신뢰 순서대로:

1. `github.com/anthropics/*` 공식 repo (README, docs, CHANGELOG)
2. Anthropic 공식 docs / 엔지니어링 블로그
3. 1차 연구 (arXiv 등) — 단, "기법"으로 채택 전 재현/합의 여부 확인
4. (그 외 오픈 웹은 보조 신호로만, 단독 근거 금지)

### A2. 절차

1. `ai-reference/META.md §6 업데이트 가이드`의 절차를 따른다 (새 repo 추가 / 기존 문서 갱신 / 카테고리 변경).
2. 각 카테고리 문서에 대해 원본 소스의 최신 내용과 **diff 되는 지점만** 식별한다.
3. 변경 후보를 표로 출력:

   | 파일 | 변경 유형 | 출처(URL) | 무엇이 새로워졌나 (1줄) |
   |---|---|---|---|

4. **여기서 멈추고 사람 승인을 받는다.** 승인된 항목만 파일에 반영한다.
5. 반영 후 `META.md §6.1~6.4`에 따라 README/CLAUDE.md의 카운트·라우팅 테이블을 함께 갱신한다.

### A3. 산출물

- 갱신된 `ai-reference/` 문서
- `self_upgrade-changelog.md`(repo 루트)에 한 줄 추가: `날짜 | A | 파일 | 출처 | 요약`

---

## Loop B — 프롬프트 개선 (고위험, 게이트 필수)

목적: 대상 프롬프트 1개를, 갱신된 지식과 rubric에 근거해 작은 폭으로 개선.

### B1. 입력

- **대상**: 명령에서 지정한 프롬프트 1개 (없으면 사용자에게 묻는다)
- **지식**: `ai-reference/` (필요 시 Loop A를 먼저 돌린 결과) + A1 화이트리스트
- **기준**: `prompt-evaluation-rubric.md`

### B2. 절차

1. **대상 분석**: 현재 프롬프트의 의도·scope·출력 형식을 1문단으로 요약한다. (의도는 보존 대상이다 — `improve-prompt.md` "원본의 의도를 변경하지 말 것" 규칙 준수.)
2. **개선 후보 도출**: `ai-reference`/화이트리스트에서 이 대상에 **직접 적용 가능한** 최신 기법만 추린다. 각 후보에 출처를 붙인다. 적용 불가/추측성 팁은 버린다.
3. **Pre-eval**: 개선안에 대해 `prompt-evaluation-rubric §1 Pre-execution Checklist`(P1~P7)를 적용한다. P1~P5 중 하나라도 fail이면 개선안을 고치거나 폐기한다.
4. **diff 작성**: 작은 단위 diff로 변경안을 만든다. 변경마다 옆에 `← 출처: …`.
5. **Post-eval**: 개선 전/후 프롬프트를 같은 입력으로 비교하고 rubric 5축 점수를 낸다. 채점 주체는 §B4 정책을 따른다 — 기본은 **독립 채점자(별도 세션/다른 LLM)** 이며, 자가 채점만 했을 때는 점수 옆 `[self-eval 경고]`를 단다.
6. **게이트(사람 승인)**: 아래 형식으로 출력하고 **멈춘다.** 승인 전에는 파일을 절대 수정하지 않는다.

```
## self_upgrade B 제안 — <대상 파일>

### 변경 요약
- (한 줄씩, 각 줄에 출처)

### diff
<리뷰 가능한 작은 diff>

### eval (rubric)
- Pre: P1~P7 통과/실패
- Post: 5축 점수 (개선 전 → 후) — 채점자: <gemini/codex/별도 세션/자가>  [self-eval 경고?]

### 출처
- (URL 목록, ai-reference 우선)

### 위험 / 보류 사항
- (있으면)

승인하면 파일에 반영하고 commit 합니다. 수정 의견을 주셔도 됩니다.
```

### B3. 승인 후

1. 승인된 diff만 파일에 반영.
2. `self_upgrade-changelog.md`에 한 줄 추가: `날짜 | B | 대상 | 출처 | eval 점수 변화 | 요약`.
3. **실행마다 git commit** (롤백 단위). 메시지: `chore(self-upgrade): <대상> — <한 줄 요약>`. (`commit_rules.md`상 이 repo는 markdown commit 예외 대상.)

### B4. 독립 채점 (별도 세션 / 다른 LLM)

self-eval 편향을 깨기 위해, **개선을 만든 주체와 점수를 매기는 주체를 분리한다.** 채점 신뢰도 순서:

1. **다른 LLM 채점 (권장)** — `codex-bridge` / `gemini-bridge`로 외부 LLM에 채점만 위임. 이 repo의 `multi-llm-debate-orchestration.md §2.1~2.2` 컨벤션을 그대로 사용한다.
2. **별도 세션 채점** — 같은 모델이라도 새 Claude 세션에서 채점. 개선 맥락을 모른 채 결과만 본다.
3. **자가 채점** — 위 둘 다 불가할 때만. 점수에 `[self-eval 경고]` 필수.

**채점자에게 넘기는 입력 (개선 의도·근거는 숨긴다):**
- rubric 파일: `plugins/prompts-pack/lib/prompt-composer-system/builder/prompt-evaluation-rubric.md`
- 개선 전 프롬프트, 개선 후 프롬프트 (라벨을 A/B로 가려 어느 쪽이 "개선본"인지 알리지 않는다 — 블라인드)
- 채점 지시: "rubric 5축으로 A와 B를 각각 채점하고, 축별 점수와 1줄 근거만 출력하라. 어느 쪽이 개선본인지 추측하지 마라."

**호출 예 (gemini-bridge 경유):**

```
role_prompt = plugins/prompts-pack/lib/prompt-composer-system/builder/prompt-evaluation-rubric.md + 위 블라인드 채점 지시
context_files = [<before>.md, <after>.md]
out_path = .eval/self_upgrade/<대상>_<날짜>_gemini.md
→ Agent(gemini-bridge) 호출, 결과 파일을 그대로 받아 게이트 출력에 인용
```

**규칙:**
- 채점 LLM의 응답은 **해석·편집하지 않고 그대로** 게이트에 인용한다 (bridge 규칙과 동일).
- 외부 CLI(`codex`/`gemini`) 미로그인 등으로 실패하면 별도 세션 → 자가 채점 순으로 폴백하고, 폴백 사실을 게이트에 명시한다.
- 채점 결과 파일은 `.eval/self_upgrade/`에 보관한다.
- spec이 IRREVERSIBLE/고위험이면 1번(다른 LLM) 채점을 **필수**로 한다.

---

## 게이트가 막는 4가지 실패 모드

| 위험 | 방어 장치 |
|---|---|
| 표류(drift) — 측정 없는 "개선" | rubric pre/post 점수에 묶음 (B2.3, B2.5) |
| 웹 검색 노이즈 | 화이트리스트 + 출처 인용 강제 (§0-2, A1) |
| 무제한 scope | 1회 1대상 + 작은 diff (§0-1, §0-5) |
| self-eval 편향 / 복리 환각 | **독립 채점(다른 LLM/별도 세션) + 블라인드 A/B** (B4), `[self-eval 경고]` 표기, 사람 승인 게이트 (§0-4, B2.6) |

---

## 안 하는 것

- 출처 없는 자유 재작성
- 한 번에 여러 프롬프트 수정
- 승인 없는 파일 반영 / commit
- 보안 파일·임시 diff 파일 commit (`commit_rules.md`)
