#!/usr/bin/env node
/**
 * auto-save.js — UserPromptSubmit hook에서 호출
 * stdin으로 전달된 사용자 프롬프트를 평가하여 저장 가치가 있으면 서버에 저장
 */

const PROMPT_SERVER_URL = process.env.PROMPT_SERVER_URL || 'http://localhost:24123';
const PROMPT_API_KEY = process.env.PROMPT_API_KEY || '';
const MIN_LENGTH = 20;

// 단답형/사소한 패턴
const TRIVIAL_PATTERNS = [
  /^(네|예|응|아니|ㅇㅇ|ㄴㄴ|ok|yes|no|nope|yep|y|n|sure)\.?$/i,
  /^(고마워|감사|ㄱㅅ|ㅊㅋ|ㅎㅎ|ㅋㅋ|thanks|thx|ty|lgtm|sgtm)\.?$/i,
  /^(계속|진행|해줘|해|하자|ㄱㄱ|go|continue|proceed|next)\.?$/i,
  /^(커밋|push|푸시|머지|merge)[\s]*(해줘|해|하자)?\.?$/i,
  /^(확인|알겠|알았|good|great|nice|cool|perfect|맞아|맞다)\.?$/i,
  /^(뭐|왜|어디|언제|뭔데)\?*$/,
  /^\/\w/,  // slash 커맨드
  /^![\s]/,  // shell 커맨드
];

function isTrivial(text) {
  const trimmed = text.trim();

  if (trimmed.length < MIN_LENGTH) return true;

  for (const pattern of TRIVIAL_PATTERNS) {
    if (pattern.test(trimmed)) return true;
  }

  // 단어 수 체크 — 3단어 이하면 사소한 것으로 간주
  const words = trimmed.split(/\s+/).filter(w => w.length > 0);
  if (words.length <= 3) return true;

  return false;
}

function extractTitle(content) {
  // 첫 줄 또는 첫 50자를 제목으로
  const firstLine = content.split('\n')[0].trim();
  if (firstLine.length <= 60) return firstLine;
  return firstLine.substring(0, 57) + '...';
}

async function main() {
  // stdin에서 hook input 읽기
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  let prompt;
  try {
    const data = JSON.parse(input);
    // UserPromptSubmit hook input 형식
    prompt = data.prompt || data.content || data.message || '';
    if (typeof prompt !== 'string') {
      prompt = JSON.stringify(prompt);
    }
  } catch {
    prompt = input.trim();
  }

  if (!prompt || isTrivial(prompt)) {
    process.exit(0);
  }

  const hostname = require('os').hostname();
  const payload = JSON.stringify({
    title: extractTitle(prompt),
    content: prompt,
    repo: 'general',
    tags: ['auto-saved'],
    source: 'hook-auto-save',
    hostname: hostname,
  });

  try {
    const res = await fetch(`${PROMPT_SERVER_URL}/external/prompts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': PROMPT_API_KEY,
      },
      body: payload,
    });
    if (!res.ok) {
      // 실패해도 조용히 종료 (사용자 경험 방해 안 함)
      process.exit(0);
    }
  } catch {
    // 서버 미실행 등 — 조용히 무시
    process.exit(0);
  }
}

main();
