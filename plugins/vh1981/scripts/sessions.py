#!/usr/bin/env python3
"""Keep <repo>/.claude/sessions.md: the Claude sessions open in a repo, so they can
be brought back after tmux or the host dies.

  sessions.py hook                           # SessionStart / UserPromptSubmit / Stop / SessionEnd
  sessions.py summarize <record.json>        # background: two-line summary from the LLM
  sessions.py list [DIR]                     # every session with its state on this host
  sessions.py restore [DIR] [--host H] [--only ID|NAME,...] [--dry-run]

Each session keeps one record, <repo>/.claude/sessions/<session id>.json, and every
hook run renders all records into sessions.md. Records are per session and written by
rename, so sessions on several NFS clients never write the same file at once. Both
paths go into .git/info/exclude.

The summary comes from an OpenAI-compatible endpoint named in VH1981_SUMMARY_LLM or
~/.config/vh1981/summary-llm ("<base url> <model>"). It runs in a detached process so
the hook returns at once; without an endpoint, or when it fails, the summary is the
last request and the first sentence of the last reply.

Opt out with VH1981_SESSIONS=0. The hook never blocks or fails a session: it exits 0.
"""
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location

HERE = os.path.dirname(os.path.abspath(__file__))
SID_RE = re.compile(r"^[A-Za-z0-9-]{1,128}$")
KEEP_DAYS = 14
TAIL = 400_000
# A deliberate exit drops the record; any other end (SIGHUP when tmux dies) keeps it.
EXPLICIT_END = {"clear", "logout", "prompt_input_exit"}
VALUE_FLAGS = {"--model", "--effort", "--permission-mode", "--add-dir", "--agent", "--agents",
               "--settings", "--mcp-config", "--append-system-prompt", "--system-prompt",
               "--allowedTools", "--allowed-tools", "--disallowedTools", "--disallowed-tools",
               "--fallback-model", "--plugin-dir", "--setting-sources"}
DROP_FLAGS = {"-c", "--continue", "--fork-session"}
DROP_WITH_VALUE = {"-r", "--resume", "--session-id"}

_spec = spec_from_file_location("vh1981_prompt_hook", os.path.join(HERE, "prompt-hook.py"))
_ph = module_from_spec(_spec)
_spec.loader.exec_module(_ph)
mask, repo_info = _ph.mask, _ph.repo_info


def kst(ts):
    return datetime.fromtimestamp(ts, timezone(timedelta(hours=9))).strftime("%m-%d %H:%M KST")


def host():
    return re.sub(r"[^A-Za-z0-9._-]", "_", socket.gethostname().split(".")[0]) or "unknown"


def paths(top):
    d = os.path.join(top, ".claude")
    return os.path.join(d, "sessions"), os.path.join(d, "sessions.md")


