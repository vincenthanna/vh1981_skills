---
name: release
description: Finalize and publish a release from a release branch — merge PR to main, create git tag (vX.Y.Z), generate GitHub release notes, and set up the next release branch. Use this skill when the user says "create a release", "ship this version", "release v3.5.0", "finalize the release", "make the release", "cut the release", or "do the release". This is for FINAL releases only. Do NOT use this for release candidates (RC tags) — use the releasebranch skill instead for RC tagging. Do NOT use for deployments, rollbacks, or branch creation without tagging.
disable-model-invocation: true
---

# Git Context

- **Current branch**: !`git branch --show-current`
- **Is release branch**: !`git branch --show-current | grep -qE '^release/[0-9]+\.[0-9]+(\.[0-9]+)?$' && echo "YES" || echo "NO"`
- **Commits ahead of main**: !`git rev-list --count main..HEAD 2>/dev/null || echo "0"`
- **Existing PR**: !`gh pr list --head $(git branch --show-current) --json number,url --jq '.[0] | "PR #\(.number): \(.url)"' 2>/dev/null || echo "No PR"`

---

# Create a New Release

This skill automates the release process including version synchronization, tagging, and release note generation. Supports both minor releases (`release/X.Y`) and patch releases (`release/X.Y.Z`).

## Prerequisites Check

### Step 0: Validate Permissions and Branch

**0.1 Check Admin Access**
- Run `gh api repos/{owner}/{repo}/collaborators/$USER/permission --jq '.permission'`
- If permission is NOT `admin`, display error and stop:
  ```
  ❌ Error: This skill requires admin access to the repository.
  Your permission level: {permission}
  Required: admin
  ```

**0.2 Validate Current Branch**
- Get current branch: `git branch --show-current`
- Must match pattern `release/X.Y` OR `release/X.Y.Z` (e.g., `release/3.4` or `release/3.4.1`)
- If NOT on a release branch, display error and stop:
  ```
  ❌ Error: This skill must be run from a release branch.
  Current branch: {current_branch}
  Expected: release/X.Y (minor) or release/X.Y.Z (patch)

  Examples:
    git checkout release/3.4     # Minor release
    git checkout release/3.4.1   # Patch release
  ```

**0.3 Determine Release Type**
- Parse the branch name to determine release type:
  - `release/X.Y` → **Minor Release** (e.g., `release/3.4` → `v3.4.0`)
  - `release/X.Y.Z` → **Patch Release** (e.g., `release/3.4.1` → `v3.4.1`)
- Store the release type for later workflow branching

### Step 1: Analyze and Visualize the Release

**1.1 Gather Information**
- Get current release branch version from branch name
  - Minor: `release/3.4` → `v3.4.0`
  - Patch: `release/3.4.1` → `v3.4.1`
- Count commits ahead of main: `git rev-list --count main..HEAD`
- Get PR number for current branch: `gh pr list --head $(git branch --show-current) --json number --jq '.[0].number'`

**1.2 For Patch Releases: Find Next Minor Branch**
- If this is a patch release (e.g., `release/3.4.1`):
  - Extract base version (e.g., `3.4`)
  - Calculate next minor version (e.g., `3.5`)
  - Check if `release/{next_minor}` branch exists: `git ls-remote --heads origin release/{next_minor}`
  - If exists, get its PR number: `gh pr list --head release/{next_minor} --json number --jq '.[0].number'`

**1.3 Display Release Diagram**

