---
name: develop
description: "Orchestrates feature development with multi-agent consensus, TDD, and automated testing. USE THIS SKILL whenever the user wants to: implement a feature, fix a bug, add an endpoint/processor/component/migration, refactor code, update a Dockerfile, write tests for new functionality, add UI controls, create database tables, or make ANY code change that modifies files. This includes tasks like 'add a new toggle to the settings page', 'fix the build', 'create an Alembic migration', 'add cypress tests for X', 'implement rate limiting', 'refactor the adapter'. Even if the task seems simple, use this skill if it involves writing or changing code. Do NOT use for read-only tasks: explaining code, reading files, answering questions, reviewing PRs without changes, searching the codebase, or comparing files."
argument-hint: "Feature description or task to implement"
---

# Git Context

- **Current branch**: !`git branch --show-current`
- **mgrep available**: !`which mgrep >/dev/null 2>&1 && echo "YES" || echo "NO"`
- **testbranch available**: !`test -d ~/plusinsight && echo "YES (~/plusinsight found)" || echo "NO (~/plusinsight not found)"`
- **Uncommitted changes**: !`git status --short`

---

# Development Principles

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

# Feature Development Workflow

Usage: `/develop "Feature to develop"`

This skill orchestrates a complete feature development workflow including exploration, testing strategy, and multi-agent consensus development.

## Headless Mode Support

This skill supports headless mode (running with `claude -p` or `--print`).

**Headless Mode Detection:**
- In headless mode, the `AskUserQuestion` tool is NOT available
- If `AskUserQuestion` is not available, **skip all user confirmations and proceed directly**
- All other steps execute normally

**Behavior in headless mode:**
- Step 5 (User Confirmation) is automatically skipped
- Development proceeds directly after prompt construction
- All constitutions and development patterns are still enforced

## Step 1: Prerequisites Check

**1.1 Check ralph-loop availability:**
- Use the Skill tool to check if `ralph-loop:ralph-loop` is accessible
- If NOT available, output error and STOP:
  ```
  ERROR: ralph-loop skill is not installed.
  Please install the ralph-loop plugin before using /develop.
  Run: /ralph-loop:help for installation instructions.
  ```

**1.2 Check mgrep availability:**
- If mgrep is NOT available, warn the user:
  ```
  WARNING: mgrep is not available. Using standard Explore agents instead of deep-explore.
  For better code exploration, install mgrep: npm install -g @mixedbread/mgrep
  ```

## Step 2: Codebase Exploration

Explore the codebase to understand relevant code for implementing: **$ARGUMENTS**

**If mgrep is available (preferred):**
- Use `deep-explore` agent (Task tool with subagent_type=deep-explore) to:
  - Search for code related to the feature intent using semantic search
  - Identify all files that need modification
  - Find existing patterns and conventions to follow

**If mgrep is NOT available (fallback):**
- Use `Explore` agent (Task tool with subagent_type=Explore) with thoroughness="very thorough" to:
  - Find relevant files using glob patterns
  - Search for related keywords and patterns
  - Identify dependencies and related code

**Exploration output should include:**
- List of files that need to be modified
- Existing patterns/conventions discovered
- Dependencies and related components
- Potential impact areas

## Step 3: Test Strategy Determination

Based on the exploration results, determine the testing approach:

1. **Identify test types needed:**
   - Unit tests (isolated component testing)
   - Integration tests (component interaction)
   - Docker-based tests (full system validation)

2. **Find existing test patterns:**
   - Look for existing tests in the identified components
   - Note testing frameworks used (pytest, TestContainers, etc.)
   - Identify test fixtures and helpers available

3. **Docker test strategy:**
   - Determine which Docker services are needed for testing
   - Identify the docker-compose configuration to use
   - Plan the container build and test execution sequence

