---
name: qa
description: RC tag release verification loop - monitors RC tags, verifies GitHub Actions, installs, and validates deployment. Use this skill whenever the user wants to verify an RC build, run QA on a release candidate, check if RC CI passed, validate deployment health after tagging, or confirm that an RC is ready for release. Also use it when the user says things like "did the build pass", "check the RC", "verify the release", "is the deployment healthy", or "run post-release checks". Do NOT use for creating releases, cutting branches, deploying to production, or general version inquiries.
---

# Git Context

- **Current branch**: !`git branch --show-current`
- **Recent RC tags**: !`git tag --sort=-creatordate | grep -E 'rc[0-9]+' | head -5 2>/dev/null || echo "No RC tags found"`
- **Latest workflow runs**: !`gh run list --branch $(git branch --show-current) --limit 3 --json status,conclusion,name,databaseId --jq '.[] | "\(.databaseId) \(.name): \(.conclusion // .status)"' 2>/dev/null || echo "No runs found"`

---

# RC Tag Release Verification Loop

This skill verifies that the most recent RC tag on the current branch builds, installs,
and runs correctly end-to-end. The verification is a loop: if any phase fails, diagnose
the issue, fix the code, create a new RC tag via `/releasebranch`, and restart from Phase 1.

The loop exists because a single fix may uncover further issues downstream. Each iteration
ensures the entire pipeline is validated from scratch with the new tag.

## Phase 1: Discover the RC Tag

Use a `deployment-engineer` subagent (Task tool, `subagent_type=deployment-engineer`):

- [ ] List recent RC tags: `git tag --sort=-creatordate | grep -E 'rc[0-9]+' | head -5`
- [ ] Store the latest RC tag (e.g. `v3.3.2-PII-1610-rc0`) for subsequent phases
- [ ] Read `.github/workflows/` to understand which workflows the tag triggers

## Phase 2: Verify GitHub Actions

Use a `deployment-engineer` subagent:

- [ ] `gh run list --branch <tag>` to find workflow runs for the RC tag
- [ ] Confirm every triggered workflow completed with `conclusion: success`
- [ ] If an installer/NAS-upload workflow exists, confirm it finished (artifact available)

**On failure:**

1. Fetch failed logs: `gh run view <run-id> --log-failed`
2. Use a `debugger` subagent (`subagent_type=debugger`) to diagnose and fix the code
3. Commit the fix with `/commit`
4. Run `/releasebranch` to cut a new RC tag
5. Restart from Phase 1

## Phase 3: Install the Build

Run these commands via Bash (each step must succeed before the next):

```bash
# 1. Extract the installer (SETUP_NOCHECK=1 prevents interactive launch)
VERSION="<discovered-version>"
SETUP_NOCHECK=1 bash /qa/pi-installer/pi-installer-${VERSION}.run \
  --keep --target /qa/pi-installer/pi-installer-${VERSION}

# 2. Run the upgrade
cd /qa/pi-installer/pi-installer-${VERSION}/installer
bash setup.sh --upgrade
```

**On failure:** same loop as Phase 2 -- diagnose, fix, commit, new RC tag, restart.

## Phase 4: Verify Deployment Health

Run these checks. Credentials come from installer `.env` -- never hardcode them.

```bash
# Source credentials from the installation
source ~/plusinsight/installer/.env

# Data flow: vision table (d-platform -> ClickHouse)
clickhouse-client -h localhost --port 9000 \
  -u "${CLICKHOUSE_USER}" --password "${CLICKHOUSE_PASSWORD}" \
  -d plusinsight \
  -q "SELECT count() FROM vision WHERE created_at > now() - INTERVAL 5 MINUTE"

# Data flow: raw table (postprocessor -> ClickHouse)
clickhouse-client -h localhost --port 9000 \
  -u "${CLICKHOUSE_USER}" --password "${CLICKHOUSE_PASSWORD}" \
  -d plusinsight \
  -q "SELECT count() FROM raw WHERE created_at > now() - INTERVAL 5 MINUTE"

# Container health (superset is non-critical, exclude from checks)
docker compose ps --format 'table {{.Name}}\t{{.Status}}'
```

Review logs for the critical services:

```bash
for svc in ai-mediaserver d-platform dashboard-postprocessor schema_migrator; do
  echo "=== $svc ==="
  docker compose logs --tail 50 "$svc"
done
```

**On failure:** same loop -- diagnose, fix, commit, new RC tag, restart.

## Success Criteria

All five must be true before the RC is considered verified:

1. Every GitHub Actions workflow for the RC tag passed
2. Installer upgrade completed without errors
3. Both `vision` and `raw` tables show rows from the last 5 minutes (count > 0)
4. All critical containers report `Up` status (ignore superset)
5. No critical errors (FATAL, unhandled exception) in service logs

## Agent Reference

| Phase | Subagent Type | Purpose |
|-------|---------------|---------|
| Discovery | `deployment-engineer` | Tag listing, workflow analysis |
| GitHub Actions | `deployment-engineer` | CI/CD status verification |
| Failure Analysis | `debugger` | Root cause analysis, code fixes |
| Installation | (direct Bash) | Installer extraction and upgrade |
| Health Check | (direct Bash) | ClickHouse queries, container status, log review |

## Important Notes

- The loop continues until ALL success criteria are met or you've exhausted reasonable fix attempts (3 iterations is a reasonable ceiling before escalating to the user)
- Each failure triggers: fix -> `/commit` -> `/releasebranch` -> restart from Phase 1
- Use parallel subagents when phases are independent (e.g., log review + data checks in Phase 4)
- Always use `/commit` for code fixes (ensures pre-commit hooks run)
- Always use `/releasebranch` to create new RC tags after fixes
- Execute autonomously -- do not ask for confirmation between phases
