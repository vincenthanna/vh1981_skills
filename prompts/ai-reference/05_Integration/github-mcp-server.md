---

GitHub MCP Server
GitHub MCP Server는 GitHub API와의 원활한 통합을 제공하는 Model Context Protocol (MCP) 서버로, 개발자 및 도구를 위한 고급 자동화와 상호작용 기능을 가능하게 한다.
 
사용 사례

GitHub workflow와 프로세스 자동화.
GitHub repository에서 데이터를 추출하고 분석.
GitHub 생태계와 상호작용하는 AI 기반 도구 및 애플리케이션 구축.

사전 요구사항

서버를 container에서 실행하려면 Docker가 설치되어 있어야 한다.
Docker가 설치되었으면 Docker가 실행 중인지도 확인해야 한다. 이미지는 public이며, pull 시 오류가 발생하면 만료된 token이 있을 수 있으니 docker logout ghcr.io를 실행해야 할 수 있다.
마지막으로 GitHub Personal Access Token을 생성해야 한다.
MCP 서버는 다양한 GitHub API를 사용할 수 있으므로, AI 도구에 부여해도 괜찮다고 판단되는 권한을 활성화한다 (access token에 대한 자세한 내용은 문서를 참고).

설치
VS Code에서 사용하기
빠른 설치를 위해서는 이 README 상단에 있는 원클릭 설치 버튼 중 하나를 사용한다. 해당 흐름을 완료한 후, Agent mode를 토글하면 (Copilot Chat 텍스트 입력 옆에 위치) 서버가 시작된다.
수동 설치의 경우, VS Code의 User Settings (JSON) 파일에 다음 JSON 블록을 추가한다. Ctrl + Shift + P를 누르고 Preferences: Open User Settings (JSON)을 입력하여 이 작업을 수행할 수 있다.
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "github_token",
        "description": "GitHub Personal Access Token",
        "password": true
      }
    ],
    "servers": {
      "github": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "-e",
          "GITHUB_PERSONAL_ACCESS_TOKEN",
          "ghcr.io/github/github-mcp-server"
        ],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
        }
      }
    }
  }
}
선택적으로, workspace 내 .vscode/mcp.json 파일에 유사한 예제(즉, mcp 키 없이)를 추가할 수 있다. 이렇게 하면 다른 사람들과 설정을 공유할 수 있다.
{
  "inputs": [
    {
      "type": "promptString",
      "id": "github_token",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ],
  "servers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
      }
    }
  }
}

VS Code의 agent mode 문서에서 MCP 서버 도구 사용에 대해 자세히 알아본다.
Claude Desktop에서 사용하기
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
      }
    }
  }
}
소스에서 빌드
Docker가 없다면 go build를 사용하여 cmd/github-mcp-server 디렉터리에서 binary를 빌드하고, GITHUB_PERSONAL_ACCESS_TOKEN 환경 변수를 token으로 설정한 상태에서 github-mcp-server stdio 명령을 사용할 수 있다. 빌드의 출력 위치를 지정하려면 -o 플래그를 사용한다. 서버가 빌드된 실행 파일을 command로 사용하도록 설정해야 한다. 예를 들면:
{
  "mcp": {
    "servers": {
      "github": {
        "command": "/path/to/github-mcp-server",
        "args": ["stdio"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
        }
      }
    }
  }
}
도구 설정
GitHub MCP Server는 --toolsets 플래그를 통해 특정 기능 그룹을 활성화하거나 비활성화하는 것을 지원한다. 이를 통해 AI 도구에서 어떤 GitHub API 기능을 사용할 수 있는지 제어할 수 있다. 필요한 toolset만 활성화하면 LLM의 도구 선택을 도울 수 있고 context 크기를 줄일 수 있다.
사용 가능한 Toolset
다음 도구 그룹을 사용할 수 있다 (모두 기본적으로 활성화됨):

Toolset
Description

repos
Repository 관련 도구 (파일 작업, branch, commit)

issues
Issue 관련 도구 (create, read, update, comment)

users
GitHub Users와 관련된 모든 것

pull_requests
Pull request 작업 (create, merge, review)

code_security
Code scanning alert 및 보안 기능

experiments
실험적 기능 (안정적이지 않음)

Toolset 지정하기
LLM에서 사용 가능하게 하려는 toolset을 지정하려면 두 가지 방식으로 allow-list를 전달할 수 있다:

