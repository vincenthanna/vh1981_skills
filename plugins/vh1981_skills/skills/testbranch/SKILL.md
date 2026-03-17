---
description: "Test branch code changes on a live PLUSINSIGHT installation by volume-mounting source into Docker containers and running automated verification (infrastructure, data pipeline, browser/UI). USE THIS SKILL when the user wants to: test changes on the live system, mount branch code into running containers, verify changes on the installation, run testbranch, check what is different between branch and installed version (--diff), restore the installation to its original state (--restore), check dev-mount status (--status), do a dry run of changes (--dry-run), run only verification without remounting (--qa-only), mount without verification (--mount-only), or test browser/minimap rendering after changes. Also triggers for phrases like 'try this on the live system', 'verify on the installation', 'check if my changes work on the running system'. Do NOT use for: running unit tests (use pytest), deploying to production (use /release), creating Docker images (use docker build), running pre-commit checks, creating Alembic migrations, reviewing PRs, debugging ClickHouse queries, or managing Kubernetes deployments."
argument-hint: "[FLAGS] [--install-path PATH]"
---

# /testbranch Skill

Rapidly test the current branch's code changes on a live PLUSINSIGHT installation.
Compares installed component versions against branch HEAD, volume-mounts changed
source code into running Docker containers, and runs automated verification.

## Path Resolution

Resolve these two paths before any operation:

1. **repo_root**: Run `git rev-parse --show-toplevel` from the current working directory.
2. **install_path**: Default is `~/plusinsight`. Override with `--install-path <PATH>`.
   Expand `~` to the user's home directory and resolve to an absolute path.

## Flag Reference

| Flag             | Behavior                                       | Exclusive With                               |
|------------------|-------------------------------------------------|----------------------------------------------|
| (none)           | Full flow: snapshot, diff, update, verification | --diff, --restore, --qa-only, --status       |
| `--diff`         | Show version comparison table only              | --restore, --mount-only, --qa-only           |
| `--restore`      | Revert to saved snapshot                        | All others                                   |
| `--mount-only`   | Apply changes, skip verification                | --qa-only, --diff, --restore                 |
| `--qa-only`      | Run verification without remounting             | --mount-only, --diff, --restore              |
| `--no-qa`        | Skip all verification after mounting            | --qa-only, --browser-only, --data-only       |
| `--browser-only` | Run only browser tests (minimap + E2E)          | --no-browser, --data-only, --no-qa           |
| `--no-browser`   | Skip browser tests, run infra + data only       | --browser-only                               |
| `--data-only`    | Run only ClickHouse + Redis checks              | --browser-only, --no-qa                      |
| `--status`       | Show current dev-mount state                    | All others                                   |
| `--dry-run`      | Show plan without executing                     | --status                                     |
| `--install-path` | Override install path (default: ~/plusinsight)   | -                                            |

Parse flags from the user's input text. Flags may appear in any order.
Validate mutual exclusivity. If conflicting flags are given, print an error
message listing the conflict and stop.

---

## Precondition Checks

Before executing any flow, run these checks in order. Stop on the first failure.

### 1. Docker Running

```bash
docker info > /dev/null 2>&1
```

If this fails, print: `ERROR: Docker is not running. Start Docker and try again.`

### 2. Install Path Valid

```python
from pathlib import Path
from plusinsight_installer.core.dev_test import DevTestManager

repo_root = Path('<resolved_repo_root>')
install_path = Path('<resolved_install_path>')

manager = DevTestManager(repo_root=repo_root, install_path=install_path)
manager.validate_install_path()
```

If `FileNotFoundError` is raised, print the error message (it already includes
`Use --install-path.` guidance) and stop.

### 3. Branch Detection

```bash
git rev-parse --abbrev-ref HEAD
```

Store the result as `branch_name` for use in display output.

### 4. Playwright MCP Available

Only check Playwright if the branch contains frontend changes. First, detect
whether any frontend components changed by doing a lightweight git diff:

```python
import subprocess
from pathlib import Path
from plusinsight_installer.core.dev_test import DevTestManager

repo_root = Path('<resolved_repo_root>')
install_path = Path('<resolved_install_path>')

manager = DevTestManager(repo_root=repo_root, install_path=install_path)

base_ref_result = subprocess.run(
    ['git', 'rev-parse', '--abbrev-ref', '@{u}'],
    capture_output=True, text=True, cwd=str(repo_root),
)
upstream = base_ref_result.stdout.strip()
# Guard: if upstream points to the feature branch itself, fall back
if not upstream or base_ref_result.returncode != 0:
    base_ref = 'main'
elif upstream.split('/')[-1] == repo_root.name or 'PII-' in upstream:
    base_ref = 'release/3.5'  # fallback -- detect_changed_components will refine
else:
    base_ref = upstream.removeprefix('origin/')

preflight_components = manager.detect_changed_components(base_ref=base_ref)

from plusinsight_installer.core.version_diff import VersionDiffEngine, has_frontend_changes, ChangeCategory
from plusinsight_installer.core.dev_test import COMPONENT_REGISTRY

engine = VersionDiffEngine(repo_root=repo_root, components=preflight_components)
# Use empty snapshot for preflight -- we only need change categories, not installed hashes
preflight_diffs = engine.compute_diffs(snapshot_hashes={})
frontend_in_branch = has_frontend_changes(preflight_diffs, COMPONENT_REGISTRY)
```

