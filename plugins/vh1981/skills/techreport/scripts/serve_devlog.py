#!/usr/bin/env python3
"""Serve the devlog's HTML reports, grouped by topic, from one always-on port.

Two things this must never do, both learned from what sits in that tree:

* **Never serve a path the caller supplies.** `docs/devlog/**` can hold data files,
  logs and images of private individuals (CCTV crops, panel sheets). A static file
  server rooted there would publish them, and would publish anything added later. So the
  server builds an **allowlist of .html documents** at scan time and addresses them by
  an opaque id; no request path ever reaches the filesystem.
* **Never publish embedded personal imagery by accident.** A report that inlines
  images as base64 `data:` URIs is detected at scan time and **locked by default**;
  `--include-personal` opens it deliberately.

Discovery is re-run on a timer, so a new report appears without a restart.

Usage:
  serve_devlog.py --root docs/devlog [--port 8800] [--host 0.0.0.0] [--include-personal]
"""
from __future__ import annotations

import argparse
import html as H
import re
import socketserver
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path

HEAD_BYTES = 16384          # enough for <title>, and bounded for a 20 MB file
CHUNK = 1 << 18


def _title(p: Path) -> str:
    try:
        head = p.read_bytes()[:HEAD_BYTES].decode('utf-8', 'replace')
    except OSError:
        return p.stem
    for pat in (r'<title[^>]*>(.*?)</title>', r'<h1[^>]*>(.*?)</h1>'):
        m = re.search(pat, head, re.S | re.I)
        if m:
            t = re.sub(r'<[^>]+>', '', m.group(1))
            t = re.sub(r'\s+', ' ', t).strip()
            if t:
                return t
    return p.stem


def _has_personal(p: Path) -> int:
    """Count inlined raster images (data: URIs), e.g. embedded CCTV crops."""
    n = 0
    try:
        with open(p, 'rb') as f:
            while chunk := f.read(CHUNK):
                n += chunk.count(b'data:image')
    except OSError:
        return 0
    return n


def _rows(gid: str, base: Path, files, newest_first: bool = False) -> list:
    docs: dict[str, dict] = {}
    for f in files:
        rel = f.relative_to(base)
        # `X.artifact.html` is the published twin of `X.html`; collapse to one row.
        stem = str(rel)[:-len('.artifact.html')] if str(rel).endswith('.artifact.html') \
            else str(rel)[:-len('.html')]
        st = f.stat()
        d = docs.setdefault(stem, {'stem': stem, 'variants': {}})
        d['variants']['artifact' if str(rel).endswith('.artifact.html') else 'plain'] = {
            'path': f, 'size': st.st_size, 'mtime': st.st_mtime,
            'imgs': _has_personal(f), 'title': _title(f),
        }
    rows = []
    for stem, d in docs.items():
        v = d['variants'].get('plain') or d['variants'].get('artifact')
        num = (m.group(1) if (m := re.match(r'^(\d+)', Path(stem).name)) else '')
        rows.append({
            'id': f'{gid}/{stem}', 'stem': stem, 'num': '' if newest_first else num,
            'title': v['title'], 'size': v['size'], 'mtime': v['mtime'],
            'imgs': v['imgs'], 'path': v['path'],
            'also': sorted(k for k in d['variants'] if d['variants'][k] is not v),
        })
    if newest_first:            # log pages are named by date: newest first
        return sorted(rows, key=lambda r: r['stem'], reverse=True)
    return sorted(rows, key=lambda r: (r['num'] == '', r['num'], r['stem']))


def is_kb(root: Path) -> bool:
    return (root / 'KB.md').is_file() and (root / '.kb').is_dir()


def scan(root: Path) -> dict:
    """Build {group: [doc, ...]} from .html files only.

    A devlog root groups by project (two levels deep). A knowledge-base root
    (has KB.md) lists the daily and weekly logs newest first, then each KB
    project's reports."""
    out: dict[str, list[dict]] = {}
    if is_kb(root):
        for label, sub in (('Daily log', 'reports/daily'), ('Weekly log', 'reports/weekly')):
            d = root / sub
            if d.is_dir():
                rows = _rows(sub, d, sorted(d.glob('*.html')), newest_first=True)
                if rows:
                    out[label] = rows
        for kind in ('repos', 'topics'):
            for proj in sorted(p for p in (root / kind).glob('*/*') if p.is_dir()):
                files = sorted(p for p in proj.rglob('*.html')
                               if not any(x.startswith('.') for x in p.relative_to(proj).parts))
                gid = f'{kind}/{proj.parent.name}/{proj.name}'
                rows = _rows(gid, proj, files)
                if rows:
                    out[gid] = rows
        return out
    for proj in sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith('_')):
        rows = _rows(proj.name, proj, sorted(proj.glob('*.html')) + sorted(proj.glob('*/*.html')))
        if rows:
            out[proj.name] = rows
    return out


