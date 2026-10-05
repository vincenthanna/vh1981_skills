#!/usr/bin/env python3
"""kb.py: devlog knowledge base (KB) client and store.

The KB is a plain directory, local or reached over ssh. This one file plays two
roles:

* client (default): runs in a checkout. It identifies the repo, selects which
  devlog files may leave the machine, and talks to the store.
* store (`kb.py store <cmd> --root <kb>`): runs where the KB lives. Over ssh
  the client copies this same file to `<kb>/.kb/bin/kb.py` and runs it there,
  so the KB host needs only python3 >= 3.8 and no plugin install.

Client and store exchange one JSON line on stdin (plus a tar.gz payload for
uploads) and one JSON object on stdout. Arguments never travel through a remote
shell command line except the store command name and root path.

Ownership model: a KB project is written by exactly one checkout (its owner).
Another checkout holding a copy of the same project is reported as a conflict
and writes nothing unless it passes --take-over. Real devlogs had diverged
copies of one project across worktrees and clones, so merging is never
automatic. Conflicts are detected with per-file sha256 in a manifest; mtimes
are not trusted because cp and tar rewrite them.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tarfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

SCRIPT = os.path.realpath(__file__) if "__file__" in globals() else ""
CONFIG = os.path.expanduser("~/.config/vh1981/kb")
# Shared default KB, used only when nothing else names one. It comes from the
# environment (VH1981_KB_DEFAULT) so no host or user name lives in this public repo.
TEXT_EXT = {".md", ".txt", ".py", ".sh", ".yaml", ".yml", ".json", ".jsonl", ".csv", ".log",
            ".toml", ".cfg", ".ini", ".patch", ".diff"}
TEXT_MAX = 512 * 1024
HTML_MAX = 1024 * 1024
SEARCH_SKIP = {"history", "rejected", "_archived"}
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STALE_DAYS = 30
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
            # Reuse one connection across the probe and the store call: sshd's
            # MaxStartups dropped back-to-back connections ("banner exchange").
            "-o", "ControlMaster=auto", "-o", "ControlPath=~/.ssh/kb-%C", "-o", "ControlPersist=60"]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def die(msg: str, code: int = 1):
    print(f"kb: {msg}", file=sys.stderr)
    sys.exit(code)


# ===================================================================== store

class StoreError(Exception):
    pass


def safe_name(n: str, what: str) -> str:
    if not n or not NAME_RE.match(n):
        raise StoreError(f"invalid {what}: {n!r}")
    return n


def safe_rel(rel: str) -> str:
    """A relative path that cannot escape its base directory."""
    norm = os.path.normpath(rel)
    if os.path.isabs(norm) or norm == ".." or norm.startswith("../") or norm == ".":
        raise StoreError(f"unsafe path: {rel!r}")
    if any(p.startswith(".") for p in norm.split("/")):
        raise StoreError(f"dot path not allowed: {rel!r}")
    return norm


def write_atomic(path: str, data, mode: str = "w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        f.write(data)
    os.replace(tmp, path)


class Lock:
    """mkdir lock: atomic on every POSIX filesystem, no fcntl over NFS worries."""

    def __init__(self, root: str, wait: float = 60, stale: float = 300):
        self.dir = os.path.join(root, ".kb", "lock")
        self.wait, self.stale = wait, stale

    def __enter__(self):
        deadline = time.time() + self.wait
        while True:
            try:
                os.mkdir(self.dir)
                with open(os.path.join(self.dir, "owner"), "w") as f:
                    f.write(f"{socket.gethostname()} {os.getpid()} {now_iso()}\n")
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.dir) > self.stale:
                        shutil.rmtree(self.dir, ignore_errors=True)
                        continue
                except OSError:
                    continue
                if time.time() > deadline:
                    raise StoreError("KB is locked by another upload (.kb/lock); retry later")
                time.sleep(0.2)

    def __exit__(self, *exc):
        shutil.rmtree(self.dir, ignore_errors=True)


def is_kb(root: str) -> bool:
    return os.path.isfile(os.path.join(root, "KB.md")) and os.path.isdir(os.path.join(root, ".kb"))


def manifest_path(root, kind, name, project):
    return os.path.join(root, ".kb", "manifest", kind, name, f"{project}.json")


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def registry_path(root, kind, name):
    return os.path.join(root, "registry", kind, f"{name}.md")


REG_BLOCK = re.compile(r"```json\n(.*?)\n```", re.S)


def load_registry(root, kind, name) -> tuple:
    """Registry file = a ```json block (machine fields) + free prose kept as-is."""
    p = registry_path(root, kind, name)
    try:
        text = open(p, encoding="utf-8").read()
    except OSError:
        return {"id": f"{kind}/{name}", "checkouts": []}, ""
    m = REG_BLOCK.search(text)
    data = json.loads(m.group(1)) if m else {}
    prose = text[m.end():].lstrip("\n") if m else text
    data.setdefault("id", f"{kind}/{name}")
    data.setdefault("checkouts", [])
    return data, prose


def save_registry(root, kind, name, data, prose):
    body = (f"# {kind}/{name}\n\n"
            "<!-- kb.py owns the json block; edit it with `kb.py register`. Prose below is free. -->\n\n"
            "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```\n\n" + (prose or ""))
    write_atomic(registry_path(root, kind, name), body)


def iter_manifests(root):
    base = os.path.join(root, ".kb", "manifest")
    for kind in ("repos", "topics"):
        kd = os.path.join(base, kind)
        if not os.path.isdir(kd):
            continue
        for name in sorted(os.listdir(kd)):
            nd = os.path.join(kd, name)
            if not os.path.isdir(nd):
                continue
            for fn in sorted(os.listdir(nd)):
                if fn.endswith(".json"):
                    m = load_json(os.path.join(nd, fn))
                    if m:
                        yield m


def iter_registries(root):
    for kind in ("repos", "topics"):
        kd = os.path.join(root, "registry", kind)
        if not os.path.isdir(kd):
            continue
        for fn in sorted(os.listdir(kd)):
            if fn.endswith(".md"):
                yield load_registry(root, kind, fn[:-3])[0]


def short_at(at: str) -> str:
    host, _, path = at.partition(":")
    return f"{host}:{os.path.basename(path.rstrip('/'))}"