**For Minor Releases (`release/X.Y`):**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                      MINOR RELEASE WORKFLOW PREVIEW                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Current State:                                                              ║
║  ─────────────                                                               ║
║                                                                              ║
║    main ────●────●────●────●                                                 ║
║                          \                                                   ║
║                           ●────●────●────● release/{version}                 ║
║                           └──────────────┘                                   ║
║                             {commit_count} commits                           ║
║                                                                              ║
║  After Release:                                                              ║
║  ──────────────                                                              ║
║                                                                              ║
║    main ────●────●────●────●────●────●────●────● (tag: v{version}.0)        ║
║                                                                              ║
║                           ↓                                                  ║
║                     release/{next_minor} created                             ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Release Details:                                                            ║
║  • Type: MINOR RELEASE                                                       ║
║  • Branch: release/{version}                                                 ║
║  • Commits: {commit_count}                                                   ║
║  • PR: #{pr_number}                                                          ║
║  • Tag to create: v{version}.0                                               ║
║  • Next branch: release/{next_minor} (will be created)                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**For Patch Releases (`release/X.Y.Z`):**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                      PATCH RELEASE WORKFLOW PREVIEW                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Current State:                                                              ║
║  ─────────────                                                               ║
║                                                                              ║
║    main ────●────●────●────●                                                 ║
║                          \                                                   ║
║                           ●────● release/{patch_version} ({commit_count} commits)
║                          \                                                   ║
║                           ●────●────●────● release/{next_minor} (existing)   ║
║                                                                              ║
║  After Release:                                                              ║
║  ──────────────                                                              ║
║                                                                              ║
║    main ────●────●────●────●────●────● (tag: v{patch_version})              ║
║                                      \                                       ║
║                                       ●────●────●────● release/{next_minor}  ║
║                                       (rebased onto new main)                ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Release Details:                                                            ║
║  • Type: PATCH RELEASE                                                       ║
║  • Branch: release/{patch_version}                                           ║
║  • Commits: {commit_count}                                                   ║
║  • PR: #{pr_number}                                                          ║
║  • Tag to create: v{patch_version}                                           ║
║  • Next branch: release/{next_minor} (will be rebased onto new main)         ║
║  • Next branch PR: #{next_minor_pr_number}                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

If commit count > 100, show this additional warning:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  LARGE PR DETECTED - SPLIT REQUIRED                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  GitHub limits PRs to 100 commits. This release has {commit_count} commits.  ║
║                                                                              ║
║  The following temporary PRs will be created:                                ║
║                                                                              ║
║    tmp/{version}-pt1 ──→ main  (commits 1-100)                               ║
║    tmp/{version}-pt2 ──→ main  (commits 101-200)                             ║
║    ... (as many as needed)                                                   ║
║                                                                              ║
║  Original PR #{pr_number} will be closed with a comment linking              ║
║  to the temporary PRs.                                                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**1.4 Display Summary and Proceed**

After displaying the diagram, proceed immediately with the release workflow. Do not ask for confirmation -- the user invoked this skill intentionally.

## Main Workflow

### Step 2: Handle Large PRs (if commit count > 100)

If the release branch has more than 100 commits, split into temporary PRs:

**2.1 Calculate Split**
- Total commits: `git rev-list --count main..HEAD`
- Number of parts: ceil(total_commits / 100)
- Commits per part: 100 (except last part may have fewer)

**2.2 Create Temporary Branches and PRs**

For each part (1 to N):
```bash
# Get the commit range for this part
START_COMMIT=$((($PART - 1) * 100 + 1))
END_COMMIT=$(($PART * 100))

# Get list of all commits from main to HEAD
ALL_COMMITS=$(git rev-list --reverse main..HEAD)

# Get the Nth commit (END_COMMIT) as the branch point
TARGET_COMMIT=$(echo "$ALL_COMMITS" | sed -n "${END_COMMIT}p")

# Create temporary branch at that commit
git checkout -b tmp/{version}-pt{PART} $TARGET_COMMIT

# Push the branch (no -u flag per constitution)
git push origin tmp/{version}-pt{PART}

# Create PR (base is main for pt1, previous tmp branch for others)
if [ $PART -eq 1 ]; then
  gh pr create --base main --head tmp/{version}-pt{PART} \
    --title "Release v{version} - Part {PART}/{N}" \
    --body "Part {PART} of {N} for release v{version}. See original PR #{original_pr} for full context."
else
  # After pt1 is merged, subsequent PRs target main
  gh pr create --base main --head tmp/{version}-pt{PART} \
    --title "Release v{version} - Part {PART}/{N}" \
    --body "Part {PART} of {N} for release v{version}. See original PR #{original_pr} for full context."
fi
```

