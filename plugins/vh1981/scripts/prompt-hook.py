#!/usr/bin/env python3
"""UserPromptSubmit / PreCompact hook: guard the guideline injection and log prompts.

A SessionStart hook that hits its timeout is cancelled without a word (seen when
NFS stalled for 10 s), and the session runs without the default guidelines.
inject-guidelines.sh leaves a per-session marker once it has printed them; on
each prompt this hook re-injects when the marker is missing, and PreCompact
removes it so a compaction whose SessionStart hook fails is caught as well.

Every prompt is also appended to <log dir>/<host>/<YYYY-MM>.jsonl, with likely
secrets masked. One file per host, because appends from several NFS clients to
one file can interleave.

Opt out with VH1981_GUIDELINES=0 (no re-injection) and VH1981_PROMPT_LOG=0.
Never blocks or fails the prompt: every path exits 0.
"""
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SID_RE = re.compile(r"^[A-Za-z0-9-]{1,128}$")
MAX_PROMPT = 4000

SECRETS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|\Z)", re.S),
     "[PRIVATE KEY]"),
    (re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
                r"|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})"),
     "[SECRET]"),
    (re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{16,}"), r"\1 [SECRET]"),
    (re.compile(r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key)(\s*[:=]\s*)"
                r"(\"[^\"]*\"|'[^']*'|\S+)"),
     r"\1\2[SECRET]"),
]


def mask(text):
    for rx, rep in SECRETS:
        text = rx.sub(rep, text)
    return text


# Must match the marker path in inject-guidelines.sh.
def state_dir():
    base = os.environ.get("VH1981_STATE_DIR") or os.path.join(
        os.environ.get("TMPDIR") or "/tmp", "vh1981-%d" % os.getuid())
    return os.path.join(base, "injected")


def guard(sid):
    if os.environ.get("VH1981_GUIDELINES", "1") == "0" or not sid:
        return None
    if os.path.exists(os.path.join(state_dir(), sid)):
        return None
    # The injector renders core.md and writes the marker, so the next prompt is quiet.
    r = subprocess.run(["/bin/sh", os.path.join(HERE, "inject-guidelines.sh")],
                       input=json.dumps({"session_id": sid}).encode(),
                       capture_output=True, timeout=5)
    text = r.stdout.decode("utf-8", "replace").strip()
    if not text:
        return None
    return {
        "systemMessage": "vh1981: 세션 시작 때 기본 가이드라인이 주입되지 않아 이번 prompt 에 다시 넣었다.",
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text},
    }


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().strip()


def repo_info(cwd):
    """Return (top, branch, devlog .active) without running git, which is slow on NFS."""
    d = os.path.abspath(cwd)
    while True:
        g = os.path.join(d, ".git")
        if os.path.exists(g):
            break
        parent = os.path.dirname(d)
        if parent == d:
            return None, None, None
        d = parent
    branch = active = None
    try:
        if os.path.isfile(g):  # worktree or submodule: "gitdir: <path>"
            line = read(g)
            g = os.path.join(d, line[len("gitdir:"):].strip()) if line.startswith("gitdir:") else None
        if g:
            head = read(os.path.join(g, "HEAD"))
            branch = head[len("ref: refs/heads/"):] if head.startswith("ref: refs/heads/") else head[:12]
    except OSError:
        pass
    try:
        active = read(os.path.join(d, "docs", "devlog", ".active")) or None
    except OSError:
        pass
    return d, branch, active


def log_prompt(p, sid):
    if os.environ.get("VH1981_PROMPT_LOG", "1") == "0":
        return
    prompt = p.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return
    now = datetime.now().astimezone()
    host = re.sub(r"[^A-Za-z0-9._-]", "_", socket.gethostname().split(".")[0]) or "unknown"
    cwd = p.get("cwd") if isinstance(p.get("cwd"), str) else os.getcwd()
    top, branch, active = repo_info(cwd)
    text = mask(prompt)
    rec = {
        "ts": now.isoformat(timespec="seconds"),
        "host": host,
        "session_id": sid,
        "cwd": cwd,
        "repo": os.path.basename(top) if top else None,
        "branch": branch,
        "devlog": active,
        "prompt": text[:MAX_PROMPT],
    }
    if len(text) > MAX_PROMPT:
        rec["truncated_from"] = len(text)
    base = os.environ.get("VH1981_PROMPT_LOG_DIR") or os.path.join(
        os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"), "vh1981", "prompts")
    d = os.path.join(base, host)
    os.makedirs(d, mode=0o700, exist_ok=True)
    fd = os.open(os.path.join(d, now.strftime("%Y-%m") + ".jsonl"),
                 os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        # One write() per record keeps concurrent sessions on this host from interleaving.
        os.write(fd, (json.dumps(rec, ensure_ascii=False) + "\n").encode("utf-8"))
    finally:
        os.close(fd)


def main():
    try:
        p = json.loads(sys.stdin.buffer.read() or b"{}")
    except ValueError:
        return
    if not isinstance(p, dict):
        return
    sid = p.get("session_id")
    sid = sid if isinstance(sid, str) and SID_RE.match(sid) else None
    event = p.get("hook_event_name")
    if event == "PreCompact":
        if sid:
            try:
                os.remove(os.path.join(state_dir(), sid))
            except OSError:
                pass
        return
    if event != "UserPromptSubmit":
        return
    try:
        log_prompt(p, sid)
    except Exception:
        pass
    try:
        out = guard(sid)
    except Exception:
        out = None
    if out:
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