Command Line Argument 사용:
github-mcp-server --toolsets repos,issues,pull_requests,code_security

Environment Variable 사용:
GITHUB_TOOLSETS="repos,issues,pull_requests,code_security" ./github-mcp-server

두 가지가 모두 제공되면 환경 변수 GITHUB_TOOLSETS가 command line argument보다 우선한다.
Docker와 함께 Toolset 사용
Docker를 사용할 때는 toolset을 환경 변수로 전달할 수 있다:
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-token> \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests,code_security,experiments" \
  ghcr.io/github/github-mcp-server
"all" Toolset
특수 toolset all을 제공하면 다른 설정과 관계없이 사용 가능한 모든 toolset을 활성화할 수 있다:
./github-mcp-server --toolsets all
또는 환경 변수를 사용하여:
GITHUB_TOOLSETS="all" ./github-mcp-server
Dynamic Tool Discovery
참고: 이 기능은 현재 beta이며 모든 환경에서 사용할 수 없을 수 있다. 사용해 보고 문제가 발생하면 알려달라.
모든 도구가 활성화된 상태로 시작하는 대신, dynamic toolset discovery를 켤 수 있다. Dynamic toolset은 MCP host가 사용자 prompt에 따라 toolset을 나열하고 활성화할 수 있게 한다. 이는 사용 가능한 도구의 엄청난 수로 인해 모델이 혼란스러워하는 상황을 방지하는 데 도움이 된다.
Dynamic Tool Discovery 사용하기
binary를 사용할 때는 --dynamic-toolsets 플래그를 전달할 수 있다.
./github-mcp-server --dynamic-toolsets
Docker를 사용할 때는 toolset을 환경 변수로 전달할 수 있다:
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-token> \
  -e GITHUB_DYNAMIC_TOOLSETS=1 \
  ghcr.io/github/github-mcp-server
GitHub Enterprise Server
플래그 --gh-host와 환경 변수 GITHUB_HOST를 사용하여 GitHub Enterprise Server hostname을 설정할 수 있다.
i18n / 설명 오버라이드
도구의 설명은 binary와 같은 디렉터리에 github-mcp-server-config.json 파일을 만들어 오버라이드할 수 있다. 이 파일은 도구 이름을 키로, 새 설명을 값으로 하는 JSON 객체를 포함해야 한다. 예를 들면:
{
  "TOOL_ADD_ISSUE_COMMENT_DESCRIPTION": "an alternative description",
  "TOOL_CREATE_BRANCH_DESCRIPTION": "Create a new branch in a GitHub repository"
}
binary를 --export-translations 플래그와 함께 실행하여 현재 번역의 export를 생성할 수 있다. 이 플래그는 마지막으로 export한 이후 binary에 추가된 새 번역을 추가하면서, 사용자가 만든 모든 번역/오버라이드를 보존한다.
./github-mcp-server --export-translations
cat github-mcp-server-config.json
ENV 변수를 사용하여 설명을 오버라이드할 수도 있다. 환경 변수 이름은 JSON 파일의 키와 동일하며, GITHUB_MCP_ 접두사가 붙고 모두 대문자이다. 예를 들어, TOOL_ADD_ISSUE_COMMENT_DESCRIPTION 도구를 오버라이드하려면 다음 환경 변수를 설정할 수 있다:
export GITHUB_MCP_TOOL_ADD_ISSUE_COMMENT_DESCRIPTION="an alternative description"
Tools
Users

get_me - 인증된 사용자의 세부 정보 가져오기

매개변수 필요 없음

Issues

get_issue - Repository 내 issue의 내용 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number (number, required)

get_issue_comments - GitHub issue에 대한 comment 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number (number, required)

create_issue - GitHub repository에 새 issue 생성

owner: Repository owner (string, required)
repo: Repository name (string, required)
title: Issue title (string, required)
body: Issue body content (string, optional)
assignees: Usernames to assign to this issue (string[], optional)
labels: Labels to apply to this issue (string[], optional)

add_issue_comment - issue에 comment 추가

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number (number, required)
body: Comment text (string, required)

list_issues - Repository issue 목록 조회 및 필터링

