# Baseline

여러 repo에서 작업할 때 공통으로 적용하고 싶은 규칙과, 자주 쓰는 prompt들의 위치/기능을 모아둔 인덱스 문서.

작업 시작 시점에 이 파일을 읽혀서 컨텍스트를 잡는 용도로 사용한다.

---

## 1. 공통 작업 규칙 (Global Rules)

공통 작업 규칙의 정본은 `plugins/vh1981/guidelines/core.md` 이다.
`vh1981` 플러그인이 설치된 세션에는 SessionStart hook 이 이 규칙을 자동으로 주입하므로 따로 읽힐 필요가 없다.

---

## 2. Repo별 오버라이드

> repo 고유 규칙이 있으면 여기에 추가. 비어 있어도 됨.

### 2.1 `vh1981_skills`
- skill / prompt 자산 저장소. 코드 실행보다는 문서 정리 위주.

### 2.2 `<repo-name>`
- (TODO)

---

## 3. Prompt 인덱스

자주 쓰는 prompt 자산. 경로는 이 repo 기준 상대 경로.

| 경로 | 용도 | 비고 |
|------|------|------|
| `prompts/autorun.md` | 작업 지시서를 받아 조사, 실행, 검증, 보고까지 한 번에 진행하는 절차 | 외부 게시물은 초안만, 교훈은 `prompts/autorun-learnings.md` |
| `prompts/code_visualization.md` | 코드 구조를 mermaid 5종 view로 시각화 | C++/GStreamer 위주 |
| `prompts/commands/` | user-level slash command 원본 (`~/.claude/commands/`와 동일) | 아래 4번 참고 |
| `prompts/deepingsource/tests/` | deepingsource 테스트 관련 prompt | (TODO: 세부 정리) |
| `prompts/ai-reference/` | Anthropic SDK / Claude 제품군 reference 문서 | 10개 카테고리 (`01_SDK` ~ `10_Safety`) |
| `prompts/ai-reference/USAGE_GUIDE.md` | ai-reference 사용 가이드 | 먼저 읽을 것 |

---

## 4. Skill 인덱스

이 plugin에서 제공하는 skill 요약. 자세한 trigger 조건은 각 skill의 SKILL.md 참고.

| Skill | 용도 |
|-------|------|
| `vh1981:devlog` | 통합 작업 로그 + 조사 보고서 (`docs/devlog/<project>/`) |
| `vh1981:worklog` | 세션 작업 히스토리 (`docs/history/<subject>/`) |
| `vh1981:prjdocs` | 프로젝트 조사/분석 보고서 (`docs/projects/<project>/`) |
| `bug-fix` | 분석 → 방향 제시 → 승인 후 구현의 3단계 버그 수정 |
| `analyze` | 코드 수정 없이 분석만 |
| `verify` | 검증-수정 반복 사이클 |
| `write-report` | 분석/테스트 결과 보고서화 |
| `improve-prompt` | prompt를 Claude Code용으로 개선 |
| `search-prompt` | prompt 자연어 검색 |
| `pr-audit` | 현재 branch PR 수정 내용 감사 |
| `build_prompt` | `/build_prompt <요청>` — composer trigger.md를 실행하면서 `<요청>`을 `[Rough request]` 아래에 자동 삽입 |

---

## 5. 외부 참조

> 자주 참조하는 외부 문서/대시보드/이슈 트래커가 있으면 여기.

- (TODO)
