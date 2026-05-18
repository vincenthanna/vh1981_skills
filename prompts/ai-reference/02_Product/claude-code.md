---

Claude Code

Claude Code는 터미널에 상주하는 agentic 코딩 도구로, 코드베이스를 이해하고 정형화된 작업을 실행하며, 복잡한 코드를 설명하고, git workflow를 처리해 더 빠르게 코딩하도록 돕는다 -- 모두 자연어 명령으로 가능하다. 터미널, IDE에서 사용하거나 GitHub에서 @claude를 태그하라.

자세한 내용은 official documentation에서 확인한다.

Get started
참고: npm을 통한 설치는 deprecated 되었다. 아래 권장 방식 중 하나를 사용하라.

추가 설치 옵션, 제거 절차, 문제 해결은 setup documentation을 참조한다.

Claude Code 설치:
MacOS/Linux (권장):
curl -fsSL https://claude.ai/install.sh | bash
Homebrew (MacOS/Linux):
brew install --cask claude-code
Windows (권장):
irm https://claude.ai/install.ps1 | iex
WinGet (Windows):
winget install Anthropic.ClaudeCode
NPM (Deprecated):
npm install -g @anthropic-ai/claude-code

프로젝트 디렉터리로 이동한 뒤 claude를 실행한다.

Key Features

Agentic Code Execution: 리팩토링, 테스트 작성, 버그 수정 같은 정형 코딩 작업을 자율적으로 실행
Codebase Understanding: 프로젝트 구조, 의존성, 패턴을 분석하고 이해
Natural Language Interface: 대화형 명령으로 모든 것을 제어 -- 특별한 문법 불필요
Git Workflow Integration: commit, pull request, 코드 리뷰, branch 관리를 처리
Code Explanation: 복잡한 코드 영역, 아키텍처, 디자인 패턴을 설명
Multi-File Editing: 프로젝트 내 여러 파일에 걸친 조율된 변경을 수행
Command Execution: shell 명령, 빌드, 테스트, 기타 개발 도구를 실행

Platform Support

Terminal/CLI: 주된 인터랙티브 인터페이스 -- 임의의 프로젝트 디렉터리에서 claude 실행
IDE Integration: 통합 개발 경험을 위한 VS Code extension 제공
GitHub Integration: issue와 pull request에서 @claude를 태그해 자동 지원
Codespaces: GitHub Codespaces 및 기타 클라우드 개발 환경에서 동작

CLI Commands
터미널에서 claude를 실행해 Claude Code를 시작한다. 내장 slash command는 다음과 같다:

/bug - Claude Code 내에서 직접 issue를 보고
/help - 사용 가능한 명령과 사용법 표시
/plugin - plugin 탐색, 설치, 관리
/clear - 대화 이력 삭제
/config - 설정 확인 및 수정

Configuration
Claude Code는 여러 방법으로 설정할 수 있다:

Project-level settings: 프로젝트 루트의 .claude/ 디렉터리
Custom commands: .claude/commands/에서 재사용 가능한 명령 정의
Environment variables: ANTHROPIC_API_KEY 및 기타 설정을 환경 변수로 지정

Hooks
hook은 Claude agent loop의 특정 지점에서 agent의 동작을 가로채고 제어할 수 있게 한다. 결정론적 처리와 자동화된 피드백을 가능하게 한다. hook은 다음과 같은 이벤트에 대해 정의할 수 있다:

PreToolUse: 도구가 실행되기 전에 동작 (승인, 거부, 또는 수정 가능)
PostToolUse: 도구 실행이 완료된 뒤 동작
Notification: agent 알림 시 트리거

MCP (Model Context Protocol) Support
Claude Code는 외부 도구와 데이터 소스로 기능을 확장하기 위한 MCP 서버를 지원한다. 프로젝트의 .mcp.json 파일에 MCP 서버를 설정해 데이터베이스, API, 기타 서비스에 연결한다.

Plugins
이 저장소는 커스텀 명령과 agent로 기능을 확장하는 여러 Claude Code plugin을 포함한다. plugin은 표준 구조를 따른다:

plugin-name/
  .claude-plugin/
    plugin.json      # Plugin metadata (required)
  .mcp.json          # MCP server configuration (optional)
  commands/          # Slash commands (optional)
  agents/            # Agent definitions (optional)
  skills/            # Skill definitions (optional)

/plugin install {plugin-name}로 plugin을 설치하거나 /plugin > Discover로 탐색한다. 자세한 문서는 plugin 디렉터리를 참조한다.

Claude Agent SDK
Claude Code의 기능에 프로그래밍 방식으로 접근하려면 TypeScript와 Python 양쪽에서 제공되는 Claude Agent SDK를 사용한다. 코드베이스를 이해하고 파일을 편집하며 명령을 실행하고 복잡한 workflow를 수행하는 자율 agent를 구축할 수 있다.

Reporting Bugs
피드백을 환영한다. Claude Code 내에서 직접 issue를 보고하려면 /bug 명령을 사용하거나 GitHub issue를 등록한다.

Connect on Discord
Claude Developers Discord에 참여해 Claude Code를 사용하는 다른 개발자들과 소통하라. 도움을 받고, 피드백을 공유하며, 커뮤니티와 프로젝트를 논의할 수 있다.

Data collection, usage, and retention
Claude Code를 사용할 때 우리는 사용 데이터(코드 수락 또는 거절 등), 관련 대화 데이터, /bug 명령을 통해 제출된 사용자 피드백을 포함한 피드백을 수집한다.
How we use your data
data usage policies를 참조한다.
Privacy safeguards
민감한 정보에 대한 제한된 보관 기간, 사용자 세션 데이터에 대한 접근 제한, 피드백을 모델 학습에 사용하지 않는다는 명확한 정책을 포함해 데이터를 보호하기 위한 여러 안전장치를 마련해 두었다.
자세한 내용은 Commercial Terms of Service와 Privacy Policy를 검토하라.