def human(n: int) -> str:
    for u in ('B', 'KB', 'MB'):
        if n < 1024 or u == 'MB':
            return f'{n:.0f}{u}' if u == 'B' else f'{n:.1f}{u}'
        n /= 1024
    return f'{n:.1f}MB'


INDEX_CSS = """
:root{--bg:#faf9f7;--card:#fff;--ink:#1a1a1c;--mut:#6b6b72;--line:#e3e0da;--blue:#2f6fd0;--red:#cf4a3e;--amber:#c88a1e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#16161a;--card:#1e1e24;--ink:#e9e8e4;--mut:#9b9aa3;--line:#32323a;--blue:#74a6f0;--red:#f08478;--amber:#e8b85a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR",sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:0 20px 80px}
header{padding:48px 0 20px;border-bottom:1px solid var(--line)}
h1{font-size:clamp(23px,3.6vw,32px);margin:0 0 8px;letter-spacing:-.02em}
.sub{color:var(--mut);font-size:14px;margin:0}
h2{font-size:19px;margin:40px 0 4px;letter-spacing:-.01em}
h2 .c{color:var(--mut);font-weight:400;font-size:14px;margin-left:8px}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
.doc{display:flex;gap:14px;align-items:baseline;padding:11px 14px;border:1px solid var(--line);
 border-radius:10px;background:var(--card);margin:8px 0}
.doc .num{font-variant-numeric:tabular-nums;color:var(--mut);font-size:13px;min-width:2.2em}
.doc .t{flex:1;min-width:0}
.doc .t b{font-weight:600}
.doc .m{color:var(--mut);font-size:12.5px;margin-top:2px;display:block}
.doc .s{color:var(--mut);font-size:12.5px;white-space:nowrap;font-variant-numeric:tabular-nums}
.doc.locked{opacity:.72;border-style:dashed}
.lock{color:var(--red);font-size:12px;font-weight:700}
.box{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--amber);
 border-radius:0 10px 10px 0;padding:12px 16px;margin:22px 0;font-size:14px}
.box b{color:var(--ink)}
code{font:12.5px ui-monospace,Menlo,Consolas,monospace;background:color-mix(in srgb,var(--ink) 8%,transparent);
 padding:1px 5px;border-radius:4px}
footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);color:var(--mut);font-size:13px}
@media(max-width:560px){.doc{flex-wrap:wrap}.doc .s{width:100%}}
"""


def render_index(tree: dict, include_personal: bool, root: Path) -> bytes:
    n_doc = sum(len(v) for v in tree.values())
    n_lock = sum(1 for v in tree.values() for d in v if d['imgs'] and not include_personal)
    title = 'knowledge base — daily · weekly log' if is_kb(root) else 'devlog 보고서'
    parts = [f"""<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title><style>{INDEX_CSS}</style><div class="wrap">
<header><h1>{title}</h1>
<p class="sub">{len(tree)}개 주제 · 문서 {n_doc}개 ·
 <span style="font-variant-numeric:tabular-nums">{datetime.now(timezone.utc):%Y-%m-%d %H:%MZ}</span> 기준</p></header>"""]

    if n_lock:
        parts.append(f"""<div class="box"><b>잠긴 문서 {n_lock}건</b> — 본문에 이미지가 내장돼 있어
 기본값으로 막아 두었습니다. 열려면 서버를 <code>--include-personal</code> 로 다시 띄우세요.</div>""")

    for proj, docs in tree.items():
        parts.append(f'<h2>{H.escape(proj)}<span class="c">문서 {len(docs)}개</span></h2>')
        for d in docs:
            locked = d['imgs'] and not include_personal
            when = datetime.fromtimestamp(d['mtime'], timezone.utc).strftime('%Y-%m-%d')
            meta = f"{H.escape(d['stem'])}"
            if d['imgs']:
                meta += f' · 내장 이미지 {d["imgs"]}장'
            if d['also']:
                meta += ' · artifact 사본 있음'
            title = H.escape(d['title'])[:160]
            body = (f'<b>{title}</b>' if locked else
                    f'<a href="/d/{H.escape(d["id"])}"><b>{title}</b></a>')
            parts.append(
                f'<div class="doc{" locked" if locked else ""}">'
                f'<span class="num">{H.escape(d["num"]) or "—"}</span>'
                f'<span class="t">{body}<span class="m">{meta}</span></span>'
                f'<span class="s">{"<span class=lock>잠김</span> · " if locked else ""}'
                f'{human(d["size"])} · {when}</span></div>')

    parts.append(f"""<footer>
<p>경로가 아니라 <b>허용 목록</b>으로만 서빙합니다 — 요청 경로는 파일 시스템에 닿지 않으므로
 이 트리에 파일을 추가해도 공개되지 않습니다.</p>
<p>루트 <code>{H.escape(str(root))}</code> · <code>/healthz</code> 로 상태 확인</p></footer>
</div></html>""")
    return ''.join(parts).encode()