def write_atomic(path, text):
    tmp = "%s.%s.%d.tmp" % (path, host(), os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        return rec if isinstance(rec, dict) else {}
    except (OSError, ValueError):
        return {}


def exclude(top):
    """Keep the session files out of git, in the shared info/exclude of every worktree."""
    g = os.path.join(top, ".git")
    try:
        if os.path.isfile(g):
            line = open(g, encoding="utf-8").read().strip()
            if not line.startswith("gitdir:"):
                return
            g = os.path.join(top, line[len("gitdir:"):].strip())
            common = os.path.join(g, "commondir")
            if os.path.isfile(common):
                g = os.path.join(g, open(common, encoding="utf-8").read().strip())
        if not os.path.isdir(g):
            return
        ex = os.path.join(g, "info", "exclude")
        have = open(ex, encoding="utf-8").read() if os.path.isfile(ex) else ""
        need = [p for p in ("/.claude/sessions.md", "/.claude/sessions/") if p not in have.split("\n")]
        if need:
            os.makedirs(os.path.dirname(ex), exist_ok=True)
            with open(ex, "a", encoding="utf-8") as f:
                f.write(("" if not have or have.endswith("\n") else "\n") + "\n".join(need) + "\n")
    except OSError:
        pass


def proc_stat(pid):
    """(comm, ppid, start ticks) from /proc, or None."""
    try:
        s = open("/proc/%d/stat" % pid, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    comm, rest = s[s.index("(") + 1:s.rindex(")")], s[s.rindex(")") + 2:].split()
    return comm, int(rest[1]), int(rest[19])


def claude_proc():
    """The claude process that runs this hook: (pid, start ticks, argv)."""
    pid = os.getppid()
    for _ in range(8):
        st = proc_stat(pid)
        if not st or pid <= 1:
            return None
        try:
            argv = open("/proc/%d/cmdline" % pid, "rb").read().decode("utf-8", "replace").split("\0")[:-1]
        except OSError:
            argv = []
        if st[0] == "claude" or (argv and os.path.basename(argv[0]) == "claude"):
            return pid, st[2], argv[1:]
        pid = st[1]
    return None


def alive(rec):
    """True or False on this host, None for a session of another host."""
    p = rec.get("pid")
    if rec.get("host") != host():
        return None
    if not isinstance(p, int):
        return False
    st = proc_stat(p)
    return bool(st) and st[2] == rec.get("pid_start")


def tmux_info():
    pane, sock = os.environ.get("TMUX_PANE"), os.environ.get("TMUX")
    if not pane or not sock:
        return None
    info = {"pane": pane, "socket": sock.split(",")[0]}
    try:
        r = subprocess.run(["tmux", "display-message", "-p", "-t", pane,
                            "#{session_name}\t#{window_index}\t#{window_name}"],
                           capture_output=True, timeout=2)
        out = r.stdout.decode("utf-8", "replace").rstrip("\n").split("\t")
        if r.returncode == 0 and len(out) == 3:
            info.update(session=out[0], window=int(out[1]), name=out[2])
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return info


def pane_gone(rec):
    """True when tmux still runs but the pane is gone, i.e. someone closed the window."""
    t = rec.get("tmux") or {}
    if not t.get("pane"):
        return True
    # display-message exits 0 for a pane that no longer exists, so look it up in the list.
    try:
        r = subprocess.run(["tmux", "list-panes", "-a", "-F", "#{pane_id}"], capture_output=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and t["pane"] not in r.stdout.decode().split()


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def replies(transcript, limit=4):
    """The last assistant replies, oldest first. Requests come from UserPromptSubmit
    instead: one turn's tool output can push them out of the transcript tail."""
    try:
        with open(transcript, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - TAIL))
            lines = f.read().decode("utf-8", "replace").split("\n")
    except OSError:
        return []
    if size > TAIL:
        lines = lines[1:]
    out, last = [], None
    for line in lines:
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if not isinstance(m, dict) or m.get("isSidechain") or m.get("isMeta") or m.get("isCompactSummary"):
            continue
        if m.get("type") == "user" and not isinstance((m.get("message") or {}).get("content"), list):
            last = None
        elif m.get("type") == "assistant":
            t = text_of((m.get("message") or {}).get("content")).strip()
            if not t:
                continue
            # Text blocks of one turn, split by tool calls, make one reply.
            if last is not None:
                out[last] += "\n" + t
            else:
                out.append(t)
                last = len(out) - 1
    return out[-limit:]


def first_line(text, n):
    t = " ".join(text.split())
    return t if len(t) <= n else t[:n - 1] + "…"


def plain_summary(reqs, reps):
    req = reqs[-1] if reqs else ""
    rep = reps[-1] if reps else ""
    rep = re.split(r"(?<=[.!?다요])\s", " ".join(rep.split()), maxsplit=1)[0]
    lines = []
    if req:
        lines.append("요청: " + first_line(mask(req), 110))
    if rep:
        lines.append("결과: " + first_line(mask(rep), 110))
    return lines


def llm_config():
    v = os.environ.get("VH1981_SUMMARY_LLM")
    if v is None:
        try:
            v = open(os.path.expanduser("~/.config/vh1981/summary-llm"), encoding="utf-8").read()
        except OSError:
            return None
    parts = v.split()
    return parts[:2] if len(parts) >= 2 and parts[0].startswith("http") else None


PROMPT = ("아래는 Claude Code 세션의 최근 대화다. 이 세션에서 최근에 진행한 일을 한국어 두 줄로 요약해라. "
          "첫 줄은 무엇을 하고 있는지, 둘째 줄은 마지막 상태나 다음 할 일이다. 각 줄은 80자 이내의 완전한 "
          "문장으로 쓰고, 머리말, 번호, 글머리표 없이 두 줄만 출력한다.")


def llm_summary(cfg, reqs, reps):
    chat = "[사용자의 최근 요청]\n%s\n\n[Claude 의 최근 답]\n%s" % (
        "\n".join("- " + r[:900] for r in reqs), "\n\n".join(mask(r)[:1500] for r in reps))
    body = {"model": cfg[1], "max_tokens": 300, "temperature": 0.3,
            "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": chat[-9000:]}],
            "chat_template_kwargs": {"enable_thinking": False}}
    for attempt in (0, 1):
        req = urllib.request.Request(cfg[0].rstrip("/") + "/chat/completions",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=90))
            break
        except urllib.error.HTTPError as e:
            # Endpoints other than vLLM may reject the thinking switch.
            if e.code != 400 or attempt:
                return None
            body.pop("chat_template_kwargs")
        except (OSError, ValueError):
            return None
    text = (r.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    lines = [first_line(re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", l), 120) for l in text.split("\n") if l.strip()]
    return lines[:2] or None


def restore_argv(rec):
    """Claude's own flags, without the ones that pick or start a session, then --resume <id>."""
    args, out, i = rec.get("argv") or [], [], 0
    while i < len(args):
        a = args[i]
        key = a.split("=", 1)[0]
        nxt = args[i + 1] if i + 1 < len(args) else None
        if key in DROP_WITH_VALUE:
            i += 1 if "=" in a or nxt is None or nxt.startswith("-") else 2
            continue
        if key in DROP_FLAGS or not a.startswith("-"):
            i += 1
            continue
        out.append(a)
        if key in VALUE_FLAGS and "=" not in a and nxt is not None:
            out.append(nxt)
            i += 1
        i += 1
    if rec.get("permission_mode") not in (None, "default") and not any(
            a.split("=")[0] in ("--permission-mode", "--dangerously-skip-permissions") for a in out):
        out += ["--permission-mode", rec["permission_mode"]]
    return ["claude"] + out + ["--resume", rec["session_id"]]


def restore_cmd(rec):
    return "cd %s && %s" % (shlex.quote(rec["cwd"]), " ".join(shlex.quote(a) for a in restore_argv(rec)))


def records(rdir):
    out = []
    try:
        names = os.listdir(rdir)
    except OSError:
        return out
    cutoff = time.time() - KEEP_DAYS * 86400
    for n in names:
        if not n.endswith(".json"):
            continue
        p = os.path.join(rdir, n)
        rec = load(p)
        if not rec.get("session_id"):
            continue
        if rec.get("updated", 0) < cutoff:
            try:
                os.remove(p)
            except OSError:
                pass
            continue
        out.append(rec)
    return out


def sort_key(rec):
    t = rec.get("tmux") or {}
    return (rec.get("host", ""), t.get("session") or "~", t.get("window", 1 << 30), -rec.get("updated", 0))


def render(top):
    rdir, md = paths(top)
    recs = sorted(records(rdir), key=sort_key)
    me = os.path.join(HERE, "sessions.py")
    out = ["# Claude 세션 목록", "",
           "`vh1981` 플러그인이 세션이 시작되거나 답을 마칠 때마다 고쳐 쓴다. 손으로 고치지 않는다.",
           "tmux 나 서버가 죽으면 그 머신에서 아래 명령으로 세션을 다시 띄운다. `--dry-run` 을 붙이면 실행할 명령만 보여 준다.",
           "", "```bash", "python3 %s restore %s" % (shlex.quote(me), shlex.quote(top)), "```", "",
           "갱신: %s (%s), 세션 %d개" % (kst(time.time()), host(), len(recs))]
    cur = None
    for rec in recs:
        if rec.get("host") != cur:
            cur = rec.get("host")
            out += ["", "## %s" % cur]
        t = rec.get("tmux") or {}
        if t.get("session") is not None:
            where = "`%s:%s` %s" % (t["session"], t.get("window", "?"), t.get("name") or "")
        elif t:
            where = "tmux 응답 없음 (pane `%s`)" % t.get("pane")
        else:
            where = "tmux 밖"
        state = " · 종료(%s)" % rec["ended"] if rec.get("ended") else ""
        out += ["", "### %s · %s%s" % (where.strip(), kst(rec.get("updated", 0)), state)]
        summary = rec.get("summary") or []
        if summary:
            out.append("- 최근 한 일:")
            out += ["  - " + s for s in summary]
        ctx = ["`%s`" % rec.get("cwd")]
        if rec.get("branch"):
            ctx.append("branch `%s`" % rec["branch"])
        if rec.get("devlog"):
            ctx.append("devlog `%s`" % rec["devlog"])
        out += ["- 위치: " + ", ".join(ctx),
                "- 세션: `%s`" % rec["session_id"],
                "- 복구: `%s`" % restore_cmd(rec)]
    os.makedirs(os.path.dirname(md), exist_ok=True)
    write_atomic(md, "\n".join(out) + "\n")


def spawn_summary(rec_path):
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "summarize", rec_path],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, close_fds=True)


def hook():
    if os.environ.get("VH1981_SESSIONS", "1") == "0":
        return
    try:
        p = json.loads(sys.stdin.buffer.read() or b"{}")
    except ValueError:
        return
    sid = p.get("session_id") if isinstance(p, dict) else None
    if not isinstance(sid, str) or not SID_RE.match(sid):
        return
    proc = claude_proc()
    # claude -p and SDK runs (cron, scripts) have no window to bring back.
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT", "cli").startswith("sdk") or (
            proc and any(a in ("-p", "--print") for a in proc[2])):
        return
    event = p.get("hook_event_name")
    cwd = p.get("cwd") if isinstance(p.get("cwd"), str) else os.getcwd()
    top, branch, active = repo_info(cwd)
    top = top or os.path.abspath(cwd)
    rdir, _ = paths(top)
    path = os.path.join(rdir, sid + ".json")
    rec = load(path)

    if event == "SessionEnd":
        if not rec:
            return
        if p.get("reason") in EXPLICIT_END or pane_gone(rec):
            try:
                os.remove(path)
            except OSError:
                pass
        else:
            rec["ended"] = p.get("reason") or "other"
            write_atomic(path, json.dumps(rec, ensure_ascii=False, indent=1))
        render(top)
        return
    if event not in ("SessionStart", "UserPromptSubmit", "Stop"):
        return

    if not os.path.isdir(rdir):
        os.makedirs(rdir, exist_ok=True)
        exclude(top)
    now = time.time()
    rec.update(session_id=sid, host=host(), cwd=cwd, top=top, branch=branch, devlog=active,
               updated=now, tmux=tmux_info(), permission_mode=p.get("permission_mode"))
    rec.setdefault("started", now)
    rec.pop("ended", None)
    prompt = p.get("prompt")
    if event == "UserPromptSubmit" and isinstance(prompt, str) and prompt.strip() \
            and not prompt.lstrip().startswith("<"):
        rec["requests"] = (rec.get("requests") or [])[-2:] + [mask(prompt.strip())[:1500]]
    if proc:
        rec.update(pid=proc[0], pid_start=proc[1], argv=proc[2])
    transcript = p.get("transcript_path")
    if isinstance(transcript, str):
        rec["transcript"] = transcript
        if event != "UserPromptSubmit" and (not rec.get("summary") or not llm_config()):
            rec["summary"] = plain_summary(rec.get("requests"), replies(transcript)) or rec.get("summary") or []
    write_atomic(path, json.dumps(rec, ensure_ascii=False, indent=1))
    render(top)
    if event == "Stop" and rec.get("transcript") and llm_config():
        spawn_summary(path)


