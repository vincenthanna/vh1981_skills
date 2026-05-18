---

Claude Agent SDK for Python
Claude Agent를 위한 Python SDK다. 자세한 내용은 Claude Agent SDK documentation을 참조한다.
Installation
pip install claude-agent-sdk
사전 요구 사항:

Python 3.10+

참고: Claude Code CLI는 패키지에 자동으로 번들되어 있어 별도 설치가 필요 없다! SDK는 기본적으로 번들된 CLI를 사용한다. 시스템 전역 설치나 특정 버전을 사용하고 싶다면 다음을 활용할 수 있다:

Claude Code를 별도로 설치: curl -fsSL https://claude.ai/install.sh | bash
커스텀 경로 지정: ClaudeAgentOptions(cli_path="/path/to/claude")

Quick Start
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
Basic Usage: query()
query()는 Claude Code에 질의하기 위한 비동기 함수다. 응답 메시지의 AsyncIterator를 반환한다. src/claude_agent_sdk/query.py를 참조한다.
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

# Simple query
async for message in query(prompt="Hello Claude"):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)

# With options
options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant",
    max_turns=1
)

async for message in query(prompt="Tell me a joke", options=options):
    print(message)
Using Tools
기본적으로 Claude는 전체 Claude Code 도구 세트(Read, Write, Edit, Bash 등)에 접근할 수 있다. allowed_tools는 권한 허용 목록이다: 나열된 도구는 자동 승인되고, 나열되지 않은 도구는 permission_mode와 can_use_tool로 넘어가 결정된다. Claude의 도구 세트에서 도구를 제거하지는 않는다. 특정 도구를 차단하려면 disallowed_tools를 사용한다. 전체 평가 순서는 permissions guide를 참조한다.
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Bash"],  # auto-approve these tools
    permission_mode='acceptEdits'  # auto-accept file edits
)

async for message in query(
    prompt="Create a hello.py file",
    options=options
):
    # Process tool use and results
    pass
Working Directory
from pathlib import Path

options = ClaudeAgentOptions(
    cwd="/path/to/project"  # or Path("/path/to/project")
)
ClaudeSDKClient
ClaudeSDKClient는 Claude Code와의 양방향 인터랙티브 대화를 지원한다.
src/claude_agent_sdk/client.py를 참조한다.
query()와 달리 ClaudeSDKClient는 커스텀 도구와 hook을 추가로 지원하며, 둘 다 Python 함수로 정의할 수 있다.
Custom Tools (as In-Process SDK MCP Servers)
커스텀 도구는 Claude가 필요에 따라 호출할 수 있도록 제공할 수 있는 Python 함수다.
커스텀 도구는 in-process MCP 서버로 구현되어 Python 애플리케이션 내부에서 직접 실행되므로, 일반적인 MCP 서버가 요구하는 별도 프로세스가 필요 없다.
end-to-end 예시는 MCP Calculator를 참조한다.
Creating a Simple Tool
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

# Define a tool using the @tool decorator
@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Hello, {args['name']}!"}
        ]
    }

# Create an SDK MCP server
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)

# Use it with Claude. allowed_tools pre-approves the tool so it runs
# without a permission prompt; it does not control tool availability.
options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Greet Alice")

    # Extract and print response
    async for msg in client.receive_response():
        print(msg)
외부 MCP 서버 대비 장점

서브프로세스 관리 불필요 - 애플리케이션과 동일한 프로세스에서 실행
더 나은 성능 - 도구 호출에 대한 IPC 오버헤드가 없음
더 단순한 배포 - 여러 프로세스 대신 단일 Python 프로세스
더 쉬운 디버깅 - 모든 코드가 동일한 프로세스에서 실행
타입 안전성 - 타입 힌트가 있는 직접적인 Python 함수 호출

Migration from External Servers
# BEFORE: External MCP server (separate process)
options = ClaudeAgentOptions(
    mcp_servers={
        "calculator": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "calculator_server"]
        }
    }
)

# AFTER: SDK MCP server (in-process)
from my_tools import add, subtract  # Your tool functions

calculator = create_sdk_mcp_server(
    name="calculator",
    tools=[add, subtract]
)

options = ClaudeAgentOptions(
    mcp_servers={"calculator": calculator}
)
Mixed Server Support
SDK MCP 서버와 외부 MCP 서버를 함께 사용할 수 있다:
options = ClaudeAgentOptions(
    mcp_servers={
        "internal": sdk_server,      # In-process SDK server
        "external": {                # External subprocess server
            "type": "stdio",
            "command": "external-server"
        }
    }
)
Hooks
hook은 Claude(가 아니라) Claude Code 애플리케이션이 Claude agent loop의 특정 지점에서 호출하는 Python 함수다. hook은 Claude에 대한 결정론적 처리와 자동화된 피드백을 제공할 수 있다. 자세한 내용은 Intercept and control agent behavior with hooks를 참조한다.
추가 예시는 examples/hooks.py를 참조한다.
Example
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher

async def check_bash_command(input_data, tool_use_id, context):
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]
    if tool_name != "Bash":
        return {}
    command = tool_input.get("command", "")
    block_patterns = ["foo.sh"]
    for pattern in block_patterns:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Command contains invalid pattern: {pattern}",
                }
            }
    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_bash_command]),
        ],
    }
)