**2.3 Rebase Temporary PRs to Main (in order)**

For each temporary PR in order (pt1, pt2, pt3, ...):
```bash
# Checkout main and pull latest
git checkout main
git pull origin main

# Merge the temporary PR using rebase
gh pr merge tmp/{version}-pt{PART} --rebase --delete-branch

# Wait for merge to complete
sleep 2
```

**2.4 Comment and Close Original PR**

After all temporary PRs are merged:
```bash
# Build comment with links to all temporary PRs
COMMENT="This release was split into multiple PRs due to GitHub's 100 commit limit.

The following PRs were created and merged to main:
"

for PART in $(seq 1 $N); do
  PR_URL=$(gh pr view tmp/{version}-pt${PART} --json url --jq '.url' 2>/dev/null || echo "merged")
  COMMENT="${COMMENT}
- Part ${PART}/${N}: ${PR_URL}"
done

COMMENT="${COMMENT}

All commits have been successfully rebased to main."

# Add comment to original PR
gh pr comment {original_pr_number} --body "$COMMENT"

# Close the original PR
gh pr close {original_pr_number}
```

**2.5 Continue to Step 3**

After handling the large PR, continue with the release process from Step 3.

### Step 3: Handle Normal PRs (if commit count <= 100)

If the release branch has 100 or fewer commits:

**3.1 Rebase to Main**
```bash
# Checkout main
git checkout main
git pull origin main

# Merge the release PR using rebase
gh pr merge {pr_number} --rebase --delete-branch
```

### Step 3.5: Run Linting (MANDATORY)

**CRITICAL: This step must NEVER be skipped. Linting issues can break CI/CD pipelines and deployments.**

After the PR is merged to main (or after resolving any cherry-pick conflicts for patch releases):

**3.5.1 Run pre-commit hooks**
```bash
# Pull latest main after merge
git checkout main
git pull origin main

# Run pre-commit on all files
uv run pre-commit run --all-files
```

**3.5.2 Check for auto-fixed issues**
```bash
# Check if any files were modified by pre-commit
git diff --name-only
```

**3.5.3 Commit any linting fixes**
If files were modified:
- Stage the specific modified files (never blind `git add .`)
- Use the `/commit` skill to commit with message: "style: apply pre-commit auto-fixes"
- Push to main: `git push origin main`

**3.5.4 Verify linting passes**
```bash
# Run pre-commit again to ensure all checks pass
uv run pre-commit run --all-files
# This should show all checks passing with no modifications
```

If linting still fails after auto-fixes, manually fix the issues before proceeding.

### Step 4: Create Release

**4.1 Synchronize pyproject.toml version**
- Read current version from `pyproject.toml`
- Compare with release branch version
- Update if different (without 'v' prefix in pyproject.toml)

**4.2 Update dependencies lock file**
- Run `uv lock` to update `uv.lock` with any changes

**4.3 Commit version changes**
- Stage `pyproject.toml` and `uv.lock` if modified
- Use the `/commit` skill to commit with message: `bump up vX.Y.Z`
- Skip if no changes
- Push the commit to remote: `git push origin main`

**4.4 Create git tag**
- Tag the current commit as `vX.Y.Z`
- Push the tag to remote

