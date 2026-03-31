---

Claude Agent SDK (TypeScript)

The Claude Agent SDK enables you to programmatically build AI agents with Claude Code's capabilities. Create autonomous agents that can understand codebases, edit files, run commands, and execute complex workflows.

Learn more in the official documentation.

Installation
npm install @anthropic-ai/claude-agent-sdk

Requirements: Node.js 18+

Note: The Claude Code CLI is automatically bundled with the package. The SDK will use the bundled CLI by default. If you prefer a system-wide installation, you can install Claude Code separately or specify a custom path in options.

Quick Start
import { query } from '@anthropic-ai/claude-agent-sdk';

for await (const message of query({ prompt: 'What is 2 + 2?' })) {
  console.log(message);
}

Key Features

Codebase Understanding: Analyze and navigate project structures programmatically
File Operations: Read, write, and edit files through AI-powered agents
Command Execution: Run shell commands and scripts within agent workflows
Complex Workflows: Build autonomous agents for multi-step development tasks
Tool Integration: Access Claude Code's full toolset (Read, Write, Edit, Bash, and more)
MCP Server Support: Connect to Model Context Protocol servers for extended capabilities
Custom Hooks: Intercept and control agent behavior at specific points in the agent loop

API Overview

query() Function
The simplest way to interact with Claude. Returns an async iterator of response messages:
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
allowedTools is a permission allowlist: listed tools are auto-approved, and unlisted tools fall through to permissionMode for a decision. To block specific tools, use disallowedTools.
const options: ClaudeAgentOptions = {
  allowedTools: ['Read', 'Write', 'Bash'],
  permissionMode: 'acceptEdits',
};

Migrating from the Claude Code SDK
The Claude Code SDK is now the Claude Agent SDK. Key breaking changes include:

ClaudeCodeOptions renamed to ClaudeAgentOptions
Merged system prompt configuration
Settings isolation and explicit control
New programmatic subagents and session forking features

Please check out the migration guide for full details.

Reporting Bugs
We welcome your feedback. File a GitHub issue to report bugs or request features.

Connect on Discord
Join the Claude Developers Discord to connect with other developers building with the Claude Agent SDK. Get help, share feedback, and discuss your projects with the community.

Data collection, usage, and retention
When you use the Claude Agent SDK, we collect feedback, which includes usage data (such as code acceptance or rejections), associated conversation data, and user feedback submitted via the /bug command.
How we use your data
See our data usage policies.
Privacy safeguards
We have implemented several safeguards to protect your data, including limited retention periods for sensitive information, restricted access to user session data, and clear policies against using feedback for model training.
For full details, please review our Commercial Terms of Service and Privacy Policy.
License and terms
Use of this SDK is governed by Anthropic's Commercial Terms of Service, including when you use it to power products and services that you make available to your own customers and end users, except to the extent a specific component or dependency is covered by a different license as indicated in that component's LICENSE file.
