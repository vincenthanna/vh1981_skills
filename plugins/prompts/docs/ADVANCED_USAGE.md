# 고급 사용법

프롬프트 저장소의 고급 기능: 원격 저장, MCP 통합, Hook 자동화 등을 다룹니다.

---

## 원격 서버 설정

여러 머신에서 하나의 프롬프트 저장소를 공유할 수 있습니다.

### 서버 설정

1. **환경 변수 설정**

   ```bash
   cp .env.example .env
   ```

   `.env` 파일 수정:
   ```env
   PORT=24123
   HOST=0.0.0.0      # 외부 접속 허용
   API_KEY=secure-random-key-here
   ```

2. **서버 시작**

   ```bash
   npm start
   ```

3. **방화벽 설정**

   ```bash
   # Ubuntu/Debian
   sudo ufw allow 24123/tcp

   # CentOS/RHEL
   sudo firewall-cmd --add-port=24123/tcp --permanent
   sudo firewall-cmd --reload
   ```

### 클라이언트 설정

각 클라이언트 머신에서:

```json
{
  "env": {
    "PROMPT_SERVER_URL": "http://서버IP:24123",
    "PROMPT_API_KEY": "secure-random-key-here"
  }
}
```

### CLI 도구 사용

```bash
# 환경 변수 설정
export PROMPT_SERVER_URL=http://192.168.1.100:24123
export PROMPT_API_KEY=your-key

# 프롬프트 저장
./save-remote.js "제목" "프롬프트 내용"
./save-remote.js "제목" "내용" --repo my-project --tags tag1,tag2

# 파이프라인 사용
cat prompt.txt | ./save-remote.js "파일에서 읽은 프롬프트"
```

---

## MCP 서버 통합

Model Context Protocol(MCP)을 통해 Claude Code에서 직접 프롬프트를 관리할 수 있습니다.

### MCP 서버 설정

Claude Code 설정 파일에 추가:

**macOS**: `~/.config/claude-code/config.json`
**Linux**: `~/.config/claude-code/config.json`

```json
{
  "mcpServers": {
    "prompts-storage": {
      "command": "node",
      "args": ["/path/to/prompts_storage/mcp-server.js"]
    }
  }
}
```

### HTTP 기반 MCP 서버

원격 서버와 연동:

```json
{
  "mcpServers": {
    "prompts-storage": {
      "command": "node",
      "args": ["/path/to/prompts_storage/mcp-server-http.js"],
      "env": {
        "PROMPT_API_URL": "http://서버IP:24123/api"
      }
    }
  }
}
```

### MCP 도구 목록

| 도구 | 설명 |
|------|------|
| `save_prompt` | 프롬프트 저장 |
| `list_prompts` | 프롬프트 목록 조회 |
| `get_prompt` | 특정 프롬프트 조회 |
| `search_prompts` | 프롬프트 검색 |
| `get_repos` | repo 목록 |
| `get_tags` | 태그 목록 |

### MCP 사용 예시

Claude Code에서 자연어로 요청:

```
"리팩토링 관련 프롬프트 검색해줘"
→ search_prompts 도구 호출

"모든 프롬프트 보여줘"
→ list_prompts 도구 호출

"이 대화 저장해줘"
→ save_prompt 도구 호출
```

---

## Hook 자동화

Claude Code Hook을 사용하여 프롬프트를 자동으로 저장할 수 있습니다.

### Hook 설정

Claude Code 설정 파일에 추가:

```json
{
  "hooks": {
    "UserPromptSubmit": "/path/to/prompts_storage/save-prompt.sh \"{{prompt}}\" \"{{repo}}\" \"claude-code\" \"{{full_prompt}}\""
  }
}
```

### Hook 스크립트 (save-prompt.sh)

```bash
#!/bin/bash
TITLE="$1"
REPO="$2"
TAGS="$3"
CONTENT="$4"

curl -X POST "${PROMPT_SERVER_URL:-http://localhost:24123}/external/prompts" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${PROMPT_API_KEY}" \
  -d "{
    \"title\": \"$TITLE\",
    \"repo\": \"$REPO\",
    \"tags\": [\"$TAGS\"],
    \"content\": \"$CONTENT\",
    \"source\": \"hook\"
  }"
```

### 주의사항

- Hook은 모든 프롬프트를 자동으로 저장합니다
- 민감한 정보가 포함된 프롬프트도 저장될 수 있습니다
- 필요한 경우 필터링 로직을 추가하세요

---

## API 고급 사용법

### 프롬프트 결합

여러 프롬프트를 하나로 결합:

```bash
curl -X POST "http://localhost:24123/api/prompts/combine" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["repo1/prompt1", "repo2/prompt2"],
    "newTitle": "결합된 프롬프트",
    "separator": "\n\n---\n\n"
  }'
```

### 템플릿 변수 치환

`{{variable}}` 형식의 변수를 치환:

```bash
curl -X POST "http://localhost:24123/api/prompts/template" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "repo/prompt-id",
    "variables": {
      "language": "Python",
      "framework": "FastAPI"
    }
  }'
```

### 대화 일괄 저장

여러 메시지를 한 번에 저장:

```bash
curl -X POST "http://localhost:24123/external/conversation" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "repo": "conversations",
    "tags": ["session-20240115"],
    "messages": [
      {"title": "첫 번째 질문", "content": "..."},
      {"title": "두 번째 질문", "content": "..."}
    ]
  }'
```

---

## 백업 및 복원

### Git으로 백업

```bash
cd prompts_storage
git add prompts/
git commit -m "Backup prompts $(date +%Y-%m-%d)"
git push origin main
```

### 자동 백업 스크립트

```bash
#!/bin/bash
# backup-prompts.sh
cd /path/to/prompts_storage
git add prompts/
git commit -m "Auto backup $(date +%Y-%m-%d_%H:%M)" 2>/dev/null || true
git push origin main 2>/dev/null || true
```

Cron 설정:
```bash
# 매일 자정에 백업
0 0 * * * /path/to/backup-prompts.sh
```

---

## 보안 권장사항

1. **API 키 관리**
   - 강력한 랜덤 키 사용 (`openssl rand -hex 32`)
   - 키를 환경 변수로 관리
   - `.env` 파일은 `.gitignore`에 추가

2. **네트워크 보안**
   - 내부 네트워크에서만 사용
   - 공용 인터넷 노출 시 HTTPS 사용 (역방향 프록시)
   - 방화벽으로 접근 제한

3. **데이터 보안**
   - 민감한 정보가 포함된 프롬프트 주의
   - 정기적인 백업
   - 접근 로그 모니터링

### HTTPS 설정 (nginx 예시)

```nginx
server {
    listen 443 ssl;
    server_name prompts.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:24123;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 문제 해결

### 서버 로그 확인

```bash
# 포그라운드 실행으로 로그 확인
node server.js

# 또는 pm2 사용
pm2 start server.js --name prompts-storage
pm2 logs prompts-storage
```

### 연결 테스트

```bash
# 서버 상태 확인
curl http://localhost:24123/external/health

# API 키 테스트
curl -H "X-API-Key: your-key" http://localhost:24123/external/health

# 프롬프트 목록
curl http://localhost:24123/api/prompts
```

### 일반적인 문제

| 문제 | 해결 방법 |
|------|----------|
| 연결 거부 | 서버 실행 여부, 포트, 방화벽 확인 |
| 401 Unauthorized | API 키 확인 |
| CORS 에러 | 서버의 CORS 설정 확인 |
| 파일 저장 실패 | prompts/ 디렉토리 권한 확인 |
