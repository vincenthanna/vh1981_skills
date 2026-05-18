---

Claude Code Security Reviewer
Claude를 사용해 코드 변경의 보안 취약점을 분석하는 AI 기반 보안 리뷰 GitHub Action이다. 이 action은 Anthropic의 Claude Code 도구를 사용해 pull request에 대한 지능적이고 컨텍스트를 인식하는 보안 분석을 제공하며, 깊은 의미론적 보안 분석을 수행한다. 자세한 내용은 블로그 게시물을 참조하라.
Features

AI-Powered Analysis: Claude의 고급 추론을 사용해 깊은 의미론적 이해로 보안 취약점을 탐지
Diff-Aware Scanning: PR의 경우 변경된 파일만 분석
PR Comments: PR에 보안 발견 사항을 자동으로 코멘트
Contextual Understanding: 패턴 매칭을 넘어 코드 의미론을 이해
Language Agnostic: 모든 프로그래밍 언어와 호환
False Positive Filtering: 노이즈를 줄이고 실제 취약점에 집중하기 위한 고급 필터링

Quick Start
리포지토리의 .github/workflows/security.yml에 다음을 추가하라:
name: Security Review

permissions:
  pull-requests: write  # Needed for leaving PR comments
  contents: read

on:
  pull_request:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
          fetch-depth: 2
      
      - uses: anthropics/claude-code-security-review@main
        with:
          comment-pr: true
          claude-api-key: ${{ secrets.CLAUDE_API_KEY }}
Security Considerations
이 action은 prompt injection 공격에 대해 강화되어 있지 않으므로 신뢰할 수 있는 PR을 검토할 때만 사용해야 한다. 메인테이너가 PR을 검토한 후에만 workflow가 실행되도록 리포지토리에 "Require approval for all external contributors" 옵션을 구성하기를 권장한다.
Configuration Options
Action Inputs

Input
Description
Default
Required

claude-api-key
보안 분석을 위한 Anthropic Claude API 키. 참고: 이 API 키는 Claude API와 Claude Code 사용 모두에 대해 활성화되어야 한다.
None
Yes

comment-pr
PR에 발견 사항을 코멘트할지 여부
true
No

upload-results
결과를 artifact로 업로드할지 여부
true
No

exclude-directories
스캔에서 제외할 디렉터리의 쉼표 구분 목록
None
No

claude-model
사용할 Claude 모델 이름. 기본값은 Opus 4.1이다.
claude-opus-4-1-20250805
No

claudecode-timeout
ClaudeCode 분석의 타임아웃(분 단위)
20
No

run-every-commit
모든 commit에서 ClaudeCode 실행 (캐시 검사 건너뜀). 경고: commit이 많은 PR에서 false positive를 증가시킬 수 있다.
false
No

false-positive-filtering-instructions
커스텀 false positive 필터링 지시문 텍스트 파일 경로
None
No

custom-security-scan-instructions
audit prompt에 추가할 커스텀 보안 스캔 지시문 텍스트 파일 경로
None
No

Action Outputs

Output
Description

findings-count
총 보안 발견 사항 수

results-file
결과 JSON 파일 경로

How It Works
Architecture
claudecode/
├── github_action_audit.py  # Main audit script for GitHub Actions
├── prompts.py              # Security audit prompt templates
├── findings_filter.py      # False positive filtering logic
├── claude_api_client.py    # Claude API client for false positive filtering
├── json_parser.py          # Robust JSON parsing utilities
├── requirements.txt        # Python dependencies
├── test_*.py               # Test suites
└── evals/                  # Eval tooling to test CC on arbitrary PRs

Workflow

PR Analysis: pull request가 열리면 Claude가 diff를 분석해 무엇이 변경되었는지 이해한다
Contextual Review: Claude가 컨텍스트 안에서 코드 변경을 살펴 목적과 잠재적 보안 함의를 파악한다
Finding Generation: 상세한 설명, 심각도 등급, 수정 가이드와 함께 보안 이슈가 식별된다
False Positive Filtering: 고급 필터링이 영향이 낮거나 false positive 경향이 있는 발견 사항을 제거해 노이즈를 줄인다
PR Comments: 발견 사항은 특정 코드 라인에 대한 리뷰 코멘트로 게시된다