def lock_dir():
    base = os.environ.get("VH1981_STATE_DIR") or os.path.join(
        os.environ.get("TMPDIR") or "/tmp", "vh1981-%d" % os.getuid())
    d = os.path.join(base, "summarizing")
    os.makedirs(d, exist_ok=True)
    return d


def summarize(path):
    cfg = llm_config()
    rec = load(path)
    if not cfg or not rec.get("transcript"):
        return
    lock = os.path.join(lock_dir(), rec["session_id"])
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        # A summarizer for this session is running and re-checks the transcript when done.
        try:
            if time.time() - os.path.getmtime(lock) < 300:
                return
            os.remove(lock)
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return
    os.close(fd)
    try:
        for _ in range(3):
            try:
                size = os.path.getsize(rec["transcript"])
            except OSError:
                return
            if size == rec.get("summary_size"):
                return
            lines = llm_summary(cfg, rec.get("requests") or [], replies(rec["transcript"]))
            rec = load(path)
            if not rec:
                return
            rec["summary_size"] = size
            if lines:
                rec.update(summary=lines, summary_at=time.time())
            write_atomic(path, json.dumps(rec, ensure_ascii=False, indent=1))
            render(rec["top"])
            if not lines:
                return
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


# Run from inside Claude Code, a new tmux server would hand these to the resumed sessions,
# which would then take themselves for children of this one.
CHILD_ENV = ("CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT", "CLAUDE_CODE_")


