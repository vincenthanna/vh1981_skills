---

⚠️ 이것은 Mirror Repository이다
이 repository는 anthropics/claude-code-action의 base-action 디렉터리의 자동화된 mirror이다.
이 repository에 PR이나 issue를 제출하지 말 것. 대신, main repository에 기여하라:

🐛 issue 보고
🔧 pull request 제출
📖 문서 보기

Claude Code Base Action
이 GitHub Action을 사용하면 GitHub Actions workflow 내에서 Claude Code를 실행할 수 있다. 이를 활용하여 Claude Code 위에 임의의 커스텀 workflow를 구축할 수 있다.
별도 설정 없이 issue와 PR에서 @claude를 태깅하는 용도라면 Claude Code action과 GitHub app을 확인하라.
사용법
workflow 파일에 다음을 추가한다:
# Using a direct prompt
- name: Run Claude Code with direct prompt
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# Or using a prompt from a file
- name: Run Claude Code with prompt file
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt_file: "/path/to/prompt.txt"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# Or limiting the conversation turns
- name: Run Claude Code with limited turns
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    max_turns: "5" # Limit conversation to 5 turns
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# Using custom system prompts
- name: Run Claude Code with custom system prompt
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Build a REST API"
    system_prompt: "You are a senior backend engineer. Focus on security, performance, and maintainability."
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# Or appending to the default system prompt
- name: Run Claude Code with appended system prompt
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Create a database schema"
    append_system_prompt: "After writing code, be sure to code review yourself."
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# Using custom environment variables
- name: Run Claude Code with custom environment variables
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Deploy to staging environment"
    claude_env: |
      ENVIRONMENT: staging
      API_URL: https://api-staging.example.com
      DEBUG: true
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# Using fallback model for handling API errors
- name: Run Claude Code with fallback model
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Review and fix TypeScript errors"
    model: "claude-opus-4-1-20250805"
    fallback_model: "claude-sonnet-4-20250514"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# Using OAuth token instead of API key
- name: Run Claude Code with OAuth token
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Update dependencies"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
Inputs

Input
Description
Required
Default

prompt
Claude Code로 보낼 prompt
No*
''

prompt_file
Claude Code로 보낼 prompt가 담긴 파일의 경로
No*
''

allowed_tools
Claude Code가 사용할 수 있는 도구의 콤마 구분 목록
No
''

disallowed_tools
Claude Code가 사용할 수 없는 도구의 콤마 구분 목록
No
''

max_turns
최대 대화 turn 수 (default: no limit)
No
''

mcp_config
MCP 설정 JSON 파일의 경로 또는 MCP 설정 JSON 문자열
No
''

settings
Claude Code 설정 JSON 파일의 경로 또는 설정 JSON 문자열
No
''

system_prompt
system prompt 오버라이드
No
''

append_system_prompt
system prompt에 추가
No
''

claude_env
Claude Code 실행에 전달할 커스텀 환경 변수 (YAML 멀티라인 형식)
No
''

model
사용할 모델 (Bedrock/Vertex의 경우 provider-specific 형식 필요)
No
'claude-4-0-sonnet-20250219'

anthropic_model
DEPRECATED: 대신 'model'을 사용하라
No
'claude-4-0-sonnet-20250219'

fallback_model
default 모델이 과부하 상태일 때 지정된 모델로 자동 fallback 활성화
No
''

anthropic_api_key
Anthropic API key (direct Anthropic API에 필요)
No
''

claude_code_oauth_token
Claude Code OAuth token (anthropic_api_key의 대안)
No
''

use_bedrock
direct Anthropic API 대신 OIDC 인증으로 Amazon Bedrock 사용
No
'false'

use_vertex
direct Anthropic API 대신 OIDC 인증으로 Google Vertex AI 사용
No
'false'

use_node_cache
Node.js 의존성 캐싱 사용 여부 (lock 파일이 있는 Node.js 프로젝트에만 true로 설정)
No
'false'

show_full_output
전체 JSON 출력 표시 (⚠️ secret이 노출될 수 있음 - 보안 문서 참조)
No
'false'**

*prompt 또는 prompt_file 중 하나는 반드시 제공해야 하며, 둘 다 제공해서는 안 된다.
**show_full_output은 GitHub Actions debug mode가 활성화되면 자동으로 활성화된다. 중요한 보안 고려사항은 보안 문서를 참조하라.
Outputs

Output
Description

conclusion
Claude Code의 실행 상태 ('success' 또는 'failure')

execution_file
Claude Code 실행 로그를 포함하는 JSON 파일의 경로

Environment Variables
다음 환경 변수를 사용하여 action을 설정할 수 있다:

Variable
Description
Default

