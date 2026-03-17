---
name: releasebranch
description: Create release candidate (RC) tags for release or feature branches. Use this skill whenever the user says "tag an RC", "create a release candidate", "cut an RC", "cut a new RC", "make an RC tag", "tag a release candidate", or any variation of creating/tagging an RC. Do NOT use this for final releases (use the release skill instead), listing/querying existing RC tags, deleting tags, or creating release branches.
---

# Git Context

- **Current branch**: !`git branch --show-current`
- **Is release branch**: !`git branch --show-current | grep -qE '^release/' && echo "YES - Release Branch" || echo "NO - Feature Branch"`
- **Existing RC tags**: !`git tag -l '*-rc*' | grep "$(git branch --show-current | sed 's|release/||' | sed 's|.*/||')" | tail -5 2>/dev/null || echo "None"`

---

# Create Release Candidate Tag

This skill creates release candidate (RC) tags for:
1. **Release branches** (release/X.Y) → Creates `vX.Y.Z-rcN` tags
2. **Feature branches** targeting release branches → Creates `vX.Y.Z-JIRA-XXXX-rcN` tags

## Prerequisites

- Must be on a release branch or feature branch targeting a release branch
- Cannot be run from main branch
- Git and GitHub CLI must be configured

## Steps:

### 1. Validate Branch Context

**Detect if on release branch or feature branch:**
```bash
# Get current branch name
current_branch=$(git branch --show-current)

# Check if it's main branch (not allowed)
if [[ "$current_branch" == "main" ]]; then
    echo "Error: This skill cannot be run from main branch"
    exit 1
fi

# Determine if this is a release branch or feature branch
is_release_branch=false
base_branch=""

if [[ "$current_branch" =~ ^release/ ]]; then
    # Running from release branch
    is_release_branch=true
    base_branch="$current_branch"
    echo "[OK] Running from release branch: $current_branch"
else
    # Running from feature branch - need to find target release branch
    echo "--> Detecting target branch for feature branch: $current_branch"

    # Try to get from PR if one exists
    base_branch=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo "")

    # If no PR exists, get the upstream branch
    if [[ -z "$base_branch" ]]; then
        base_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null | sed 's|origin/||' || echo "")
    fi

    # If still no base branch, check merge-base with release branches
    if [[ -z "$base_branch" ]]; then
        for branch in $(git branch -r | grep "origin/release/" | sed 's|origin/||' | sed 's|^[[:space:]]*||'); do
            if git merge-base --is-ancestor HEAD "origin/$branch" 2>/dev/null; then
                base_branch="$branch"
                break
            fi
        done
    fi

    # Validate base branch is a release branch
    if [[ "$base_branch" =~ ^release/ ]]; then
        echo "[OK] Feature branch '$current_branch' targets release branch '$base_branch'"
    else
        echo "Error: Feature branch must be targeting a release branch (found: $base_branch)"
        echo "This skill is only for branches related to release/* branches"
        exit 1
    fi
fi
```

### 2. Extract Version from Branch

**Parse version from release branch name:**
```bash
# Extract version from release/X.Y or release/X.Y.Z format
if [[ "$base_branch" =~ ^release/([0-9]+\.[0-9]+(\.[0-9]+)?)$ ]]; then
    version_number="${BASH_REMATCH[1]}"

    # Add .0 if only major.minor provided (release/3.0 → 3.0.0)
    if [[ "$version_number" =~ \.[0-9]+\.[0-9]+$ ]]; then
        # Already has patch version, use as-is
        version="v${version_number}"
    else
        # Only major.minor, add .0
        version="v${version_number}.0"
    fi

    echo "[OK] Extracted version: $version from $base_branch"
else
    echo "Error: Unable to parse version from branch name: $base_branch"
    exit 1
fi
```

### 3. Extract JIRA Tag (Feature Branches Only)

**Find JIRA tag from branch name or commit messages (skip if on release branch):**
```bash
jira_tag=""

if [[ "$is_release_branch" == false ]]; then
    # Only extract JIRA tag for feature branches
    echo "--> Extracting JIRA tag for feature branch..."

    # Try to extract from current branch name
    if [[ "$current_branch" =~ (PII-[0-9]+) ]] || \
       [[ "$current_branch" =~ ([A-Z]+-[0-9]+) ]]; then
        jira_tag="${BASH_REMATCH[1]}"
        echo "[OK] Found JIRA tag from branch name: $jira_tag"
    fi

    # If not found in branch name, search commit messages
    if [[ -z "$jira_tag" ]]; then
        echo "--> Searching for JIRA tag in commit messages..."

        # Get commits in this branch that aren't in the base branch
        jira_tag=$(git log origin/$base_branch..HEAD --pretty=format:"%s %b" | \
                    grep -oE '\[([A-Z]+-[0-9]+)\]' | \
                    head -1 | \
                    sed 's/\[\(.*\)\]/\1/')

        if [[ -n "$jira_tag" ]]; then
            echo "[OK] Found JIRA tag from commits: $jira_tag"
        else
            echo "Error: No JIRA tag found in branch name or commit messages"
            echo "Please ensure your branch name or commits contain a JIRA tag (e.g., PII-1234)"
            exit 1
        fi
    fi
else
    echo "--> Release branch detected - skipping JIRA tag extraction"
fi
```

