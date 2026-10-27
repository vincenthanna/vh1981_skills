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

Discovery is re-run on a timer, so a new report appears without a restart. The tree
usually sits on NFS, so a file is read again only when its mtime or size changed.

Usage:
  serve_devlog.py --root docs/devlog [--port 8800] [--host 0.0.0.0] [--include-personal]
"""
from __future__ import annotations

import argparse
import html as H
import json
import re
import socketserver
import threading
import time
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path

HEAD_BYTES = 16384          # enough for <title>, and bounded for a 20 MB file
CHUNK = 1 << 18
KST = timezone(timedelta(hours=9))
WEEKDAY = '월화수목금토일'
CAL_WEEKS = (8, 16)            # min, max columns
LOG_GROUPS = (('daily', 'Daily log', 'reports/daily'), ('techdocs', 'Tech docs', 'reports/techdocs'),
              ('weekly', 'Weekly log', 'reports/weekly'))
OPEN_ROWS = {'daily': 7, 'techdocs': 8, 'weekly': 6}
# A renamed subset of Pretendard (OFL, see fonts/OFL.txt), served from a fixed path
# so pages need no external font host. Without the file the system stack is used.
FONT = Path(__file__).resolve().parent / 'fonts' / 'KBSans-Variable.woff2'
FONT_URL = '/f/kb-sans.woff2'

_memo: dict = {}


def _cached(fn, p: Path, st=None):
    """fn(p), recomputed only when p's mtime or size changed."""
    try:
        st = st or p.stat()
    except OSError:
        return fn(p)
    key, sig = (fn.__name__, str(p)), (st.st_mtime_ns, st.st_size)
    hit = _memo.get(key)
    if hit and hit[0] == sig:
        return hit[1]
    val = fn(p)
    _memo[key] = (sig, val)
    return val


def _text(s: str) -> str:
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def _head(p: Path) -> dict:
    """Title, plus a one-paragraph lede: a log page's `.lede`, or a tech doc's question."""
    try:
        head = p.read_bytes()[:HEAD_BYTES].decode('utf-8', 'replace')
    except OSError:
        return {'title': p.stem, 'lede': ''}
    title = p.stem
    for pat in (r'<title[^>]*>(.*?)</title>', r'<h1[^>]*>(.*?)</h1>'):
        if (m := re.search(pat, head, re.S | re.I)) and (t := _text(m.group(1))):
            title = t
            break
    lede = ''
    if m := re.search(r'<p[^>]*class="[^"]*\blede\b[^"]*"[^>]*>(.*?)</p>', head, re.S | re.I):
        lede = _text(m.group(1))
    elif m := re.search(r'질문:\s*[“"](.+?)[”"]', _text(head)):
        lede = m.group(1)
    return {'title': title, 'lede': lede[:600]}


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


def _rows(gid: str, base: Path, files, newest_first: bool = False, by_mtime: bool = False) -> list:
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
            'imgs': _cached(_has_personal, f, st), **_cached(_head, f, st),
        }
    rows = []
    for stem, d in docs.items():
        v = d['variants'].get('plain') or d['variants'].get('artifact')
        num = (m.group(1) if (m := re.match(r'^(\d+)', Path(stem).name)) else '')
        rows.append({
            'id': f'{gid}/{stem}', 'stem': stem, 'num': '' if newest_first else num,
            'title': v['title'], 'lede': v['lede'], 'size': v['size'], 'mtime': v['mtime'],
            'imgs': v['imgs'], 'path': v['path'],
            'also': sorted(k for k in d['variants'] if d['variants'][k] is not v),
        })
    if by_mtime:                # tech docs: most recently (re)written first
        return sorted(rows, key=lambda r: r['mtime'], reverse=True)
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
        for _, label, sub in LOG_GROUPS:
            d = root / sub
            if d.is_dir():
                rows = _rows(sub, d, sorted(d.glob('*.html')), newest_first=True,
                             by_mtime=sub == 'reports/techdocs')
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


INDEX_LINE = re.compile(r'^- `([^`]+)` · ([^·]+?) · ([^·]*?) · (\S+) · ([^·]*?) · (.*)$')


def _cards(p: Path) -> dict:
    """Project cards from the KB's INDEX.md: {id: {status, tags, uploaded, summary}}."""
    out = {}
    try:
        lines = p.read_text(encoding='utf-8').splitlines()
    except OSError:
        return out
    for line in lines:
        if m := INDEX_LINE.match(line):
            tags = [] if m.group(3).strip() in ('', '-') else [t.strip() for t in m.group(3).split(',')]
            out[m.group(1)] = {'status': m.group(2).strip().rstrip('*'), 'tags': tags,
                               'uploaded': m.group(4), 'summary': m.group(6).strip()}
    return out


def _activity(p: Path):
    """Projects with dated entries in one daily collect file, deduplicated across copies.

    Entry ids are full KB ids or bare project names depending on the checkout, so the
    last path segment is the key; this matches the daily page's project count."""
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    names = {str(e.get('id', '')).rsplit('/', 1)[-1]
             for c in data.get('checkouts', []) for e in c.get('entries', [])}
    names.discard('')
    return len(names)


def load_meta(root: Path) -> dict:
    if not is_kb(root):
        return {'cards': {}, 'activity': {}}
    data = root / 'reports' / '.data'
    activity = {}
    if data.is_dir():
        for f in data.glob('daily-*.json'):
            n = _cached(_activity, f)
            if n is not None:
                activity[f.stem[len('daily-'):]] = n
    return {'cards': _cached(_cards, root / 'INDEX.md'), 'activity': activity}