class State:
    def __init__(self, root: Path, include_personal: bool, interval: int = 60):
        self.root, self.include_personal, self.interval = root, include_personal, interval
        self.lock = threading.Lock()
        self.refresh()
        threading.Thread(target=self._loop, daemon=True).start()

    def refresh(self):
        tree = scan(self.root)
        index = render_index(tree, self.include_personal, self.root)
        allow = {d['id']: d for v in tree.values() for d in v
                 if self.include_personal or not d['imgs']}
        with self.lock:
            self.tree, self.index, self.allow = tree, index, allow

    def _loop(self):
        while True:
            time.sleep(self.interval)
            try:
                self.refresh()
            except Exception as e:                      # a bad file must not kill the server
                print(f'rescan failed: {type(e).__name__}: {e}', flush=True)


def make(state: State):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, fmt, *a):
            print(f'{datetime.now(timezone.utc):%H:%M:%SZ} {self.client_address[0]} {fmt % a}',
                  flush=True)

        def _hdr(self, code, ctype, length):
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(length))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()

        def do_GET(self):
            path = self.path.split('?', 1)[0]
            with state.lock:
                index, allow = state.index, state.allow
            if path == '/healthz':
                return self._hdr(200, 'text/plain', 4) or self.wfile.write(b'ok\n\n'[:4])
            if path in ('/', '/index.html'):
                self._hdr(200, 'text/html; charset=utf-8', len(index))
                return self.wfile.write(index)
            if path.startswith('/d/'):
                # the id is a dict key, never a path: an unknown id is simply absent
                doc = allow.get(path[3:])
                if doc is None:
                    b = b'<!doctype html><meta charset=utf-8><p>No such document.</p>'
                    self._hdr(404, 'text/html; charset=utf-8', len(b))
                    return self.wfile.write(b)
                p = doc['path']
                try:
                    size = p.stat().st_size
                    self._hdr(200, 'text/html; charset=utf-8', size)
                    with open(p, 'rb') as f:            # streamed: these reach 20 MB
                        while chunk := f.read(CHUNK):
                            self.wfile.write(chunk)
                except (OSError, BrokenPipeError, ConnectionResetError):
                    pass
                return
            self.send_response(302)
            self.send_header('Location', '/')
            self.send_header('Content-Length', '0')
            self.end_headers()
    return Handler


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', required=True, help='devlog root, e.g. docs/devlog')
    ap.add_argument('--port', type=int, default=8800)
    ap.add_argument('--host', default='0.0.0.0')
    ap.add_argument('--include-personal', action='store_true',
                    help='also serve reports that inline images (locked by default)')
    ap.add_argument('--rescan', type=int, default=60, help='seconds between rescans')
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not root.is_dir():
        raise SystemExit(f'not a directory: {root}')
    st = State(root, a.include_personal, a.rescan)
    n = sum(len(v) for v in st.tree.values())
    print(f'devlog: {len(st.tree)} topics, {n} documents, '
          f'{len(st.allow)} served ({n - len(st.allow)} locked)', flush=True)
    for proj, docs in st.tree.items():
        print(f'  {proj}: ' + ', '.join(d['stem'] + ('*' if d['imgs'] else '') for d in docs),
              flush=True)
    print(f'serving on http://{a.host}:{a.port}/  (rescan {a.rescan}s)', flush=True)
    try:
        Server((a.host, a.port), make(st)).serve_forever()
    except KeyboardInterrupt:
        print('\nstopped')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