NODE_VERSION
사용할 Node.js 버전 (예: '18.x', '20.x', '22.x')
'18.x'

사용 예제:
- name: Run Claude Code with Node.js 20
  uses: anthropics/claude-code-base-action@beta
  env:
    NODE_VERSION: "20.x"
  with:
    prompt: "Your prompt here"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
Custom Environment Variables
claude_env 입력을 사용하여 Claude Code 실행에 커스텀 환경 변수를 전달할 수 있다. 이를 통해 Claude가 실행 중에 환경별 설정에 접근할 수 있다.
claude_env 입력은 key-value 쌍의 YAML 멀티라인 형식을 받는다:
- name: Deploy with custom environment
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Deploy the application to the staging environment"
    claude_env: |
      ENVIRONMENT: staging
      API_BASE_URL: https://api-staging.example.com
      DATABASE_URL: ${{ secrets.STAGING_DB_URL }}
      DEBUG: true
      LOG_LEVEL: debug
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
기능:

YAML 형식: 표준 YAML key-value 문법 사용 (KEY: value)
멀티라인 지원: 단일 입력에서 여러 환경 변수 정의
주석: #으로 시작하는 라인은 무시됨
GitHub Secrets: ${{ secrets.SECRET_NAME }}을 사용하여 GitHub secret 참조 가능
런타임 접근: 환경 변수는 실행 중 Claude에서 사용 가능

사용 사례 예시:
# Development configuration
claude_env: |
  NODE_ENV: development
  API_URL: http://localhost:3000
  DEBUG: true

# Production deployment
claude_env: |
  NODE_ENV: production
  API_URL: https://api.example.com
  DATABASE_URL: ${{ secrets.PROD_DB_URL }}
  REDIS_URL: ${{ secrets.REDIS_URL }}

# Feature flags and configuration
claude_env: |
  FEATURE_NEW_UI: enabled
  MAX_RETRIES: 3
  TIMEOUT_MS: 5000
Settings 설정 사용
Claude Code 설정 구성은 두 가지 방식으로 제공할 수 있다:
Option 1: Settings 설정 파일
Claude Code 설정을 포함하는 JSON 파일의 경로를 제공한다:
- name: Run Claude Code with settings file
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    settings: "path/to/settings.json"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
Option 2: 인라인 Settings 설정
JSON 문자열로 설정 구성을 직접 제공한다:
- name: Run Claude Code with inline settings
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    settings: |
      {
        "model": "claude-opus-4-1-20250805",
        "env": {
          "DEBUG": "true",
          "API_URL": "https://api.example.com"
        },
        "permissions": {
          "allow": ["Bash", "Read"],
          "deny": ["WebFetch"]
        },
        "hooks": {
          "PreToolUse": [{
            "matcher": "Bash",
            "hooks": [{
              "type": "command",
              "command": "echo Running bash command..."
            }]
          }]
        }
      }
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
설정 파일은 다음을 포함한 모든 Claude Code 설정 옵션을 지원한다:

model: default 모델 오버라이드
env: 세션의 환경 변수
permissions: 도구 사용 권한
hooks: 도구 실행 전/후 hook
includeCoAuthoredBy: git commit에 co-authored-by 포함
기타...

참고: enableAllProjectMcpServers 설정은 MCP 서버가 올바르게 작동하도록 이 action에 의해 항상 true로 설정된다.
MCP Config 사용
MCP 설정은 두 가지 방식으로 제공할 수 있다:
Option 1: MCP 설정 파일
MCP 설정을 포함하는 JSON 파일의 경로를 제공한다:
- name: Run Claude Code with MCP config file
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    mcp_config: "path/to/mcp-config.json"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
Option 2: 인라인 MCP 설정
JSON 문자열로 MCP 설정을 직접 제공한다:
- name: Run Claude Code with inline MCP config
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    mcp_config: |
      {
        "mcpServers": {
          "server-name": {
            "command": "node",
            "args": ["./server.js"],
            "env": {
              "API_KEY": "your-api-key"
            }
          }
        }
      }
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
MCP 설정 파일은 다음 형식을 따라야 한다:
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["./server.js"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
허용 도구와 같은 다른 입력과 MCP 설정을 결합할 수 있다:
# Using multiple inputs together
- name: Run Claude Code with MCP and custom tools
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Access the custom MCP server and use its tools"
    mcp_config: "mcp-config.json"
    allowed_tools: "Bash(git:*),View,mcp__server-name__custom_tool"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
예시: PR Code Review
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Run Code Review with Claude
        id: code-review
        uses: anthropics/claude-code-base-action@beta
        with:
          prompt: "Review the PR changes. Focus on code quality, potential bugs, and performance issues. Suggest improvements where appropriate. Write your review as markdown text."
          allowed_tools: "Bash(git diff --name-only HEAD~1),Bash(git diff HEAD~1),View,GlobTool,GrepTool,Write"
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Extract and Comment PR Review
        if: steps.code-review.outputs.conclusion == 'success'
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const executionFile = '${{ steps.code-review.outputs.execution_file }}';
            const executionLog = JSON.parse(fs.readFileSync(executionFile, 'utf8'));

            // Extract the review content from the execution log
            // The execution log contains the full conversation including Claude's responses
            let review = '';

            // Find the last assistant message which should contain the review
            for (let i = executionLog.length - 1; i >= 0; i--) {
              if (executionLog[i].role === 'assistant') {
                review = executionLog[i].content;
                break;
              }
            }

            if (review) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: "## Claude Code Review\n\n" + review + "\n\n*Generated by Claude Code*"
              });
            }
