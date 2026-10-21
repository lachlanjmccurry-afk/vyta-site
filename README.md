# Vyta website

Marketing site for Vyta. Plain HTML and CSS, no frameworks: open any `.html` file straight from the folder.

## How it's organised

- `*.html`: one file per page. The site map and build order are in "Build plan" below.
- `partials/`: the shared `<head>` links, header (with the dropdown menus) and footer (with the call-to-action band).
  **Edit these, then run `py build.py`**, which copies them into every page between `<!-- site:... -->` markers,
  highlights the current page in the menus, and lists links to pages that aren't written yet.
- `css/site.css`: the whole design system (colours, type, buttons, result pills, band bars, the drawn product
  screen, header, footer). It uses the same colours and font as the dashboard (`vyta/ui.py`, `vyta/charts.py`).
- `js/site.js`: header menus (dropdowns and the phone menu) and the waitlist form.
- `assets/`: logos made from the dashboard's logo files by `tools/make_logos.py`.
- `styleguide.html`: a preview of every building block. Not linked from the site and marked `noindex`.

Product screens are drawn in HTML/CSS, not screenshots, using figures from the dashboard's made-up test
businesses (scored by the real engine). Never use real business data on the site.

## Build plan

1. Design system and site frame (header with dropdowns, footer, style guide). **Done**
2. Home page
3. Product pages: overview, health-check, indicators, cash, what-if, history, find-an-adviser, reports
4. Audience pages: for-owners, for-accountants, for-insolvency
5. Security & trust
6. Guides (resources + first articles), about, contact, privacy, terms, disclaimer
7. Go live: hosting, waitlist form saving sign-ups, search basics (titles, descriptions, sitemap)

No pricing page for now; the main call to action is the waitlist, plus the live demo:
https://demoapppy-djuv3vyyz3ynzokj86m8ix.streamlit.app/

## Still to do

- **Waitlist form:** checks the fields and shows a thank-you, but nothing is saved yet (step 7).