def regenerate(root):
    """Rebuild INDEX.md, NOW.md and catalog.json from manifests and registries."""
    mans = list(iter_manifests(root))
    regs = {r["id"]: r for r in iter_registries(root)}
    rows = []
    for m in mans:
        card = m.get("card") or {}
        own = next((c for c in regs.get(f"{m['kind']}/{m['name']}", {}).get("checkouts", [])
                    if c.get("at") == m["owner"]), {})
        rows.append({
            "id": m["id"], "status": card.get("status") or "?", "tags": card.get("tags") or [],
            "summary": " ".join((card.get("summary") or "").split()) or f"{m.get('title') or m['project']} (카드 없음)",
            "related": card.get("related") or [], "updated": m.get("updated", ""), "owner": m["owner"],
            "branch": own.get("branch", ""), "title": m.get("title", ""), "period": m.get("period", ""),
            "open_items": m.get("open_items", []), "files": len(m.get("files", {})),
            "copies": {k: v for k, v in (m.get("sources") or {}).items() if k != m["owner"] and v.get("diverged")},
            "has_card": bool(card),
        })
    rows.sort(key=lambda r: r["updated"], reverse=True)
    ts = now_iso()

    idx = [
        "# KB INDEX", "",
        "<!-- kb.py가 만든 파일이다. 손으로 고치지 않는다. 이 파일을 먼저 통째로 읽고, 본문은 `kb.py search` 로 찾는다. -->", "",
        f"갱신: {ts} · 프로젝트 {len(rows)}개", "",
        "## 프로젝트", "",
        "형식: `ID` · status · tags · 마지막 업로드 · 소유 checkout(branch) · summary", "",
    ]
    for r in rows:
        br = f"@{r['branch']}" if r["branch"] else ""
        idx.append(f"- `{r['id']}` · {r['status']} · {', '.join(r['tags']) or '-'} · {r['updated'][:10]} · "
                   f"{short_at(r['owner'])}{br} · {r['summary']}")
    idx += ["", "## 출처", "", "형식: `ID` · remote · 하는 일 · 분야 · checkout 수", ""]
    for rid, g in sorted(regs.items()):
        idx.append(f"- `{rid}` · {g.get('remote') or '-'} · {g.get('work') or '(미등록)'} · "
                   f"{', '.join(g.get('domains') or []) or '-'} · checkout {len(g.get('checkouts', []))}개")
    write_atomic(os.path.join(root, "INDEX.md"), "\n".join(idx) + "\n")

    cut = (datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)).isoformat()
    active = [r for r in rows if r["status"] == "active"]
    now = ["# NOW", "", "<!-- kb.py가 업로드마다 다시 만든다. 손으로 고치지 않는다. -->", "",
           f"갱신: {ts}", "", "## 진행 중", ""]
    now += [f"- `{r['id']}` · {r['updated'][:10]} · {short_at(r['owner'])}"
            f"{'@' + r['branch'] if r['branch'] else ''} · {r['summary']}" for r in active] or ["- 없음"]
    now += ["", "## 열린 항목 (Critical, High)", ""]
    items = [f"- `{r['id']}` {it}" for r in active for it in r["open_items"]]
    now += items or ["- 없음"]
    now += ["", "## 갈라진 사본", "", "소유 checkout 밖에서 내용이 다른 사본이 올라온 프로젝트다. `kb.py upload --take-over` 로 소유자를 바꿀 수 있다.", ""]
    div = [f"- `{r['id']}` 소유 {short_at(r['owner'])}, 다른 사본 {short_at(at)} "
           f"(그쪽에만 {c.get('only_source', 0)}, 내용 다름 {c.get('differ', 0)}, KB에만 {c.get('only_kb', 0)}; {c.get('last_seen', '')[:10]})"
           for r in rows for at, c in r["copies"].items()]
    now += div or ["- 없음"]
    now += ["", f"## 멈춘 것 ({STALE_DAYS}일 넘게 업로드 없음)", ""]
    now += [f"- `{r['id']}` 마지막 업로드 {r['updated'][:10]}" for r in active if r["updated"] < cut] or ["- 없음"]
    write_atomic(os.path.join(root, "NOW.md"), "\n".join(now) + "\n")
    write_atomic(os.path.join(root, ".kb", "catalog.json"),
                 json.dumps({"updated": ts, "projects": rows, "sources": list(regs.values())},
                            ensure_ascii=False, indent=1))