**If `frontend_in_branch` is True**: Verify that the Playwright MCP browser
automation is reachable by calling `browser_navigate(url="about:blank")`.
If this call fails or the Playwright MCP tool is not available, print:
```
ERROR: Playwright MCP is not available. Browser tests are mandatory for frontend changes.
Ensure the Playwright MCP server is running and configured in Claude Code.
```
Then FAIL the entire skill -- do not proceed with any flow.

**If `frontend_in_branch` is False**: Skip the Playwright check entirely.
Print:
```
INFO: No frontend component changes detected -- Playwright check skipped.
```
Browser tests will be auto-skipped during verification (see Browser Test
Auto-Detection in the --qa-only flow).

### 5. ECR Authentication

Verify that Docker can pull from the AWS ECR registry.  Read `AWS_ECR_URL`
from `install_path/.env` and attempt a lightweight check:

```bash
docker manifest inspect <AWS_ECR_URL>/pi-bootstrap-schema-migrator:latest > /dev/null 2>&1
```

If this fails, automatically refresh ECR credentials:

```bash
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin <AWS_ECR_URL>
```

If the refresh also fails, print:
```
WARNING: ECR authentication failed. ONNX models cannot be extracted
from ECR. All 7 C++ plugins are built in-container, but models may be
stale. Run 'aws ecr get-login-password --region ap-northeast-2 |
docker login --username AWS --password-stdin <ECR_URL>' manually if
needed.
```
Continue with the flow (ECR is not a hard blocker -- all plugins are
built in-container).

### 6. Version Comparison Table

After all preconditions pass, **always** display the version comparison table
regardless of which flag is used. This shows the user what is currently
installed versus what the branch will upgrade each component to.

```python
manager.show_version_comparison()
```

This prints a rich table with columns: Component, Local Version, Branch Version,
and Status (up to date / upgrade / unknown). It reads installed versions from
the `.env` file and computes branch hashes from git -- no snapshot required.

The table includes two sections:
1. **Application components** -- git-hash-based version comparison (e.g. mediaserver, postprocessor)
2. **Infrastructure services** -- semantic version comparison from `installer/.env` vs installed `.env`
   (e.g. clickhouse 24.8 -> 25.1, redis 7.0 -> 7.2)

---

## Flow: --status

Show current dev-mount state. No snapshot or diff operations.

```python
from pathlib import Path
from plusinsight_installer.core.dev_test import DevTestManager

repo_root = Path('<resolved_repo_root>')
install_path = Path('<resolved_install_path>')

manager = DevTestManager(repo_root=repo_root, install_path=install_path)
manager.status()
```

Print the output and stop. No further steps.

---

## Flow: --restore

Revert the installation to its pre-testbranch state.

