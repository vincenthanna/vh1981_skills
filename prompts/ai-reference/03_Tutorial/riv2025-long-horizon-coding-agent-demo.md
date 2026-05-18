---

Long-Horizon Coding Agent Demo

AWS re:Invent 2025에서 시연된 자율 agent 시스템. AWS Bedrock AgentCore와 Claude Agent SDK를 사용해 GitHub issue로부터 React 애플리케이션을 만든다.

## Overview

사용자가 기능 요청과 함께 GitHub issue를 생성한다. 커뮤니티는 thumbs-up reaction으로 투표하고, 권한 있는 사용자는 rocket reaction으로 승인하며, agent가 자율적으로 기능을 빌드하고, 테스트하고, 스크린샷을 찍고, 배포한다.

## Architecture

- **Issue Management**: GitHub reaction을 통한 투표 기반 우선순위 지정
- **Agent Pipeline**: AWS Bedrock AgentCore 위의 Claude Agent SDK
- **CI/CD**: 오케스트레이션을 위한 GitHub Actions
- **Deployment**: CloudFront deploy preview
- **Monitoring**: 자동 재시작이 포함된 CloudWatch 헬스 모니터링

## Key Features

- issue에서 배포까지의 자율적인 end-to-end 코딩
- 점진적 빌드
- 개발 중 Playwright 스크린샷 캡처
- CloudFront deploy preview
- 자동 재시작이 포함된 헬스 모니터링

## Requirements

- Bedrock AgentCore 접근 권한이 있는 AWS 계정
- GitHub Actions
- Docker
- Anthropic API key
- 다양한 AWS IAM 역할과 secret

## License

Apache-2.0

## Links

- GitHub: https://github.com/anthropics/riv2025-long-horizon-coding-agent-demo