def store_init(root, meta, _payload):
    created = not is_kb(root)
    for d in ("repos", "topics", "registry/repos", "registry/topics", ".kb/manifest", ".kb/staging"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    write_atomic(os.path.join(root, ".kb", "host"), socket.gethostname() + "\n")
    kbmd = os.path.join(root, "KB.md")
    if not os.path.exists(kbmd) and meta.get("kb_md"):
        write_atomic(kbmd, meta["kb_md"])
    with Lock(root):
        regenerate(root)
    legacy = sorted(os.listdir(os.path.join(root, "projects"))) if os.path.isdir(os.path.join(root, "projects")) else []
    return {"status": "ok", "created": created, "root": root, "legacy_projects": legacy,
            "python": sys.version.split()[0]}


def diff_sets(src: dict, kb: dict) -> dict:
    only_source = sorted(p for p in src if p not in kb)
    only_kb = sorted(p for p in kb if p not in src)
    differ = sorted(p for p in src if p in kb and kb[p]["sha256"] != src[p]["sha256"])
    return {"only_source": only_source, "differ": differ, "only_kb": only_kb}


def upsert_checkout(reg: dict, co: dict, project: str, copy_only: bool):
    entry = next((c for c in reg["checkouts"] if c.get("at") == co["at"]), None)
    if entry is None:
        entry = {"at": co["at"], "access": co.get("access", ""), "branch": co.get("branch", ""),
                 "work": "", "projects": [], "copies": []}
        reg["checkouts"].append(entry)
    entry["branch"] = co.get("branch", entry.get("branch", ""))
    if not entry.get("access"):
        entry["access"] = co.get("access", "")
    key = "copies" if copy_only else "projects"
    other = "projects" if copy_only else "copies"
    entry.setdefault(key, [])
    entry.setdefault(other, [])
    if project not in entry[key]:
        entry[key].append(project)
        entry[key].sort()
    if project in entry[other]:
        entry[other].remove(project)
    entry["last_upload"] = now_iso()


def store_upload(root, meta, payload):
    if not is_kb(root):
        raise StoreError(f"not a KB: {root} (run `kb.py init` first)")
    kind = meta["kind"]
    if kind not in ("repos", "topics"):
        raise StoreError(f"invalid kind: {kind}")
    name = safe_name(meta["name"], "repo/topic name")
    project = safe_name(meta["project"], "project name")
    co = meta["checkout"]
    me = co["at"]
    src = {safe_rel(f["path"]): f for f in meta["files"]}
    dest = os.path.join(root, kind, name, project)
    mpath = manifest_path(root, kind, name, project)
    dry = meta.get("dry_run", False)

    with Lock(root):
        reg, prose = load_registry(root, kind, name)
        if kind == "repos" and meta.get("remote") and reg.get("remote") and reg["remote"] != meta["remote"]:
            return {"status": "repo-collision", "existing_remote": reg["remote"], "remote": meta["remote"],
                    "hint": "같은 이름의 다른 repo가 이미 있다. --as <org>__<repo> 로 다시 올린다"}
        man = load_json(mpath)
        kbf = (man or {}).get("files", {})
        owner = (man or {}).get("owner")
        d = diff_sets(src, kbf)
        if owner and owner != me and not meta.get("take_over"):
            diverged = bool(d["only_source"] or d["differ"] or d["only_kb"])
            res = {"status": "conflict" if diverged else "same-as-owner",
                   "id": f"{kind}/{name}/{project}", "owner": owner, **d}
            if not dry:
                man.setdefault("sources", {})[me] = {"last_seen": now_iso(), "diverged": diverged,
                                                     **{k: len(v) for k, v in d.items()}}
                write_atomic(mpath, json.dumps(man, ensure_ascii=False, indent=1))
                if meta.get("remote"):
                    reg["remote"] = meta["remote"]
                upsert_checkout(reg, co, project, copy_only=True)
                save_registry(root, kind, name, reg, prose)
                regenerate(root)
            return res

        to_write = sorted(p for p in src if kbf.get(p, {}).get("sha256") != src[p]["sha256"])
        to_delete = d["only_kb"]
        res = {"id": f"{kind}/{name}/{project}", "owner_before": owner, "write": to_write,
               "delete": to_delete, "unchanged": len(src) - len(to_write)}
        if owner and owner != me:
            res["displaced"] = sorted(set(d["only_kb"]) | set(d["differ"]))
        if dry:
            return {"status": "dry-run", **res}
        if to_delete and not meta.get("yes"):
            return {"status": "needs-confirm", **res}

        stage = os.path.join(root, ".kb", "staging", uuid.uuid4().hex)
        os.makedirs(stage)
        try:
            seen = set()
            with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as tf:
                for m in tf.getmembers():
                    if not m.isfile():
                        continue
                    rel = safe_rel(m.name)
                    data = tf.extractfile(m).read()
                    if rel not in src or sha256_bytes(data) != src[rel]["sha256"]:
                        raise StoreError(f"payload does not match the file list: {rel}")
                    out = os.path.join(stage, rel)
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with open(out, "wb") as f:
                        f.write(data)
                    seen.add(rel)
            missing = sorted(set(src) - seen)
            if missing:
                raise StoreError(f"payload is missing files: {missing[:5]}")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            old = None
            if os.path.exists(dest):
                old = stage + ".old"
                os.rename(dest, old)
            os.rename(stage, dest)
            if old:
                shutil.rmtree(old, ignore_errors=True)
        finally:
            shutil.rmtree(stage, ignore_errors=True)

        ts = now_iso()
        files = {p: {"sha256": src[p]["sha256"], "size": src[p]["size"],
                     "by": me, "at": ts if p in to_write else kbf.get(p, {}).get("at", ts)} for p in src}
        sources = (man or {}).get("sources", {})
        sources[me] = {"last_seen": ts, "diverged": False}
        new = {"id": f"{kind}/{name}/{project}", "kind": kind, "name": name, "project": project,
               "owner": me, "updated": ts, "files": files, "sources": sources,
               "card": meta.get("card") or {}, "title": meta.get("title", ""),
               "period": meta.get("period", ""), "open_items": meta.get("open_items", [])}
        if owner and owner != me:
            new["previous_owner"] = owner
        write_atomic(mpath, json.dumps(new, ensure_ascii=False, indent=1))
        if meta.get("remote"):
            reg["remote"] = meta["remote"]
        upsert_checkout(reg, co, project, copy_only=False)
        if owner and owner != me:
            prev = next((c for c in reg["checkouts"] if c.get("at") == owner), None)
            if prev and project in prev.get("projects", []):
                prev["projects"].remove(project)
                prev.setdefault("copies", []).append(project)
        save_registry(root, kind, name, reg, prose)
        regenerate(root)
        return {"status": "ok", **res}


def store_register(root, meta, _payload):
    if not is_kb(root):
        raise StoreError(f"not a KB: {root}")
    kind, name = meta["kind"], safe_name(meta["name"], "repo/topic name")
    with Lock(root):
        reg, prose = load_registry(root, kind, name)
        for k in ("work", "domains", "remote"):
            if meta.get(k) is not None:
                reg[k] = meta[k]
        co = meta.get("checkout")
        if co:
            entry = next((c for c in reg["checkouts"] if c.get("at") == co["at"]), None)
            if entry is None:
                entry = {"at": co["at"], "projects": [], "copies": []}
                reg["checkouts"].append(entry)
            for k in ("access", "branch", "work", "last_seen", "devlog_projects"):
                if co.get(k) is not None:
                    entry[k] = co[k]
        save_registry(root, kind, name, reg, prose)
        regenerate(root)
    return {"status": "ok", "registry": reg}


def store_registry(root, meta, _payload):
    if meta.get("name"):
        return {"status": "ok", "registry": load_registry(root, meta["kind"], meta["name"])[0]}
    return {"status": "ok", "registries": list(iter_registries(root))}


def store_search(root, meta, _payload):
    pats = [re.compile(p, re.I) for p in meta["patterns"]]
    scope = meta.get("scope") or ""
    inc = meta.get("include_all", False)
    per_file, total = meta.get("max_per_file", 5), meta.get("max_total", 120)
    hits = []
    for kind in ("repos", "topics"):
        base = os.path.join(root, kind)
        for dp, dns, fns in os.walk(base):
            rel_dir = os.path.relpath(dp, root)
            parts = rel_dir.split(os.sep)
            dns[:] = sorted(d for d in dns if not d.startswith(".") and (inc or len(parts) < 3 or d not in SEARCH_SKIP))
            if len(parts) >= 3 and not inc and any(p in SEARCH_SKIP for p in parts[3:]):
                continue
            for fn in sorted(fns):
                rel = os.path.join(rel_dir, fn)
                if scope and not rel.startswith(scope):
                    continue
                if os.path.splitext(fn)[1].lower() not in TEXT_EXT | {".html"}:
                    continue
                try:
                    lines = open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read().splitlines()
                except OSError:
                    continue
                found = [(i + 1, ln) for i, ln in enumerate(lines) if any(p.search(ln) for p in pats)]
                if found:
                    hits.append((len(found), rel, found[:per_file]))
    hits.sort(key=lambda h: -h[0])
    out, n = [], 0
    for cnt, rel, found in hits:
        for ln_no, text in found:
            if n >= total:
                break
            out.append({"file": rel, "line": ln_no, "text": text.strip()[:220], "file_hits": cnt})
            n += 1
    return {"status": "ok", "files": len(hits), "hits": out, "truncated": sum(h[0] for h in hits) > n,
            "top_files": [{"file": rel, "hits": cnt} for cnt, rel, _ in hits[:15]]}


DATE = r"(\d{4}-\d{2}-\d{2})"
LOG_BULLET = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(?:\[[A-Za-z]+\]\s*)?\**" + DATE + r"\**\s*[:·—–-]?\s*(.+)$")
LOG_ADDED = re.compile(r"\(added " + DATE + r"\)")
LOG_HEAD_START = re.compile(r"^#{2,4}\s+" + DATE + r"\b\s*[:·—–-]?\s*(.*)$")
LOG_HEAD_END = re.compile(r"^#{2,4}\s+(.*?)\s*\(" + DATE + r"\)\s*$")
LOG_ANY = re.compile(DATE)


def scan_log(projects, since, until, loose=False):
    """Collect dated entries from devlog docs. `projects` is [(id, dir)].

    Strict forms (the devlog dating rule): a bullet that starts with a date,
    a heading that starts or ends with a date, and `(added DATE)` on a
    Remaining item. --loose also takes any bullet holding an ISO date, for
    docs written before the rule."""
    out = []
    for pid, pdir in projects:
        for dp, dns, fns in os.walk(pdir):
            dns[:] = sorted(d for d in dns if not d.startswith("."))
            for fn in sorted(fns):
                if not fn.endswith(".md"):
                    continue
                full = os.path.join(dp, fn)
                rel = os.path.relpath(full, pdir)
                in_history = rel.split(os.sep)[0] == "history"
                section = ""
                try:
                    lines = open(full, encoding="utf-8", errors="replace").read().splitlines()
                except OSError:
                    continue
                for no, ln in enumerate(lines, 1):
                    if ln.startswith("#"):
                        section = ln.lstrip("#").strip()
                        m = LOG_HEAD_START.match(ln)
                        mm = None if m else LOG_HEAD_END.match(ln)
                        if m or mm:
                            d, text = (m.group(1), section) if m else (mm.group(2), mm.group(1))
                            kind = "history" if in_history else "finding" if "finding" in ln.lower() else "heading"
                            out.append((d, pid, rel, no, kind, text.strip()))
                        continue
                    m = LOG_BULLET.match(ln)
                    if m:
                        sec = section.lower()
                        kind = "history" if in_history else "done" if sec.startswith("done") else "dated"
                        out.append((m.group(1), pid, rel, no, kind, m.group(2).strip()))
                        continue
                    m = LOG_ADDED.search(ln)
                    if m:
                        out.append((m.group(1), pid, rel, no, "added", re.sub(r"^\s*[-*]\s+", "", ln).strip()))
                        continue
                    if loose and re.match(r"^\s*(?:[-*]|\d+\.|\|)\s", ln):
                        m = LOG_ANY.search(ln)
                        if m:
                            out.append((m.group(1), pid, rel, no, "mention", re.sub(r"^\s*[-*|]\s*", "", ln).strip()))
    out = [e for e in out if (not since or e[0] >= since) and (not until or e[0] <= until)]
    out.sort(key=lambda e: (e[0], e[1], e[2], e[3]))
    return [{"date": d, "id": i, "file": f, "line": n, "kind": k, "text": t[:300]} for d, i, f, n, k, t in out]


def store_log(root, meta, _payload):
    scope = meta.get("scope") or ""
    projects = []
    for kind in ("repos", "topics"):
        kd = os.path.join(root, kind)
        if not os.path.isdir(kd):
            continue
        for name in sorted(os.listdir(kd)):
            for proj in sorted(os.listdir(os.path.join(kd, name))):
                pid = f"{kind}/{name}/{proj}"
                if os.path.isdir(os.path.join(kd, name, proj)) and pid.startswith(scope):
                    projects.append((pid, os.path.join(kd, name, proj)))
    return {"status": "ok", "entries": scan_log(projects, meta.get("since"), meta.get("until"), meta.get("loose"))}


def store_cat(root, meta, _payload):
    rel = safe_rel(meta["path"])
    if rel.split("/")[0] not in ("repos", "topics", "registry") and rel not in ("KB.md", "INDEX.md", "NOW.md"):
        raise StoreError(f"not a KB document: {rel}")
    p = os.path.join(root, rel)
    if os.path.isdir(p):
        files = []
        for dp, dns, fns in os.walk(p):
            dns.sort()
            files += [os.path.relpath(os.path.join(dp, f), root) for f in sorted(fns)]
        return {"status": "ok", "dir": rel, "files": files}
    with open(p, encoding="utf-8", errors="replace") as f:
        return {"status": "ok", "path": rel, "text": f.read(400_000)}


def store_check(root, meta, _payload):
    mans = list(iter_manifests(root))
    regs = list(iter_registries(root))
    issues = []
    for m in mans:
        for at, c in (m.get("sources") or {}).items():
            if at != m["owner"] and c.get("diverged"):
                issues.append({"kind": "diverged-copy", "id": m["id"], "owner": m["owner"], "copy": at,
                               "detail": {k: c.get(k) for k in ("only_source", "differ", "only_kb")}})
        if not m.get("card"):
            issues.append({"kind": "no-card", "id": m["id"]})
        reg = next((r for r in regs if r["id"] == f"{m['kind']}/{m['name']}"), None)
        if not reg or not any(c.get("at") == m["owner"] for c in reg["checkouts"]):
            issues.append({"kind": "owner-unregistered", "id": m["id"], "owner": m["owner"]})
    have = {m["id"] for m in mans}
    for r in regs:
        if not r.get("work"):
            issues.append({"kind": "registry-no-work", "id": r["id"]})
        for c in r["checkouts"]:
            if not c.get("work"):
                issues.append({"kind": "checkout-no-work", "id": r["id"], "at": c["at"]})
            for p in c.get("projects", []):
                if f"{r['id']}/{p}" not in have:
                    issues.append({"kind": "registered-but-missing", "id": f"{r['id']}/{p}", "at": c["at"]})
    by_name = {}
    for m in mans:
        by_name.setdefault(m["project"], []).append(m["id"])
    for p, ids in by_name.items():
        if len(ids) > 1:
            issues.append({"kind": "same-name-elsewhere", "project": p, "ids": ids})
    if os.path.isdir(os.path.join(root, "projects")):
        issues.append({"kind": "legacy-layout", "projects": sorted(os.listdir(os.path.join(root, "projects")))})
    return {"status": "ok", "issues": issues}


STORE_CMDS = {"init": store_init, "upload": store_upload, "register": store_register, "log": store_log,
              "registry": store_registry, "search": store_search, "cat": store_cat, "check": store_check}


def store_main(argv):
    ap = argparse.ArgumentParser(prog="kb.py store")
    ap.add_argument("cmd", choices=sorted(STORE_CMDS))
    ap.add_argument("--root", required=True)
    a = ap.parse_args(argv)
    raw = sys.stdin.buffer
    line = raw.readline()
    meta = json.loads(line.decode("utf-8")) if line.strip() else {}
    payload = raw.read()
    root = os.path.realpath(os.path.expanduser(a.root))
    try:
        res = STORE_CMDS[a.cmd](root, meta, payload)
        print(json.dumps(res, ensure_ascii=False))
        return 0
    except (StoreError, OSError, KeyError, ValueError) as e:
        print(json.dumps({"status": "error", "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        return 1


# ==================================================================== client

class Loc:
    def __init__(self, spec: str, source: str = ""):
        self.spec, self.source = spec, source
        if spec.startswith("ssh://"):
            u = urlparse(spec)
            if not u.path or not u.path.startswith("/"):
                die(f"ssh location needs an absolute path: {spec}")
            self.kind = "ssh"
            self.host = (f"{u.username}@" if u.username else "") + (u.hostname or "")
            self.port = u.port
            self.path = u.path.rstrip("/") or "/"
        else:
            self.kind = "local"
            self.path = os.path.realpath(os.path.expanduser(spec))

    def localize(self):
        """An ssh location whose KB lives on this very machine is used as a local path,
        so sessions on the KB host need no ssh to themselves."""
        if self.kind == "ssh" and is_kb(self.path):
            try:
                mark = open(os.path.join(self.path, ".kb", "host"), encoding="utf-8").read().strip()
            except OSError:
                mark = ""
            if mark == socket.gethostname():
                self.kind = "local"
                self.source += " → 이 머신의 로컬 경로"
        return self

    def __str__(self):
        return self.spec if self.kind == "ssh" else self.path

    def ssh_base(self):
        return ["ssh", *SSH_OPTS, *(["-p", str(self.port)] if self.port else []), self.host]


def run_ssh(argv, **kw):
    """ssh exits 255 on connection failure; retry those twice with backoff."""
    for attempt in range(3):
        r = subprocess.run(argv, **kw)
        if r.returncode != 255 or attempt == 2:
            return r
        time.sleep(2 * (attempt + 1))
    return r


def git(args, cwd):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def git_top(cwd):
    return git(["rev-parse", "--show-toplevel"], cwd)


def default_spec() -> str:
    return os.environ.get("VH1981_KB_DEFAULT", "").strip()


NO_KB = "KB 위치가 없다. `kb.py init <위치>` 로 이 머신의 KB를 정하거나 VH1981_KB 를 설정한다"


def resolve_loc(explicit) -> Loc:
    loc = _resolve(explicit)
    if loc is None:
        die(NO_KB)
    return loc.localize()


def _resolve(explicit):
    if explicit:
        return Loc(explicit, "--kb")
    if os.environ.get("VH1981_KB"):
        return Loc(os.environ["VH1981_KB"], "VH1981_KB")
    try:
        v = open(CONFIG, encoding="utf-8").read().strip()
        if v:
            return Loc(v, CONFIG)
    except OSError:
        pass
    top = git_top(os.getcwd()) or os.getcwd()
    legacy = os.path.join(top, "docs", "devlog", ".upload-target")
    try:
        v = open(legacy, encoding="utf-8").read().strip()
        if v:
            return Loc(v, f"{legacy} (legacy)")
    except OSError:
        pass
    return Loc(default_spec(), "built-in default") if default_spec() else None


_pushed = set()


def ensure_remote_script(loc: Loc):
    if loc.spec in _pushed:
        return
    me = open(SCRIPT, "rb").read()
    target = f"{loc.path}/.kb/bin/kb.py"
    probe = ("import hashlib,sys\n"
             "assert sys.version_info >= (3, 8), sys.version\n"
             f"p={target!r}\n"
             "try: print(hashlib.sha256(open(p,'rb').read()).hexdigest())\n"
             "except OSError: print('none')\n")
    r = run_ssh([*loc.ssh_base(), "python3", "-c", shlex.quote(probe)], capture_output=True, text=True)
    if r.returncode != 0:
        die(f"ssh {loc.host} 에서 python3(3.8+) 실행 실패: {(r.stderr or r.stdout).strip()[-300:]}")
    if r.stdout.strip() != sha256_bytes(me):
        q = shlex.quote(target)
        cmd = f"mkdir -p {shlex.quote(os.path.dirname(target))} && cat > {q}.tmp && mv {q}.tmp {q}"
        r = run_ssh([*loc.ssh_base(), cmd], input=me, capture_output=True)
        if r.returncode != 0:
            die(f"원격에 kb.py 복사 실패: {r.stderr.decode(errors='replace').strip()[-300:]}")
    _pushed.add(loc.spec)


def call(loc: Loc, cmd: str, meta: dict, payload: bytes = b"") -> dict:
    data = json.dumps(meta, ensure_ascii=False).encode("utf-8") + b"\n" + payload
    if loc.kind == "local":
        argv = [sys.executable, SCRIPT, "store", cmd, "--root", loc.path]
    else:
        ensure_remote_script(loc)
        remote = f"python3 {shlex.quote(loc.path + '/.kb/bin/kb.py')} store {cmd} --root {shlex.quote(loc.path)}"
        argv = [*loc.ssh_base(), remote]
    r = (subprocess.run if loc.kind == "local" else run_ssh)(argv, input=data, capture_output=True)
    out = r.stdout.decode("utf-8", errors="replace").strip()
    try:
        res = json.loads(out.splitlines()[-1]) if out else {}
    except ValueError:
        res = {}
    if not res:
        die(f"store {cmd} 실패: {r.stderr.decode(errors='replace').strip()[-400:] or out[-400:]}")
    if res.get("status") == "error":
        die(res["error"])
    return res


def normalize_remote(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if "://" in url:
        u = urlparse(url)
        host, path = (u.hostname or "").lower(), u.path
    else:
        m = re.match(r"^(?:[^@]+@)?([^:]+):(.*)$", url)
        if not m:
            return url
        host, path = m.group(1).lower(), m.group(2)
    path = path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return f"{host}/{path}" if host else path


def host_name():
    return socket.gethostname().split(".")[0]


def ident(cwd: str) -> dict:
    top = git_top(cwd)
    if not top:
        top = os.path.realpath(cwd)
        main, remote, branch = top, "", ""
    else:
        top = os.path.realpath(top)
        common = git(["rev-parse", "--git-common-dir"], top) or ".git"
        common = os.path.realpath(common if os.path.isabs(common) else os.path.join(top, common))
        main = os.path.dirname(common) if os.path.basename(common) == ".git" else common
        remote = normalize_remote(git(["remote", "get-url", "origin"], top) or "")
        branch = git(["branch", "--show-current"], top) or ""
    host = host_name()
    parts = remote.split("/") if remote else []
    devlog = os.path.join(top, "docs", "devlog")
    projects = sorted(d for d in os.listdir(devlog)
                      if os.path.isdir(os.path.join(devlog, d)) and not d.startswith((".", "_"))) \
        if os.path.isdir(devlog) else []
    return {
        "kind": "repos" if remote else "topics",
        "name": parts[-1] if parts else os.path.basename(main),
        "org": parts[-2] if len(parts) >= 2 else "",
        "remote": remote, "top": top, "main_checkout": main, "branch": branch, "host": host,
        "at": f"{host}:{top}", "access": f"ssh://{getpass.getuser()}@{host}",
        "devlog": devlog, "projects": projects,
    }


def select_files(projdir: str):
    inc, exc = [], []
    for dp, dns, fns in os.walk(projdir):
        dns[:] = sorted(d for d in dns if not d.startswith("."))
        for fn in sorted(fns):
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, projdir)
            ext = os.path.splitext(fn)[1].lower()
            if fn.startswith("."):
                exc.append((rel, "dotfile"))
                continue
            if os.path.islink(full) or not os.path.isfile(full):
                exc.append((rel, "not-regular"))
                continue
            size = os.path.getsize(full)
            if ext == ".html":
                if size > HTML_MAX:
                    exc.append((rel, "html>1MB"))
                    continue
                data = open(full, "rb").read()
                if b"data:image" in data:
                    exc.append((rel, "html-embedded-image"))
                    continue
            elif ext in TEXT_EXT:
                if size > TEXT_MAX:
                    exc.append((rel, "text>512KB"))
                    continue
                data = open(full, "rb").read()
            else:
                exc.append((rel, f"binary{ext or ''}"))
                continue
            inc.append({"path": rel, "sha256": sha256_bytes(data), "size": size, "abs": full})
    return inc, exc


def parse_card(text: str) -> dict:
    """Read the `kb:` block of README frontmatter. Handles exactly the shapes the
    devlog template writes: scalars, [inline, lists] and >- / | folded blocks."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    lines = m.group(1).splitlines()
    try:
        i = next(k for k, ln in enumerate(lines) if ln.rstrip() == "kb:")
    except StopIteration:
        return {}
    card, k = {}, i + 1
    while k < len(lines):
        ln = lines[k]
        if ln and not ln.startswith(" "):
            break
        mm = re.match(r"^\s+([A-Za-z_]+):\s*(.*?)\s*(?:#.*)?$", ln)
        if not mm:
            k += 1
            continue
        key, val = mm.group(1), mm.group(2)
        if val in (">-", ">", "|", "|-"):
            block = []
            k += 1
            while k < len(lines) and (lines[k].startswith("    ") or not lines[k].strip()):
                block.append(lines[k].strip())
                k += 1
            card[key] = (" " if val.startswith(">") else "\n").join(b for b in block if b)
            continue
        if val.startswith("[") and val.endswith("]"):
            card[key] = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
        else:
            card[key] = val.strip("'\"")
        k += 1
    return card


def parse_readme(projdir: str) -> dict:
    try:
        text = open(os.path.join(projdir, "README.md"), encoding="utf-8").read()
    except OSError:
        return {"card": {}, "title": "", "period": "", "open_items": []}
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), "")
    pm = re.search(r"\*\*Period\*\*:\s*(.+)", text)
    sec = re.search(r"^##\s*Remaining\s*/\s*Next.*?$(.*?)(?=^##\s|<!--\s*/AUTO-GENERATED|\Z)", text, re.S | re.M | re.I)
    items = []
    if sec:
        # ~~struck~~ items are done; their tag must not count as open.
        items = [ln.strip() for ln in sec.group(1).splitlines()
                 if re.search(r"\[(critical|high)\]", re.sub(r"~~.*?~~", "", ln), re.I)][:10]
    return {"card": parse_card(text), "title": title, "period": pm.group(1).strip() if pm else "",
            "open_items": items}


def make_tar(files) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for f in files:
            tf.add(f["abs"], arcname=f["path"], recursive=False)
    return buf.getvalue()


def summarize_excluded(exc):
    by = {}
    for rel, why in exc:
        by.setdefault(why, []).append(rel)
    return by


def upload_one(loc, idt, kind, name, p, take_over=False, dry_run=False, yes=False):
    pdir = os.path.join(idt["devlog"], p)
    inc, exc = select_files(pdir)
    rd = parse_readme(pdir)
    co = {"at": idt["at"], "host": idt["host"], "path": idt["top"], "branch": idt["branch"], "access": idt["access"]}
    meta = {"kind": kind, "name": name, "project": p, "remote": idt["remote"] if kind == "repos" else "",
            "checkout": co, "files": [{k: f[k] for k in ("path", "sha256", "size")} for f in inc],
            "take_over": take_over, "dry_run": dry_run, "yes": yes,
            "card": rd["card"], "title": rd["title"], "period": rd["period"], "open_items": rd["open_items"]}
    return call(loc, "upload", meta, b"" if dry_run else make_tar(inc)), inc, exc


def cmd_upload(a):
    loc = resolve_loc(a.kb)
    idt = ident(os.getcwd())
    if not os.path.isdir(idt["devlog"]):
        die(f"devlog 가 없다: {idt['devlog']}")
    if a.topic:
        kind, name = "topics", a.topic
    elif idt["kind"] == "topics":
        die(f"origin remote 가 없는 checkout 이다. --topic <이름> 을 정해서 다시 실행한다 (제안: {idt['name']})")
    else:
        kind, name = "repos", a.as_name or idt["name"]
    projects = idt["projects"] if a.all else [a.project] if a.project else []
    if not projects:
        die("올릴 프로젝트를 지정한다: <project> 또는 --all")
    rc = 0
    for p in projects:
        if not os.path.isdir(os.path.join(idt["devlog"], p)):
            print(f"[{p}] 없음: {os.path.join(idt['devlog'], p)}")
            rc = 1
            continue
        res, inc, exc = upload_one(loc, idt, kind, name, p, take_over=a.take_over, dry_run=a.dry_run, yes=a.yes)
        print(render_upload(p, res, inc, exc, a.verbose))
        if res["status"] not in ("ok", "dry-run", "same-as-owner"):
            rc = 2
    if rc == 0 and not a.dry_run:
        print(f"KB: {loc}  (git 이면 그쪽에서 커밋: git -C {loc.path} add -A && git -C {loc.path} commit -m 'kb: upload')")
    return rc


def render_upload(p, res, inc, exc, verbose):
    st = res["status"]
    out = [f"[{p}] {st}  {res.get('id', '')}"]
    if st == "repo-collision":
        out.append(f"  기존 remote {res['existing_remote']} ≠ 이 checkout {res['remote']}. {res['hint']}")
        return "\n".join(out)
    if st in ("conflict", "same-as-owner"):
        out.append(f"  소유 checkout: {res['owner']}")
        if st == "same-as-owner":
            out.append("  이 사본은 소유 checkout과 내용이 같다. 쓸 것이 없다")
            return "\n".join(out)
        for k, label in (("only_source", "이 사본에만"), ("differ", "내용 다름"), ("only_kb", "KB에만")):
            v = res.get(k, [])
            out.append(f"  {label} {len(v)}개" + (": " + ", ".join(v[:8]) + (" …" if len(v) > 8 else "") if v else ""))
        out.append("  아무것도 쓰지 않았다. 이 사본을 정본으로 하려면 --take-over, 아니면 그대로 둔다")
        return "\n".join(out)
    w, dl = res.get("write", []), res.get("delete", [])
    out.append(f"  포함 {len(inc)}개 · 쓸 것 {len(w)} · 지울 것 {len(dl)} · 그대로 {res.get('unchanged', 0)}")
    if res.get("owner_before") and res.get("displaced") is not None:
        out.append(f"  소유자 변경: {res['owner_before']} → 이 checkout. 밀려난 파일 {len(res['displaced'])}개: "
                   + ", ".join(res["displaced"][:8]))
    if dl:
        out.append("  지울 파일: " + ", ".join(dl[:10]) + (" …" if len(dl) > 10 else ""))
    if st == "needs-confirm":
        out.append("  KB에서 지울 파일이 있어 멈췄다. 목록을 확인하고 --yes 로 다시 실행한다")
    if exc:
        by = summarize_excluded(exc)
        out.append("  제외: " + ", ".join(f"{why} {len(v)}" for why, v in sorted(by.items())))
        if verbose:
            for why, v in sorted(by.items()):
                out.append(f"    {why}: " + ", ".join(v[:10]) + (" …" if len(v) > 10 else ""))
    if verbose and w:
        out.append("  쓸 파일: " + ", ".join(w[:15]) + (" …" if len(w) > 15 else ""))
    return "\n".join(out)


def cmd_init(a):
    if not a.location and not default_spec():
        die("KB 위치를 지정한다: kb.py init <로컬 경로 | ssh://user@host/abs/path>")
    loc = Loc(a.location or default_spec(), "argument" if a.location else "built-in default")
    tmpl = os.path.join(os.path.dirname(SCRIPT), "..", "templates", "KB.md")
    kb_md = open(tmpl, encoding="utf-8").read() if os.path.isfile(tmpl) else "# KB\n"
    if loc.kind == "local":
        os.makedirs(loc.path, exist_ok=True)
    res = call(loc, "init", {"kb_md": kb_md})
    print(f"KB {'생성' if res['created'] else '확인'}: {loc}  (python {res['python']})")
    if res["legacy_projects"]:
        print(f"기존 projects/ 레이아웃 발견: {', '.join(res['legacy_projects'])}. 새 구조(repos/, topics/)로 옮길지 사용자에게 확인한다")
    if not a.no_save:
        os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
        write_atomic(CONFIG, loc.spec if loc.kind == "ssh" else loc.path)
        print(f"이 머신의 기본 KB로 저장: {CONFIG}")
    return 0


def cmd_where(a):
    loc = resolve_loc(a.kb)
    print(f"{loc}  (출처: {loc.source})")
    if a.configured and loc.source.startswith("built-in default"):
        return 1
    return 0


def cmd_ident(a):
    print(json.dumps(ident(a.path or os.getcwd()), ensure_ascii=False, indent=1))
    return 0


def cmd_search(a):
    loc = resolve_loc(a.kb)
    res = call(loc, "search", {"patterns": a.patterns, "scope": a.scope or "", "include_all": a.all,
                               "max_per_file": a.per_file, "max_total": a.max})
    for h in res["hits"]:
        print(f"{h['file']}:{h['line']}: {h['text']}")
    print(f"-- 파일 {res['files']}개 일치" + (" (일부만 표시. --scope 로 좁힌다)" if res["truncated"] else ""))
    if res["files"] > 1:
        print("-- 일치 수 상위 파일: " + ", ".join(f"{t['file']}({t['hits']})" for t in res.get("top_files", [])))
    return 0


def cmd_cat(a):
    loc = resolve_loc(a.kb)
    res = call(loc, "cat", {"path": a.path})
    if "files" in res:
        print("\n".join(res["files"]))
    else:
        sys.stdout.write(res["text"])
    return 0


def checkin_stamp(at: str) -> str:
    base = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "vh1981", "kb-checkin")
    return os.path.join(base, hashlib.sha256(at.encode()).hexdigest()[:16])


def cmd_checkin(a):
    """SessionStart check-in: register this checkout and upload the devlog projects it owns.
    Runs in the background, once per checkout per day. Never asks: conflicts and
    deletions are skipped (they need a human), so a check-in cannot overwrite or remove."""
    if os.environ.get("VH1981_KB_CHECKIN", "1") == "0":
        return 0
    loc = _resolve(a.kb)
    if loc is None or (loc.source.startswith("built-in default") and not a.force):
        return 0                      # only machines that ran `kb init` (or set VH1981_KB)
    loc.localize()
    idt = ident(os.getcwd())
    if not idt["projects"]:
        return 0
    today = datetime.now().strftime("%Y-%m-%d")
    stamp = checkin_stamp(idt["at"])
    try:
        if not a.force and open(stamp).read().strip() == today:
            return 0
    except OSError:
        pass
    kind, name = ("repos", idt["name"]) if idt["kind"] == "repos" else ("topics", idt["name"])
    if kind == "topics":              # reuse the topic this checkout was registered under
        for r in call(loc, "registry", {})["registries"]:
            if r["id"].startswith("topics/") and any(c.get("at") == idt["at"] for c in r["checkouts"]):
                name = r["id"].split("/", 1)[1]
                break
    call(loc, "register", {"kind": kind, "name": name, **({"remote": idt["remote"]} if idt["remote"] else {}),
                           "checkout": {"at": idt["at"], "branch": idt["branch"], "last_seen": now_iso(),
                                        "devlog_projects": idt["projects"]}})
    results = []
    for p in idt["projects"]:
        try:
            res, _, _ = upload_one(loc, idt, kind, name, p)
            results.append(f"{p}={res['status']}")
        except SystemExit:
            results.append(f"{p}=error")
    os.makedirs(os.path.dirname(stamp), exist_ok=True)
    write_atomic(stamp, today + "\n")
    print(f"{now_iso()} checkin {kind}/{name} {idt['at']} " + " ".join(results))
    return 0


def collect_local(top, since, until):
    """What happened in one checkout between since and until (inclusive, local dates):
    dated devlog entries, devlog files modified, and the checkout owner's git commits."""
    top = os.path.realpath(top)
    idt = ident(top)
    projects = [(p, os.path.join(idt["devlog"], p)) for p in idt["projects"]]
    entries = scan_log(projects, since, until)[:300]
    modified = []
    for pid, pdir in projects:
        for dp, dns, fns in os.walk(pdir):
            dns[:] = [d for d in dns if not d.startswith(".")]
            for fn in fns:
                if fn.endswith(".md"):
                    d = datetime.fromtimestamp(os.path.getmtime(os.path.join(dp, fn))).strftime("%Y-%m-%d")
                    if since <= d <= until:
                        modified.append({"project": pid, "file": os.path.relpath(os.path.join(dp, fn), pdir), "date": d})
    commits = []
    email = git(["config", "user.email"], top) or ""
    if git(["rev-parse", "--git-dir"], top):
        out = git(["log", "--all", f"--since={since} 00:00:00", f"--until={until} 23:59:59",
                   *([f"--author={email}"] if email else []), "--no-merges",
                   "--date=format:%Y-%m-%d %H:%M", "--format=%h%x09%ad%x09%s"], top) or ""
        for ln in out.splitlines()[:200]:
            h, _, rest = ln.partition("\t")
            d, _, subj = rest.partition("\t")
            commits.append({"sha": h, "date": d, "subject": subj})
    return {"at": idt["at"], "branch": idt["branch"], "entries": entries,
            "modified": sorted(modified, key=lambda m: (m["date"], m["project"], m["file"]))[:200],
            "commits": commits, "author": email}


def cmd_collect_local(a):
    print(json.dumps(collect_local(a.path, a.since, a.until), ensure_ascii=False))
    return 0


def cmd_collect(a):
    """Crawl every registered checkout for a period. Live data where the KB host can
    reach the checkout (this machine, or its ssh access); otherwise the KB copy."""
    loc = resolve_loc(a.kb)
    since, until = a.since, a.until or a.since
    regs = call(loc, "registry", {})["registries"]
    me = host_name()
    script = open(SCRIPT, "rb").read() if SCRIPT else b""
    out = {"since": since, "until": until, "generated": now_iso(), "kb": str(loc), "checkouts": []}
    for r in regs:
        for c in r["checkouts"]:
            host, _, path = c["at"].partition(":")
            row = {"source_id": r["id"], "repo_work": r.get("work", ""), "at": c["at"], "branch": c.get("branch", ""),
                   "work": c.get("work", ""), "projects": c.get("projects", []), "copies": c.get("copies", []),
                   "last_seen": c.get("last_seen", ""), "last_upload": c.get("last_upload", "")}
            data, err = None, ""
            if host == me and os.path.isdir(path):
                data, row["via"] = collect_local(path, since, until), "live-local"
            elif (c.get("access") or "").startswith("ssh://") and script:
                l2 = Loc(c["access"].rstrip("/") + "/")
                rr = run_ssh([*l2.ssh_base(), "python3 - collect-local " + shlex.quote(path)
                              + f" --since {since} --until {until}"], input=script, capture_output=True)
                try:
                    data, row["via"] = json.loads(rr.stdout.decode("utf-8")), "live-ssh"
                except ValueError:
                    err = (rr.stderr.decode(errors="replace") or "no output").strip()[-200:]
            if data is None:
                row["via"] = "kb-copy"
                if err:
                    row["error"] = err
                ents = []
                for p in c.get("projects", []):
                    ents += call(loc, "log", {"since": since, "until": until, "scope": f"{r['id']}/{p}"})["entries"]
                data = {"entries": ents, "modified": [], "commits": []}
            row.update({k: data.get(k, []) for k in ("entries", "modified", "commits")})
            if data.get("author"):
                row["author"] = data["author"]
            row["active"] = bool(row["entries"] or row["modified"] or row["commits"])
            out["checkouts"].append(row)
    out["checkouts"].sort(key=lambda x: (not x["active"], x["source_id"], x["at"]))
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if a.out:
        write_atomic(a.out, text + "\n")
        act = [x for x in out["checkouts"] if x["active"]]
        print(f"{a.out}: checkout {len(out['checkouts'])}개 중 활동 {len(act)}개 · "
              + ", ".join(f"{short_at(x['at'])}({x['via']}: 항목 {len(x['entries'])}, 수정 {len(x['modified'])}, 커밋 {len(x['commits'])})"
                          for x in act))
    else:
        print(text)
    return 0


def cmd_log(a):
    if a.local:
        idt = ident(os.getcwd())
        projects = [(p, os.path.join(idt["devlog"], p)) for p in idt["projects"]
                    if not a.scope or p.startswith(a.scope)]
        entries = scan_log(projects, a.since, a.until, a.loose)
    else:
        entries = call(resolve_loc(a.kb), "log", {"since": a.since, "until": a.until,
                                                  "scope": a.scope or "", "loose": a.loose})["entries"]
    if a.json:
        print(json.dumps(entries, ensure_ascii=False, indent=1))
        return 0
    last = None
    for e in entries:
        if e["date"] != last:
            print(f"\n## {e['date']}")
            last = e["date"]
        print(f"- `{e['id']}` · {e['kind']} · {e['file']}:{e['line']} · {e['text']}")
    kinds = {}
    for e in entries:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(f"\n-- {len(entries)}건 ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items())) or '없음'})"
          f" · 기간 {a.since or '처음'} ~ {a.until or '지금'}")
    return 0


def cmd_status(a):
    loc = resolve_loc(a.kb)
    sys.stdout.write(call(loc, "cat", {"path": "NOW.md"})["text"])
    return 0


def cmd_check(a):
    loc = resolve_loc(a.kb)
    issues = call(loc, "check", {})["issues"]
    if not issues:
        print("문제 없음")
    for i in issues:
        rest = {k: v for k, v in i.items() if k != "kind"}
        print(f"- {i['kind']}: {json.dumps(rest, ensure_ascii=False)}")
    return 0


def cmd_register(a):
    loc = resolve_loc(a.kb)
    idt = ident(os.getcwd())
    kind = "topics" if a.topic else idt["kind"]
    name = a.topic or a.as_name or idt["name"]
    meta = {"kind": kind, "name": name}
    if a.work is not None:
        meta["work"] = a.work
    if a.domains is not None:
        meta["domains"] = [d.strip() for d in a.domains.split(",") if d.strip()]
    if kind == "repos" and idt["remote"]:
        meta["remote"] = idt["remote"]
    co = {"at": idt["at"], "branch": idt["branch"]}
    if a.checkout_work is not None:
        co["work"] = a.checkout_work
    if a.access is not None:
        co["access"] = a.access
    meta["checkout"] = co
    reg = call(loc, "register", meta)["registry"]
    print(json.dumps(reg, ensure_ascii=False, indent=1))
    return 0


def cmd_fetch(a):
    loc = resolve_loc(a.kb)
    kind, _, name = a.source.partition("/") if "/" in a.source else ("repos", "", a.source)
    reg = call(loc, "registry", {"kind": kind, "name": name})["registry"]
    cos = [c for c in reg["checkouts"]
           if not a.project or a.project in c.get("projects", []) + c.get("copies", [])]
    if not cos:
        die(f"{kind}/{name} 에 {a.project or ''} 를 가진 checkout 이 등록돼 있지 않다")
    me = host_name()
    for c in cos:
        host, _, path = c["at"].partition(":")
        sub = os.path.join(path, "docs", "devlog", a.project or "")
        target = os.path.join(sub, a.file) if a.file else sub
        print(f"=== {c['at']} (branch {c.get('branch') or '-'}, access {c.get('access') or '-'})")
        if a.file:
            sh = f"cat {shlex.quote(target)}"
        else:
            sh = (f"cd {shlex.quote(sub)} && find . -name '*.md' -not -path './history/*' | sort && echo && "
                  f"( [ -f README.md ] && cat README.md || true )")
        if host == me and os.path.isdir(path):
            r = subprocess.run(["sh", "-c", sh], capture_output=True, text=True)
        else:
            acc = c.get("access") or ""
            if not acc.startswith("ssh://"):
                print(f"  접속 방법이 없다. `kb.py register --access ssh://user@host` 로 등록한다")
                continue
            l2 = Loc(acc.rstrip("/") + "/")
            r = run_ssh([*l2.ssh_base(), sh], capture_output=True, text=True)
        sys.stdout.write(r.stdout if r.returncode == 0 else f"  실패: {r.stderr.strip()[-300:]}\n")
    return 0


def cmd_survey(a):
    """Group every devlog project under the given workspace dirs by KB id.
    Used before the first bulk upload to pick an owner among diverged copies."""
    groups = {}
    for base in a.dirs:
        base = os.path.realpath(os.path.expanduser(base))
        cands = [base] + [os.path.join(base, d) for d in sorted(os.listdir(base))
                          if os.path.isdir(os.path.join(base, d, "docs", "devlog"))]
        for top in cands:
            if not os.path.isdir(os.path.join(top, "docs", "devlog")):
                continue
            idt = ident(top)
            for p in idt["projects"]:
                pdir = os.path.join(idt["devlog"], p)
                mds = [os.path.join(dp, f) for dp, _, fs in os.walk(pdir) for f in fs if f.endswith(".md")]
                newest = max((os.path.getmtime(m) for m in mds), default=0)
                rd = ""
                try:
                    rd = sha256_bytes(open(os.path.join(pdir, "README.md"), "rb").read())[:8]
                except OSError:
                    pass
                groups.setdefault(f"{idt['kind']}/{idt['name']}/{p}", []).append(
                    {"at": idt["at"], "branch": idt["branch"], "md": len(mds),
                     "newest": datetime.fromtimestamp(newest).strftime("%Y-%m-%d %H:%M") if newest else "-",
                     "readme": rd})
    for gid in sorted(groups, key=lambda g: (-len(groups[g]), g)):
        cs = groups[gid]
        print(f"{gid}" + (f"   ← 사본 {len(cs)}개" if len(cs) > 1 else ""))
        for c in sorted(cs, key=lambda c: c["newest"], reverse=True):
            print(f"    {c['at']}  branch={c['branch'] or '-'}  md={c['md']}  newest={c['newest']}  README={c['readme'] or '-'}")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "store":
        return store_main(argv[1:])
    ap = argparse.ArgumentParser(prog="kb.py", description="devlog knowledge base")
    ap.add_argument("--kb", help="KB 위치: 로컬 경로 또는 ssh://user@host/abs/path")
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("init", help="KB를 만들고 이 머신의 기본 KB로 저장")
    p.add_argument("location", nargs="?", help="생략하면 VH1981_KB_DEFAULT")
    p.add_argument("--no-save", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sp.add_parser("where", help="해석된 KB 위치와 그 출처")
    p.add_argument("--configured", action="store_true",
                   help="기본값만 있고 이 머신에서 정한 위치가 없으면 종료 코드 1")
    p.set_defaults(fn=cmd_where)

    p = sp.add_parser("ident", help="checkout 식별 정보(JSON)")
    p.add_argument("path", nargs="?")
    p.set_defaults(fn=cmd_ident)

    p = sp.add_parser("upload", help="devlog 프로젝트 업로드")
    p.add_argument("project", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--topic")
    p.add_argument("--as", dest="as_name")
    p.add_argument("--take-over", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true", help="KB에서 지울 파일이 있어도 진행")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(fn=cmd_upload)

    p = sp.add_parser("search", help="KB 본문 검색 (정규식, 대소문자 무시, 여러 개는 OR)")
    p.add_argument("patterns", nargs="+")
    p.add_argument("--scope", help="경로 접두어. 예: repos/<repo>/<project>")
    p.add_argument("--all", action="store_true", help="history/, rejected/, _archived/ 포함")
    p.add_argument("--per-file", type=int, default=2)
    p.add_argument("--max", type=int, default=40)
    p.set_defaults(fn=cmd_search)

    p = sp.add_parser("cat", help="KB 문서 읽기. 디렉토리면 파일 목록")
    p.add_argument("path")
    p.set_defaults(fn=cmd_cat)

    p = sp.add_parser("checkin", help="SessionStart 용: 이 checkout 등록 + 소유 devlog 업로드 (하루 1회)")
    p.add_argument("--force", action="store_true", help="오늘 이미 했어도, 기본값 KB여도 실행")
    p.set_defaults(fn=cmd_checkin)

    p = sp.add_parser("collect", help="등록된 모든 checkout 에서 기간의 작업 수집(JSON). daily/weekly log 재료")
    p.add_argument("--since", required=True)
    p.add_argument("--until")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_collect)

    p = sp.add_parser("collect-local", help="(내부용) 한 checkout 의 기간 작업 JSON")
    p.add_argument("path")
    p.add_argument("--since", required=True)
    p.add_argument("--until", required=True)
    p.set_defaults(fn=cmd_collect_local)

    p = sp.add_parser("log", help="기간 안에 날짜가 붙은 devlog 항목 뽑기 (작업 기록)")
    p.add_argument("--since", help="YYYY-MM-DD (포함)")
    p.add_argument("--until", help="YYYY-MM-DD (포함)")
    p.add_argument("--scope", help="KB ID 접두어, --local 이면 프로젝트 이름 접두어")
    p.add_argument("--local", action="store_true", help="KB 대신 현재 checkout 의 docs/devlog")
    p.add_argument("--loose", action="store_true", help="날짜 규칙 이전 문서용: 날짜가 든 모든 bullet")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_log)

    sp.add_parser("status", help="NOW.md 출력").set_defaults(fn=cmd_status)
    sp.add_parser("check", help="KB 점검").set_defaults(fn=cmd_check)

    p = sp.add_parser("register", help="현재 checkout 의 등록 정보 수정")
    p.add_argument("--topic")
    p.add_argument("--as", dest="as_name")
    p.add_argument("--work")
    p.add_argument("--domains", help="쉼표로 구분")
    p.add_argument("--checkout-work")
    p.add_argument("--access", help="ssh://user@host")
    p.set_defaults(fn=cmd_register)

    p = sp.add_parser("fetch", help="등록된 checkout 에서 최신 devlog 읽기")
    p.add_argument("source", help="<repo> 또는 repos/<repo> 또는 topics/<topic>")
    p.add_argument("project", nargs="?")
    p.add_argument("--file")
    p.set_defaults(fn=cmd_fetch)

    p = sp.add_parser("survey", help="작업 디렉토리들의 devlog 사본을 KB ID로 묶어 비교")
    p.add_argument("dirs", nargs="+")
    p.set_defaults(fn=cmd_survey)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
