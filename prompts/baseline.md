# Baseline

여러 repo에서 작업할 때 공통으로 적용하고 싶은 규칙과, 자주 쓰는 prompt들의 위치/기능을 모아둔 인덱스 문서.

작업 시작 시점에 이 파일을 읽혀서 컨텍스트를 잡는 용도로 사용한다.

---

## 1. 공통 작업 규칙 (Global Rules)

### 1.1 응답 스타일
- 한국어로 응답한다.
- 결과/결정만 직접 말한다. 사고 과정 narration 금지.
- 불필요한 칭찬, 사과, 머리말 금지.

### 1.2 코드 작성
- 기존 파일 수정 우선, 새 파일 생성은 꼭 필요할 때만.
- 주석은 *왜* 가 명확하지 않을 때만. *무엇* 을 설명하는 주석 금지.
- 요청 범위를 벗어나는 리팩터, 추상화, 미래 대비 코드 금지.
- 사용하지 않는 코드/import는 남기지 말고 삭제.
- 에러 처리는 시스템 경계에서만. 내부 코드는 신뢰.

### 1.3 위험 동작
- 파괴적/되돌리기 어려운 동작 전에는 반드시 확인 (rm -rf, force push, reset --hard, DB drop 등).
- `--no-verify`, hook skip 금지 (명시 요청 시에만).
- commit/push는 명시 요청 시에만.

### 1.4 작업 진행
- 모호한 요구는 추측하지 말고 질문.
- UI 변경은 브라우저에서 실제 동작 확인 후 완료 보고.
- 작업 중간/종료 보고는 1-2문장.

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
| `worklog:devlog` | 통합 작업 로그 + 조사 보고서 (`docs/devlog/<project>/`) |
| `worklog:worklog` | 세션 작업 히스토리 (`docs/history/<subject>/`) |
| `worklog:prjdocs` | 프로젝트 조사/분석 보고서 (`docs/projects/<project>/`) |
| `bug-fix` | 분석 → 방향 제시 → 승인 후 구현의 3단계 버그 수정 |
| `analyze` | 코드 수정 없이 분석만 |
| `verify` | 검증-수정 반복 사이클 |
| `write-report` | 분석/테스트 결과 보고서화 |
| `improve-prompt` | prompt를 Claude Code용으로 개선 |
| `search-prompt` | prompt 자연어 검색 |
| `pr-audit` | 현재 branch PR 수정 내용 감사 |

---

## 5. 외부 참조

> 자주 참조하는 외부 문서/대시보드/이슈 트래커가 있으면 여기.

- (TODO)
