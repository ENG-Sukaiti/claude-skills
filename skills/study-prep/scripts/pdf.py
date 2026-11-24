# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.24"]
# ///
"""PDF helper, same on macOS and Linux (no poppler or other system tools).

    sh scripts/run pdf.py text <file.pdf> [--pages 1-3]
        the text layer, page by page. Empty pages = a scan: render them and look.
    sh scripts/run pdf.py info <file.pdf>
        page count, author, creator, creation/modification dates, and how
        many pages have a text layer
    sh scripts/run pdf.py render <file.pdf> --to <dir> [--pages 1-3] [--dpi 110]
        each page as a PNG (page-001.png ...), for reading scans and photos
"""

import argparse
from pathlib import Path

import pymupdf


def page_list(spec, n):
    if not spec:
        return list(range(n))
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += range(int(a) - 1, min(int(b or a), n))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("text", "info", "render"):
        sp = sub.add_parser(name)
        sp.add_argument("file")
        sp.add_argument("--pages", help="e.g. 1-3,7 (1-based)")
        if name == "render":
            sp.add_argument("--to", required=True)
            sp.add_argument("--dpi", type=int, default=110)
    a = p.parse_args()
    doc = pymupdf.open(a.file)

    if a.cmd == "info":
        m = doc.metadata or {}
        texty = sum(1 for pg in doc if pg.get_text().strip())
        print(f"pages: {doc.page_count} ({texty} with a text layer)")
        for k in ("title", "author", "creator", "producer", "creationDate", "modDate"):
            if m.get(k):
                print(f"{k}: {m[k]}")
    elif a.cmd == "text":
        for i in page_list(a.pages, doc.page_count):
            print(f"===== page {i + 1}")
            print(doc[i].get_text().strip() or "(no text layer: scanned page)")
    elif a.cmd == "render":
        out = Path(a.to)
        out.mkdir(parents=True, exist_ok=True)
        for i in page_list(a.pages, doc.page_count):
            f = out / f"page-{i + 1:03d}.png"
            doc[i].get_pixmap(dpi=a.dpi).save(f)
            print(f)


if __name__ == "__main__":
    main()