owner: Repository owner (string, required)
repo: Repository name (string, required)
state: Filter by state ('open', 'closed', 'all') (string, optional)
labels: Labels to filter by (string[], optional)
sort: Sort by ('created', 'updated', 'comments') (string, optional)
direction: Sort direction ('asc', 'desc') (string, optional)
since: Filter by date (ISO 8601 timestamp) (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)

update_issue - GitHub repository의 기존 issue 업데이트

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number to update (number, required)
title: New title (string, optional)
body: New description (string, optional)
state: New state ('open' or 'closed') (string, optional)
labels: New labels (string[], optional)
assignees: New assignees (string[], optional)
milestone: New milestone number (number, optional)

search_issues - issue와 pull request 검색

query: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)

Pull Requests

get_pull_request - 특정 pull request의 세부 정보 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)

list_pull_requests - Repository pull request 목록 조회 및 필터링

owner: Repository owner (string, required)
repo: Repository name (string, required)
state: PR state (string, optional)
sort: Sort field (string, optional)
direction: Sort direction (string, optional)
perPage: Results per page (number, optional)
page: Page number (number, optional)

merge_pull_request - pull request merge

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
commit_title: Title for the merge commit (string, optional)
commit_message: Message for the merge commit (string, optional)
merge_method: Merge method (string, optional)

get_pull_request_files - pull request에서 변경된 파일 목록 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)

get_pull_request_status - pull request에 대한 모든 status check의 조합된 상태 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)

update_pull_request_branch - base branch에서 최신 변경사항으로 pull request branch 업데이트

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
expectedHeadSha: The expected SHA of the pull request's HEAD ref (string, optional)

get_pull_request_comments - pull request의 review comment 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)

get_pull_request_reviews - pull request의 review 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)

create_pull_request_review - pull request에 대한 review 생성

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
body: Review comment text (string, optional)
event: Review action ('APPROVE', 'REQUEST_CHANGES', 'COMMENT') (string, required)
commitId: SHA of commit to review (string, optional)
comments: Line-specific comments array of objects to place comments on pull request changes (array, optional)

인라인 comment의 경우: path, position (또는 line), body 제공
다중 라인 comment의 경우: path, start_line, line, 선택적 side/start_side, body 제공

create_pull_request - 새 pull request 생성

owner: Repository owner (string, required)
repo: Repository name (string, required)
title: PR title (string, required)
body: PR description (string, optional)
head: Branch containing changes (string, required)
base: Branch to merge into (string, required)
draft: Create as draft PR (boolean, optional)
maintainer_can_modify: Allow maintainer edits (boolean, optional)

add_pull_request_review_comment - pull request에 review comment를 추가하거나 기존 comment에 답글 달기

owner: Repository owner (string, required)
repo: Repository name (string, required)
pull_number: Pull request number (number, required)
body: The text of the review comment (string, required)
commit_id: The SHA of the commit to comment on (string, required unless using in_reply_to)
path: The relative path to the file that necessitates a comment (string, required unless using in_reply_to)
line: The line of the blob in the pull request diff that the comment applies to (number, optional)
side: The side of the diff to comment on (LEFT or RIGHT) (string, optional)
start_line: For multi-line comments, the first line of the range (number, optional)
start_side: For multi-line comments, the starting side of the diff (LEFT or RIGHT) (string, optional)
subject_type: The level at which the comment is targeted (line or file) (string, optional)
in_reply_to: The ID of the review comment to reply to (number, optional). When specified, only body is required and other parameters are ignored.

update_pull_request - GitHub repository의 기존 pull request 업데이트

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number to update (number, required)
title: New title (string, optional)
body: New description (string, optional)
state: New state ('open' or 'closed') (string, optional)
base: New base branch name (string, optional)
maintainer_can_modify: Allow maintainer edits (boolean, optional)

Repositories

create_or_update_file - Repository에서 단일 파일 생성 또는 업데이트

owner: Repository owner (string, required)
repo: Repository name (string, required)
path: File path (string, required)
message: Commit message (string, required)
content: File content (string, required)
branch: Branch name (string, optional)
sha: File SHA if updating (string, optional)

list_branches - GitHub repository의 branch 목록

owner: Repository owner (string, required)
repo: Repository name (string, required)
page: Page number (number, optional)
perPage: Results per page (number, optional)

push_files - 단일 commit으로 여러 파일 push

owner: Repository owner (string, required)
repo: Repository name (string, required)
branch: Branch to push to (string, required)
files: Files to push, each with path and content (array, required)
message: Commit message (string, required)

