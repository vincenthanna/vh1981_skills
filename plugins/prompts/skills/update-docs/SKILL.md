# update-docs

저장소의 변경사항을 분석하여 문서를 자동으로 업데이트합니다.

## 입력
$ARGUMENTS

## 동작

### 1단계: 변경사항 분석

```bash
git status --porcelain
git diff HEAD --name-only
```

### 2단계: 영향받는 문서 파악

| 변경 파일 | 업데이트 대상 |
|-----------|--------------|
| `server.js` | README.md, CLAUDE.md |
| `.claude/commands/*.md` | docs/SKILL_GUIDE.md |
| `mcp-server*.js` | MCP.md, docs/ADVANCED_USAGE.md |
| `web/*` | README.md |
| `package.json` | README.md |

### 3단계: 문서 업데이트

변경사항을 반영하여 관련 문서를 업데이트

### 4단계: 업데이트 내용 요약

- 변경된 파일
- 업데이트된 문서
- 주요 변경 내용

## 옵션

- `--check`: 실제 수정 없이 업데이트 필요 여부만 확인
- `--verbose`: 상세한 분석 결과 출력

## 사용 예시

```
/update-docs              # 변경사항 분석 후 문서 업데이트
/update-docs --check      # 업데이트 필요 여부만 확인
```
