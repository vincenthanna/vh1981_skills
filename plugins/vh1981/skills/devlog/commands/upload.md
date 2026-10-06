# Command: Upload — delegates to the kb skill

Read this file when the user invokes `/devlog upload ...` or when `update`
finishes with a KB configured. Uploading is owned by the `vh1981:kb` skill:
its `scripts/kb.py` selects files, plans a three-way update per file (this
checkout's last upload, the KB copy, the local copy), adds and updates what
only one side changed, holds back files both sides changed (conflicts), and
hold copies of the same project, and maintains the KB index. This command only
maps the old syntax onto it.

```
KB="python3 ${CLAUDE_PLUGIN_ROOT}/skills/kb/scripts/kb.py"
```

## Syntax mapping

| devlog form | kb call |
|------|---------|
| `upload` | `$KB upload <active project>` |
| `upload <project>` | `$KB upload <project>` |
| `upload --to <path>` / `upload <project> <path>` | `$KB --kb <path> upload <project>`; then offer `$KB init <path>` so the path becomes this machine's default |

`<path>` may be a local path or `ssh://user@host/abs/path`. The old
per-repo `docs/devlog/.upload-target` is still read as a last-resort location;
when it is the source (`$KB where` says `legacy`), suggest `$KB init <that path>`
once.

## Steps

1. Resolve `<project>`: explicit, else the active project per SKILL.md
   `## Active Project`. If that resolution landed at level 3–4, confirm the
   project name with the user once before uploading (external-write exception).
2. Follow the `vh1981:kb` skill's §업로드 (read `${CLAUDE_PLUGIN_ROOT}/skills/kb/SKILL.md`
   if it is not in context): fill or refresh the README `kb:` card, run the
   upload, and handle each result status as that table says.
3. Never pass `--take-over` or `--yes` without the user's agreement.

## Auto-upload after `update`

`update` calls this command as its last step when this machine has a KB
location set (`$KB where --configured` exits 0 — the built-in default alone
does not count, so machines off the office network are not slowed by ssh
timeouts). In that mode:

- Upload once with no flags. Report the result in one line inside the update
  summary.
- `ok` and `up-to-date` need nothing more. For `needs-confirm`, show the
  deletions and ask. For `partial` or `conflict`, the non-conflicting files
  are already up; list the conflicting files and offer the kb skill's merge
  step (`kb.py conflicts`, then `--resolve`). Do not retry with `--yes`,
  `--take-over` or `--resolve` on your own.
- If `where --configured` exits 1, skip silently.