./examples에서 추가 예제를 확인하라.
Cloud Provider 사용
다음 방법 중 하나로 Claude에 인증할 수 있다:

Direct Anthropic API (default) - API key 또는 OAuth token 필요
Amazon Bedrock - OIDC 인증 필요, 자동으로 cross-region inference profile 사용
Google Vertex AI - OIDC 인증 필요

참고:

Bedrock과 Vertex는 OIDC 인증을 독점적으로 사용한다
AWS Bedrock은 특정 모델에 대해 자동으로 cross-region inference profile을 사용한다
Cross-region inference profile 모델의 경우, inference profile이 사용하는 모든 region에서 Claude 모델 접근을 요청하고 승인받아야 한다
Bedrock API endpoint URL은 AWS_REGION 환경 변수를 사용하여 자동으로 구성된다 (예: https://bedrock-runtime.us-west-2.amazonaws.com)
ANTHROPIC_BEDROCK_BASE_URL 환경 변수를 설정하여 Bedrock API endpoint URL을 오버라이드할 수 있다

Model 설정
선택한 provider에 따라 provider-specific 모델 이름을 사용한다:
# For direct Anthropic API (default)
- name: Run Claude Code with Anthropic API
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    model: "claude-3-7-sonnet-20250219"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# For Amazon Bedrock (requires OIDC authentication)
- name: Configure AWS Credentials (OIDC)
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
    aws-region: us-west-2

- name: Run Claude Code with Bedrock
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    model: "anthropic.claude-3-7-sonnet-20250219-v1:0"
    use_bedrock: "true"

# For Google Vertex AI (requires OIDC authentication)
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
    service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

- name: Run Claude Code with Vertex AI
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    model: "claude-3-7-sonnet@20250219"
    use_vertex: "true"
예시: AWS Bedrock에 대한 OIDC 인증 사용
이 예제는 AWS Bedrock에서 OIDC 인증을 사용하는 방법을 보여준다:
- name: Configure AWS Credentials (OIDC)
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
    aws-region: us-west-2

- name: Run Claude Code with AWS OIDC
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    use_bedrock: "true"
    model: "anthropic.claude-3-7-sonnet-20250219-v1:0"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
예시: GCP Vertex AI에 대한 OIDC 인증 사용
이 예제는 GCP Vertex AI에서 OIDC 인증을 사용하는 방법을 보여준다:
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
    service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

- name: Run Claude Code with GCP OIDC
  uses: anthropics/claude-code-base-action@beta
  with:
    prompt: "Your prompt here"
    use_vertex: "true"
    model: "claude-3-7-sonnet@20250219"
    allowed_tools: "Bash(git:*),View,GlobTool,GrepTool,BatchTool"
보안 모범 사례
⚠️ **매우 중요**: 절대 API key를 repository에 직접 commit하지 말 것! 항상 GitHub Actions secret을 사용하라.
Anthropic API key를 안전하게 사용하려면:

repository secret으로 API key 추가:

Repository의 Settings로 이동
"Secrets and variables" → "Actions"로 이동
"New repository secret" 클릭
이름을 ANTHROPIC_API_KEY로 지정
값으로 API key 붙여넣기

workflow에서 secret 참조:
anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

**절대 이렇게 하지 말 것**:
# ❌ WRONG - Exposes your API key
anthropic_api_key: "sk-ant-..."
**항상 이렇게 할 것**:
# ✅ CORRECT - Uses GitHub secrets
anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
이는 API key, access token, credential을 포함한 모든 민감한 값에 적용된다.
또한 가능하면 항상 수명이 짧은 token을 사용하는 것을 권장한다.
License
이 프로젝트는 MIT License에 따라 라이선스가 부여된다—자세한 내용은 LICENSE 파일을 참조하라.