Prefers installer-based restore (re-runs the base version's ``setup.sh --upgrade``)
over snapshot-based file restore.  Installer restore is more reliable because it
uses the actual installer artifacts (Docker images + config templates) instead of
file-level backups that can become stale across sessions.

```python
from pathlib import Path
from plusinsight_installer.core.snapshot import SnapshotManager

install_path = Path('<resolved_install_path>')

snap = SnapshotManager(install_path=install_path)

# Try installer-based restore first (preferred)
if snap.restore_via_installer():
    print('Installation restored via installer upgrade.')
elif snap.exists():
    # Fall back to snapshot-based restore
    snap.restore()
    print('Installation restored from snapshot.')
else:
    print('ERROR: No installer or snapshot found. Run /testbranch first.')
    # Stop here
```

The installer-based restore reads ``PLUSINSIGHT_VERSION`` from the installed
``.env`` (e.g. ``v3.5.0-rc1``) and looks for the matching installer package at
``/qa/pi-installer/pi-installer-{version}/installer/setup.sh``.  If found, it
runs ``bash setup.sh --upgrade`` which cleanly restores all Docker images,
configs, and services to the base version state.

---

## Flow: --diff (Diff Only)

Show the version comparison table without making any changes.

### Step 1: Snapshot

```python
from pathlib import Path
from plusinsight_installer.core.snapshot import SnapshotManager

install_path = Path('<resolved_install_path>')
snap = SnapshotManager(install_path=install_path)

if not snap.exists():
    snap.create()

snapshot_hashes = snap.load()
```

### Step 2: Detect Changed Components

```python
from plusinsight_installer.core.dev_test import DevTestManager

repo_root = Path('<resolved_repo_root>')
manager = DevTestManager(repo_root=repo_root, install_path=install_path)

# Detect base branch dynamically -- NEVER hardcode 'main' or a specific release branch
import subprocess
base_ref_result = subprocess.run(
    ['git', 'rev-parse', '--abbrev-ref', '@{u}'],
    capture_output=True, text=True, cwd=str(repo_root),
)
base_ref = base_ref_result.stdout.strip().removeprefix('origin/') if base_ref_result.returncode == 0 else 'main'

components = manager.detect_changed_components(base_ref=base_ref)
```

If no components have changes, print a message saying no changes detected and stop.

### Step 3: Compute and Display Diffs

```python
from plusinsight_installer.core.version_diff import VersionDiffEngine

engine = VersionDiffEngine(repo_root=repo_root, components=components)
diffs = engine.compute_diffs(snapshot_hashes=snapshot_hashes)

table_output = engine.format_table(
    diffs=diffs,
    install_path=str(install_path),
    branch_name=branch_name,
)
print(table_output)
```

Stop here. Do not apply any changes.

### Sub-Component Change Detection

Each `VersionDiff` carries a `change_categories: frozenset[ChangeCategory]` field
that classifies WHAT kind of files changed within the component (not just whether
the hash differs). This enables skipping expensive operations when irrelevant
files changed.

**Categories:**

| Category | Meaning | Example Files |
|----------|---------|---------------|
| `CPP` | C++ source code | `cpp/**/*.cpp`, `cpp/**/*.h`, `cpp/**/*.cu`, `cpp/**/Makefile` |
| `MODELS` | Model configuration | `model_id.yaml` |
| `PYTHON` | Python source | `**/*.py` |
| `DOCKER` | Dockerfile changes | `Dockerfile*` |
| `DEPS` | Dependency files | `pyproject.toml`, `package.json`, `uv.lock` |
| `CODE` | Frontend source | `**/*.ts`, `**/*.tsx`, `**/*.css` |
| `CYTHON` | Cython source | `**/*.pyx`, `**/*.pxd` |
| `CONFIG` | Config files | `*.yaml`, `*.json`, `*.toml` |
| `OTHER` | Unmatched files | Everything else |

**Gating rules in `start()`:**

| Action | Only runs when | Skip message |
|--------|----------------|--------------|
| C++ plugin build (`_sync_cpp_plugins`) | `CPP` in categories | `Skipping C++ plugin build (no C++ file changes)` |
| Frontend build (`build_frontend`) | `CODE` or `DEPS` in categories | `Skipping frontend build (no code/deps changes)` |
| TRT engine sync (`_sync_dplatform_engines`) | `MODELS` in categories | `Skipping TRT engine sync (no model file changes)` |
| Post-mount commands (`_run_post_mount_cmds`) | `CYTHON`, `DOCKER`, or `DEPS` in categories | Silently skipped |

When `category_map` is `None` (direct CLI usage without the dispatcher),
all actions run unconditionally for backward compatibility.

```python
from plusinsight_installer.core.version_diff import ChangeCategory
# Available on each diff:
diff.change_categories  # frozenset[ChangeCategory]
```

---

## Flow: --dry-run

Show the full plan (snapshot, diff, classification) without executing updates.

Execute all steps from the **--diff** flow above, then continue:

### Step 4: Classify Changes

```python
from plusinsight_installer.core.update_dispatch import UpdateDispatcher

dispatcher = UpdateDispatcher(manager=manager)
classified = dispatcher.classify_changes(diffs=diffs)
# classified is list[tuple[VersionDiff, UpdateStrategy]]
```

Iterate with tuple unpacking: `for diff, strategy in classified:`.
Print the classified changes as a plan table showing each component, its
strategy, and estimated time.

If any component has `ChangeType.BUILD_REQUIRED` or `ChangeType.IMAGE_REBUILD`,
print the appropriate warning:

- **C++ changes in d-platform**: C++ plugins and models are automatically extracted from the CI-built ECR image when the branch hash differs from the installed hash. If ECR pull fails, print: `WARNING: ECR pull failed (run awslogin?). C++ plugins not synced.`
- **Dockerfile changed**: `WARNING: Dockerfile changes detected in <component>. Runtime environment may differ. Consider full CI for final validation.`

Stop here. Do not execute updates.

---

## Flow: --qa-only

Run verification checks without making any mount changes.

### Verification Scope

Determine which checks to run based on additional flags:

| Flag             | Infrastructure | Data Pipeline | Browser/UI |
|------------------|----------------|---------------|------------|
| (default)        | Yes            | Yes           | Yes        |
| `--browser-only` | No             | No            | Yes        |
| `--no-browser`   | Yes            | Yes           | No         |
| `--data-only`    | No             | Yes           | No         |

### Browser Test Auto-Detection

After computing version diffs (Steps 1-3), automatically determine whether
browser tests should be included based on which components changed. Use the
`has_frontend_changes()` utility from `plusinsight_installer.core.version_diff`:

```python
from plusinsight_installer.core.version_diff import has_frontend_changes
from plusinsight_installer.core.dev_test import COMPONENT_REGISTRY

frontend_changed = has_frontend_changes(diffs, COMPONENT_REGISTRY)
```

Resolve the effective verification scope according to this table:

| Condition                                      | Effective Scope | Action                                      |
|------------------------------------------------|-----------------|----------------------------------------------|
| `--browser-only` flag given                    | `browser-only`  | Run only browser tests (existing behavior)   |
| `--data-only` flag given                       | `data-only`     | Run only data pipeline checks (existing)     |
| `--no-browser` AND frontend changed            | `no-browser`    | Print `WARNING: Frontend changes detected in branch but --no-browser flag skips browser tests.` |
| `--no-browser` AND no frontend changes         | `no-browser`    | Silent, no warning needed                    |
| No scope flag AND frontend changed             | `all`           | Auto-include browser tests; print `INFO: Frontend component changes detected -- including browser verification.` |
| No scope flag AND no frontend changes          | `no-browser`    | Auto-skip browser tests; print `INFO: No frontend component changes detected -- skipping browser tests.` |

This auto-detection applies to the `--qa-only` flow and the default (full) flow's
Step 6 verification phase. The `--mount-only` and `--no-qa` flows do not run verification.

### Infrastructure Checks

Run these checks if infrastructure scope is enabled:

1. **Container Health**: `docker compose ps --format json` at install_path.
   Verify all expected services are running. Report count (e.g., `PASS (8/8 services up)`).

2. **Log Analysis**: `docker compose logs --tail=100 --no-color` at install_path.
   Scan for ERROR-level log lines. Report PASS if none, WARN if non-critical, FAIL if critical.

3. **API Health**: Check key API endpoints respond:
   - dashboard-api health endpoint
   - ai-mediaserver health endpoint
   - usertool health endpoint
   - debug-view health endpoint
   Use `curl -sf http://localhost:<port>/health` or equivalent for each.

### Data Pipeline Checks

Run these checks if data pipeline scope is enabled:

1. **ClickHouse Tables**: Connect via `clickhouse-client` and verify:
   - `vision` table has recent rows (within last 1 minute)
   - `vision_head` table has recent rows (within last 1 minute)
   - Aggregated tables have today's data
   - Mapping tables have data

2. **Redis Keys**: Connect via `redis-cli` and verify:
   - `camera:*` keys exist for configured cameras (without site_key prefix)
   - `roi:*` keys exist (without site_key prefix)
   - Vision pub/sub is active (use `PUBSUB CHANNELS`)
   - No duplicate keys with site_key prefix (e.g., both `camera:*` and `DS6:camera:*`).
     If duplicates found, report as WARN and note the inconsistency.

3. **D-Platform Detection**: Uses `DplatformDetectionChecker` to verify:
   - **Detection status**: Inspects logs for active detections (idle-to-active
     transitions).  If zero detections, checks for crash signatures (`malloc()`,
     `Segmentation`, `FileNotFoundError`).  Reports FAIL on crash, WARN on no
     detections but pipeline running, PASS on active detections.
   - **Restart stability**: Checks container restart count.  >5 restarts = FAIL
     (crash-loop), 3-5 = WARN, <=2 = PASS.

```python
from plusinsight_installer.core.verification.dplatform_check import DplatformDetectionChecker

checker = DplatformDetectionChecker()
results = checker.check(install_path)
```

### Browser/UI Checks (Playwright MCP Execution Protocol)

Run these checks if browser scope is enabled. Browser tests are **mandatory** --
if Playwright MCP is unavailable, the entire skill fails (see Precondition #4).

#### Step 1: Get Test Specs

```python
from plusinsight_installer.core.verification.browser_check import BrowserChecker

checker = BrowserChecker()
test_specs = checker.get_test_specs()
```

This returns 4 specs: `Minimap dots`, `Console Errors`, `Network Errors`, `Usertool page`.

#### Step 2: Authenticate to Dashboard

Read credentials from the `.env` file at `install_path`:
- `NEXTAUTH_URL` -- base URL (e.g., `http://localhost:5601`)
- Dashboard login credentials (user/password from `.env`)
- Usertool setter credentials: `DASHBOARD_FRONT_SETTER_USERNAME` / `DASHBOARD_FRONT_SETTER_PASSWORD`

Use `browser_navigate` to open the login page, then `browser_fill_form` and
`browser_click` to log in via NextAuth. Wait for redirect to confirm success.
For the usertool test, if the page shows "Unauthorized", navigate to the
usertool login and authenticate with setter credentials.

#### Step 3: Execute Each Test Spec

For each `BrowserTestSpec`, execute its `steps` using Playwright MCP tools:

- **Minimap dots**: `browser_navigate` to the **monitoring** page (`/monitoring`),
  `browser_snapshot` to verify the canvas elements exist and read the Dweller
  count from the page. `browser_evaluate` to inspect the canvas structure.

  **Canvas layout (Konva.js):** Konva creates **two canvases per layer** inside
  a single `.konvajs-content` container:
  - **Scene canvas** (even index, e.g. canvas[0]): the visible rendering surface
    containing both the floor plan image AND the visitor dots.
  - **Hit canvas** (odd index, e.g. canvas[1]): an internal canvas used for
    click/event detection. It is always transparent and must NOT be inspected
    for pixel content.

  A separate **ScatterChart canvas** (parent class contains `ScatterChart`) may
  also be present outside the Konva container.

  **Pass criteria** (ALL must be true):
  1. Dweller count > 0 from the page snapshot.
  2. The Konva scene canvas (canvas[0], parent `.konvajs-content`) has
     `nonTransparentPixels > 0`.
  3. Optionally, the ScatterChart canvas (if present) has
     `nonTransparentPixels > 0`, confirming the chart is also rendering.

  Do NOT check canvas[1] -- it is the Konva hit canvas and is always empty.
  `browser_take_screenshot` for evidence.

- **Console Errors**: `browser_console_messages` to read all console output,
  filter for severity "error" and uncaught exceptions.

- **Network Errors**: `browser_network_requests` to read all network activity,
  filter for HTTP status codes >= 400.

- **Usertool page**: `browser_navigate` to `/usertool`. If the page shows
  "Unauthorized", log in with the setter credentials from `.env`
  (`DASHBOARD_FRONT_SETTER_USERNAME` / `DASHBOARD_FRONT_SETTER_PASSWORD`).
  These are the camera calibration admin credentials. After authentication,
  verify the main UI renders (camera list, calibration tools, or minimap editor).
  `browser_take_screenshot` for evidence.

#### Step 4: Collect Outcomes

Build outcome tuples from the execution results:

```python
outcomes: list[tuple[str, str, bool, str]] = [
    # (check_name, detail, passed, error_msg)
    ('Minimap dots', 'canvas: 800x600, pixels rendered', True, ''),
    ('Console Errors', '0 uncaught exceptions', True, ''),
    ('Network Errors', '0 failed API calls', True, ''),
    ('Usertool page', 'usertool UI rendered with camera list', True, ''),
]
```

For failed checks, set `passed=False` and provide the error in `error_msg`.

#### Step 5: Pass Outcomes to VerificationRunner

```python
from plusinsight_installer.core.verification import VerificationRunner

runner = VerificationRunner(
    install_path=install_path,
    branch=branch_name,
    site_key=site_key,
    browser_outcomes=outcomes,
)
report = runner.run(scope=effective_scope)
```

The `browser_outcomes` parameter feeds directly into `BrowserChecker.create_results()`,
producing proper `VerificationResult` instances with category `'UI Verification'`.

### Targeted Fix Verification

After the standard checks, always run targeted verification based on what the
branch actually changed. Analyse the branch's commit subjects and diff to
understand the fix intent, then craft specific ClickHouse queries or log
inspections that confirm the fix works.

#### Step 1: Read Branch Commits

```bash
# Detect base ref dynamically (same guard as elsewhere in this skill)
BASE_REF=$(git rev-parse --abbrev-ref @{u} 2>/dev/null | sed 's|^origin/||')
# Guard: if upstream points at the feature branch itself, fall back
if echo "$BASE_REF" | grep -qE '^PII-|^feature/'; then
  BASE_REF=$(git log --oneline | grep -oP 'release/[0-9.]+' | head -1)
fi
git log "${BASE_REF}..HEAD" --format="%s" | head -20
```

Also read the list of changed files for extra context:

```bash
git diff "${BASE_REF}..HEAD" --name-only
```

#### Step 2: Infer Fix Intent

Use the commit subjects and changed files to infer one or more **fix intents**.
Apply the first matching rule below:

| Signal in commits / changed files | Fix Intent |
|-----------------------------------|------------|
| `gender`, `GENDER_MALE`, `proto3` | **gender-recovery** |
| `occupancy`, `dwell`, `queueing`  | **occupancy-pipeline** |
| `reid`, `re-id`, `tracking`       | **reid-pipeline** |
| `vector`, `VRL`, `transform_vision` | **vector-transform** |
| `clickhouse`, `migration`, `schema` | **schema-migration** |
| `age`, `AGE_`                     | **age-recovery** |
| `dashboard`, `front`, `UI`, `chart` | **frontend-render** |
| `crash`, `malloc`, `segfault`     | **crash-stability** |

Multiple intents can match; run checks for all of them.

#### Step 3: Run Intent-Specific Queries

For each matched fix intent, run the following targeted check.  Print the
results clearly labelled as `[TARGETED] <intent>: PASS/WARN/FAIL`.

---

**gender-recovery**

Confirm that `GENDER_MALE` (proto3 zero-default) appears in the vision table
after the fix was applied.  Prior to the fix, `GENDER_MALE` would be absent.

```sql
-- Run via clickhouse-client against the plusinsight DB
SELECT
    attr_gender,
    count() AS cnt,
    round(count() * 100.0 / sum(count()) OVER (), 1) AS pct
FROM vision FINAL
WHERE timestamp >= now() - INTERVAL 3 MINUTE
GROUP BY attr_gender
ORDER BY attr_gender
```

Pass criteria:
- `GENDER_MALE` row exists with `cnt > 0`
- `attr_gender IS NULL` row does NOT exist (no null leakage)

---

**vector-transform**

Confirm that the running Vector container is volume-mounting the branch's
config (not the installed one) and that no errors appear in its logs.

```bash
docker exec plusinsight-vector-1 cat /etc/vector/vector.yaml | grep -c 'GENDER_MALE'
docker compose logs --tail=50 --no-color vector | grep -iE 'error|warn'
```

Pass criteria: grep count ≥ 1; no ERROR lines in logs.

---

**occupancy-pipeline**

Confirm recent rows in the occupancy output table.

```sql
SELECT count() AS cnt
FROM occupancy_realtime FINAL
WHERE timestamp >= now() - INTERVAL 5 MINUTE
```

Pass criteria: `cnt > 0`.

---

**reid-pipeline**

Confirm the mapping table has recent entries (ReID produces them).

```sql
SELECT count() AS cnt FROM mapping WHERE timestamp >= now() - INTERVAL 5 MINUTE
```

Pass criteria: `cnt > 0`.

---

**schema-migration**

Confirm the schema_migrator ran cleanly.

```bash
docker compose logs --tail=30 --no-color schema-migrator | tail -5
```

Pass criteria: last line contains `completed` or `up to date`; no `ERROR`.

---

**crash-stability**

Confirm d-platform container has not restarted and is producing detections.

```bash
docker inspect --format '{{.RestartCount}}' plusinsight-dplatform-1
docker compose logs --tail=50 --no-color dplatform | grep -c 'Active person'
```

Pass criteria: restart count ≤ 2; active person count > 0.

---

**age-recovery**

Same pattern as gender-recovery but for `attr_age`.

```sql
SELECT attr_age, count() AS cnt
FROM vision FINAL
WHERE timestamp >= now() - INTERVAL 3 MINUTE
  AND attr_age IS NOT NULL
GROUP BY attr_age
ORDER BY cnt DESC
LIMIT 5
```

Pass criteria: at least one non-null `attr_age` row exists.

---

**frontend-render**

Only applies when browser scope is active.  Confirm that the dashboard page
loads without console errors and that key widgets render.  Use the browser
checks already defined in this skill (Console Errors, Network Errors,
Minimap dots).

---

#### Step 4: Report Targeted Results

Print each targeted check on its own line:

```
[TARGETED] gender-recovery:    PASS  (GENDER_MALE: 186 rows, 0.7%)
[TARGETED] vector-transform:   PASS  (VRL gender recovery found in config)
```

Include targeted results in the overall summary that follows.

---

### Verification Report

Format the report using the `format_report` function:

```python
from plusinsight_installer.core.verification.report import format_report

formatted = format_report(report)
print(formatted)
```

The `VerificationReport` dataclass has these fields: `branch`, `install_path`,
`site_key`, `results`, `overall_status`, and `duration_s` (seconds as float).

---

## Flow: --mount-only

Apply changes without running verification.

Execute all steps from the **--diff** flow (Steps 1-3), then:

### Step 4: Classify Changes

```python
from plusinsight_installer.core.update_dispatch import UpdateDispatcher

dispatcher = UpdateDispatcher(manager=manager)
classified = dispatcher.classify_changes(diffs=diffs)
# classified is list[tuple[VersionDiff, UpdateStrategy]]
```

### Step 5: Execute Updates

```python
dispatcher.execute_updates(classified)
# Returns list[str] of service names that were updated
```

This generates the docker-compose.override.yml, builds frontends if needed,
restarts affected services, runs post-mount commands, and **exports artifacts**.

Internally this calls (in order):
1. Stop data-writing services (postprocessor, mediaserver, dplatform)
2. **`manager._upgrade_infra_services()`** -- upgrade infrastructure Docker images
   (e.g. ClickHouse, Redis, PostgreSQL) when the branch `installer/.env` specifies
   newer versions than the installed `.env`. This MUST run BEFORE schema-migrator
   so migrations execute against the correct database version.
3. **`manager._regenerate_compose_from_template()`** -- regenerate
   `docker-compose.yml` from the branch's `installer/docker-compose.yml.template`.
   Reads the currently enabled services from the installed compose file, copies
   the branch template, and uses `ServiceSelector` to produce a new compose file
   that preserves the same service set but picks up any template changes (health
   checks, environment variables, new service definitions, etc.). The snapshot
   already captures the original `docker-compose.yml` so `--restore` reverts it.
4. `manager._run_oneshot(comp)` for python-oneshot components (schema-migrator)
5. `manager._sync_cpp_plugins(components)` to build all 7 C++ plugins in-container
   (primary) with ECR extraction fallback for models -- **gated on CPP category**
6. `manager.generate_override_yaml(components)` for regular components
7. Inject C++ plugin/model volume mounts and Vector config mounts into override dict
8. `manager.write_override(override)` to write the file
9. `manager.build_frontend(comp)` for nextjs/nestjs components -- **gated on CODE/DEPS categories**
10. `manager._docker_compose_up(service_names)` to restart services (includes Vector
    when dplatform is present)
11. `manager._sync_dplatform_engines()` to copy pre-built TRT engines -- **gated on MODELS category**
12. `manager._run_post_mount_cmds(components)` for post-mount commands -- **gated on CYTHON/DOCKER/DEPS categories**
13. `manager.export_testbranch(components, branch_hashes)` to persist artifacts

### Artifact Export (Automatic)

After `execute_updates` completes, it automatically exports artifacts:

1. **Docker commit** each modified container with an `ecr_image_name` to a local
   image tagged `{ecr_registry}/{ecr_image_name}:{branch_hash}`. Images are NOT
   pushed to ECR.

2. **Generate a timestamped docker-compose file** in
   `{install_path}/testbranch/testbranch_{branch}_{YYYYMMDD}_{HHMMSS}/` with
   committed image tags replacing the original tags.

3. **Copy diverged config files** (`.env`, `docker-compose.override.yml`) to the
   same output directory.

A summary table is printed showing committed images and artifact locations.

### TRT Engine Sync (Automatic for d-platform)

When d-platform is among the changed components, the update flow automatically
synchronizes pre-built TensorRT engines from the local engine cache into the
running container. This bridges the gap between CI-built engines and local
testbranch runs.

```python
from plusinsight_installer.core.engine_sync import sync_engines

result = sync_engines(
    container_name='dplatform',
    install_path=install_path,
    model_id_yaml=repo_root / 'd-platform' / 'model_id.yaml',
)
```

The sync process:
1. Computes the model hash from the branch's `model_id.yaml` (SHA256, first 8 chars)
2. Detects the local GPU architecture via `nvidia-smi` (ampere, ada, hopper)
3. Reads the TensorRT version from the container's `TENSORRT_VERSION` env var
4. Searches for pre-built engines at:
   - `/data/dplatform_engines/{gpu_arch}_{trt_version}_{model_hash}/`
   - `/data_server/dplatform_engines/{gpu_arch}_{trt_version}_{model_hash}/`
5. If found, `docker cp` copies each model directory and timing cache into
   `container:/app/mtmc/models/{gpu_arch}_{trt_version}/`

Engine cache directory structure (from CI):
```
/data_server/dplatform_engines/
  ampere_10.3.0_d3f00740/
    od_yolov11s_ppg_gaze_degree_1280x1280_onnx/
      c3a68c092ea946bba54ef5727bc10af4/
        *.engine
    reid_swin_base_128x384_1024_onnx/
      8210ef68c6ec40be84f59bdf9fed9e19/
        *.engine
    timing_cache.bin
```

If no matching engines are found, a warning is printed and d-platform falls
back to building engines at startup (slow but functional).

### C++ Plugin Build (Automatic for d-platform)

When the d-platform image hash differs from the installed version,
`_sync_cpp_plugins()` orchestrates a two-phase C++ plugin sync:

**Phase 1 -- In-container build (primary):**
`_build_cpp_in_container()` creates a temporary container from the installed
d-platform image, copies the branch's C++ source in, installs build
dependencies, applies `nvds_deepingsource.patch`, and compiles all 7
GStreamer plugins.  For dsrefiner, the `.pb.h`/`.pb.cpp` files are
regenerated from `.proto` sources (`installer/resources/schemas/pi-schemas/`)
using the container's `/root/.local/bin/protoc` (v3.21.12) to match
its protobuf library version at `/root/.local/include/`.  Built `.so`
files are extracted to `{install_path}/testbranch/cpp-plugins/` and
returned as volume mounts.

Required apt packages (auto-detected CUDA version for versioned packages):
`cuda-nvcc-{ver} libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
libopencv-dev libhiredis-dev libeigen3-dev libnvidia-ml-dev
libcufft-dev-{ver} libnpp-dev-{ver}`

**Phase 2 -- ECR extraction (fallback):**
For any plugins that failed to build in-container, falls back to extracting
pre-compiled `.so` files from the CI-built ECR image.  ONNX models are
always extracted from ECR.  If ECR is unavailable, only the in-container
built plugins are returned.

See the Error Handling section for details on build order and failure handling.

Stop here. Do not run verification.

---

## Flow: --no-qa

Same as **--mount-only**. Apply changes, skip all verification.

---

## Flow: Default (No Flags)

Full flow: snapshot, diff, update, and verification.

### Steps 1-3: Snapshot and Diff

Follow the **--diff** flow (Steps 1-3) to create/load snapshot and compute diffs.

### Step 4: Classify Changes

Follow the **--dry-run** flow (Step 4) to classify changes.

### Step 5: Execute Updates

Follow the **--mount-only** flow (Step 5) to apply changes.

### Step 6: Verification

Follow the **--qa-only** flow to run verification.

Determine verification scope from additional flags:

- If `--browser-only` is set: run browser checks only
- If `--no-browser` is set: run infra + data only
- If `--data-only` is set: run data pipeline checks only
- Otherwise: run all checks

### Step 7: Report

Print the full verification report. If overall status is FAIL, print a
recommendation to check logs and consider running `--restore`.

### Step 8: Self-Heal Analysis

After verification (or after mount-only), run the self-heal analysis to detect
gaps, suggest improvements, and track patterns across runs:

```python
from plusinsight_installer.core.self_heal import SelfHealRunner, format_self_heal_report

healer = SelfHealRunner(
    repo_root=repo_root,
    install_path=install_path,
    verification_report=report,  # None for --mount-only / --no-qa
)
heal_report = healer.run()
formatted = format_self_heal_report(heal_report)
print(formatted)
```

The self-heal module performs four checks:

1. **Registry Sync**: Compares `COMPONENT_REGISTRY` against docker-compose
   template services.  Flags untracked services and stale source directories.

2. **Verification Coverage**: Detects ClickHouse tables with today's data that
   lack verification checks, and frontend routes without browser test specs.

3. **Benign Pattern Learning**: Tracks log error patterns across runs.  When a
   pattern appears 3+ times while services are healthy, it suggests adding it
   to `_BENIGN_PATTERNS` in `container_health.py`.  Maintains a history file
   at `{install_path}/testbranch/.self-heal-history.json`.

4. **SKILL.md Drift Detection**: Verifies that documented import paths, class
   signatures, and spec counts still match the actual Python implementations.

Findings are categorised as `info`, `warning`, or `action-taken`.  The only
auto-write is the JSON history file (inside `testbranch/`).  All code changes
are suggestions only -- the AI agent executing this skill should review the
suggestions and apply them if appropriate, then re-run `/testbranch` to
validate the fixes.

---

## Error Handling

### Docker Not Running

If `docker info` fails at any point, print:
```
ERROR: Docker is not running. Start Docker and try again.
```

### Invalid Install Path

If `validate_install_path()` raises `FileNotFoundError`, print the exception
message (it includes guidance about `--install-path`) and stop.

### No Snapshot for Restore

If `--restore` is used and `snap.exists()` returns False, print:
```
ERROR: No snapshot found. Run /testbranch first to create one.
```

### C++ Plugin and Model Sync

When the branch's d-platform image hash differs from the installed version,
`_sync_cpp_plugins()` orchestrates a two-phase sync:

**Phase 1 -- In-container build (primary):**
`_build_cpp_in_container()` creates a temporary container from the installed
d-platform image (`sleep infinity` entrypoint), copies branch C++ source in,
installs build dependencies via apt, applies `nvds_deepingsource.patch`, and
compiles all 7 GStreamer plugins (dsmtmctracker, gst-nvdsosd-custom,
dsimagedump, dsrefiner, head_detect, yolo_pose, nvdsinfer_yolov5parser).
For dsrefiner, the `.pb.h`/`.pb.cpp` files are regenerated from `.proto`
sources (`installer/resources/schemas/pi-schemas/`) using the container's
`/root/.local/bin/protoc` (v3.21.12) to match its protobuf library
version at `/root/.local/include/`.  The `basic` static library
is built first as a shared dependency.  Built `.so` files are extracted to
`{install_path}/testbranch/cpp-plugins/`.

**Phase 2 -- ECR extraction (fallback):**
For any plugins that failed in Phase 1, falls back to pulling the CI-built
ECR image (`mtmc-deepstream:{branch_hash}`) and extracting pre-compiled
`.so` files.  ONNX models (`/app/mtmc/models/`) are always extracted from
ECR.  If ECR is unavailable (auth expired), only the in-container built
plugins are returned.

Both phases store files in `{install_path}/testbranch/cpp-plugins/` and
`dplatform-models/`, returning volume mount strings for the override YAML.
This runs **before** the override is written, so plugins persist across
container restarts.

### Vector Config Sync

When d-platform is among the mounted components, the branch's Vector config
is also volume-mounted via `_get_vector_override_volumes()`.  This ensures
Vector subscribes to the correct Redis channel (e.g. `DS6:vision` with
site-key prefix) instead of the potentially stale installed config that may
use the unprefixed `vision` channel.  Protobuf descriptors (`.desc` files)
are also mounted.

If ECR pull fails, print a warning and continue without C++ sync.  The
pipeline may crash with `malloc()` if plugins are stale.

### Zero Detection (d-platform)

Streams in this environment always have people visible.  Zero detections after
pipeline warmup (~30s) indicates a bug.  The `DplatformDetectionChecker` automatically:

1. Inspects d-platform logs for crash signatures (`malloc()`, `Segmentation fault`,
   `FileNotFoundError`)
2. Checks for detection events (idle-to-active transitions)
3. Monitors restart count for crash-loop detection (>5 restarts = FAIL)

Common root causes for zero detection:
- **malloc() crash**: C++ plugin / model format mismatch (e.g. `gaze_8d` vs `gaze_degree`).
  `_sync_cpp_plugins()` builds all 7 plugins in-container.  If a build fails,
  it falls back to ECR extraction.  If ECR auth failed, run `awslogin` and retry.
- **FileNotFoundError**: Missing ONNX or TRT engine files.  Run engine sync or
  ensure model cache is populated.
- **Crash-loop**: Container repeatedly exiting.  Check `docker inspect --format '{{.RestartCount}}'`
  and recent logs for the root cause.
- **Data flow gap**: d-platform may be detecting but data not reaching ClickHouse.
  Check Vector subscribes to the correct Redis channel (`{site_key}:vision` not `vision`).
  The `_get_vector_override_volumes()` method handles this automatically.

### Dockerfile Changes

If any diff indicates Dockerfile modifications (check changed files for
`Dockerfile` in the component's source_dir), print:
```
WARNING: Dockerfile changes detected in <component>. Runtime environment may differ.
Consider full CI for final validation.
```
Continue with the flow.

### Snapshot Already Exists

If `snap.create()` raises `FileExistsError`, this is expected on repeat runs.
Call `snap.load()` to proceed with the existing snapshot.

### Build Failures

If `manager.build_frontend()` returns False for a frontend component, print
the error and stop the flow. Do not proceed with partial mounts.

---

## Python Import Paths

All imports come from the installer package:

```python
from plusinsight_installer.core.dev_test import DevTestManager, DevComponent, COMPONENT_REGISTRY
from plusinsight_installer.core.snapshot import SnapshotManager
from plusinsight_installer.core.version_diff import VersionDiffEngine, VersionDiff, ChangeType, ChangeCategory, has_frontend_changes
from plusinsight_installer.core.update_dispatch import UpdateDispatcher, UpdateStrategy
from plusinsight_installer.core.verification import VerificationRunner
from plusinsight_installer.core.verification.report import format_report
from plusinsight_installer.core.verification.browser_check import BrowserChecker
from plusinsight_installer.core.verification.dplatform_check import DplatformDetectionChecker
from plusinsight_installer.core.self_heal import SelfHealRunner, format_self_heal_report
```

Run all Python code via `uv run` from the `installer/` directory within the
repo root, or use `sys.path` manipulation to ensure the package is importable:

```bash
cd <repo_root>/installer && uv run python -c "
from plusinsight_installer.core.dev_test import DevTestManager
# ... rest of the code
"
```

---

## File Safety Constraint

**CRITICAL**: The testbranch skill must NEVER modify files in `~/plusinsight`
outside of the `~/plusinsight/testbranch/` directory, except for:

- `docker-compose.yml` (regenerated from branch template via
  `_regenerate_compose_from_template()`; original preserved in snapshot)
- `docker-compose.override.yml` (standard Docker Compose mechanism, properly cleaned up)
- `.dev-test-snapshot/` (backup directory for safe restore)
- `.testbranch.lock` (transient lock file)
- `.env` (infrastructure version keys only, via `_upgrade_infra_services()`;
  original values are preserved in the snapshot for `--restore`)

All other changes (new service definitions, nginx templates, superset home)
are applied via the override YAML using volume mounts, not by copying or
modifying production files.  This ensures `--restore` always succeeds.

## Output Format

Follow the output contracts defined in the CLI interface contract:

- **Version diff table**: Fixed-width columns as produced by `VersionDiffEngine.format_table()`
- **Verification report**: Structured report with Infrastructure, Data Pipeline, and UI sections
- **Error messages**: Prefixed with `ERROR:` or `WARNING:` as appropriate
- **No emojis** in any output