search_repositories - GitHub repository 검색

query: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)

create_repository - 새 GitHub repository 생성

name: Repository name (string, required)
description: Repository description (string, optional)
private: Whether the repository is private (boolean, optional)
autoInit: Auto-initialize with README (boolean, optional)

get_file_contents - 파일 또는 디렉터리 내용 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
path: File path (string, required)
ref: Git reference (string, optional)

fork_repository - repository fork

owner: Repository owner (string, required)
repo: Repository name (string, required)
organization: Target organization name (string, optional)

create_branch - 새 branch 생성

owner: Repository owner (string, required)
repo: Repository name (string, required)
branch: New branch name (string, required)
sha: SHA to create branch from (string, required)

list_commits - Repository 내 branch의 commit 목록 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
sha: Branch name, tag, or commit SHA (string, optional)
path: Only commits containing this file path (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)

get_commit - Repository에서 commit의 세부 정보 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
sha: Commit SHA, branch name, or tag name (string, required)
page: Page number, for files in the commit (number, optional)
perPage: Results per page, for files in the commit (number, optional)

search_code - GitHub repository 전반에서 코드 검색

query: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)

Users

search_users - GitHub 사용자 검색

q: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)

Code Scanning

get_code_scanning_alert - code scanning alert 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
alertNumber: Alert number (number, required)

list_code_scanning_alerts - Repository의 code scanning alert 목록

owner: Repository owner (string, required)
repo: Repository name (string, required)
ref: Git reference (string, optional)
state: Alert state (string, optional)
severity: Alert severity (string, optional)
tool_name: The name of the tool used for code scanning (string, optional)

Secret Scanning

get_secret_scanning_alert - secret scanning alert 가져오기

owner: Repository owner (string, required)
repo: Repository name (string, required)
alertNumber: Alert number (number, required)

list_secret_scanning_alerts - Repository의 secret scanning alert 목록

owner: Repository owner (string, required)
repo: Repository name (string, required)
state: Alert state (string, optional)
secret_type: The secret types to be filtered for in a comma-separated list (string, optional)
resolution: The resolution status (string, optional)

Resources
Repository Content

Get Repository Content
특정 경로의 repository 내용을 가져온다.

Template: repo://{owner}/{repo}/contents{/path*}
Parameters:

owner: Repository owner (string, required)
repo: Repository name (string, required)
path: File or directory path (string, optional)

Get Repository Content for a Specific Branch
주어진 branch에 대한 특정 경로의 repository 내용을 가져온다.

Template: repo://{owner}/{repo}/refs/heads/{branch}/contents{/path*}
Parameters:

owner: Repository owner (string, required)
repo: Repository name (string, required)
branch: Branch name (string, required)
path: File or directory path (string, optional)

Get Repository Content for a Specific Commit
주어진 commit에 대한 특정 경로의 repository 내용을 가져온다.

Template: repo://{owner}/{repo}/sha/{sha}/contents{/path*}
Parameters:

owner: Repository owner (string, required)
repo: Repository name (string, required)
sha: Commit SHA (string, required)
path: File or directory path (string, optional)

Get Repository Content for a Specific Tag
주어진 tag에 대한 특정 경로의 repository 내용을 가져온다.

Template: repo://{owner}/{repo}/refs/tags/{tag}/contents{/path*}
Parameters:

owner: Repository owner (string, required)
repo: Repository name (string, required)
tag: Tag name (string, required)
path: File or directory path (string, optional)

Get Repository Content for a Specific Pull Request
주어진 pull request에 대한 특정 경로의 repository 내용을 가져온다.

Template: repo://{owner}/{repo}/refs/pull/{prNumber}/head/contents{/path*}
Parameters:

owner: Repository owner (string, required)
repo: Repository name (string, required)
prNumber: Pull request number (string, required)
path: File or directory path (string, optional)

Library Usage
이 모듈의 export된 Go API는 현재 불안정한 것으로 간주되어야 하며, breaking change의 대상이 된다. 향후에는 안정성을 제공할 수 있으며, 이것이 가치 있는 사용 사례가 있다면 issue를 등록해주기 바란다.
License
이 프로젝트는 MIT 오픈 소스 라이선스 조건에 따라 라이선스가 부여된다. 전체 조건은 MIT를 참조한다.