**4.5 Generate release notes**
- Get previous version tag to compare
- Analyze code diff: `git diff {previous_tag}...HEAD`
- Review all commit messages between versions
- Extract contributors from the **specific release range only**:
  ```bash
  # IMPORTANT: Only get contributors from commits in THIS release range
  # DO NOT use `gh pr list` - it returns contributors from ALL PRs, not just this release!

  # Step 1: Get unique authors from git log for the release range
  git log --format='%an <%ae>' {previous_tag}..{new_tag} | sort -u

  # Step 2: Get commit counts per author to verify
  git shortlog -sn {previous_tag}..{new_tag}

  # Step 3: For each unique author, try to find their GitHub username
  # Use a commit from that author to look up via GitHub API
  for author in $(git log --format='%ae' {previous_tag}..{new_tag} | sort -u); do
    commit=$(git log --format='%H' --author="$author" {previous_tag}..{new_tag} | head -1)
    gh api repos/DeepingSource/plusinsight/commits/$commit \
      --jq '.author.login // .commit.author.name' 2>/dev/null
  done | grep -v 'github-actions' | sort -u
  ```
- If GitHub API returns the git author name (not a username), use the name without `@` prefix
- Structure release notes:

```markdown
# vX.Y.Z

---

## 📋 For Product Managers & Stakeholders

### 🎯 Highlights
[이번 릴리스의 핵심 변경사항을 비기술적인 언어로 요약]
- 사용자가 체감할 수 있는 변화 위주로 작성
- 기술 용어 대신 기능/효과 중심으로 설명

### ✨ New Features
- [기능 설명 - 사용자 관점에서 어떤 것이 가능해졌는지]
- JIRA 링크 포함: [PII-1234](https://deepingsource.atlassian.net/browse/PII-1234)

### 🐛 Bug Fixes
- [수정된 문제 설명 - 이전에 발생하던 문제와 해결 내용]
- 해당되는 경우 JIRA 링크 포함

### 📈 Improvements
- 성능 개선 (예: "대시보드 로딩 속도 향상")
- 안정성 개선 (예: "카메라 연결 안정성 강화")
- 사용성 개선 (예: "설정 화면 UI 개선")

### ⚠️ Cautions
- [이번 업데이트로 인해 실제로 주의해야 할 사항만 작성]
- 예: "기존 ROI 설정이 초기화되므로 재설정 필요"
- 예: "환경변수 ABC가 XYZ로 이름 변경됨"
- 예: "v3.0 이전 버전에서 업그레이드 시 DB 마이그레이션 필수"
- 주의사항이 없으면 "없음" 으로 표기

---

## 🔧 For Developers

### ⚙️ Technical Changes
- [기술적 변경사항 상세 설명]
- API 변경, 아키텍처 변경, 마이그레이션 필요사항 등
- Breaking changes가 있다면 명시

### 📦 Component Updates
- **d-platform**: [vX.Y.Z](https://github.com/deepingsource/d-platform/releases/tag/vX.Y.Z) - 변경 요약
- **dashboard-front**: [vX.Y.Z](https://github.com/deepingsource/dashboard-front/releases/tag/vX.Y.Z) - 변경 요약
- 이전 릴리스 대비 버전이 변경된 컴포넌트만 나열

### 📝 Migration Guide
- [업그레이드 시 필요한 작업이 있다면 설명]
- 설정 변경, 환경변수 추가, DB 마이그레이션 등

---

## 👥 Contributors
- @github_username1
- @github_username2
- @github_username3
```

**4.6 Create GitHub release**
- Use `gh release create vX.Y.Z`
- Set title: `vX.Y.Z`
- Include generated release notes
- Attach to the tagged commit

### Step 5: Post-Release Branch Management

**This step differs based on release type (Minor vs Patch).**

---

#### Step 5A: For MINOR Releases (`release/X.Y`)

**5A.1 Calculate next minor version**
- If recent was `release/3.4` → create `release/3.5`
- If recent was `release/2.6` → create `release/2.7`

**5A.2 Create and setup new branch**
```bash
git checkout -b release/X.Y
```

**5A.3 Update version**
- Update `pyproject.toml` version to `X.Y.0-rc0`
- Run `uv lock` to update dependencies

**5A.4 Commit and push**
- Stage `pyproject.toml` and `uv.lock`
- Use the `/commit` skill to commit with message: `bump up vX.Y.0-rc0`
- Push without -u flag: `git push origin release/X.Y`
- Then set upstream to base branch: `git branch --set-upstream-to=origin/main`