Security Analysis Capabilities
Types of Vulnerabilities Detected

Injection Attacks: SQL injection, command injection, LDAP injection, XPath injection, NoSQL injection, XXE
Authentication & Authorization: 인증 결함, 권한 상승, insecure direct object references, 우회 로직, 세션 결함
Data Exposure: 하드코딩된 시크릿, 민감한 데이터 로깅, 정보 노출, PII 처리 위반
Cryptographic Issues: 취약한 알고리즘, 부적절한 키 관리, 안전하지 않은 난수 생성
Input Validation: 검증 누락, 부적절한 sanitization, 버퍼 오버플로
Business Logic Flaws: race condition, time-of-check-time-of-use (TOCTOU) 이슈
Configuration Security: 안전하지 않은 기본값, 누락된 보안 헤더, 허용적 CORS
Supply Chain: 취약한 의존성, typosquatting 위험
Code Execution: 역직렬화를 통한 RCE, pickle injection, eval injection
Cross-Site Scripting (XSS): 반사형, 저장형, DOM 기반 XSS

False Positive Filtering
이 도구는 영향이 큰 취약점에 집중하기 위해 영향이 낮거나 false positive 경향이 있는 다양한 발견 사항을 자동으로 제외한다:

Denial of Service 취약점
Rate limiting 우려
메모리/CPU 고갈 이슈
입증된 영향 없는 일반적 입력 검증
Open redirect 취약점

False positive 필터링은 특정 프로젝트의 보안 목표에 맞춰 조정할 수도 있다.
Benefits Over Traditional SAST

Contextual Understanding: 패턴이 아닌 코드 의미론과 의도를 이해
Lower False Positives: AI 기반 분석이 실제로 코드가 취약한 시점을 이해해 노이즈를 줄인다
Detailed Explanations: 무언가가 왜 취약점인지와 어떻게 수정해야 하는지에 대한 명확한 설명 제공
Adaptive Learning: 조직별 보안 요구사항으로 커스터마이징 가능

Installation & Setup
GitHub Actions
위의 Quick Start 가이드를 따르라. Action이 모든 의존성을 자동으로 처리한다.
Local Development
로컬에서 특정 PR에 대해 보안 스캐너를 실행하려면 평가 프레임워크 문서를 참조하라.

Claude Code Integration: /security-review Command
기본적으로 Claude Code는 GitHub Action workflow와 동일한 보안 분석 capability를 제공하지만 Claude Code 개발 환경에 직접 통합된 /security-review slash command를 함께 제공한다. 사용하려면 /security-review를 실행해 모든 대기 중인 변경 사항에 대한 종합적인 보안 리뷰를 수행하라.
Customizing the Command
기본 /security-review command는 대부분의 경우에 잘 동작하도록 설계되어 있지만, 특정 보안 요구에 따라 커스터마이징할 수도 있다. 그러려면:

이 리포지토리의 security-review.md 파일을 프로젝트의 .claude/commands/ 폴더로 복사한다.
보안 분석을 커스터마이징하기 위해 security-review.md를 편집한다. 예를 들어 false positive 필터링 지시문에 추가적인 조직별 지침을 추가할 수 있다.

Custom Scanning Configuration
커스텀 스캔 및 false positive 필터링 지시문을 구성하는 것도 가능하다. 자세한 내용은 docs/ 폴더를 참조하라.
Testing
기능을 검증하려면 테스트 스위트를 실행하라:
cd claude-code-security-review
# Run all tests
pytest claudecode -v
Support
이슈나 질문이 있는 경우:

이 리포지토리에 이슈를 연다
디버깅 정보는 GitHub Actions 로그를 확인한다

License
MIT License - 자세한 내용은 LICENSE 파일을 참조하라.
