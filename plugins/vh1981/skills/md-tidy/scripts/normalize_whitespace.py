#!/usr/bin/env python3
"""md-tidy Pass A — conservative whitespace/blank-line normalizer for Markdown.

Deterministic, safe whitespace cleanup. NEVER touches the interior of fenced
code blocks, and NEVER changes content: no list markers, no heading levels,
no code, no URLs, no numbers. Whitespace and blank lines only.

Rules (applied OUTSIDE fenced code blocks only):
  1. Strip trailing spaces/tabs from every line.
  2. Collapse runs of 3+ blank lines down to 2 (at most two consecutive blanks;
     a single or double blank line is preserved as-is). See MAX_BLANK.
  3. Remove blank lines at the very start of the file.
  4. Remove blank lines at the very end; ensure exactly one trailing newline.
  5. Collapse 2+ spaces after an ATX heading marker (e.g. "#   T" -> "# T").
     (A heading with no space after "#" is left untouched — adding a space
      there would turn plain text into a heading; that judgment is Pass B.)

Fenced code blocks (``` or ~~~, 3+ chars) are preserved VERBATIM, including
their blank lines and trailing whitespace. An unclosed fence at EOF is left
as-is for the agent (Pass B) to fix.

Usage:
    normalize_whitespace.py [--dry-run] PATH [PATH ...]

PATH is a markdown file or a directory (recursed for *.md / *.markdown,
excluding .git, node_modules, etc.). Prints a per-file change summary and a
final total. Exit code is 0 on success, 1 if any path was not found.
"""
import os
import re
import sys

# Maximum consecutive blank lines kept outside code fences. Runs longer than
# this are collapsed down to this many (e.g. 4 blanks -> 2). Set to 2 so a
# single OR double blank line is preserved; only 3+ get reduced.
MAX_BLANK = 2

MD_EXTS = (".md", ".markdown")
EXCLUDE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build",
                ".next", "out", "vendor", ".tox", "__pycache__", ".cache"}

FENCE_OPEN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]{2,}(\S)")


def collect_files(paths):
    """Expand paths into a de-duplicated, stable-ordered list of md files."""
    files, missing = [], []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, names in os.walk(p):
                dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
                for n in sorted(names):
                    if n.lower().endswith(MD_EXTS):
                        files.append(os.path.join(root, n))
        elif os.path.isfile(p):
            files.append(p)
        else:
            missing.append(p)
    seen, out = set(), []
    for f in files:
        rp = os.path.realpath(f)
        if rp not in seen:
            seen.add(rp)
            out.append(f)
    return out, missing


def _is_closing_fence(line, fence_char, fence_len):
    rest = line.strip()
    return bool(rest) and set(rest) == {fence_char} and len(rest) >= fence_len


def normalize(text):
    """Return (new_text, stats). Pure whitespace normalization, fence-aware."""
    lines = text.split("\n")
    if text.endswith("\n"):
        lines = lines[:-1]  # drop the empty element produced by the final "\n"

    stats = {"trailing": 0, "blank_collapsed": 0, "leading_removed": 0,
             "heading_space": 0, "eof": 0}

    out = []
    body_start = 0
    # Preserve a leading YAML frontmatter block verbatim (must be the very first
    # line, exactly "---", closed by a later "---" or "...").
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i].rstrip() in ("---", "..."):
                out.extend(lines[:i + 1])
                body_start = i + 1
                break

    in_fence = False
    fence_char = None
    fence_len = 0
    pending_blanks = 0   # buffered blank lines outside a fence
    emitted = bool(out)  # frontmatter counts as already-emitted content

    for line in lines[body_start:]:
        if in_fence:
            out.append(line)  # verbatim inside code fence
            if _is_closing_fence(line, fence_char, fence_len):
                in_fence = False
                fence_char, fence_len = None, 0
            continue

        m = FENCE_OPEN_RE.match(line)
        if m:
            # Opening fence: flush a single separating blank if appropriate.
            if emitted and pending_blanks >= 1:
                out.extend([""] * min(pending_blanks, MAX_BLANK))
                if pending_blanks > MAX_BLANK:
                    stats["blank_collapsed"] += 1
            elif not emitted and pending_blanks:
                stats["leading_removed"] += pending_blanks
            pending_blanks = 0
            stripped = line.rstrip(" \t")
            if stripped != line:
                stats["trailing"] += 1
            out.append(stripped)
            emitted = True
            in_fence = True
            fence_char, fence_len = m.group(2)[0], len(m.group(2))
            continue

        stripped = line.rstrip(" \t")
        if stripped != line:
            stats["trailing"] += 1

        if stripped == "":
            pending_blanks += 1
            continue

        new = HEADING_RE.sub(r"\1 \2", stripped)
        if new != stripped:
            stats["heading_space"] += 1

        if emitted and pending_blanks >= 1:
            out.extend([""] * min(pending_blanks, MAX_BLANK))
            if pending_blanks > MAX_BLANK:
                stats["blank_collapsed"] += 1
        elif not emitted and pending_blanks:
            stats["leading_removed"] += pending_blanks
        pending_blanks = 0

        out.append(new)
        emitted = True

    # Trailing blank lines (pending_blanks > 0) are intentionally dropped.
    new_text = "\n".join(out)
    if new_text:
        new_text += "\n"

    orig_nl = len(text) - len(text.rstrip("\n"))
    new_nl = len(new_text) - len(new_text.rstrip("\n"))
    if orig_nl != new_nl:
        stats["eof"] = 1

    return new_text, stats


def fmt_stats(stats):
    parts = []
    labels = [("trailing", "줄끝공백"), ("blank_collapsed", "빈줄축소"),
              ("leading_removed", "선두빈줄"), ("heading_space", "헤딩공백"),
              ("eof", "EOF개행")]
    for key, label in labels:
        if stats.get(key):
            parts.append(f"{label}:{stats[key]}")
    return " ".join(parts)


def main(argv):
    dry_run = False
    paths = []
    for a in argv:
        if a in ("--dry-run", "-n"):
            dry_run = True
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            paths.append(a)

    if not paths:
        print("usage: normalize_whitespace.py [--dry-run] PATH [PATH ...]",
              file=sys.stderr)
        return 2

    files, missing = collect_files(paths)
    for m in missing:
        print(f"(skip: not found) {m}", file=sys.stderr)

    changed = 0
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"(skip: {e.__class__.__name__}) {f}", file=sys.stderr)
            continue
        new_text, stats = normalize(text)
        if new_text != text:
            changed += 1
            if not dry_run:
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(new_text)
            print(f"{'[dry] ' if dry_run else ''}{f}  —  {fmt_stats(stats)}")
        else:
            print(f"{f}  —  (clean)")

    print(f"\n총 {len(files)}개 파일 검사, {changed}개 변경"
          f"{' (dry-run, 미적용)' if dry_run else ''}.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
