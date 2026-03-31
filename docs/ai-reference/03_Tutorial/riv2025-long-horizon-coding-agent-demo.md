---

Long-Horizon Coding Agent Demo

An autonomous agent system demonstrated at AWS re:Invent 2025. Builds React applications from GitHub issues using AWS Bedrock AgentCore and the Claude Agent SDK.

## Overview

Users create GitHub issues with feature requests. The community votes with thumbs-up reactions, authorized users approve with a rocket reaction, and the agent autonomously builds, tests, screenshots, and deploys the feature.

## Architecture

- **Issue Management**: Vote-based prioritization via GitHub reactions
- **Agent Pipeline**: Claude Agent SDK on AWS Bedrock AgentCore
- **CI/CD**: GitHub Actions for orchestration
- **Deployment**: CloudFront deploy previews
- **Monitoring**: CloudWatch health monitoring with auto-restart

## Key Features

- Autonomous end-to-end coding from issue to deployment
- Incremental builds
- Playwright screenshot capture during development
- CloudFront deploy previews
- Health monitoring with auto-restart

## Requirements

- AWS account with Bedrock AgentCore access
- GitHub Actions
- Docker
- Anthropic API key
- Various AWS IAM roles and secrets

## License

Apache-2.0

## Links

- GitHub: https://github.com/anthropics/riv2025-long-horizon-coding-agent-demo