**5A.5 Create Pull Request for the Release Branch**
```bash
gh pr create --title "Release vX.Y.0" --body "" --base main --head release/X.Y
```

---

#### Step 5B: For PATCH Releases (`release/X.Y.Z`)

**5B.1 Find the next minor release branch**
- Extract base version from patch (e.g., `release/3.4.1` → base is `3.4`)
- Calculate next minor (e.g., `3.4` → `3.5`)
- The branch `release/{next_minor}` should already exist

**5B.2 Verify next minor branch exists**
```bash
# Check if branch exists on remote
git ls-remote --heads origin release/{next_minor}
```
- If the branch does NOT exist, display warning and skip Step 5B:
  ```
  ⚠️ Warning: Next minor branch release/{next_minor} does not exist.
  Skipping branch rebase. You may need to create it manually.
  ```

**5B.3 Rebase next minor branch onto new main**

```bash
# Ensure we have the latest main (which now includes the patch)
git checkout main
git pull origin main

# Fetch the next minor branch
git fetch origin release/{next_minor}
git checkout release/{next_minor}
git pull origin release/{next_minor}

# Rebase onto new main, preferring main's changes on conflict
# Using -X theirs means "prefer main's version" when conflicts occur
git rebase main -X theirs
```

**5B.4 Handle rebase conflicts (if any)**

If conflicts occur during rebase:
```bash
# For each conflicted file, prefer main's version
# This is handled automatically by -X theirs flag

# If manual intervention is still needed:
# 1. For each conflict, accept the version from main (ours during rebase = main)
git checkout --theirs .
git add .
git rebase --continue

# Repeat until rebase completes
```

**5B.5 Run linting on rebased branch (MANDATORY)**

After rebase completes, run linting to catch any issues:
```bash
# Run pre-commit on all files
uv run pre-commit run --all-files
```

If files were modified by pre-commit auto-fixes:
- Stage the specific modified files (never blind `git add .`)
- Use the `/commit` skill to commit with message: "style: apply pre-commit auto-fixes after rebase"

Then verify linting passes:
```bash
uv run pre-commit run --all-files
```

**5B.6 Force push the rebased branch**
```bash
# Force push is required because we rewrote history
git push --force-with-lease origin release/{next_minor}
```

**5B.7 Update the PR for the rebased branch**
```bash
# Add a comment to the PR explaining the rebase
gh pr comment {next_minor_pr_number} --body "$(cat <<'EOF'
🔄 **Branch Rebased**

This branch has been rebased onto `main` after the patch release `v{patch_version}` was merged.

**What happened:**
- Patch release `release/{patch_version}` was merged to `main`
- This branch (`release/{next_minor}`) has been rebased onto the new `main`
- Any conflicts were resolved by preferring `main`'s version (which includes the patch)
- Pre-commit linting was applied to ensure code quality

**Action required:**
- Please review the rebased commits to ensure everything looks correct
- If any changes were lost during conflict resolution, please re-apply them
EOF
)"
```

**5B.8 Display completion message**
```
✅ Patch release complete!

Summary:
- Patch release v{patch_version} has been created and tagged
- Branch release/{next_minor} has been rebased onto new main
- PR #{next_minor_pr_number} has been updated with rebase information

Next steps:
- Review the rebased release/{next_minor} branch
- Continue development on release/{next_minor} as normal
```

---

## Release Note Guidelines:

### For Product Managers & Stakeholders Section:
- **Write in Korean**: Content should be written in Korean
- **Use non-technical language**: Focus on features/effects instead of technical terms
  - Bad: "Redis 캐시 TTL 최적화로 메모리 사용량 감소"
  - Good: "시스템 메모리 사용량을 줄여 안정성 향상"
- **User perspective**: Write so that PMs and non-developers can understand
  - Bad: "API 엔드포인트에 rate limiting 추가"
  - Good: "서버 과부하 방지를 위한 요청 제한 기능 추가"