4. **Live E2E testing via testbranch (if local installation available):**
   - Check if `~/plusinsight` directory exists (local PLUSINSIGHT installation)
   - If present: **use `/testbranch` as the exclusive E2E test strategy** -- ignore all other
     E2E/integration test plans (items 1-3 above are for unit tests only)
   - The testbranch skill replaces Docker-based testing by mounting branch changes directly
     into the live installation and running full verification:
     - Infrastructure checks (container health, API endpoints)
     - Data pipeline checks (ClickHouse tables, Redis keys)
     - Browser/UI checks via Playwright MCP (minimap dots, console errors, network errors, usertool)
   - Set `testbranch_available = True` for use in the ralph-loop prompt
   - If `~/plusinsight` does NOT exist: fall back to Docker-based testing (items 1-3 above)

## Step 4: Construct Ralph Loop Prompt

Generate a comprehensive ralph-loop prompt based on exploration and test strategy.

**The prompt MUST include these constitutions (non-negotiable):**

```
## Development Constitutions (MANDATORY)

1. **Test-Driven Development**: Always develop test code and type check code alongside the feature itself. No feature code without corresponding tests.

2. **Testbranch-First Testing**: If ~/plusinsight exists, use /testbranch as the exclusive E2E test -- it mounts changes onto the live installation and runs full verification (infra + data + browser). Fall back to Docker-based testing only when ~/plusinsight is NOT present.

3. **Commit Protocol**: Always use /commit slash command to commit and push changes. Never use raw git commands for commits.

4. **Multi-Agent Consensus Development**: When making ANY code changes (small or big):
   a. Select the most suitable agent for the task (python-pro, fastapi-pro, frontend-developer, etc.)
   b. Fire 5 IDENTICAL agents with the SAME prompt using parallel Task tool calls
   c. Wait for all 5 agents to complete their implementations
   d. Review all 5 implementations to reach consensus:
      - **Python code**: invoke /everything-claude-code:python-review on each implementation
      - **Non-Python code**: invoke /everything-claude-code:code-review on each implementation
      - Synthesize the reviews into a single consensus solution
   e. Implement ONLY the consensus solution
   f. Do NOT create markdown review documents - the review is verbal/internal only
```

**Prompt structure:**
```
/ralph-loop:ralph-loop "## Feature Development: {feature_description}

### Context
{Summary of exploration findings}
{Files to modify}
{Existing patterns to follow}

### Development Constitutions (MANDATORY)
[Include all 4 constitutions above]

### Phase 1: Test Development
For EACH test implementation task:
- [ ] Fire 5 identical {test-automator or suitable_agent} agents with the test implementation prompt
- [ ] Review test implementations: /everything-claude-code:python-review (Python) or /everything-claude-code:code-review (other) to reach consensus
- [ ] Implement the consensus test solution
- [ ] Build Docker containers for testing: docker-compose build {services}
- [ ] Run tests in Docker environment to verify test infrastructure

### Phase 2: Feature Implementation
For EACH code change task:
- [ ] Fire 5 identical {suitable_agent} agents with the implementation prompt
- [ ] Review implementations: /everything-claude-code:python-review (Python) or /everything-claude-code:code-review (other) to reach consensus
- [ ] Implement the consensus solution
- [ ] Run type checking (uv run pre-commit run --all-files)

### Phase 3: Integration & Validation

**If ~/plusinsight exists (testbranch_available = True):**
- [ ] Run unit tests only (no Docker E2E -- testbranch replaces it)
- [ ] Verify type checking passes
- [ ] Run /testbranch to mount branch changes onto the live ~/plusinsight installation
- [ ] Review the testbranch verification report (infrastructure, data pipeline, browser/UI)
- [ ] If testbranch verification fails, fix issues and re-run /testbranch until it passes
- [ ] /testbranch is the SOLE E2E validation gate -- do NOT run separate Docker E2E tests

**If ~/plusinsight does NOT exist (fallback):**
- [ ] Run full test suite in Docker
- [ ] Verify type checking passes
- [ ] Ensure no regressions in existing functionality

### Phase 4: Commit & Push
- [ ] Use /commit to create atomic commits
- [ ] Verify all changes are pushed

### Success Criteria
- All unit tests pass
- Pre-commit checks pass (ruff format, ruff check, ty)
- If ~/plusinsight exists: /testbranch verification passes (infrastructure + data + browser)
- If ~/plusinsight does NOT exist: all tests pass in Docker environment
- Feature works as specified
- Code follows existing patterns and conventions

Output <promise>FEATURE COMPLETE</promise> ONLY when ALL requirements are met." --completion-promise "FEATURE COMPLETE"
```

