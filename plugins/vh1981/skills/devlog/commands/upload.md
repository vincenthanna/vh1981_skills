# Command: Upload — detailed procedure

Read this file when the user invokes `/devlog upload ...`. SKILL.md carries the
routing and the one-line summary; this file has the steps. Upload publishes a
devlog project to an external knowledge-base repo so the docs are visible
alongside other projects.

## Syntax

| Form | Meaning |
|------|---------|
| `upload` | upload the active project to the saved target |
| `upload <project>` | upload `<project>` to the saved target |
| `upload --to <path>` | upload the active project to `<path>`, and save `<path>` as the new default |
| `upload <project> --to <path>` | upload `<project>` to `<path>`, and save it as the new default |
| `upload <project> <path>` | positional form — same as `upload <project> --to <path>` |

`<path>` is the absolute or `~`-expanded path of a knowledge-base repo (e.g. `~/workspace/ds_knowledge_base`). Expand `~` before use.

## Target-path resolution

Resolve in this priority order, error out if all fail:

1. Explicit `--to <path>` (or trailing positional) in the current command — and save it to `docs/devlog/.upload-target` for future calls.
2. `docs/devlog/.upload-target` (single line, repo absolute path) — written by a prior `upload` call.
3. Error: "No upload target. Use `/devlog upload <project> --to <path>` first."

## Steps

1. Parse `<project>` and `<path>`. If `<project>` was not given, resolve the active project per SKILL.md `## Active Project`.
2. Resolve the target path as described above. If level 1 supplied a new path, write it (single line, no trailing newline) to `docs/devlog/.upload-target`.
3. Validate target:
   - Target directory exists. If not, ask the user before creating it — do not silently `mkdir` an external repo.
   - If `<target>/projects/` exists, use `<target>/projects/<project>/` as the destination root (knowledge-base convention).
   - Otherwise, default to `<target>/<project>/` and warn the user in the output that the target lacks a `projects/` directory.
4. `mkdir -p <dest>` if it doesn't exist.
5. Copy `docs/devlog/<project>/` recursively into `<dest>`, overwriting same-named files. Files that exist only in the destination are left untouched (no delete sync). The copy includes everything under the project directory — investigation docs, `history/`, `runs/`, `comparisons/`, `_archived/`, `README.md`.
   - Use `cp -a docs/devlog/<project>/. <dest>/` (the trailing `/.` copies contents into `<dest>` directly).
   - Do NOT copy `docs/devlog/.active` or `docs/devlog/.upload-target` — those are not inside the project directory anyway, but verify with `ls -A docs/devlog/<project>/` before the copy.
6. Count copied files (`find <dest> -type f -newer ...` is overkill — just count source files: `find docs/devlog/<project>/ -type f | wc -l`).
7. Output a one-line summary in the form:
   ```
   Uploaded <project> → <dest>  (N files)
   ```
   If step 2 wrote a new `.upload-target`, add a second line: `Saved target to docs/devlog/.upload-target`. If the destination layout was non-standard (no `projects/`), add a warning line.

## Notes

- `upload` does NOT git-commit anything in the target repo. The user runs `cd <target> && git add . && git commit` themselves.
- `upload` is read-only against the source devlog — it only writes to the destination and to `docs/devlog/.upload-target`.
- This is a bulk copy, not a merge. Hand-edits in the destination that diverge from the source will be overwritten.
- `.upload-target` lives at `docs/devlog/.upload-target` (one path per repo, shared across all projects in this repo). To change the target, pass `--to <new-path>` and it will be overwritten.
