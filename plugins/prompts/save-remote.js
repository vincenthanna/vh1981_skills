#!/usr/bin/env node

/**
 * 원격 프롬프트 저장 CLI 도구
 * 다른 머신에서 프롬프트 저장소 서버로 프롬프트를 전송
 */

const readline = require('readline');

// 설정 (환경 변수 또는 명령행 인자)
const SERVER_URL = process.env.PROMPT_SERVER_URL || 'http://localhost:3000';
const API_KEY = process.env.PROMPT_API_KEY || 'your-secret-api-key';

async function savePrompt(title, content, options = {}) {
  const url = `${SERVER_URL}/external/prompts`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({
        title,
        content,
        repo: options.repo || 'general',
        tags: options.tags ? options.tags.split(',').map(t => t.trim()) : [],
        source: 'cli',
        hostname: require('os').hostname()
      })
    });

    const result = await response.json();

    if (response.ok && result.success) {
      console.error('✅ 프롬프트가 저장되었습니다!');
      console.error(`ID: ${result.id}`);
      console.error(`제목: ${result.title}`);
      console.error(`Repo: ${result.repo}`);
      return result;
    } else {
      console.error('❌ 저장 실패:', result.error || 'Unknown error');
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ 연결 실패:', error.message);
    console.error(`서버가 실행 중인지 확인하세요: ${SERVER_URL}`);
    process.exit(1);
  }
}

async function saveConversation(messages, options = {}) {
  const url = `${SERVER_URL}/external/conversation`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({
        messages,
        repo: options.repo || 'general',
        tags: options.tags ? options.tags.split(',').map(t => t.trim()) : [],
        title: options.title || 'Conversation'
      })
    });

    const result = await response.json();

    if (response.ok && result.success) {
      console.error(`✅ ${result.saved}개의 프롬프트가 저장되었습니다!`);
      return result;
    } else {
      console.error('❌ 저장 실패:', result.error || 'Unknown error');
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ 연결 실패:', error.message);
    process.exit(1);
  }
}

// 표준 입력에서 읽기
async function readFromStdin() {
  const rl = readline.createInterface({
    input: process.stdin,
    crlfDelay: Infinity
  });

  const lines = [];
  for await (const line of rl) {
    lines.push(line);
  }
  return lines.join('\n');
}

// 메인
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error(`
프롬프트 저장소 CLI 도구

사용법:
  echo "내용" | save-remote "제목"                    # 표준 입력에서 내용 읽기
  save-remote "제목" "내용"                           # 직접 내용 입력
  save-remote "제목" "내용" --repo my-project         # 특정 repo에 저장
  save-remote "제목" "내용" --tags tag1,tag2          # 태그 지정

환경 변수:
  PROMPT_SERVER_URL  서버 URL (기본: http://localhost:3000)
  PROMPT_API_KEY     API 키 (기본: your-secret-api-key)

예시:
  export PROMPT_SERVER_URL=http://192.168.1.100:3000
  export PROMPT_API_KEY=my-secret-key
  cat prompt.txt | save-remote "내 프롬프트"
    `);
    process.exit(1);
  }

  const title = args[0];
  let content = args[1];
  const options = {};

  // 옵션 파싱
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--repo' && args[i + 1]) {
      options.repo = args[++i];
    } else if (args[i] === '--tags' && args[i + 1]) {
      options.tags = args[++i];
    } else if (args[i] === '--title' && args[i + 1]) {
      options.title = args[++i];
    }
  }

  // 표준 입력 확인
  if (!content && !process.stdin.isTTY) {
    content = await readFromStdin();
  }

  if (!content) {
    console.error('❌ 내용이 필요합니다');
    process.exit(1);
  }

  await savePrompt(title, content, options);
}

main();
