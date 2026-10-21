# Vyta website

Marketing site for Vyta. Plain HTML and CSS, no frameworks: open any `.html` file straight from the folder.

## Pages

| Area | Pages |
|---|---|
| Home | `index.html` |
| Product | `product.html` (tour), `health-check.html`, `indicators.html`, `cash.html`, `what-if.html`, `history.html`, `find-an-adviser.html`, `reports.html` |
| Who it's for | `for-owners.html`, `for-accountants.html`, `for-insolvency.html` |
| Trust | `security.html` |
| Guides | `resources.html` (hub and glossary), `guides/warning-signs-of-insolvency.html`, `guides/safe-harbour.html`, `guides/ato-payment-plans.html` |
| Company | `about.html`, `contact.html`, `waitlist.html` |
| Legal | `privacy.html` and `terms.html` (drafts), `disclaimer.html` |
| Other | `404.html`, `styleguide.html` (design preview, not linked, `noindex`) |

No pricing page for now; the main call to action is the waitlist, plus the live demo:
https://demoapppy-djuv3vyyz3ynzokj86m8ix.streamlit.app/

## How it's organised

- `partials/`: shared pieces, written once.
  - `head.html`, `header.html` (dropdown menus), `cta.html` (navy call-to-action band), `footer.html`
  - `screen-*.html`: the drawn dashboard screens (overview, details, cash, whatif, history, help, report)
    and `screen-side.html` (their navy sidebar)
  - `indicator-table.html`: made by `tools/make_indicator_table.py`
- `charts/`: SVG charts, made by `tools/make_charts.py`
- **`py build.py`** copies the partials and charts into every page between `<!-- site:... -->` /
  `<!-- chart:... -->` markers, highlights the current page in the menus, lists broken page links, and writes
  `sitemap.xml` once `SITE_URL` is set. Run it after editing anything in `partials/` or `charts/`, or adding a page.
- `css/site.css`: the whole design system, using the dashboard's colours and font.
- `js/site.js`: header menus and the forms.
- `assets/`: logos, made from the dashboard's logo by `tools/make_logos.py`.

## Figures on the site

Every product screen and chart uses the dashboard's **made-up** test business "TEST - Stressed Co", scored
by the real engine, and is captioned "Example only". Never use real business data on the site.
If the scoring changes, re-run the tools (they need the `vyta` folder next to this one):

    ..\vyta\.venv\Scripts\python.exe tools\make_charts.py
    py tools\make_indicator_table.py
    py build.py

The numbers written into page text (e.g. "Distress 89", "$68,455 owed to the ATO") were checked against the
engine on 21 Oct 2026; update them by hand if the scoring changes.

## Before going live

- **"To fill in" boxes** (dashed amber): about (founder story, team), contact (email), security (storage
  and encryption), for-accountants (which practice features to promise), privacy and terms (legal drafts),
  disclaimer and the three guides (professional review). Search for `class="todo"`.
- **Forms:** the waitlist and contact forms check the fields and say thank you, but nothing is sent or
  saved yet. Connect them to a form service (e.g. Netlify Forms or Formspree).
- **Hosting and address:** pick a host and domain, then set `SITE_URL` in `build.py` and run it to write
  `sitemap.xml`.