## Step 5: User Confirmation

**CRITICAL: Before starting development, present the finalized prompt to the user.**

### Headless Mode Check

**First, check if running in headless mode:**
- Attempt to use `AskUserQuestion` tool
- If the tool is NOT available (headless mode), **skip this step entirely** and proceed directly to Step 6
- If the tool IS available (interactive mode), proceed with confirmation below

### Interactive Mode Confirmation

Use AskUserQuestion to show:
1. The complete ralph-loop prompt that will be executed
2. Summary of:
   - Files to be modified
   - Test strategy
   - Agents to be used
3. Ask for confirmation to proceed

**Format:**
```
## Development Plan for: {feature}

### Files to Modify
{list of files}

### Test Strategy
{test approach}

### Primary Agents
{agents that will be used}

### Ralph Loop Prompt
{full prompt}

---
Proceed with development?
```

**Options:**
- "Yes, start development" - Proceed to Step 6
- "Modify the plan" - Allow user to provide feedback, regenerate prompt
- "Cancel" - Stop execution

### Headless Mode Behavior

When running in headless mode (`claude -p` or `--print`):
- This confirmation step is **automatically skipped**
- Development proceeds directly to Step 6
- Output the development plan summary to stdout for logging purposes

## Step 6: Execute Development

Once user confirms, invoke the ralph-loop skill with the finalized prompt:

```
/ralph-loop:ralph-loop "{finalized_prompt}" --completion-promise "FEATURE COMPLETE"
```

## Agent Reference

| Task | Agent | Purpose |
|------|-------|---------|
| Code exploration (with mgrep) | `deep-explore` | Semantic search, code discovery |
| Code exploration (fallback) | `Explore` | Pattern matching, file discovery |
| Python development | `python-pro` | Python code, async patterns |
| FastAPI development | `fastapi-pro` | API endpoints, Pydantic models |
| Frontend development | `frontend-developer` | React, Next.js components |
| Database work | `database-architect` | Schema design, migrations |
| Test development | `test-automator` | Test patterns, fixtures |
| Python code review & consensus | `/everything-claude-code:python-review` | Python implementation review |
| General code review & consensus | `/everything-claude-code:code-review` | Non-Python implementation review |
| Live E2E validation | `/testbranch` | Mount & verify on live installation |
| Debugging | `debugger` | Error fixing, root cause |

## Multi-Agent Consensus Pattern

When implementing any code change:

```
1. Determine suitable agent (e.g., python-pro for Python code)

2. Create 5 parallel Task tool calls with IDENTICAL prompts:
   Task(subagent_type="python-pro", prompt="Implement X...")
   Task(subagent_type="python-pro", prompt="Implement X...")
   Task(subagent_type="python-pro", prompt="Implement X...")
   Task(subagent_type="python-pro", prompt="Implement X...")
   Task(subagent_type="python-pro", prompt="Implement X...")

3. Collect all 5 implementations

4. Review all 5 implementations using the appropriate review skill:
   - Python code: invoke /everything-claude-code:python-review for each implementation
   - Non-Python code: invoke /everything-claude-code:code-review for each implementation
   - Synthesize reviews into a single consensus solution

5. Implement ONLY the consensus solution
```

## Important Notes

- **Headless mode supported** - User confirmation (Step 5) is automatically skipped when running with `claude -p`
- **Always use /commit** for all commits - never raw git commands
- **Testbranch-first E2E** - if ~/plusinsight exists, /testbranch is the sole E2E gate (replaces Docker E2E)
- **Docker testing is fallback** - only when ~/plusinsight is NOT present
- **Multi-agent consensus is required** for all code changes
- **Review skills for consensus** - /everything-claude-code:python-review (Python) or /everything-claude-code:code-review (other)
- **Tests are not optional** - every feature must have corresponding tests
- **Type checking is required** - ensure `uv run pre-commit run --all-files` passes (uses ruff + ty, never mypy/pyright)
