# save-prompt

프롬프트를 원격 저장소에 저장합니다.

## 입력
$ARGUMENTS

## 환경변수 (필수)
- `PROMPT_SERVER_URL`: 저장소 서버 URL (예: http://192.168.1.100:24123)
- `PROMPT_API_KEY`: API 인증 키

## 동작

1. 저장 대상 결정:
   - `$ARGUMENTS`에 직접 내용이 있으면: 해당 내용을 저장
   - `$ARGUMENTS`가 없거나 옵션만 있으면: 이전 대화에서 **사용자가 Claude에게 보낸 메시지(질문/요청)**를 추출하여 저장
   - **중요: Claude의 응답이 아닌, 사용자가 입력한 프롬프트를 저장해야 함**

2. 검색 범위 (기본값: 최근 5개):
   - `--last N` : 최근 N개의 사용자 메시지에서 추출
   - `--all` : 전체 대화에서 추출
   - 옵션 없으면: 최근 5개 사용자 메시지에서 가장 유용한 것 선택

3. 추가 옵션:
   - `--repo <name>` : 저장할 repo 지정 (기본값: general 또는 현재 프로젝트명)
   - `--tags <tag1,tag2>` : 태그 지정 (쉼표로 구분)

4. 다음 curl 명령으로 원격 서버에 저장하세요:

```bash
curl -X POST "${PROMPT_SERVER_URL}/external/prompts" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${PROMPT_API_KEY}" \
  -d '{
    "title": "프롬프트 제목",
    "content": "프롬프트 내용",
    "repo": "프로젝트명 또는 general",
    "tags": ["태그1", "태그2"],
    "source": "claude-code-skill",
    "hostname": "'$(hostname)'"
  }'
```

5. 저장 결과를 사용자에게 알려주세요.

## 사용 예시
- `/save-prompt` - 최근 5개 메시지에서 유용한 프롬프트 추출하여 저장
- `/save-prompt --last 10` - 최근 10개 메시지에서 추출
- `/save-prompt --all` - 전체 대화에서 추출
- `/save-prompt 이 코드 리팩토링해줘` - 특정 내용 직접 저장
- `/save-prompt --repo my-project --tags refactoring` - repo와 태그 지정