### 4. Determine Release Candidate Number

**Find the next RC number by checking existing tags:**
```bash
# Fetch all tags from remote to ensure we have the latest
git fetch --tags -q

# Construct tag pattern based on branch type
if [[ "$is_release_branch" == true ]]; then
    # Pattern for release branch RC tags: vX.Y.Z-rcN
    tag_pattern="${version}-rc"
else
    # Pattern for feature branch RC tags: vX.Y.Z-JIRA-XXXX-rcN
    tag_pattern="${version}-${jira_tag}-rc"
fi

# Get all existing RC tags matching the pattern
existing_rc_tags=$(git tag -l "${tag_pattern}*" | sort -V)

if [[ -z "$existing_rc_tags" ]]; then
    # No existing RC tags, start with rc1
    rc_number=1
    echo "--> No existing RC tags found, starting with rc1"
else
    # Extract the highest RC number
    highest_rc=$(echo "$existing_rc_tags" | tail -1 | grep -oE 'rc([0-9]+)$' | sed 's/rc//')

    if [[ -n "$highest_rc" ]]; then
        rc_number=$((highest_rc + 1))
        echo "--> Found existing RC tags:"
        echo "$existing_rc_tags" | sed 's/^/  - /'
        echo "--> Next RC number: rc${rc_number}"
    else
        rc_number=1
        echo "--> Starting with rc1"
    fi
fi

# Construct the new tag
if [[ "$is_release_branch" == true ]]; then
    new_tag="${version}-rc${rc_number}"
else
    new_tag="${version}-${jira_tag}-rc${rc_number}"
fi

echo "[OK] New tag will be: $new_tag"
```

### 5. Create and Push Tag

**Tag the current commit and push to remote:**
```bash
# Get the current commit hash for reference
current_commit=$(git rev-parse HEAD)
commit_short=$(git rev-parse --short HEAD)

echo ""
echo "Tagging commit $commit_short with $new_tag"

# Create annotated tag with message
if [[ "$is_release_branch" == true ]]; then
    tag_message="Release candidate ${rc_number} for ${version}

Version: ${version}
Branch: ${current_branch}
Commit: ${commit_short}"
else
    tag_message="Release candidate ${rc_number} for ${jira_tag}

Version: ${version}
Branch: ${current_branch}
Target: ${base_branch}
JIRA: https://deepingsource.atlassian.net/browse/${jira_tag}
Commit: ${commit_short}"
fi

git tag -a "$new_tag" -m "$tag_message"

# Push the tag to remote
echo "--> Pushing tag to remote..."
git push origin "$new_tag"

echo ""
echo "Successfully created release candidate tag!"
echo ""
echo "Tag: $new_tag"
echo "Commit: $commit_short"

if [[ "$is_release_branch" == false ]]; then
    echo "JIRA: https://deepingsource.atlassian.net/browse/${jira_tag}"
fi
```

### 6. Display Next Steps

**Show helpful information for the developer:**
```bash
echo ""
echo "Next Steps:"
echo "1. This RC tag can be used for testing and validation"
echo "2. To create another RC, make new commits and run this skill again"
echo "3. View all RC tags: git tag -l '${tag_pattern}*'"

if [[ "$is_release_branch" == true ]]; then
    echo "4. When ready for final release, create tag: ${version}"
else
    echo "4. When ready to merge, the release will use version: $version"
fi
```

## Error Handling

The skill will exit with appropriate error messages if:
- Run from main branch
- Feature branch is not targeting a release branch
- Unable to determine version from release branch name
- No JIRA tag found for feature branches
- Git operations fail

## Examples

### Example 1: Release branch (new workflow)
```bash
# Current branch: release/3.0
# No existing tags
# Result: v3.0.0-rc1

# After more commits on release/3.0
# Existing tag: v3.0.0-rc1
# Result: v3.0.0-rc2
```

### Example 2: Feature branch with JIRA tag
```bash
# Current branch: PII-1234-new-feature
# Base branch: release/3.0
# No existing tags
# Result: v3.0.0-PII-1234-rc1
```

### Example 3: Feature branch with JIRA in commits
```bash
# Current branch: feature/awesome-update
# Base branch: release/3.0.1
# Commit message contains: [PII-5678] Add new feature
# Existing tag: v3.0.1-PII-5678-rc1
# Result: v3.0.1-PII-5678-rc2
```

### Example 4: Multiple RC iterations on release branch
```bash
# Current branch: release/2.5
# Existing tags: v2.5.0-rc1, v2.5.0-rc2
# Result: v2.5.0-rc3
```

## Important Notes

- **Version Format**: Tags use `vX.Y.Z` format (with 'v' prefix)
- **RC Formats**:
  - Release branch: `vX.Y.Z-rcN`
  - Feature branch: `vX.Y.Z-JIRA-XXXX-rcN`
- **JIRA Integration**: Only required for feature branches
- **Incremental RCs**: Each run increments the RC number
- **Tag Persistence**: Tags are pushed to remote immediately
- **Use Cases**:
  - Release branch RCs: For pre-release testing of the entire release
  - Feature branch RCs: For testing specific features before merging to release
