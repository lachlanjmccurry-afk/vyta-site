"""
VYTA website - copy the shared pieces into every page
------------------------------------------------------
Run with:   py build.py

Shared pieces are written once and copied into every page between marker comments:
    <!-- site:header -->  ...replaced...  <!-- /site:header -->
Pages stay plain HTML that opens straight from the folder; there's no separate output folder.

Markers:
  site:head, site:header, site:cta, site:footer   from partials\\<name>.html
  site:screen-side:Overview                       the drawn dashboard sidebar, with that page highlighted
  chart:waterfall                                 an SVG chart from charts\\<name>.svg (made by tools\\make_charts.py)

It also:
  - fills {{root}} with "" or "../" so links work from pages in subfolders (e.g. guides\\)
  - marks the current page's menu link with aria-current="page" (and its dropdown as current)
  - writes sitemap.xml once SITE_URL below is filled in
  - lists links to pages that don't exist yet

Run it after editing anything in partials\\ or charts\\, and after adding a page.
Uses only the Python standard library.
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE_URL = ""  # e.g. "https://vyta.com.au" - fill in when the site has its address (step 7)
SKIP_DIRS = {"partials", "tools", ".git", "assets", "css", "js", "charts"}
NOT_IN_SITEMAP = {"styleguide.html", "404.html"}
# Which dropdown each page belongs to, so the dropdown's button can be highlighted too
SECTIONS = {
    "product": {"product.html", "health-check.html", "indicators.html", "reports.html", "cash.html",
                "what-if.html", "history.html", "find-an-adviser.html"},
    "who": {"for-owners.html", "for-accountants.html", "for-insolvency.html"},
    "company": {"about.html", "contact.html"},
}
MARKER = re.compile(r"([ \t]*)<!-- (site|chart):([\w-]+)(?::([^>]*?))? -->.*?<!-- /\2:\3 -->", re.S)


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        if not SKIP_DIRS & set(p.relative_to(ROOT).parts[:-1]):
            yield p


def render(kind, name, arg, page):
    rel = page.relative_to(ROOT)
    root = "../" * (len(rel.parts) - 1)
    here = rel.as_posix()
    if kind == "chart":
        return (ROOT / "charts" / f"{name}.svg").read_text(encoding="utf-8").strip()
    html = (ROOT / "partials" / f"{name}.html").read_text(encoding="utf-8").replace("{{root}}", root)
    if name == "screen-side" and arg:
        html = html.replace(f'<span data-p="{arg}">', f'<span data-p="{arg}" class="on">')
    if name in ("header", "footer"):
        html = re.sub(rf'href="{re.escape(root)}{re.escape(here)}"', lambda m: m.group(0) + ' aria-current="page"', html)
        for section, members in SECTIONS.items():
            if here in members:
                html = re.sub(rf'class="nav-trigger"([^>]*data-section="{section}")', r'class="nav-trigger is-current"\1', html)
    return fill(html, page).strip("\n")  # shared pieces can contain other shared pieces


def fill(text, page):
    def swap(m):
        indent, kind, name, arg = m.group(1), m.group(2), m.group(3), m.group(4)
        body = "\n".join((indent + line) if line.strip() else "" for line in render(kind, name, arg, page).split("\n"))
        tag = f"{kind}:{name}" + (f":{arg}" if arg else "")
        return f"{indent}<!-- {tag} -->\n{body}\n{indent}<!-- /{kind}:{name} -->"
    return MARKER.sub(swap, text)


def main():
    changed, missing, listed = 0, {}, []
    for page in pages():
        text = page.read_text(encoding="utf-8")
        new = fill(text, page)
        if new != text:
            page.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
        rel = page.relative_to(ROOT).as_posix()
        if rel not in NOT_IN_SITEMAP:
            listed.append(rel)
        for href in re.findall(r'href="([^"#:]+\.html)', new):
            if not (page.parent / href).resolve().exists():
                missing.setdefault(Path(href).name, set()).add(rel)

    if SITE_URL:
        urls = "\n".join(f"  <url><loc>{SITE_URL.rstrip('/')}/{'' if p == 'index.html' else p}</loc>"
                         f"<lastmod>{date.today().isoformat()}</lastmod></url>" for p in listed)
        (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                          f"{urls}\n</urlset>\n", encoding="utf-8", newline="\n")
        print("Wrote sitemap.xml")

    print(f"Updated {changed} page(s).")
    if missing:
        print("Links to pages that aren't written yet:")
        for name in sorted(missing):
            print(f"  {name}")
    print("[DONE]")


if __name__ == "__main__":
    sys.exit(main())
