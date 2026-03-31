#!/bin/bash

# MCP 자동 설치 스크립트

set -e

CONFIG_DIR="$HOME/.claude"
CONFIG_FILE="$CONFIG_DIR/settings.json"
# 스크립트 위치 기준으로 프로젝트 경로 자동 감지
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=${1:-24123}

echo "🔧 MCP 플러그인 자동 설치를 시작합니다..."

# 설정 디렉토리 자동 생성
if [ ! -d "$CONFIG_DIR" ]; then
  echo "📁 설정 디렉토리를 생성합니다: $CONFIG_DIR"
  mkdir -p "$CONFIG_DIR"
fi

# 기존 설정 백업
if [ -f "$CONFIG_FILE" ]; then
  cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d%H%M%S)"
  echo "✅ 기존 설정을 백업했습니다"
fi

# 설정 파일 생성/업데이트
if [ ! -f "$CONFIG_FILE" ]; then
  echo "{}" > "$CONFIG_FILE"
fi

# MCP 설정 추가 (jq가 없으면 node 사용)
if command -v jq &> /dev/null; then
  tmp=$(mktemp)
  jq --arg port "$PORT" --arg dir "$PROJECT_DIR" '.mcpServers["prompts-storage"] = {
    "command": "node",
    "args": [$dir + "/mcp-server-http.js"],
    "env": {"PROMPT_API_URL": ("http://localhost:" + $port + "/api")}
  }' "$CONFIG_FILE" > "$tmp"
  mv "$tmp" "$CONFIG_FILE"
else
  # node.js로 JSON 수정
  node -e "
    const fs = require('fs');
    const config = JSON.parse(fs.readFileSync('$CONFIG_FILE', 'utf8'));
    config.mcpServers = config.mcpServers || {};
    config.mcpServers['prompts-storage'] = {
      command: 'node',
      args: ['$PROJECT_DIR/mcp-server-http.js'],
      env: { PROMPT_API_URL: 'http://localhost:$PORT/api' }
    };
    fs.writeFileSync('$CONFIG_FILE', JSON.stringify(config, null, 2));
  "
fi

echo "✅ MCP 설치 완료!"
echo ""
echo "📋 설정 정보:"
echo "  - 설정 파일: $CONFIG_FILE"
echo "  - 포트: $PORT"
echo "  - 서버 경로: $PROJECT_DIR"
echo ""
echo "🔄 다음 단계:"
echo "  1. 서버 실행: npm start"
echo "  2. Claude Code 재시작"
echo ""
echo "✨ 사용 방법:"
echo '  "내 프롬프트 목록 보여줘"'
echo '  "이 프롬프트 저장해줘"'
