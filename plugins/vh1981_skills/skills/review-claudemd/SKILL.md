---
name: review-claudemd
description: >
  Analyze recent Claude conversation history to improve CLAUDE.md files and .claude/rules/.
  Extracts patterns from past sessions — violated instructions, missing rules, redundant entries —
  and applies edits to both global (~/.claude/CLAUDE.md) and project-level CLAUDE.md and rules files.
  Use this skill whenever the user wants to review CLAUDE.md, update Claude instructions,
  improve Claude configuration, audit .claude/rules, optimize context token usage in config files,
  or learn from recent conversations to refine agent behavior.
  Also trigger when users say things like "what should we add to CLAUDE.md",
  "clean up the rules", or "review recent sessions for improvements".
---

# Review CLAUDE.md from Conversation History

Analyze recent Claude Code conversations to find actionable improvements for CLAUDE.md files and `.claude/rules/`. The goal is to keep these configuration files accurate, non-redundant, and effective at steering agent behavior.

This skill has five phases:
1. Locate and extract conversation history
2. Analyze conversations against current config (parallel subagents)
3. Test each rule for redundancy (blind subagents)
4. Aggregate findings into a unified report
5. Apply edits automatically

## Step 1: Find and extract conversation history

Claude Code stores conversation logs as JSONL files. Locate the project folder and extract the 15-20 most recent conversations (excluding the current one).

```bash
# Derive the project folder path
PROJECT_PATH=$(pwd | sed 's|/|-|g' | sed 's|^-||')
CONVO_DIR=~/.claude/projects/-${PROJECT_PATH}

# Verify the directory exists
ls -lt "$CONVO_DIR"/*.jsonl 2>/dev/null | head -20

# Extract conversations to a scratch directory
SCRATCH=/tmp/claudemd-review-$(date +%s)
mkdir -p "$SCRATCH"

CURRENT_SESSION_ID=""  # Set this if you can identify the current session

for f in $(ls -t "$CONVO_DIR"/*.jsonl | head -20); do
  basename_f=$(basename "$f" .jsonl)
  # Skip current session
  [ "$basename_f" = "$CURRENT_SESSION_ID" ] && continue

  jq -r '
    if .type == "user" then
      "USER: " + (
        if (.message.content | type) == "string" then .message.content
        elif (.message.content | type) == "array" then
          [.message.content[] | select(.type == "text") | .text] | join("\n")
        else ""
        end
      )
    elif .type == "assistant" then
      "ASSISTANT: " + (
        if (.message.content | type) == "string" then .message.content
        elif (.message.content | type) == "array" then
          [.message.content[] | select(.type == "text") | .text] | join("\n")
        else ""
        end
      )
    else empty
    end
  ' "$f" 2>/dev/null | grep -v "^ASSISTANT: $" > "$SCRATCH/${basename_f}.txt"
done

ls -lhS "$SCRATCH"
```

If the directory does not exist or contains no `.jsonl` files, inform the user that no conversation history was found and stop.

## Step 2: Analyze conversations against current config

Launch parallel **Sonnet** subagents to find patterns in conversations. Each agent receives a batch of conversation files and reads all configuration files.

### Batching strategy

Group conversation files by size to keep subagent context balanced:
- Large (>100KB): 1-2 per agent
- Medium (10-100KB): 3-5 per agent
- Small (<10KB): 5-10 per agent

### Subagent prompt

Each subagent receives this prompt (fill in the file lists):

```
Read these configuration files:
1. Global CLAUDE.md: ~/.claude/CLAUDE.md
2. Local CLAUDE.md: [project]/CLAUDE.md
3. Rules directory: all files under [project]/.claude/rules/**/*.md
4. Conversations: [list of conversation .txt files in scratch dir]

Analyze the conversations against ALL configuration files. Find:

1. VIOLATED RULES — instructions that exist but the agent broke them.
   Include the rule location (file + section) and the conversation where it was violated.

2. MISSING RULES (LOCAL) — project-specific patterns that should be added to
   the local CLAUDE.md or a file under .claude/rules/.
   These are recurring corrections, workarounds, or decisions that came up multiple times.

3. MISSING RULES (GLOBAL) — patterns that apply to any project, not just this one.
   These belong in ~/.claude/CLAUDE.md.

4. OUTDATED RULES — items in config files that seem no longer relevant,
   contradict actual practice, or reference deprecated tools/patterns.

5. DUPLICATED RULES — rules that appear in multiple files and should be consolidated
   into one location.

Output bullet points only. Be specific: quote the rule text and cite the conversation file.
```

