---

Claude Agent SDK Demos

Claude Agent SDK를 시연하는 데모 애플리케이션 모음. 로컬 개발과 학습 용도이며, production 사용을 위한 것은 아니다.

## Demos

| Demo | Description |
|------|-------------|
| Hello World | Agent SDK 시작하기 |
| Hello World V2 | Session API 사용 (`unstable_v2_*`) |
| Email Agent | IMAP 기반 email 어시스턴트 |
| Excel Demo | Claude로 스프레드시트 조작 |
| Research Agent | 병렬 subagent를 사용한 다중 agent 시스템 |
| AskUserQuestion Previews | agent 질문에 대한 HTML 미리보기 카드 |
| Simple Chat App | WebSocket streaming을 사용하는 React + Express 채팅 UI |
| Resume Generator | 웹 검색 기반 `.docx` 이력서 생성 |

## Installation

```bash
git clone https://github.com/anthropics/claude-agent-sdk-demos.git
cd claude-agent-sdk-demos
```

각 데모는 자체 디렉터리와 셋업 지침이 있다.

## Requirements

- Bun runtime (또는 Node.js 18+)
- Anthropic API key (`ANTHROPIC_API_KEY`)

## Key Features

- 다중 agent 조정 패턴
- WebSocket을 통한 streaming
- HTML 미리보기 렌더링
- V2 Session API 예제

## License

MIT

## Links

- GitHub: https://github.com/anthropics/claude-agent-sdk-demos