def human(n: int) -> str:
    for u in ('B', 'KB', 'MB'):
        if n < 1024 or u == 'MB':
            return f'{n:.0f}{u}' if u == 'B' else f'{n:.1f}{u}'
        n /= 1024
    return f'{n:.1f}MB'


def _iso(s: str):
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


_DARK = """--bg:#111318;--surface:#191c22;--ink:#e5e8ed;--mut:#a9b0bb;--faint:#8e96a3;--line:#2a2f38;--hover:#20242c;
 --accent:#7ea8f3;--accent-soft:#1c2740;--focus:#9bbcf7;--mark:#5c4a12;--mark-ink:#f5efd8;
 --ok:#62c08b;--hold:#e3b45b;--stop:#f08a7e;
 --c0:#21252d;--c1:#1d3157;--c2:#24498a;--c3:#3a6cc4;--c4:#6a9cf0;--c5:#a9c8fa;
 --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 18px rgba(0,0,0,.25);color-scheme:dark"""

INDEX_CSS = """
/* Layout: one 960px column; a sticky search bar, an overview (latest pages + activity
   calendar), then lists. Cards only mark the three entry points and projects.
   Type scale 12.5 / 14 / 15 / 16 / 20 / 32 px: nothing a reader needs is below 12.5,
   and every text colour clears 4.5:1 on both surfaces. */
:root{
 --bg:#f4f6f9;--surface:#fff;--ink:#141820;--mut:#545c69;--faint:#636b78;--line:#dde2e9;--hover:#eaeff6;
 --accent:#2759c4;--accent-soft:#e6eefb;--focus:#2759c4;--mark:#fde68a;--mark-ink:#141820;
 --ok:#1f7346;--hold:#8a5a00;--stop:#b3342a;
 --c0:#e7eaef;--c1:#d3e2fa;--c2:#9fbff0;--c3:#5f92e0;--c4:#2f68c9;--c5:#1a4795;
 --shadow:0 1px 2px rgba(20,24,32,.06),0 6px 18px rgba(20,24,32,.07);
 --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
 --sans:"KB Sans",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Segoe UI",Roboto,"Noto Sans KR","Malgun Gothic",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){{dark}}}
:root[data-theme="dark"]{{dark}}
*{box-sizing:border-box}
[hidden]{display:none!important}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 var(--sans);word-break:keep-all;
 overflow-wrap:break-word;-webkit-font-smoothing:antialiased;-webkit-text-size-adjust:100%}
.wrap{max-width:960px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));
 padding-right:max(16px,env(safe-area-inset-right,0px));padding-bottom:96px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline;text-underline-offset:3px}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px;border-radius:6px}
header{padding-block:44px 18px}
h1{font-size:clamp(26px,4vw,32px);line-height:1.2;margin:0 0 8px;letter-spacing:-.025em;font-weight:750;text-wrap:balance}
.sub{color:var(--mut);font-size:14px;margin:0;font-variant-numeric:tabular-nums}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);padding-block:12px;
 border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center}
.search{order:1;flex:1 1 280px;min-width:0;display:flex;align-items:center;gap:10px;background:var(--surface);
 border:1px solid var(--line);border-radius:12px;padding:0 12px 0 14px;min-height:46px}
.search:focus-within{border-color:var(--focus);box-shadow:0 0 0 3px var(--accent-soft)}
.search>svg{flex:none;color:var(--mut)}
.search input{flex:1;min-width:0;border:0;background:transparent;color:var(--ink);font:inherit;font-size:16px;
 padding:10px 0;outline:none}
.search input::placeholder{color:var(--faint)}
.search kbd{font:12.5px/1.5 var(--mono);color:var(--mut);border:1px solid var(--line);border-bottom-width:2px;
 border-radius:6px;padding:0 6px;white-space:nowrap}
.jump{order:2;display:flex;gap:2px;font-size:14px}
.jump a{color:var(--mut);padding:9px 10px;border-radius:8px;white-space:nowrap}
.jump a:hover{color:var(--ink);background:var(--hover);text-decoration:none}
.jump b{font-weight:500;color:var(--faint);font-variant-numeric:tabular-nums;margin-left:5px}
.theme{order:3;flex:none;width:46px;height:46px;display:grid;place-items:center;border:1px solid var(--line);
 border-radius:12px;background:var(--surface);color:var(--mut);cursor:pointer;padding:0}
.theme:hover{color:var(--ink);border-color:var(--mut)}
.theme svg{display:none}
.theme[data-mode="system"] .i-system,.theme[data-mode="light"] .i-light,.theme[data-mode="dark"] .i-dark{display:block}
.result{order:4;width:100%;font-size:14px;color:var(--mut);margin:0}
mark{background:var(--mark);color:var(--mark-ink);border-radius:3px;padding:0 1px}
.empty{margin-top:28px;padding:32px 20px;text-align:center;border:1px dashed var(--line);border-radius:14px;
 color:var(--mut);font-size:15px}
.empty p{margin:0 0 4px}.empty b{color:var(--ink)}
.empty button{margin-top:10px;font:inherit;font-size:15px;color:var(--accent);background:var(--surface);
 border:1px solid var(--line);border-radius:999px;padding:8px 18px;cursor:pointer}
.box{border:1px solid var(--line);border-left:3px solid var(--hold);background:var(--surface);
 border-radius:0 10px 10px 0;padding:12px 16px;margin:20px 0 0;font-size:14px}
.over{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:20px 32px;margin-top:26px;align-items:start}
.latest{display:grid;gap:10px;min-width:0}
.latest a{display:grid;gap:3px;background:var(--surface);border:1px solid var(--line);border-radius:14px;
 padding:14px 18px;color:var(--ink);min-width:0;transition:border-color .15s,box-shadow .15s,transform .15s}
.latest a:hover{border-color:var(--accent);box-shadow:var(--shadow);text-decoration:none}
.latest a:active{transform:translateY(1px)}
.latest .k{font-size:14px;font-weight:650;color:var(--accent);letter-spacing:.01em}
.latest .t{font-weight:650;font-size:17px;line-height:1.45;letter-spacing:-.01em}
.latest .x,.rows .x,details.proj .sm{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.latest .x{font-size:15px;line-height:1.65;color:var(--mut)}
.latest .w{font-size:14px;color:var(--faint);font-variant-numeric:tabular-nums}
.calbox{min-width:0}
.calbox h3{font-size:15px;font-weight:650;margin:0 0 10px}
.calscroll{overflow-x:auto;padding:3px}
.cal{display:grid;grid-template-columns:2.2em repeat(var(--weeks),24px);grid-auto-rows:24px;gap:3px;
 font-size:12.5px;color:var(--mut);width:max-content}
.cal .m{white-space:nowrap;line-height:24px}
.cal .d{line-height:24px}
.cal .c{border-radius:6px;background:var(--c0)}
.cal a.c:hover{outline:2px solid var(--ink);outline-offset:1px}
.cal .l1{background:var(--c1)}.cal .l2{background:var(--c2)}.cal .l3{background:var(--c3)}
.cal .l4{background:var(--c4)}.cal .l5{background:var(--c5)}
.cal .lx{background:var(--surface);box-shadow:inset 0 0 0 2px var(--c3)}
.cal .wk{background:var(--surface);box-shadow:inset 0 0 0 1px var(--line)}
.cal a.wk{background:var(--accent-soft);box-shadow:inset 0 0 0 2px var(--accent)}
.cal .gap{visibility:hidden}
.legend{display:flex;align-items:center;gap:4px;font-size:12.5px;color:var(--mut);margin-top:12px;flex-wrap:wrap}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px}
.legend span{margin:0 4px}
.calinfo{font-size:14px;margin:8px 0 0;min-height:1.7em;font-variant-numeric:tabular-nums}
section{margin-top:48px}
h2{font-size:20px;line-height:1.3;margin:0 0 8px;letter-spacing:-.015em;font-weight:750;display:flex;
 align-items:baseline;gap:10px;scroll-margin-top:90px}
h2 .c{color:var(--mut);font-weight:500;font-size:14px;font-variant-numeric:tabular-nums}
h2 .hint{color:var(--mut);font-weight:400;font-size:14px;margin-left:auto}
ul.rows{list-style:none;margin:0 -12px;padding:0}
.rows li{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 20px;padding:13px 12px;
 border-radius:10px;min-height:52px}
.rows li+li::before{content:"";position:absolute;left:12px;right:12px;top:0;border-top:1px solid var(--line)}
.rows li:hover{background:var(--hover)}
.rows li:hover::before,.rows li:hover+li::before{opacity:0}
.rows .t{min-width:0}
.rows .t b{font-weight:650}
.rows .t a{color:var(--ink);scroll-margin-block:110px 24px}
.rows .t a::after{content:"";position:absolute;inset:0;border-radius:10px}
.rows .t a:hover{text-decoration:none}
.rows li:hover .t a{color:var(--accent)}
.rows .t a:focus-visible{outline:none}
.rows .t a:focus-visible::after{outline:2px solid var(--focus);outline-offset:-2px}
.rows .x{font-size:15px;line-height:1.65;color:var(--mut);margin-top:3px;max-width:46em}
.rows .meta{display:block;font-size:14px;color:var(--mut);margin-top:3px}
.rows .w{font-size:14px;color:var(--mut);white-space:nowrap;font-variant-numeric:tabular-nums;text-align:right}
.rows .n{font:14px var(--mono);color:var(--faint);margin-right:10px}
.id{font-family:var(--mono);font-size:13.5px}
.pill{display:inline-block;font-size:12.5px;font-weight:650;line-height:1.6;border-radius:999px;padding:0 8px;
 border:1px solid currentColor;vertical-align:1px;margin-left:8px;white-space:nowrap}
.pill.active{color:var(--ok)}.pill.paused{color:var(--hold)}.pill.done{color:var(--mut)}.pill.lock{color:var(--stop)}
details.more>summary{cursor:pointer;color:var(--accent);font-size:15px;font-weight:500;padding:12px 0;min-height:48px;
 list-style:none;border-top:1px solid var(--line);display:flex;align-items:center;gap:10px}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::after,details.proj>summary .nm b::before{content:"";display:inline-block;width:7px;height:7px;
 border:solid currentColor;border-width:0 2px 2px 0;transform:rotate(45deg);transition:transform .15s}
details.more>summary::after{margin-top:-4px}
details.more[open]>summary{color:var(--mut)}
details.more[open]>summary::after{transform:rotate(-135deg);margin-top:4px}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 16px}
.filters button{font:inherit;font-size:14px;color:var(--mut);background:var(--surface);border:1px solid var(--line);
 border-radius:999px;padding:6px 16px;min-height:38px;cursor:pointer;font-variant-numeric:tabular-nums}
.filters button:hover{color:var(--ink);border-color:var(--mut)}
.filters button[aria-pressed="true"]{color:var(--bg);background:var(--ink);border-color:var(--ink);font-weight:650}
.projs{display:grid;gap:10px}
details.proj{background:var(--surface);border:1px solid var(--line);border-radius:14px;
 transition:border-color .15s,box-shadow .15s}
details.proj:hover,details.proj[open]{box-shadow:var(--shadow)}
details.proj>summary{cursor:pointer;list-style:none;padding:16px 20px;display:grid;
 grid-template-columns:minmax(0,1fr) auto;gap:4px 20px;border-radius:14px}
details.proj>summary::-webkit-details-marker{display:none}
details.proj>summary .nm{min-width:0;overflow-wrap:anywhere}
details.proj>summary .nm b{font-weight:650;font-size:17px;letter-spacing:-.01em}
details.proj>summary .nm b::before{color:var(--mut);margin:0 12px 3px 0;transform:rotate(-45deg)}
details.proj[open]>summary .nm b::before{transform:rotate(45deg)}
details.proj>summary .id{color:var(--faint);margin-left:8px}
details.proj>summary .w{font-size:14px;color:var(--mut);white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums}
details.proj .sm{grid-column:1/-1;font-size:15px;line-height:1.65;color:var(--mut);max-width:46em;padding-left:19px}
details.proj .tags{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:6px;padding-left:19px;margin-top:4px}
details.proj .tags span{font-size:12.5px;color:var(--mut);background:var(--bg);border:1px solid var(--line);
 border-radius:6px;padding:1px 8px}
details.proj .rows{margin:0;padding:6px 8px 10px 27px;border-top:1px solid var(--line)}
footer{margin-top:64px;padding-top:18px;border-top:1px solid var(--line);color:var(--mut);font-size:14px}
footer p{margin:4px 0}
code{font:13px var(--mono);background:var(--c0);padding:1px 6px;border-radius:5px}
@media (max-width:640px){
 header{padding-block:28px 12px}
 /* The section links sit above the search row and slide out while scrolling down;
    a transform, not display:none, so the page height and scroll position never move. */
 .bar{gap:6px 10px;padding-block:8px 10px;transition:transform .2s}
 .jump{order:0;width:100%;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin:0 -6px}
 .jump a{padding:6px 10px}
 .bar.min{transform:translateY(calc(-1 * var(--hide,0px)))}
 .jump::-webkit-scrollbar{display:none}
 .search kbd{display:none}
 .over{grid-template-columns:minmax(0,1fr)}
 h2 .hint{display:none}
 .rows li{gap:2px 12px}
 details.proj>summary{padding:14px 16px}
 details.proj .rows{padding-left:12px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
""".replace('{dark}', _DARK)