## Step 3: Test rules for redundancy (blind subagents)

Many rules in CLAUDE.md restate behavior that Claude already follows by default. These waste context tokens. This step identifies which rules are genuinely necessary.

### 3.1 Parse rules into testable units

Read every config file and split into individually testable rules:
- `~/.claude/CLAUDE.md`
- `./CLAUDE.md`
- All files under `.claude/rules/**/*.md`

Assign each rule an ID: `global:3`, `local:known-gotchas:2`, `rules/constitution:git:5`, `rules/python/coding-style:7`.

### 3.2 Classify rules before testing

Not all rules are testable. Skip these categories (they encode project-specific knowledge that no model would know by default):

- **Project-specific values**: env vars, hostnames, ports, file paths, image versions
- **Architecture decisions**: startup order, data flow, component relationships
- **Known gotchas and bug workarounds**: version-specific issues, migration artifacts
- **Cross-component dependencies**: which services depend on which
- **Tool configuration**: mgrep store names, Docker image tags

Only test rules about **behavioral defaults** — things like tool preferences, coding style, commit format, logging libraries, type annotation conventions.

### 3.3 Spawn blind test subagents

For each batch of 3-5 testable rules, spawn a **Haiku** subagent with these constraints:

- The subagent prompt must NOT include any content from CLAUDE.md or `.claude/rules/`
- The subagent must NOT read any config files
- Present only concrete coding scenarios and ask what the agent would do

Prompt template:

```
You are working on a Python/TypeScript monorepo project.
DO NOT read any CLAUDE.md, .claude/rules/, or constitution files.
Answer each scenario below with what you would do by default.

Scenario 1: [concrete situation testing rule X]
  Question: [what tool/approach/pattern would you use?]

Scenario 2: [concrete situation testing rule Y]
  Question: [what would you do?]

For each scenario, answer concisely.
```

Scenario design:
- Make scenarios concrete and project-agnostic (no hints about the expected answer)
- Test behavioral defaults, not project-specific knowledge
- Example: Rule "use uv, never pip" -> "You need to install requests in a Python project with pyproject.toml. What command?"
- Example: Rule "use loguru" -> "You need to add logging to a Python service. What import?"

### 3.4 Score results

Compare each blind agent response against the expected behavior:

| Result | Meaning | Action |
|--------|---------|--------|
| **REDUNDANT** | Blind agent naturally follows the rule | Candidate for removal |
| **NECESSARY** | Blind agent would do something different | Keep the rule |
| **REVIEW** | Agent gets the gist but misses specifics | Consider rewording |

### 3.5 Build redundancy report

```
REDUNDANCY TEST RESULTS
=======================

REDUNDANT (safe to remove — saves ~N context tokens):
| Rule ID | File | Rule Summary | Agent Default Behavior |
|---------|------|-------------|----------------------|

NECESSARY (keep):
| Rule ID | File | Rule Summary | Why Needed |
|---------|------|-------------|------------|

REVIEW (consider rewording):
| Rule ID | File | Rule Summary | Agent Response | Gap |
|---------|------|-------------|---------------|-----|

Estimated token savings: ~X tokens freed from context window
```

## Step 4: Aggregate findings

Combine results from Step 2 (conversation analysis) and Step 3 (redundancy testing) into a final report with these sections:

1. **Violated rules** — existing rules that were broken (need stronger wording or examples)
2. **Suggested additions (LOCAL)** — project-specific patterns to add
3. **Suggested additions (GLOBAL)** — universal patterns to add
4. **Outdated rules** — items that may no longer be relevant
5. **Redundant rules** — rules Claude follows by default (remove to save tokens)
6. **Duplicated rules** — consolidation candidates

Present the report to the user before applying changes.

## Step 5: Apply changes

After presenting the report, apply all edits automatically:

- **Redundant rules**: Remove from the source file
- **Violated rules**: Strengthen wording in place, add examples if helpful
- **New patterns**: Append to the appropriate file (local CLAUDE.md, global CLAUDE.md, or a rules file)
- **Outdated rules**: Remove or update
- **Duplicated rules**: Consolidate into one location, remove from others

After all edits, output a summary listing every file modified and what changed.

Clean up the scratch directory:
```bash
rm -rf "$SCRATCH"
```
