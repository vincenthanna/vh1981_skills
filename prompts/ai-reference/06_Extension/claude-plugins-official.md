---

Claude Code Plugins Directory
Claude Code를 위한 고품질 plugin을 큐레이션한 디렉터리이다.

매우 중요: plugin을 설치, 업데이트, 사용하기 전에 반드시 해당 plugin을 신뢰할 수 있는지 확인하라. Anthropic은 plugin에 포함된 MCP 서버, 파일, 기타 소프트웨어를 통제하지 않으며, 의도대로 동작할지 또는 변경되지 않을지 보증할 수 없다. 자세한 내용은 각 plugin의 홈페이지를 참조하라.

Structure

/plugins - Anthropic이 개발하고 유지보수하는 내부 plugin
/external_plugins - 파트너와 커뮤니티가 만든 서드파티 plugin

Plugin Categories
Plugin은 Claude Code의 기능을 다음과 같은 여러 영역에서 확장한다:

Skills: 도메인별 지식이나 동작을 Claude Code에 추가하는 재사용 가능한 capability
MCP Integrations: 외부 도구, 데이터베이스, API에 접근할 수 있게 해주는 Model Context Protocol 서버 연결
Slash Commands: 특정 동작이나 workflow를 트리거하는 커스텀 명령어 (예: /my-command)
Agents: 도메인별 자율 작업을 위한 전문 agent 정의

What Plugins Can Do

자주 쓰는 workflow를 위한 새로운 slash command 추가 (예: 배포, 테스트, 린트)
MCP 서버를 통한 외부 서비스 연결 (데이터베이스, API, 클라우드 서비스)
도메인별 작업을 위한 전문 agent 정의
Claude에 추가 컨텍스트나 capability를 제공하는 skill 추가
커스텀 도구 및 통합 기능으로 Claude Code 확장

Installation
Plugin은 Claude Code의 plugin 시스템을 통해 이 마켓플레이스에서 직접 설치할 수 있다.

Method 1 - Direct install:
/plugin install {plugin-name}@claude-plugin-directory

Method 2 - Browse and discover:
/plugin > Discover

Method 3 - From a Git repository:
/plugin install {git-url}

Managing Plugins:
/plugin list - 설치된 plugin 조회
/plugin update {plugin-name} - 특정 plugin 업데이트
/plugin remove {plugin-name} - plugin 제거

Plugin Structure
각 plugin은 표준 구조를 따른다:
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server configuration (optional)
├── commands/            # Slash commands (optional)
│   └── my-command.md    # Command definition file
├── agents/              # Agent definitions (optional)
├── skills/              # Skill definitions (optional)
└── README.md            # Documentation

The plugin.json File
plugin.json 파일이 유일한 필수 파일이다. plugin에 관한 metadata가 들어 있다:
- Plugin 이름과 설명
- 버전 정보
- 저자와 리포지토리 상세
- 의존성과 요구사항

MCP Server Configuration
외부 서비스에 연결하는 plugin은 .mcp.json을 사용해 MCP 서버 연결을 정의한다. 이는 stdio 기반(서브프로세스) 서버와 SSE 기반(HTTP) 서버 모두를 지원한다.

Creating Your Own Plugin
새로운 plugin을 만들려면:

1. /plugins/example-plugin을 참고 구현으로 사용한다
2. 필수 .claude-plugin/plugin.json metadata 파일을 만든다
3. 필요에 따라 command, agent, skill을 추가한다
4. 외부 서비스에 연결한다면 .mcp.json에 MCP 서버를 구성한다
5. 문서와 사용 안내가 포함된 README.md를 포함한다
6. 게시 전에 철저히 테스트한다

Contributing
Internal Plugins
내부 plugin은 Anthropic 팀 구성원이 개발한다. 참고 구현은 /plugins/example-plugin을 참조하라.

External Plugins
서드파티 파트너는 마켓플레이스 포함을 위해 plugin을 제출할 수 있다. 요건:
- 승인을 위해 품질 및 보안 기준을 충족해야 한다
- 적절한 문서와 LICENSE 파일이 포함되어야 한다
- clau.de/plugin-directory-submission의 plugin 디렉터리 제출 양식을 통해 제출하라

Security Considerations
- 설치 전에 plugin 소스 코드를 검토하라
- plugin의 LICENSE 파일에서 사용 조건을 확인하라
- 광범위한 파일 시스템 또는 네트워크 접근을 요구하는 plugin은 주의하라
- 신뢰할 수 있는 출처의 plugin만 설치하라
- plugin 내 MCP 서버는 시스템 리소스에 접근할 수 있다

License
관련 LICENSE 파일은 각 링크된 plugin을 참조하라.

Documentation
Claude Code plugin 개발에 관한 자세한 정보는 공식 문서를 참조하라.
