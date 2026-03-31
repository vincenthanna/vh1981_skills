# /save-prompt Skill 상세 가이드

Claude Code에서 프롬프트를 저장하는 `/save-prompt` Skill의 상세 사용법입니다.

## 기본 사용법

### 자동 추출 저장

대화 중에 `/save-prompt`만 입력하면 최근 대화에서 유용한 프롬프트를 자동으로 추출합니다.

```
사용자: 이 함수 성능을 최적화해줘
Claude: (최적화 수행)
사용자: /save-prompt
Claude: "함수 성능 최적화 요청" 프롬프트를 저장했습니다.
```

### 직접 내용 저장

특정 내용을 직접 저장할 수 있습니다.

```
/save-prompt 이 클래스를 싱글톤 패턴으로 리팩토링해줘
```

## 옵션

### --last N

최근 N개의 사용자 메시지에서 추출합니다.

```
/save-prompt --last 10    # 최근 10개 메시지 검토
/save-prompt --last 3     # 최근 3개 메시지만 검토
```

### --all

전체 대화에서 추출합니다. 긴 대화에서 중요한 프롬프트를 찾을 때 유용합니다.

```
/save-prompt --all
```

### --repo \<name\>

저장할 repo(카테고리)를 지정합니다.

```
/save-prompt --repo backend         # backend repo에 저장
/save-prompt --repo frontend         # frontend repo에 저장
/save-prompt --repo infra            # infra repo에 저장
```

기본값은 `general` 또는 현재 프로젝트명입니다.

### --tags \<tag1,tag2\>

태그를 지정합니다. 쉼표로 구분합니다.

```
/save-prompt --tags refactoring,python
/save-prompt --tags debugging,performance
```

### 옵션 조합

여러 옵션을 함께 사용할 수 있습니다.

```
/save-prompt --repo my-project --tags optimization,critical --last 10
/save-prompt --all --repo research --tags ai,prompt-engineering
```

## 자연어 사용

Skill을 직접 호출하지 않고 자연어로 요청할 수도 있습니다.

```
"이 대화 내용 저장해줘"
"방금 한 질문 프롬프트로 저장해줘"
"이 요청 나중에 재사용할 수 있게 저장해줘"
```

## 저장되는 내용

### 프롬프트 메타데이터

| 필드 | 설명 |
|------|------|
| title | 프롬프트 제목 (자동 생성 또는 지정) |
| repo | 저장 카테고리 |
| tags | 태그 목록 |
| created_at | 생성 시간 |
| source | 출처 (claude-code-skill) |
| hostname | 저장한 머신명 |

### 파일 형식

Markdown 파일로 저장됩니다:

```markdown
---
title: 함수 성능 최적화 요청
repo: my-project
tags:
  - optimization
  - python
created_at: '2024-01-15T10:30:00.000Z'
source: claude-code-skill
hostname: my-machine
---
이 함수의 시간 복잡도를 O(n)에서 O(log n)으로 개선해줘.
현재 대용량 데이터셋에서 성능 문제가 발생하고 있어.
```

## 저장 위치

```
prompts/
├── general/
│   └── 1705312200000-일반-프롬프트.md
├── my-project/
│   └── 1705312300000-리팩토링-요청.md
└── backend/
    └── 1705312400000-api-설계-요청.md
```

## 환경 변수 설정

Skill이 작동하려면 환경 변수가 필요합니다.

### 프로젝트별 설정 (.claude/settings.local.json)

```json
{
  "env": {
    "PROMPT_SERVER_URL": "http://localhost:24123",
    "PROMPT_API_KEY": "your-secret-key"
  },
  "permissions": {
    "allow": ["Bash(curl:*)"]
  }
}
```

### 전역 설정 (~/.claude/settings.json)

```json
{
  "env": {
    "PROMPT_SERVER_URL": "http://192.168.1.100:24123",
    "PROMPT_API_KEY": "your-secret-key"
  }
}
```

## 문제 해결

### Skill이 인식되지 않음

Claude Code를 재시작하세요:

```bash
exit
claude
```

### 저장 실패

1. 서버가 실행 중인지 확인:
   ```bash
   curl http://localhost:24123/external/health
   ```

2. API 키가 올바른지 확인:
   - `.claude/settings.local.json`의 `PROMPT_API_KEY`
   - 서버의 `.env` 파일의 `API_KEY`

3. 네트워크 연결 확인:
   - 원격 서버인 경우 방화벽 설정 확인
