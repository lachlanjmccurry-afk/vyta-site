"""
VYTA website - copy the shared pieces into every page
------------------------------------------------------
Run with:   py build.py

The header, footer and <head> links are written once, in partials\\, and copied into every page between
marker comments, for example:
    <!-- site:header -->  ...replaced...  <!-- /site:header -->
Pages stay plain HTML that opens straight from the folder; there's no separate output folder.

It also:
  - fills {{root}} with "" or "../" so links work from pages in subfolders (e.g. guides\\)
  - marks the current page's menu link with aria-current="page" (and its dropdown as current)
  - lists links to pages that don't exist yet

Run it after editing anything in partials\\, and after adding a new page.
Uses only the Python standard library.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ("head", "header", "footer")
SKIP_DIRS = {"partials", "tools", ".git", "assets", "css", "js"}
# Which dropdown each page belongs to, so the dropdown's button can be highlighted too
SECTIONS = {
    "product": {"product.html", "health-check.html", "indicators.html", "reports.html", "cash.html",
                "what-if.html", "history.html", "find-an-adviser.html"},
    "who": {"for-owners.html", "for-accountants.html", "for-insolvency.html"},
    "company": {"about.html", "contact.html"},
}


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        if not SKIP_DIRS & set(p.relative_to(ROOT).parts[:-1]):
            yield p


def render(part, page):
    rel = page.relative_to(ROOT)
    root = "../" * (len(rel.parts) - 1)
    html = (ROOT / "partials" / f"{part}.html").read_text(encoding="utf-8").replace("{{root}}", root)
    here = rel.as_posix()
    # Current page: links whose href (without the root prefix) is this page
    html = re.sub(rf'href="{re.escape(root)}{re.escape(here)}"', lambda m: m.group(0) + ' aria-current="page"', html)
    for section, members in SECTIONS.items():
        if here in members:
            html = re.sub(rf'class="nav-trigger"([^>]*data-section="{section}")', r'class="nav-trigger is-current"\1', html)
    return html.rstrip("\n")


def main():
    changed, missing = 0, {}
    for page in pages():
        text = page.read_text(encoding="utf-8")
        new = text
        for part in PARTS:
            pattern = re.compile(rf"([ \t]*)<!-- site:{part} -->.*?<!-- /site:{part} -->", re.S)
            m = pattern.search(new)
            if not m:
                continue
            indent = m.group(1)
            body = "\n".join((indent + line) if line else line for line in render(part, page).split("\n"))
            block = f"{indent}<!-- site:{part} -->\n{body}\n{indent}<!-- /site:{part} -->"
            new = new[:m.start()] + block + new[m.end():]
        if new != text:
            page.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
        # Local links to pages that don't exist yet
        for href in re.findall(r'href="([^"#:]+\.html)', new):
            if not (page.parent / href).resolve().exists():
                missing.setdefault(Path(href).name, set()).add(page.relative_to(ROOT).as_posix())

    print(f"Updated {changed} page(s).")
    if missing:
        print("Links to pages that aren't written yet:")
        for name in sorted(missing):
            print(f"  {name}")
    print("[DONE]")


if __name__ == "__main__":
    sys.exit(main())