def tmux(*args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(CHILD_ENV)}
    r = subprocess.run(["tmux"] + list(args), capture_output=True, text=True, env=env)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def option(argv, name):
    if name not in argv:
        return None
    i = argv.index(name)
    v = argv[i + 1] if i + 1 < len(argv) else ""
    del argv[i:i + 2]
    return v


def top_of(argv):
    d = argv[0] if argv else os.getcwd()
    top, _, _ = repo_info(d)
    return top or os.path.abspath(d)


def label(rec):
    t = rec.get("tmux") or {}
    if t.get("session") is not None:
        return "%s:%s %s" % (t["session"], t.get("window", "?"), t.get("name") or "")
    return "tmux 응답 없음" if t else "tmux 밖"


def list_(argv):
    top = top_of(argv)
    recs = sorted(records(paths(top)[0]), key=sort_key)
    me = host()
    print("%s  (이 머신 %s, 세션 %d개)" % (top, me, len(recs)))
    for rec in recs:
        a = alive(rec)
        state = "실행 중" if a else ("중단" if a is False else "다른 머신")
        if rec.get("ended"):
            state += ", 종료(%s)" % rec["ended"]
        print("\n%s  %s  [%s]  %s  %s" % (rec["session_id"][:8], rec.get("host"), state,
                                        label(rec).strip(), kst(rec.get("updated", 0))))
        print("  위치: %s" % rec.get("cwd"))
        for s in rec.get("summary") or []:
            print("  - " + s)
    return 0


