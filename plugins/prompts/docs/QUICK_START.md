# 빠른 시작 가이드

Claude Code에서 프롬프트를 저장하고 재사용하기 위한 5분 가이드.

## 1단계: 서버 실행

```bash
cd /path/to/prompts_storage
npm install
npm start
```

서버가 `http://localhost:24123`에서 실행됩니다.

## 2단계: Skill 사용 설정

### 이 프로젝트에서 직접 사용하는 경우

```bash
cd /path/to/prompts_storage
claude
```

그냥 실행하면 `/save-prompt` Skill이 바로 사용 가능합니다.

### 다른 프로젝트에서 사용하는 경우

대상 프로젝트에 `.claude/settings.local.json` 파일 생성:

```json
{
  "env": {
    "PROMPT_SERVER_URL": "http://localhost:24123",
    "PROMPT_API_KEY": "your-secret"
  },
  "permissions": {
    "allow": ["Bash(curl:*)"]
  }
}
```

그리고 skill 파일 복사:

```bash
mkdir -p /your/project/.claude/commands
cp /path/to/prompts_storage/.claude/commands/save-prompt.md /your/project/.claude/commands/
```

## 3단계: 프롬프트 저장하기

Claude Code 대화 중에:

```
/save-prompt
```

최근 대화에서 유용한 프롬프트를 자동으로 추출하여 저장합니다.

### 옵션

```
/save-prompt                           # 최근 5개 메시지에서 추출
/save-prompt --last 10                 # 최근 10개 메시지에서 추출
/save-prompt --repo my-project         # 특정 repo에 저장
/save-prompt 이 코드 리팩토링해줘      # 직접 내용 저장
```

## 4단계: 저장된 프롬프트 확인

### 웹 UI

브라우저에서 `http://localhost:24123` 접속

### 파일 시스템

`prompts/{repo}/*.md` 경로에 Markdown 형식으로 저장됨

## 완료!

이제 Claude Code에서 사용한 유용한 프롬프트들을 체계적으로 저장하고 관리할 수 있습니다.

---

## 다음 단계

- [Skill 상세 가이드](SKILL_GUIDE.md) - 더 많은 사용법
- [프롬프트 템플릿](PROMPT_TEMPLATES.md) - 재사용 가능한 템플릿들
- [고급 사용법](ADVANCED_USAGE.md) - 원격 저장, MCP, Hook 등
