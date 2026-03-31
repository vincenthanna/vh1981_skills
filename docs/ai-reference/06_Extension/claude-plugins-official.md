---

Claude Code Plugins Directory
A curated directory of high-quality plugins for Claude Code.

Important: Make sure you trust a plugin before installing, updating, or using it. Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they will work as intended or that they won't change. See each plugin's homepage for more information.

Structure

/plugins - Internal plugins developed and maintained by Anthropic
/external_plugins - Third-party plugins from partners and the community

Plugin Categories
Plugins extend Claude Code's capabilities across several areas:

Skills: Reusable capabilities that add domain-specific knowledge or actions to Claude Code
MCP Integrations: Model Context Protocol server connections that provide access to external tools, databases, and APIs
Slash Commands: Custom commands (e.g., /my-command) that trigger specific behaviors or workflows
Agents: Specialized agent definitions for domain-specific autonomous tasks

What Plugins Can Do

Add new slash commands for common workflows (e.g., deployment, testing, linting)
Connect to external services via MCP servers (databases, APIs, cloud services)
Define specialized agents for domain-specific tasks
Add skills that provide Claude with additional context or capabilities
Extend Claude Code with custom tools and integrations

Installation
Plugins can be installed directly from this marketplace via Claude Code's plugin system.

Method 1 - Direct install:
/plugin install {plugin-name}@claude-plugin-directory

Method 2 - Browse and discover:
/plugin > Discover

Method 3 - From a Git repository:
/plugin install {git-url}

Managing Plugins:
/plugin list - View installed plugins
/plugin update {plugin-name} - Update a specific plugin
/plugin remove {plugin-name} - Uninstall a plugin

Plugin Structure
Each plugin follows a standard structure:
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
The plugin.json file is the only required file. It contains metadata about the plugin:
- Plugin name and description
- Version information
- Author and repository details
- Dependencies and requirements

MCP Server Configuration
Plugins that connect to external services use .mcp.json to define MCP server connections. This supports both stdio-based (subprocess) and SSE-based (HTTP) server types.

Creating Your Own Plugin
To create a new plugin:

1. Use /plugins/example-plugin as a reference implementation
2. Create the required .claude-plugin/plugin.json metadata file
3. Add commands, agents, or skills as needed
4. Configure MCP servers in .mcp.json if connecting to external services
5. Include a README.md with documentation and usage instructions
6. Test thoroughly before publishing

Contributing
Internal Plugins
Internal plugins are developed by Anthropic team members. See /plugins/example-plugin for a reference implementation.

External Plugins
Third-party partners can submit plugins for inclusion in the marketplace. Requirements:
- Must meet quality and security standards for approval
- Must include proper documentation and a LICENSE file
- Submit via the plugin directory submission form at clau.de/plugin-directory-submission

Security Considerations
- Review plugin source code before installation
- Check the plugin's LICENSE file for usage terms
- Be cautious with plugins that request broad file system or network access
- Only install plugins from trusted sources
- MCP servers in plugins may have access to your system resources

License
Please see each linked plugin for the relevant LICENSE file.

Documentation
For more information on developing Claude Code plugins, see the official documentation.
