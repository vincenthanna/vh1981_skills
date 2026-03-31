---

Claude Code

Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster by executing routine tasks, explaining complex code, and handling git workflows -- all through natural language commands. Use it in your terminal, IDE, or tag @claude on Github.

Learn more in the official documentation.

Get started
Note: Installation via npm is deprecated. Use one of the recommended methods below.

For more installation options, uninstall steps, and troubleshooting, see the setup documentation.

Install Claude Code:
MacOS/Linux (Recommended):
curl -fsSL https://claude.ai/install.sh | bash
Homebrew (MacOS/Linux):
brew install --cask claude-code
Windows (Recommended):
irm https://claude.ai/install.ps1 | iex
WinGet (Windows):
winget install Anthropic.ClaudeCode
NPM (Deprecated):
npm install -g @anthropic-ai/claude-code

Navigate to your project directory and run claude.

Key Features

Agentic Code Execution: Autonomously executes routine coding tasks such as refactoring, writing tests, and fixing bugs
Codebase Understanding: Analyzes and comprehends your project structure, dependencies, and patterns
Natural Language Interface: Control everything through conversational commands -- no special syntax needed
Git Workflow Integration: Handles commits, pull requests, code reviews, and branch management
Code Explanation: Explains complex code sections, architectures, and design patterns
Multi-File Editing: Makes coordinated changes across multiple files in your project
Command Execution: Runs shell commands, builds, tests, and other development tools

Platform Support

Terminal/CLI: Primary interactive interface -- run claude in any project directory
IDE Integration: VS Code extension available for integrated development experience
GitHub Integration: Tag @claude in issues and pull requests for automated assistance
Codespaces: Works in GitHub Codespaces and other cloud development environments

CLI Commands
Start Claude Code by running claude in your terminal. Built-in slash commands include:

/bug - Report issues directly within Claude Code
/help - Display available commands and usage information
/plugin - Browse, install, and manage plugins
/clear - Clear conversation history
/config - View and modify configuration

Configuration
Claude Code can be configured through several mechanisms:

Project-level settings: .claude/ directory in your project root
Custom commands: Define reusable commands in .claude/commands/
Environment variables: ANTHROPIC_API_KEY and other configuration via environment

Hooks
Hooks allow you to intercept and control agent behavior at specific points in the Claude agent loop. They enable deterministic processing and automated feedback. Hooks can be defined for events such as:

PreToolUse: Runs before a tool is executed (can approve, deny, or modify)
PostToolUse: Runs after a tool execution completes
Notification: Triggered on agent notifications

MCP (Model Context Protocol) Support
Claude Code supports MCP servers for extending its capabilities with external tools and data sources. Configure MCP servers in your project's .mcp.json file to connect to databases, APIs, and other services.

Plugins
This repository includes several Claude Code plugins that extend functionality with custom commands and agents. Plugins follow a standard structure:

plugin-name/
  .claude-plugin/
    plugin.json      # Plugin metadata (required)
  .mcp.json          # MCP server configuration (optional)
  commands/          # Slash commands (optional)
  agents/            # Agent definitions (optional)
  skills/            # Skill definitions (optional)

Install plugins via /plugin install {plugin-name} or browse with /plugin > Discover. See the plugins directory for detailed documentation.

Claude Agent SDK
For programmatic access to Claude Code's capabilities, use the Claude Agent SDK available for both TypeScript and Python. Build autonomous agents that can understand codebases, edit files, run commands, and execute complex workflows.

Reporting Bugs
We welcome your feedback. Use the /bug command to report issues directly within Claude Code, or file a GitHub issue.

Connect on Discord
Join the Claude Developers Discord to connect with other developers using Claude Code. Get help, share feedback, and discuss your projects with the community.

Data collection, usage, and retention
When you use Claude Code, we collect feedback, which includes usage data (such as code acceptance or rejections), associated conversation data, and user feedback submitted via the /bug command.
How we use your data
See our data usage policies.
Privacy safeguards
We have implemented several safeguards to protect your data, including limited retention periods for sensitive information, restricted access to user session data, and clear policies against using feedback for model training.
For full details, please review our Commercial Terms of Service and Privacy Policy.