### For Developers Section:
- **Include technical details**: API changes, architecture changes, breaking changes, etc.
- **Migration guide**: Specify required tasks for upgrades
- **Component versions**: Include changed submodule versions with links

### General:
- **JIRA integration**: Convert `PII-1000` format tags to links
- **Code analysis based**: Analyze actual code changes, not just commit messages
- **Contributor extraction**:
  - **CRITICAL**: Only count contributors from the specific release range (`{previous_tag}..{new_tag}`)
  - **DO NOT** use `gh pr list` to get contributors - this returns ALL PR authors, not release-specific ones
  - Use `git shortlog -sn {previous_tag}..{new_tag}` to verify contributor count
  - For GitHub usernames, use the commit-based API lookup
  - If no GitHub account is linked, use the git author name without `@` prefix
  - Excludes github-actions[bot]
  - Format: bullet list with `- @username` (or `- name` if no GitHub account)

## Important Notes:

- **All commits via /commit skill**: Every commit during this workflow must use the `/commit` skill -- raw `git commit` is forbidden per project constitution
- **No user confirmation**: Proceed autonomously once invoked -- do not ask the user for confirmation
- **Admin access required**: Only repository admins can run this skill
- **Must be on release branch**: Skill only works when checked out to `release/X.Y` or `release/X.Y.Z`
- **Release types**:
  - **Minor** (`release/X.Y`): Creates new release branch after completion
  - **Patch** (`release/X.Y.Z`): Rebases existing next minor branch onto new main
- **Large PR handling**: PRs with >100 commits are automatically split into temporary PRs
- **Patch release conflicts**: When rebasing the next minor branch, main's version (with patch) takes precedence
- **MANDATORY LINTING**: Always run `uv run pre-commit run --all-files` after:
  - Merging to main (Step 3.5)
  - Resolving cherry-pick conflicts
  - Rebasing branches (Step 5B.5)
  - Any manual code modifications
  - **Never skip linting** - it catches style issues that break CI/CD
- Version format: `vX.Y.Z` for tags, `X.Y.Z` in pyproject.toml
- Always analyze actual code changes for accurate release notes
- Include all JIRA tags with proper links
- Group changes logically by type
- Ensure pyproject.toml stays in sync with releases

## Special Case: Cherry-Pick Patch Releases

When creating a patch release by cherry-picking commits from a newer branch:

**1. Create patch branch from tag**
```bash
git checkout v{base_version}
git checkout -b release/{patch_version}
```

**2. Cherry-pick commits**
```bash
git cherry-pick {commit_hash} --no-edit
# If conflicts occur, resolve them manually
```

**3. MANDATORY: Run linting after cherry-picks**
```bash
# Run pre-commit on all files
uv run pre-commit run --all-files
```

If files were modified by pre-commit auto-fixes:
- Stage the specific modified files (never blind `git add .`)
- Use the `/commit` skill to commit with message: "style: apply pre-commit auto-fixes"

Then verify all checks pass:
```bash
uv run pre-commit run --all-files
```

**4. Continue with normal patch release flow**
- Push branch, create PR, merge, tag, etc.

**Why linting is critical for cherry-picks:**
- Cherry-picked code may have been written with different linting rules
- Conflict resolution can introduce style inconsistencies
- Ruff may auto-fix code to use newer Python features (e.g., `removeprefix`/`removesuffix`)
- Skipping linting can break CI/CD pipelines

## Examples:

### Example 1: Minor Release (release/3.4)
```
Current branch: release/3.4
Result:
  - v3.4.0 tag created
  - GitHub release created
  - release/3.5 branch created with v3.5.0-rc0
  - PR created for release/3.5
```

### Example 2: Patch Release (release/3.4.1)
```
Current branch: release/3.4.1
Existing branch: release/3.5

Result:
  - v3.4.1 tag created
  - GitHub release created
  - release/3.5 rebased onto new main (which includes v3.4.1)
  - PR for release/3.5 updated with rebase comment
```