ICON_SEARCH = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>')
ICON_THEME = ''.join(
    f'<svg class="i-{k}" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>' for k, d in (
        ('system', '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>'),
        ('light', '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4'
                  'M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
        ('dark', '<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>')))

# Runs before first paint, so a stored theme never flashes the other one.
THEME_BOOT = ("<script>try{const t=localStorage.getItem('kb-theme');"
              "if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}catch(e){}</script>")

INDEX_JS = r"""
(()=>{
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const q=$('#q'),res=$('#res'),empty=$('#empty'),bar=$('.bar'),over=$('.over');
const leaves=$$('li[data-q]'),projs=$$('details.proj'),mores=$$('details.more'),secs=$$('section[data-sec]');
const hls=$$('.hl');let status='all',marked=false;
for(const el of hls)el.dataset.raw=el.textContent;
const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const hit=(s,terms)=>terms.every(t=>s.includes(t));
function mark(terms){
  if(!terms.length&&!marked)return;
  const re=terms.length?new RegExp('('+terms.map(t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|')+')','i'):null;
  for(const el of hls){
    if(!re){el.textContent=el.dataset.raw;continue;}
    el.innerHTML=el.dataset.raw.split(re).map((p,i)=>i%2?`<mark>${esc(p)}</mark>`:esc(p)).join('');}
  marked=!!re;
}
function apply(){
  const raw=q.value.trim(),terms=raw.toLowerCase().split(/\s+/).filter(Boolean),on=terms.length>0;
  for(const p of projs){
    const ok=status==='all'||p.dataset.status===status,card=p.dataset.card||'';
    let any=false;
    for(const li of p.querySelectorAll('li[data-q]')){
      const v=ok&&(!on||hit(li.dataset.q+' '+card,terms));li.hidden=!v;if(v)any=true;}
    p.hidden=!any;p.open=on&&any;
  }
  for(const li of leaves){if(li.closest('details.proj'))continue;li.hidden=on&&!hit(li.dataset.q,terms);}
  for(const m of mores)m.open=on&&!!m.querySelector('li[data-q]:not([hidden])');
  for(const s of secs){const v=s.querySelectorAll('li[data-q]:not([hidden])').length;s.hidden=on&&!v;}
  const n=leaves.filter(li=>!li.hidden&&!(li.closest('details.proj')||{}).hidden).length;
  const np=projs.filter(p=>!p.hidden).length;
  if(over)over.hidden=on;
  mark(terms);
  res.hidden=!on&&status==='all';
  res.textContent=on?`"${raw}" 검색 결과 보고서 ${n}개 (프로젝트 ${np}개)`+(n?' · ↓ 키로 결과 이동':'')
    :status!=='all'?`${status} 프로젝트 ${np}개 표시`:'';
  empty.hidden=n>0||(!on&&status==='all');
  $('#emptyq').textContent=raw?`"${raw}"와 일치하는 보고서가 없습니다.`:'조건에 맞는 보고서가 없습니다.';
}
q.addEventListener('input',apply);
$('#clear').addEventListener('click',()=>{q.value='';apply();q.focus();});
for(const b of $$('.filters button'))b.addEventListener('click',()=>{
  status=b.dataset.status;
  for(const x of $$('.filters button'))x.setAttribute('aria-pressed',x===b);
  apply();});
const visible=()=>$$('li[data-q] .t a').filter(a=>!a.closest('[hidden],details:not([open])'));
addEventListener('keydown',e=>{
  const k=e.key,a=document.activeElement,typing=a&&a.closest&&a.closest('input,textarea,select');
  if((k==='/'&&!typing&&!e.ctrlKey&&!e.metaKey)||((e.ctrlKey||e.metaKey)&&k.toLowerCase()==='k')){
    e.preventDefault();q.focus();q.select();return;}
  if(k==='Escape'&&a===q){q.value='';apply();q.blur();return;}
  if(k!=='ArrowDown'&&k!=='ArrowUp')return;
  const row=a&&a.closest&&a.closest('li[data-q]');
  if(a!==q&&!row)return;
  const L=visible();if(!L.length)return;
  e.preventDefault();
  if(a===q){if(k==='ArrowDown')L[0].focus();return;}
  const i=L.indexOf(row.querySelector('.t a'));
  (k==='ArrowDown'?L[i+1]||L[i]:i>0?L[i-1]:q).focus();
});
const rel=ts=>{const s=Date.now()/1000-ts;if(s<0)return null;if(s<60)return'방금';if(s<3600)return`${Math.floor(s/60)}분 전`;
  if(s<86400)return`${Math.floor(s/3600)}시간 전`;const d=Math.floor(s/86400);return d<7?`${d}일 전`:null;};
const times=()=>{for(const t of $$('time[data-ts]'))t.textContent=rel(+t.dataset.ts)||t.dataset.abs;};
times();setInterval(times,60000);
const tb=$('#theme'),modes=['system','light','dark'],names={system:'시스템 설정',light:'라이트',dark:'다크'};
let mode='system';try{mode=localStorage.getItem('kb-theme')||'system';}catch(e){}
function setMode(m){
  mode=modes.includes(m)?m:'system';tb.dataset.mode=mode;
  tb.title=`테마: ${names[mode]}`;tb.setAttribute('aria-label',`테마: ${names[mode]}, 누르면 바뀝니다`);
  if(mode==='system')delete document.documentElement.dataset.theme;else document.documentElement.dataset.theme=mode;
  try{mode==='system'?localStorage.removeItem('kb-theme'):localStorage.setItem('kb-theme',mode);}catch(e){}
}
setMode(mode);tb.addEventListener('click',()=>setMode(modes[(modes.indexOf(mode)+1)%3]));
const info=$('#calinfo');
if(info){const rest=info.textContent,cal=$('.cal'),cs=$('.calscroll');
  cs.scrollLeft=cs.scrollWidth;
  const show=e=>{const c=e.target.closest('[data-tip]');info.textContent=c?c.dataset.tip:rest;};
  cal.addEventListener('mouseover',show);cal.addEventListener('focusin',show);
  cal.addEventListener('mouseleave',()=>info.textContent=rest);cal.addEventListener('focusout',()=>info.textContent=rest);}
const narrow=matchMedia('(max-width:640px)'),srch=$('.search');let lastY=scrollY;
addEventListener('scroll',()=>{const y=scrollY;
  if(!narrow.matches||document.activeElement===q)bar.classList.remove('min');
  else if(y>lastY+4&&y>240){
    bar.style.setProperty('--hide',srch.offsetTop-6+'px');bar.classList.add('min');}
  else if(y<lastY-4)bar.classList.remove('min');
  lastY=y;},{passive:true});
})();
"""

DOC_NAV = """
<nav id="kbnav" aria-label="보고서 이동">{links}</nav>
<style>
#kbnav{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(14px + env(safe-area-inset-bottom,0px));
 z-index:2147483000;display:flex;gap:2px;padding:4px;border-radius:999px;background:rgba(20,24,32,.9);
 box-shadow:0 4px 18px rgba(0,0,0,.22);font:14px/1 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Segoe UI",Roboto,"Noto Sans KR",sans-serif;
 max-width:calc(100vw - 24px);white-space:nowrap}
#kbnav a,#kbnav span{padding:11px 15px;border-radius:999px;text-decoration:none;font-variant-numeric:tabular-nums}
#kbnav a{color:#f2f4f8}#kbnav span{color:rgba(242,244,248,.45)}
#kbnav a:hover,#kbnav a:focus-visible{background:rgba(255,255,255,.16);outline:none}
@media print{#kbnav{display:none}}
</style>
<script>addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest('input,textarea,select,[contenteditable]'))return;
const a=document.querySelector(e.key==='ArrowLeft'?'#kbnav a[rel=prev]':e.key==='ArrowRight'?'#kbnav a[rel=next]':'#kbnav-none');
if(a)location.href=a.href;});</script>
"""


def _short(stem: str) -> str:
    """Label for a neighbour link: 2026-10-26 -> 10-26, 2026-W43 -> W43."""
    return stem[5:] if re.match(r'^\d{4}-', stem) else stem[:24]


def doc_navs(tree: dict) -> dict:
    """{doc id: nav html} for pages under reports/, so every log page, old ones
    included, can step to its neighbours without being regenerated."""
    out = {}
    for key, label, _ in LOG_GROUPS:
        rows = tree.get(label, [])
        for i, d in enumerate(rows):
            links = []
            if key != 'techdocs':           # newest first: the older page is the next row
                old = rows[i + 1] if i + 1 < len(rows) else None
                new = rows[i - 1] if i > 0 else None
                links.append(f'<a rel="prev" href="/d/{H.escape(old["id"])}">← {H.escape(_short(old["stem"]))}</a>'
                             if old else '<span>←</span>')
            links.append(f'<a href="/#{key}">목록</a>')
            if key != 'techdocs':
                links.append(f'<a rel="next" href="/d/{H.escape(new["id"])}">{H.escape(_short(new["stem"]))} →</a>'
                             if new else '<span>→</span>')
            out[d['id']] = DOC_NAV.replace('{links}', ''.join(links)).encode()
    return out


def _time(ts: float, fmt: str = '%m-%d %H:%M') -> str:
    """Absolute KST time; the page script swaps in "3시간 전" for the last week."""
    dt = datetime.fromtimestamp(ts, KST)
    return (f'<time datetime="{dt.isoformat(timespec="minutes")}" data-ts="{int(ts)}" data-abs="{dt:{fmt}}" '
            f'title="{dt:%Y-%m-%d %H:%M} KST">{dt:{fmt}}</time>')


def _log_label(key: str, stem: str) -> str:
    """Reader-facing name for a log page: 2026-10-26 -> 10월 26일 (월), 2026-W43 -> W43 · 10월 20일 ~ 26일."""
    if key == 'daily' and (d := _iso(stem)):
        return f'{d.month}월 {d.day}일 ({WEEKDAY[d.weekday()]})'
    if key == 'weekly' and (m := re.match(r'^(\d{4})-W(\d{2})$', stem)):
        mon = date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
        sun = mon + timedelta(days=6)
        end = f'{sun.day}일' if sun.month == mon.month else f'{sun.month}월 {sun.day}일'
        return f'W{m.group(2)} · {mon.month}월 {mon.day}일 ~ {end}'
    return ''


def _doc_row(d: dict, include_personal: bool, meta: str = '', num: bool = False, label: str = '') -> str:
    locked = d['imgs'] and not include_personal
    title = f'<b class="hl">{H.escape(label or d["title"])[:200]}</b>'
    t = title if locked else f'<a href="/d/{H.escape(d["id"])}">{title}</a>'
    n = f'<span class="n">{H.escape(d["num"])}</span>' if num and d['num'] else ''
    extra = []
    if meta:
        extra.append(meta)
    if d['imgs']:
        extra.append(f'내장 이미지 {d["imgs"]}장')
    if d['also']:
        extra.append('artifact 사본 있음')
    lock = '<span class="pill lock">잠김</span>' if locked else ''
    lede = f'<span class="x hl">{H.escape(d["lede"])}</span>' if d.get('lede') else ''
    q = H.escape(f'{label} {d["title"]} {d["stem"]} {re.sub(r"<[^>]+>", " ", meta)} {d.get("lede", "")}'.lower())
    return (f'<li data-q="{q}"><span class="t">{n}{t}{lock}{lede}'
            + (f'<span class="meta">{" · ".join(extra)}</span>' if extra else '')
            + f'</span><span class="w">{_time(d["mtime"])}</span></li>')


def _list(rows_html: list, keep: int) -> str:
    head, rest = rows_html[:keep], rows_html[keep:]
    out = '<ul class="rows">' + ''.join(head) + '</ul>'
    if rest:
        out += (f'<details class="more"><summary>이전 {len(rest)}개 더 보기</summary>'
                f'<ul class="rows">{"".join(rest)}</ul></details>')
    return out


def _calendar(daily: list, weekly: list, activity: dict, today: date) -> str:
    pages = {d['stem']: d for d in daily}
    weeks = {d['stem']: d for d in weekly}
    this_mon = today - timedelta(days=today.weekday())
    first = min((d for d in map(_iso, pages) if d), default=today)
    n_weeks = max(CAL_WEEKS[0], min(CAL_WEEKS[1], (this_mon - first).days // 7 + 1))
    cols = [this_mon - timedelta(weeks=n_weeks - 1 - i) for i in range(n_weeks)]
    cells = ['<span></span>']
    prev_month = None
    for mon in cols:
        label = f'{mon.month}월' if mon.month != prev_month else ''
        prev_month = mon.month
        cells.append(f'<span class="m">{label}</span>')

    def level(n):
        return 0 if n == 0 else 1 if n == 1 else 2 if n <= 3 else 3 if n <= 6 else 4 if n <= 10 else 5

    for r in range(7):
        cells.append(f'<span class="d">{WEEKDAY[r] if r in (0, 2, 4) else ""}</span>')
        for mon in cols:
            day = mon + timedelta(days=r)
            if day > today:
                cells.append('<span class="gap"></span>')
                continue
            ds = day.isoformat()
            name = f'{ds} ({WEEKDAY[day.weekday()]})'
            page, n = pages.get(ds), activity.get(ds)
            if page is None:
                cells.append(f'<span class="c" data-tip="{name} · daily log 없음"></span>')
                continue
            cls, tip = ((f'l{level(n)}', f'{name} · 활동 프로젝트 {n}개') if n is not None
                        else ('lx', f'{name} · daily log 있음, 집계 파일 없음'))
            cells.append(f'<a class="c {cls}" href="/d/{H.escape(page["id"])}" data-tip="{tip}" '
                         f'aria-label="{tip}"></a>')
    cells.append('<span class="d">주</span>')
    for mon in cols:
        y, w, _ = mon.isocalendar()
        key = f'{y}-W{w:02d}'
        rng = f'{key} ({mon:%m-%d} ~ {mon + timedelta(days=6):%m-%d})'
        if key in weeks:
            cells.append(f'<a class="c wk" href="/d/{H.escape(weeks[key]["id"])}" data-tip="{rng} · weekly log" '
                         f'aria-label="{rng} weekly log"></a>')
        else:
            cells.append(f'<span class="c wk" data-tip="{rng} · weekly log 없음"></span>')
    latest = next((d for d in sorted(pages, reverse=True) if d in activity), None)
    rest = (f'최근 {latest} ({WEEKDAY[date.fromisoformat(latest).weekday()]}) · 활동 프로젝트 {activity[latest]}개'
            if latest else '칸에 마우스를 올리면 날짜와 활동이 보입니다')
    legend = ''.join(f'<i style="background:var(--c{i})"></i>' for i in range(6))
    return (f'<div class="calbox"><h3>최근 {n_weeks}주 활동</h3><div class="calscroll">'
            f'<div class="cal" style="--weeks:{n_weeks}" role="group" aria-label="일별 활동 달력">{"".join(cells)}</div></div>'
            f'<div class="legend"><span>프로젝트 0</span>{legend}<span>11+</span>'
            f'<span>· 칸을 누르면 daily log, 맨 아래 줄은 weekly log</span></div>'
            f'<p class="calinfo" id="calinfo" aria-live="polite">{H.escape(rest)}</p></div>')


def _project(gid: str, docs: list, card, include_personal: bool) -> str:
    kind, owner, name = (gid.split('/', 2) + ['', ''])[:3] if gid.count('/') == 2 else ('', '', gid)
    card = card or {}
    status = card.get('status', '')
    newest = max(docs, key=lambda d: d['mtime'])
    pill = f'<span class="pill {H.escape(status)}">{H.escape(status)}</span>' if status else ''
    tags = card.get('tags', [])
    tg = ('<span class="tags">' + ''.join(f'<span class="hl">{H.escape(t)}</span>' for t in tags[:5])
          + (f'<span>+{len(tags) - 5}</span>' if len(tags) > 5 else '') + '</span>') if tags else ''
    prefix = f'<span class="id hl">{H.escape(kind)}/{H.escape(owner)}</span>' if owner else ''
    sm = f'<span class="sm hl">{H.escape(card["summary"])}</span>' if card.get('summary') else ''
    cardq = H.escape(f'{gid} {status} {" ".join(tags)} {card.get("summary", "")}'.lower())
    rows = ''.join(_doc_row(d, include_personal, num=True) for d in docs)
    return (f'<details class="proj" data-status="{H.escape(status or "none")}" data-card="{cardq}">'
            f'<summary><span class="nm"><b class="hl">{H.escape(name)}</b>{prefix}{pill}</span>'
            f'<span class="w">보고서 {len(docs)} · {_time(newest["mtime"], "%Y-%m-%d")}</span>{sm}{tg}</summary>'
            f'<ul class="rows">{rows}</ul></details>')


def render_index(tree: dict, include_personal: bool, root: Path, meta: dict | None = None) -> bytes:
    meta = meta or {'cards': {}, 'activity': {}}
    kb = is_kb(root)
    cards, activity = meta['cards'], meta['activity']
    n_doc = sum(len(v) for v in tree.values())
    n_lock = sum(1 for v in tree.values() for d in v if d['imgs'] and not include_personal)
    now = datetime.now(KST)
    title = 'Knowledge base' if kb else 'devlog 보고서'
    logs = {key: tree.get(label, []) for key, label, _ in LOG_GROUPS} if kb else {}
    projects = {k: v for k, v in tree.items() if not kb or k not in {lbl for _, lbl, _ in LOG_GROUPS}}
    n_proj_docs = sum(len(v) for v in projects.values())

    counts = [f'보고서 {n_doc}개']
    if cards:
        counts.insert(0, f'프로젝트 {len(cards)}개')
    font = (f'<link rel="preload" href="{FONT_URL}" as="font" type="font/woff2" crossorigin>'
            f'<style>@font-face{{font-family:"KB Sans";src:url({FONT_URL}) format("woff2");'
            f'font-weight:45 930;font-display:swap}}</style>') if FONT.is_file() else ''
    parts = [f"""<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>{THEME_BOOT}{font}<style>{INDEX_CSS}</style><div class="wrap">
<header><h1>{title}</h1>
<p class="sub">{' · '.join(counts)} · {now:%Y-%m-%d %H:%M} KST 기준</p></header>"""]

    jump = [(k, lbl, len(logs[k])) for k, lbl, _ in LOG_GROUPS if logs.get(k)]
    if projects:
        jump.append(('projects', '프로젝트 보고서' if kb else '프로젝트', n_proj_docs))
    parts.append(f'<div class="bar"><label class="search" for="q">{ICON_SEARCH}'
                 '<input id="q" type="search" placeholder="제목, 프로젝트, 태그, 요약 검색" autocomplete="off" '
                 'aria-describedby="res" aria-keyshortcuts="/ Control+K"><kbd>/</kbd></label>'
                 '<nav class="jump" aria-label="섹션">'
                 + ''.join(f'<a href="#{k}">{lbl}<b>{n}</b></a>' for k, lbl, n in jump)
                 + f'</nav><button class="theme" id="theme" type="button" data-mode="system">{ICON_THEME}</button>'
                 '<p class="result" id="res" aria-live="polite" hidden></p></div>'
                 '<div class="empty" id="empty" hidden><p><b id="emptyq"></b></p>'
                 '<p>단어 수를 줄이거나 프로젝트 이름, 태그로 찾아 보세요.</p>'
                 '<button type="button" id="clear">검색 지우기</button></div>')

    if n_lock:
        parts.append(f"""<div class="box"><b>잠긴 문서 {n_lock}건</b>은 본문에 이미지가 내장돼 있어 목록에만 보입니다.
 열려면 서버를 <code>--include-personal</code> 로 다시 띄웁니다.</div>""")

    if kb and any(logs.values()):
        latest = []
        for key, label, _ in LOG_GROUPS:
            if logs[key]:
                d = logs[key][0]
                x = f'<span class="x">{H.escape(d["lede"])}</span>' if d.get('lede') else ''
                latest.append(f'<a href="/d/{H.escape(d["id"])}"><span class="k">최신 {label}</span>'
                              f'<span class="t">{H.escape(_log_label(key, d["stem"]) or d["title"])}</span>{x}'
                              f'<span class="w">{_time(d["mtime"], "%Y-%m-%d %H:%M")}</span></a>')
        parts.append(f'<div class="over"><div class="latest">{"".join(latest)}</div>'
                     f'{_calendar(logs["daily"], logs["weekly"], activity, now.date())}</div>')

    for key, label, _ in LOG_GROUPS:
        rows = logs.get(key, [])
        if not rows:
            continue
        html_rows = []
        for d in rows:
            if key == 'daily':
                n = activity.get(d['stem'])
                m = f'활동 프로젝트 {n}개' if n is not None else ''
            elif key == 'weekly':
                m = ''
            else:
                pid = d['stem'].replace('__', '/')
                st = cards.get(pid, {}).get('status', '')
                m = f'<span class="id hl">{H.escape(pid)}</span>' + (
                    f'<span class="pill {H.escape(st)}">{H.escape(st)}</span>' if st else '')
            html_rows.append(_doc_row(d, include_personal, meta=m, label=_log_label(key, d['stem'])))
        hint = '수정 시각순' if key == 'techdocs' else '최신순'
        parts.append(f'<section id="{key}" data-sec><h2>{label}<span class="c">{len(rows)}개</span>'
                     f'<span class="hint">{hint}</span></h2>{_list(html_rows, OPEN_ROWS[key])}</section>')

    if projects:
        order = sorted(projects, key=lambda g: max(d['mtime'] for d in projects[g]), reverse=True)
        stats: dict[str, int] = {}
        for g in order:
            s = cards.get(g, {}).get('status')
            if s:
                stats[s] = stats.get(s, 0) + 1
        filt = ''
        if stats:
            btn = [('all', '전체', len(order))] + [(s, s, stats[s]) for s in ('active', 'paused', 'done') if s in stats]
            filt = ('<div class="filters" role="group" aria-label="상태 필터">'
                    + ''.join(f'<button type="button" data-status="{s}" aria-pressed="{str(s == "all").lower()}">'
                              f'{lbl} {n}</button>' for s, lbl, n in btn) + '</div>')
        heading = '프로젝트 보고서' if kb else '프로젝트'
        parts.append(f'<section id="projects" data-sec><h2>{heading}<span class="c">프로젝트 {len(order)}개 · '
                     f'보고서 {n_proj_docs}개</span><span class="hint">최근 갱신순</span></h2>{filt}<div class="projs">'
                     + ''.join(_project(g, projects[g], cards.get(g), include_personal) for g in order)
                     + '</div></section>')

    parts.append(f"""<footer>
<p>경로가 아니라 허용 목록으로만 서빙합니다. 요청 경로는 파일 시스템에 닿지 않으므로 이 트리에 파일을 추가해도 공개되지 않습니다.</p>
<p>루트 <code>{H.escape(str(root))}</code> · <code>/healthz</code> 로 상태 확인 · 단축키 <code>/</code> 또는 <code>Ctrl K</code> 검색, <code>↑</code> <code>↓</code> 결과 이동</p></footer>
</div><script>{INDEX_JS}</script></html>""")
    return ''.join(parts).encode()


class State:
    def __init__(self, root: Path, include_personal: bool, interval: int = 60):
        self.root, self.include_personal, self.interval = root, include_personal, interval
        self.lock = threading.Lock()
        self.font = FONT.read_bytes() if FONT.is_file() else b''
        self.refresh()
        threading.Thread(target=self._loop, daemon=True).start()

    def refresh(self):
        tree = scan(self.root)
        index = render_index(tree, self.include_personal, self.root, load_meta(self.root))
        allow = {d['id']: d for v in tree.values() for d in v
                 if self.include_personal or not d['imgs']}
        navs = doc_navs(tree) if is_kb(self.root) else {}
        with self.lock:
            self.tree, self.index, self.allow, self.navs = tree, index, allow, navs

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
            print(f'{datetime.now(KST):%H:%M:%S} KST {self.client_address[0]} {fmt % a}',
                  flush=True)

        def _hdr(self, code, ctype, length, cache='no-store'):
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(length))
            self.send_header('Cache-Control', cache)
            self.end_headers()

        def do_GET(self):
            path = self.path.split('?', 1)[0]
            with state.lock:
                index, allow, navs = state.index, state.allow, state.navs
            if path == '/healthz':
                return self._hdr(200, 'text/plain', 4) or self.wfile.write(b'ok\n\n'[:4])
            if path == FONT_URL and state.font:
                self._hdr(200, 'font/woff2', len(state.font), 'public, max-age=604800')
                return self.wfile.write(state.font)
            if path in ('/', '/index.html'):
                self._hdr(200, 'text/html; charset=utf-8', len(index))
                return self.wfile.write(index)
            if path.startswith('/d/'):
                # the id is a dict key, never a path: an unknown id is simply absent
                doc = allow.get(path[3:])
                if doc is None:
                    b = b'<!doctype html><meta charset=utf-8><p>No such document. <a href="/">Back to the index</a></p>'
                    self._hdr(404, 'text/html; charset=utf-8', len(b))
                    return self.wfile.write(b)
                p, nav = doc['path'], navs.get(doc['id'], b'')
                try:
                    size = p.stat().st_size
                    self._hdr(200, 'text/html; charset=utf-8', size + len(nav))
                    with open(p, 'rb') as f:            # streamed: these reach 20 MB
                        while chunk := f.read(CHUNK):
                            self.wfile.write(chunk)
                    self.wfile.write(nav)
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
