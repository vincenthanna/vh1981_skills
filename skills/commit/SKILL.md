---
name: commit
description: Create atomic git commits with Conventional Commits format, including pre-commit linting, selective staging, and JIRA tagging. Invoke this skill whenever the user wants to commit, save changes, check in code, record progress, or finalize work -- even if they say "save my work" or "commit this" without mentioning git explicitly. Do NOT invoke for read-only git queries (log, status, diff), push/pull operations, or undo operations (revert, reset).
---

# Git Context

- **Current branch**: !`git branch --show-current`
- **Is release branch**: !`git branch --show-current | grep -qE '^release/' && echo "YES" || echo "NO"`
- **JIRA tag from branch**: !`git branch --show-current | grep -oP 'PII-\d+' || echo "NONE"`
- **Uncommitted changes**: !`git status --short`

---

## Workflow

### Step 1: Pre-flight checks

- If `git status --short` shows no changes, report "Nothing to commit" and stop.
- If on `main` or `master`, warn the user and stop (do not commit directly to main).

### Step 2: Run pre-commit linting

All linting must pass before any commits are created. This catches formatting and type errors early, and auto-fixes what it can.

1. Run: `uv run pre-commit run --all-files`
2. **If any files under `dashboard-front/`, `usertool/`, or `dashboard-api/` are staged or modified**, also run:
   `uv run pre-commit run --hook-stage manual --all-files`
   (Frontend hooks -- ESLint, Prettier, Stylelint -- use `stages: [manual]` to avoid slowing Python-only commits.)
3. If hooks fail:
   a. For auto-fixed files: re-stage them with `git add <specific-file>` (never `git add -A`).
   b. For manual fixes: read the failing files, apply the suggested changes, re-stage.
   c. Re-run the same command(s) until all pass.
4. Do not proceed until linting passes cleanly.

### Step 3: Analyze changes and plan atomic commits

Review `git status` and `git diff` (both staged and unstaged) to understand all changes.

**Atomicity principle**: each commit should have exactly one purpose and one commit type. Split different types into separate commits even within the same file. If you cannot describe a commit in one line, it probably is not atomic.

Common groupings (each becomes its own commit):
- Feature code separate from its tests
- Bug fixes separate from refactors
- Documentation separate from implementation
- Dependency updates separate from the code that uses them
- CI/build config separate from application code

### Step 4: Determine commit type

Check the branch name to decide the type:

- **On `release/*` branches**: use `hotfix` for every commit, regardless of the change's nature. This is because release branches follow a different versioning convention where all changes are hotfixes to the release.
- **On all other branches**: use the standard Conventional Commits type that best fits the change:
  `feat` | `fix` | `refactor` | `docs` | `style` | `perf` | `test` | `build` | `ci` | `chore`

### Step 5: Stage and commit (repeat per atomic group)

For each logical group:

1. **Stage selectively**: use `git add -p` or `git add <specific-files>` to include only related changes. Never use `git add -A` or `git add .` -- these risk including secrets, build artifacts, or unrelated files.

2. **Format the commit message**:
   ```
   [<JIRA-TAG>] <type>(<optional-scope>): <imperative-description>
   ```
   - **JIRA tag**: use the tag the user provides ("use jira tag PII-1234"). If none given, extract from the branch name (`git branch --show-current | grep -oP 'PII-\d+'`). If the branch has no PII tag, ask the user -- never guess.
   - **Description**: imperative mood ("add", not "added"), under 70 characters for the subject line.
   - **Example**: `[PII-2062] fix(postprocessor): resolve memory leak in cluster adapter`

3. **Create the commit** using a HEREDOC for proper formatting:
   ```bash
   git commit -m "$(cat <<'EOF'
   [PII-2062] feat(dashboard): add occupancy heatmap overlay
   EOF
   )"
   ```

4. **After each commit**, verify with `git log --oneline -1` that it looks correct before proceeding to the next.

### Step 6: Push and confirm

- Push all commits: `git push origin <branch>` (no `-u` flag -- to avoid resetting upstream tracking).
- Do not push if on `main` or `master`.
- Show the final `git log --oneline -5` to confirm the atomic commits.

## Rules

- Never include "Generated with Claude Code", "Co-Authored-By: Claude", or emoji in commit messages.
- Never use `git add -A`, `git add .`, or `git add --all`.
- Never use `-i` (interactive) flags -- they require terminal input that is not supported.
- If a pre-commit hook fails, the commit did NOT happen. Fix, re-stage, and create a NEW commit (do not `--amend` -- that would modify the previous unrelated commit).
