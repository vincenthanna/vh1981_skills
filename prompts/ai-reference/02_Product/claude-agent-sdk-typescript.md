---

Claude Agent SDK (TypeScript)

Claude Agent SDK를 사용하면 Claude Code의 기능을 갖춘 AI agent를 프로그래밍 방식으로 구축할 수 있다. 코드베이스를 이해하고, 파일을 편집하고, 명령을 실행하며, 복잡한 workflow를 수행하는 자율 agent를 만들 수 있다.

자세한 내용은 official documentation에서 확인한다.

Installation
npm install @anthropic-ai/claude-agent-sdk

요구 사항: Node.js 18+

참고: Claude Code CLI는 패키지에 자동으로 번들된다. SDK는 기본적으로 번들된 CLI를 사용한다. 시스템 전역 설치를 선호한다면 Claude Code를 별도로 설치하거나 옵션에서 커스텀 경로를 지정할 수 있다.

Quick Start
import { query } from '@anthropic-ai/claude-agent-sdk';

for await (const message of query({ prompt: 'What is 2 + 2?' })) {
  console.log(message);
}

Key Features

Codebase Understanding: 프로젝트 구조를 프로그래밍 방식으로 분석하고 탐색
File Operations: AI 기반 agent를 통해 파일을 읽고, 쓰고, 편집
Command Execution: agent workflow 내에서 shell 명령과 스크립트 실행
Complex Workflows: 다단계 개발 작업을 위한 자율 agent 구축
Tool Integration: Claude Code의 전체 도구 세트(Read, Write, Edit, Bash 등) 접근
MCP Server Support: 확장 기능을 위해 Model Context Protocol 서버에 연결
Custom Hooks: agent loop의 특정 지점에서 agent 동작을 가로채고 제어

API Overview

query() Function
Claude와 상호작용하는 가장 단순한 방법이다. 응답 메시지의 async iterator를 반환한다:
import { query, ClaudeAgentOptions } from '@anthropic-ai/claude-agent-sdk';

// Simple query
for await (const message of query({ prompt: 'Hello Claude' })) {
  console.log(message);
}

// With options
const options: ClaudeAgentOptions = {
  systemPrompt: 'You are a helpful assistant',
  maxTurns: 1,
  allowedTools: ['Read', 'Write', 'Bash'],
  permissionMode: 'acceptEdits',
};

for await (const message of query({ prompt: 'Create a hello.ts file', options })) {
  console.log(message);
}

Working Directory
const options: ClaudeAgentOptions = {
  cwd: '/path/to/project',
};

Tool Permissions
allowedTools는 권한 허용 목록이다: 나열된 도구는 자동 승인되고, 나열되지 않은 도구는 permissionMode로 넘어가 결정된다. 특정 도구를 차단하려면 disallowedTools를 사용한다.
const options: ClaudeAgentOptions = {
  allowedTools: ['Read', 'Write', 'Bash'],
  permissionMode: 'acceptEdits',
};

Migrating from the Claude Code SDK
Claude Code SDK는 이제 Claude Agent SDK가 되었다. 주요 breaking change는 다음과 같다:

ClaudeCodeOptions가 ClaudeAgentOptions로 이름 변경
병합된 system prompt 설정
설정 격리와 명시적 제어
새로운 프로그래밍 방식 서브에이전트(subagent) 및 session forking 기능

자세한 내용은 migration guide를 확인한다.

Reporting Bugs
피드백을 환영한다. 버그를 보고하거나 기능을 요청하려면 GitHub issue를 등록한다.

Connect on Discord
Claude Developers Discord에 참여해 Claude Agent SDK로 개발하는 다른 개발자들과 소통하라. 도움을 받고, 피드백을 공유하며, 커뮤니티와 프로젝트를 논의할 수 있다.

Data collection, usage, and retention
Claude Agent SDK를 사용할 때 우리는 사용 데이터(코드 수락 또는 거절 등), 관련 대화 데이터, /bug 명령을 통해 제출된 사용자 피드백을 포함한 피드백을 수집한다.
How we use your data
data usage policies를 참조한다.
Privacy safeguards
민감한 정보에 대한 제한된 보관 기간, 사용자 세션 데이터에 대한 접근 제한, 피드백을 모델 학습에 사용하지 않는다는 명확한 정책을 포함해 데이터를 보호하기 위한 여러 안전장치를 마련해 두었다.
자세한 내용은 Commercial Terms of Service와 Privacy Policy를 검토하라.
License and terms
이 SDK의 사용은 Anthropic's Commercial Terms of Service의 적용을 받으며, 자신의 고객 및 최종 사용자에게 제공하는 제품과 서비스에 이를 사용하는 경우에도 마찬가지다. 다만 특정 구성요소나 의존성이 해당 구성요소의 LICENSE 파일에 명시된 다른 라이선스의 적용을 받는 경우는 예외다.
