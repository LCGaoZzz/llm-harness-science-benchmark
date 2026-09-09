#!/usr/bin/env python3
"""Assemble the single-file lab.html from src/{index.html,style.css,core.js,ui.js}.

The inlined <script> blocks contain EXACTLY the bytes of src/core.js and src/ui.js,
so the code that is tested headlessly is the code that ships. The build prints the
SHA-256 of every input and of the output.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "lab.html"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    html = (SRC / "index.html").read_text(encoding="utf-8")
    css = (SRC / "style.css").read_text(encoding="utf-8")
    core = (SRC / "core.js").read_text(encoding="utf-8")
    ui = (SRC / "ui.js").read_text(encoding="utf-8")

    for marker, payload in (("/*__INLINE_CSS__*/", css),
                            ("/*__INLINE_CORE__*/", core),
                            ("/*__INLINE_UI__*/", ui)):
        if marker not in html:
            print(f"FATAL: marker {marker} missing", file=sys.stderr)
            return 2
        html = html.replace(marker, payload)

    for bad in ("/*__INLINE_", "<script src=", "http://", "https://cdn"):
        if bad in html:
            print(f"FATAL: output still contains {bad!r}", file=sys.stderr)
            return 3

    OUT.write_text(html, encoding="utf-8")
    out_b = OUT.read_bytes()
    print("inputs:")
    for name, b in (("style.css", css.encode()), ("core.js", core.encode()),
                    ("ui.js", ui.encode()), ("index.html", (SRC / "index.html").read_bytes())):
        print(f"  {name:14s} {len(b):8d} B  sha256 {sha(b)}")
    print(f"output: {OUT.name}  {len(out_b)} B  sha256 {sha(out_b)}")
    # prove the inlined blocks are byte-identical to the sources
    print("inline check:",
          "core OK" if core in html else "core MISSING",
          "|", "ui OK" if ui in html else "ui MISSING",
          "|", "css OK" if css in html else "css MISSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
