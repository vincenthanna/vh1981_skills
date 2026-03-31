#!/bin/bash
# Claude Code 프롬프트 자동 저장 스크립트
# 사용법: ./save-prompt.sh "프롬프트 제목" "repo-name" "tag1,tag2" "프롬프트 내용"

TITLE="$1"
REPO="${2:-general}"
TAGS="${3:-}"
CONTENT="$4"
SERVER_URL="${PROMPT_SERVER_URL:-http://localhost:3000}"

if [ -z "$TITLE" ] || [ -z "$CONTENT" ]; then
  echo "사용법: $0 \"제목\" \"repo\" \"태그1,태그2\" \"내용\""
  exit 1
fi

curl -s -X POST "$SERVER_URL/api/prompts" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"$TITLE\",
    \"repo\": \"$REPO\",
    \"tags\": [$(echo "$TAGS" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/' | sed 's/,/","/g')],
    \"content\": $(echo "$CONTENT" | jq -Rs .)
  }"

echo ""