def restore(argv):
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    want = option(argv, "--host") or host()
    only = [x for x in (option(argv, "--only") or "").split(",") if x]
    top = top_of(argv)
    rdir, md = paths(top)
    recs = sorted((r for r in records(rdir) if r.get("host") == want), key=sort_key)
    if only:
        recs = [r for r in recs if any(r["session_id"].startswith(x) or
                                       (r.get("tmux") or {}).get("name") == x for x in only)]
    if not recs:
        print("복구할 세션이 없다: %s (host %s%s)" % (rdir, want, ", --only " + ",".join(only) if only else ""))
        return 0
    done = 0
    for rec in recs:
        label = rec["session_id"][:8]
        if alive(rec):
            print("건너뜀 %s: 아직 실행 중 (pid %s)" % (label, rec["pid"]))
            continue
        t = rec.get("tmux") or {}
        sess = t.get("session") or "claude-restore"
        name = t.get("name") or os.path.basename(rec["cwd"].rstrip("/")) or "claude"
        cmd = " ".join(shlex.quote(a) for a in restore_argv(rec))
        if dry:
            print("tmux %s:%s %s  <-  cd %s && %s" % (sess, t.get("window", "+"), name,
                                                      shlex.quote(rec["cwd"]), cmd))
            continue
        if tmux("has-session", "-t", "=" + sess)[0] != 0:
            rc, pane, err = tmux("new-session", "-d", "-P", "-F", "#{pane_id}", "-s", sess,
                                 "-n", name, "-c", rec["cwd"])
            if rc == 0 and isinstance(t.get("window"), int):
                tmux("move-window", "-s", pane, "-t", "%s:%d" % (sess, t["window"]))
        else:
            target = "%s:%d" % (sess, t["window"]) if isinstance(t.get("window"), int) else sess + ":"
            rc, pane, err = tmux("new-window", "-d", "-P", "-F", "#{pane_id}", "-t", target,
                                 "-n", name, "-c", rec["cwd"])
            if rc != 0 and target != sess + ":":
                rc, pane, err = tmux("new-window", "-d", "-P", "-F", "#{pane_id}", "-t", sess + ":",
                                     "-n", name, "-c", rec["cwd"])
        if rc != 0:
            print("실패 %s: tmux %s" % (label, err))
            continue
        tmux("send-keys", "-t", pane, cmd, "Enter")
        # The resumed session writes its own record; drop the old one so it is not restored twice.
        try:
            os.remove(os.path.join(rdir, rec["session_id"] + ".json"))
        except OSError:
            pass
        print("복구 %s: tmux %s 창 %s  (%s)" % (label, sess, name, rec["cwd"]))
        done += 1
    if not dry:
        render(top)
        print("%d개 복구. 붙기: tmux attach" % done)
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "restore":
        return restore(sys.argv[2:])
    if cmd == "list":
        return list_(sys.argv[2:])
    if cmd == "summarize" and len(sys.argv) > 2:
        summarize(sys.argv[2])
        return 0
    if cmd == "hook":
        try:
            hook()
        except Exception:
            pass
        return 0
    print(__doc__.strip().split("\n\n")[1])
    return 2


if __name__ == "__main__":
    sys.exit(main())
