#!/usr/bin/env python3
"""Draw a tree (directories, call trees, outlines) as a PNG or SVG image.

Text trees drawn with box characters or indentation are banned by
guidelines/output-principles.md. Where mermaid does not render (terminal,
chat), draw the tree with this script and show the image instead.

    draw-tree.py OUT.png [INPUT] [--root NAME]

INPUT (default stdin) holds one path per line, e.g. `docs/devlog/README.md`.
A trailing `/` marks a directory; a note may follow after two spaces and `#`
(`a/b.md  # index`). Blank lines and lines starting with `#` are skipped.
Hangul renders with the KB Sans font shipped with techreport, converted once
to a cached TTF (needs fontTools).
"""
import argparse
import os
import sys
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

FS = 10            # label font size, pt
ROW = 0.36         # row height, inch
BOX_H = 0.26       # box height, inch
PAD = 0.12         # text padding inside a box, inch
GAP = 0.45         # gap between columns, room for the connector spine
WOFF2 = Path(__file__).resolve().parent.parent / "skills/techreport/scripts/fonts/KBSans-Variable.woff2"


class Node:
    def __init__(self, name, is_dir=False):
        self.name, self.is_dir, self.note = name, is_dir, ""
        self.children, self.x, self.y, self.w = [], 0.0, 0.0, 0.0


def text_w(s, fs=FS):
    """Approximate text width in inches."""
    pt = sum(fs if unicodedata.east_asian_width(c) in ("W", "F") else 0.62 * fs for c in s)
    return pt / 72


def font():
    cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "vh1981" / "fonts" / "KBSans.ttf"
    try:
        if not cache.exists():
            from fontTools.ttLib import TTFont
            cache.parent.mkdir(parents=True, exist_ok=True)
            f = TTFont(str(WOFF2))
            f.flavor = None
            tmp = cache.with_suffix(".tmp")
            f.save(str(tmp))
            os.replace(tmp, cache)
        fm.fontManager.addfont(str(cache))
        return fm.FontProperties(fname=str(cache))
    except Exception as e:
        print(f"warning: KB Sans unavailable ({e}); Hangul may not render", file=sys.stderr)
        return fm.FontProperties()


def parse(lines, root_name):
    items = []
    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        path, _, note = line.partition("  #")
        path = path.strip()
        if path:
            items.append((path, note.strip()))
    if not items:
        return None
    firsts = {p.strip("/").split("/")[0] for p, _ in items}
    strip_first = root_name is None and len(firsts) == 1 and all("/" in p.strip("/") for p, _ in items)
    root = Node(root_name or (firsts.pop() if strip_first else "."), True)
    for path, note in items:
        parts = [x for x in path.strip("/").split("/") if x]
        if strip_first:
            parts = parts[1:]
        node = root
        for i, part in enumerate(parts):
            last = i == len(parts) - 1
            child = next((c for c in node.children if c.name == part), None)
            if child is None:
                child = Node(part)
                node.children.append(child)
            if not last or path.endswith("/"):
                child.is_dir = True
            node = child
        if note:
            node.note = note
    return root


def layout(root):
    nodes, cols, row = [], [], [0]

    def walk(n, depth):
        nodes.append((n, depth))
        n.w = text_w(n.name) + 2 * PAD
        if len(cols) <= depth:
            cols.append(0.0)
        cols[depth] = max(cols[depth], n.w)
        if n.children:
            n.is_dir = True
            for c in n.children:
                walk(c, depth + 1)
            n.y = (n.children[0].y + n.children[-1].y) / 2
        else:
            n.y = row[0] * ROW
            row[0] += 1

    walk(root, 0)
    xs = [0.0]
    for w in cols[:-1]:
        xs.append(xs[-1] + w + GAP)
    for n, d in nodes:
        n.x = xs[d]
    return [n for n, _ in nodes], row[0]


def draw(root, out):
    prop = font()
    nodes, rows = layout(root)
    right = max(n.x + n.w + (0.1 + text_w(n.note, FS - 1) if n.note else 0) for n in nodes)
    height = max(rows, 1) * ROW
    fig = plt.figure(figsize=(right + 0.4, height + 0.3))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.2, right + 0.2)
    ax.set_ylim(height - ROW / 2 + 0.15, -ROW / 2 - 0.15)
    ax.axis("off")
    for n in nodes:
        for c in n.children:
            x0, spine = n.x + n.w, c.x - GAP / 2
            ax.plot([x0, spine, spine, c.x], [n.y, n.y, c.y, c.y], color="#6b7280", lw=1, zorder=1)
    for n in nodes:
        face, edge = ("#dbeafe", "#3b82f6") if n.is_dir else ("#ffffff", "#9ca3af")
        ax.add_patch(FancyBboxPatch((n.x, n.y - BOX_H / 2), n.w, BOX_H, boxstyle="round,pad=0,rounding_size=0.05",
                                    facecolor=face, edgecolor=edge, lw=1, zorder=2))
        ax.text(n.x + n.w / 2, n.y, n.name, ha="center", va="center", fontproperties=prop, fontsize=FS, zorder=3)
        if n.note:
            ax.text(n.x + n.w + 0.1, n.y, n.note, ha="left", va="center", color="#6b7280",
                    fontproperties=prop, fontsize=FS - 1, zorder=3)
    fig.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", help="output image, .png or .svg")
    ap.add_argument("input", nargs="?", help="path list (default: stdin)")
    ap.add_argument("--root", help="root label (default: the shared first component, else '.')")
    a = ap.parse_args()
    lines = open(a.input, encoding="utf-8").readlines() if a.input else sys.stdin.readlines()
    root = parse(lines, a.root)
    if root is None:
        sys.exit("draw-tree: no paths in input")
    draw(root, a.out)
    print(a.out)


if __name__ == "__main__":
    main()