async with ClaudeSDKClient(options=options) as client:
    # Test 1: Command with forbidden pattern (will be blocked)
    await client.query("Run the bash command: ./foo.sh --help")
    async for msg in client.receive_response():
        print(msg)

    print("\n" + "=" * 50 + "\n")

    # Test 2: Safe command that should work
    await client.query("Run the bash command: echo 'Hello from hooks example!'")
    async for msg in client.receive_response():
        print(msg)
Types
완전한 타입 정의는 src/claude_agent_sdk/types.py를 참조한다:

ClaudeAgentOptions - 설정 옵션
AssistantMessage, UserMessage, SystemMessage, ResultMessage - 메시지 타입
TextBlock, ToolUseBlock, ToolResultBlock - 컨텐츠 블록

Error Handling
from claude_agent_sdk import (
    ClaudeSDKError,      # Base error
    CLINotFoundError,    # Claude Code not installed
    CLIConnectionError,  # Connection issues
    ProcessError,        # Process failed
    CLIJSONDecodeError,  # JSON parsing issues
)

try:
    async for message in query(prompt="Hello"):
        pass
except CLINotFoundError:
    print("Please install Claude Code")
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
except CLIJSONDecodeError as e:
    print(f"Failed to parse response: {e}")
모든 에러 타입은 src/claude_agent_sdk/_errors.py를 참조한다.
Available Tools
사용 가능한 도구의 전체 목록은 Claude Code documentation을 참조한다.
Examples
완전히 동작하는 예시는 examples/quick_start.py를 참조한다.
ClaudeSDKClient를 사용하는 포괄적인 예시는 examples/streaming_mode.py를 참조한다. examples/streaming_mode_ipython.py에서 IPython으로 인터랙티브 예시를 실행할 수도 있다.
Migrating from Claude Code SDK
Claude Code SDK(버전 < 0.1.0)에서 업그레이드하는 경우, 다음을 포함한 breaking change와 신규 기능에 대한 자세한 내용은 CHANGELOG.md를 참조한다:

ClaudeCodeOptions → ClaudeAgentOptions 이름 변경
병합된 system prompt 설정
설정 격리와 명시적 제어
새로운 프로그래밍 방식 서브에이전트(subagent) 및 session forking 기능

Development
이 프로젝트에 기여한다면, 초기 설정 스크립트를 실행해 git hook을 설치한다:
./scripts/initial-setup.sh
이 스크립트는 push 전에 lint 검사를 실행하는 pre-push hook을 설치하며, CI workflow와 동일하다. hook을 일시적으로 건너뛰려면 git push --no-verify를 사용한다.
Building Wheels Locally
번들된 Claude Code CLI를 포함해 wheel을 빌드하려면:
# Install build dependencies
pip install build twine

# Build wheel with bundled CLI
python scripts/build_wheel.py

# Build with specific version
python scripts/build_wheel.py --version 0.1.4

# Build with specific CLI version
python scripts/build_wheel.py --cli-version 2.0.0

# Clean bundled CLI after building
python scripts/build_wheel.py --clean

# Skip CLI download (use existing)
python scripts/build_wheel.py --skip-download
빌드 스크립트는 다음 작업을 수행한다:

플랫폼용 Claude Code CLI 다운로드
wheel에 번들
wheel과 source distribution 양쪽 빌드
twine으로 패키지 검사

모든 옵션은 python scripts/build_wheel.py --help를 참조한다.
Release Workflow
패키지는 .github/workflows/publish.yml의 GitHub Actions workflow를 통해 PyPI에 배포된다. 새 릴리스를 만들려면:

Actions 탭에서 두 가지 입력으로 workflow를 수동으로 트리거한다:

version: 배포할 패키지 버전 (예: 0.1.5)
claude_code_version: 번들할 Claude Code CLI 버전 (예: 2.0.0 또는 latest)

workflow는 다음을 수행한다:

macOS, Linux, Windows용 플랫폼별 wheel 빌드
각 wheel에 지정된 Claude Code CLI 버전 번들
source distribution 빌드
모든 아티팩트를 PyPI에 배포
버전 갱신을 포함한 release branch 생성
main으로의 PR을 다음 내용을 포함해 오픈:

갱신된 pyproject.toml 버전
갱신된 src/claude_agent_sdk/_version.py
번들된 CLI 버전을 반영한 src/claude_agent_sdk/_cli_version.py
자동 생성된 CHANGELOG.md 항목

release PR을 검토하고 merge해 main을 새 버전 정보로 갱신한다

workflow는 패키지 버전과 번들된 CLI 버전을 별도로 추적하므로, 코드 변경 없이도 갱신된 CLI를 포함해 새 패키지 버전을 릴리스할 수 있다.
License and terms
이 SDK의 사용은 Anthropic's Commercial Terms of Service의 적용을 받으며, 자신의 고객 및 최종 사용자에게 제공하는 제품과 서비스에 이를 사용하는 경우에도 마찬가지다. 다만 특정 구성요소나 의존성이 해당 구성요소의 LICENSE 파일에 명시된 다른 라이선스의 적용을 받는 경우는 예외다.
