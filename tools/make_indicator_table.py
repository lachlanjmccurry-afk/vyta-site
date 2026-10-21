"""
Make the website's indicator table from the dashboard's scorecard settings.

Run with:   py tools\\make_indicator_table.py      (then  py build.py)

Reads  ..\\vyta\\scorecard.json  (names, warning levels, weights) and writes  partials\\indicator-table.html,
which indicators.html includes. Run it again whenever the scorecard's thresholds or weights change.
The plain-English "what it checks" sentences are below; add one when an indicator is added.
Uses only the Python standard library.
"""

import html
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
SCORECARD = SITE.parent / "vyta" / "scorecard.json"

CHECKS = {
    "D1": "Whether short-term assets (cash, money owed by customers, stock) cover the debts due within a year.",
    "D2": "The same test using only cash and money owed by customers, the things that turn into cash quickly.",
    "D3": "How many months the cash would last at the recent rate it has been going out.",
    "D4": "How many months in a row the amount owed to the ATO has grown.",
    "D5": "How much bank loans and overdraft have grown over the last six months.",
    "D6": "How much of the approved overdraft limit is being used. Needs the limit from the owner.",
    "D7": "How long, on average, suppliers are waiting to be paid.",
    "D8": "The share of unpaid supplier bills that are more than 90 days overdue.",
    "D9": "Whether customers are taking longer to pay than they were three months ago.",
    "D10": "The share of money owed by customers that is more than 90 days overdue.",
    "D11": "Months in a row where sales rose but cash fell: growth that is eating cash.",
    "D12": "Whether a year of trading produced enough cash to cover short-term debts.",
    "D13": "Total debts as a share of everything the business owns.",
    "V1": "The owners' stake (net assets) as a share of everything the business owns.",
    "V2": "What is left from each dollar of sales after the direct cost of making the sale.",
    "V3": "Whether gross margin is improving or slipping compared with the year before. Needs 24 months of data.",
    "V4": "How much of the gross profit the running costs use up.",
    "V5": "Profit before interest, depreciation and one-off costs, as a share of sales. The core test of viability.",
    "V6": "Sales over the last 12 months compared with the 12 months before.",
    "V7": "Open quotes compared with average monthly sales. Needs quotes data.",
    "V8": "Long-term assets compared with long-term debts.",
}


def level(v, unit, ind_id):
    if unit == "ratio":
        return f"{v:.2f}"
    if unit == "percent":
        return f"{v * 100:g}%"
    if unit == "percentage_points":
        return f"{v * 100:+.1f} pts".replace("-", "−")
    if unit == "months":
        return f"{v:g} months"
    if unit == "days":
        return f"+{v:g} days" if ind_id == "D9" else f"{v:g} days"
    if unit == "count":
        return f"{v:g} months running"
    return f"{v:g}"


def rows(indicators, kind):
    out = []
    for ind in indicators:
        if ind["score"] != kind or not ind.get("enabled", True):
            continue
        word = "or above" if ind["direction"] == "higher_is_worse" else "or below"
        if ind["unit"] == "count" or ind["id"] == "D9":
            word = "or more"
        out.append(
            "      <tr>"
            f'<td><span class="code">{ind["id"]}</span></td>'
            f'<td><b>{html.escape(ind["short_name"])}</b>{html.escape(CHECKS[ind["id"]])}</td>'
            f'<td class="lv"><span><span class="pill amber">Amber</span> {level(ind["amber"], ind["unit"], ind["id"])} {word}</span>'
            f'<span style="margin-top:6px"><span class="pill red">Red</span> {level(ind["red"], ind["unit"], ind["id"])} {word}</span></td>'
            f'<td class="w">{ind["weight"]}</td>'
            "</tr>")
    return "\n".join(out)


def table(indicators, kind, caption):
    return (f'<div class="table-wrap">\n  <table class="table">\n    <caption class="visually-hidden">{caption}</caption>\n'
            '    <thead><tr><th>ID</th><th>Indicator and what it checks</th><th>Warning levels</th><th style="text-align:right">Weight</th></tr></thead>\n'
            f"    <tbody>\n{rows(indicators, kind)}\n    </tbody>\n  </table>\n</div>")


def main():
    cfg = json.loads(SCORECARD.read_text(encoding="utf-8"))
    inds = cfg["indicators"]
    missing = [i["id"] for i in inds if i["id"] not in CHECKS]
    if missing:
        raise SystemExit(f"[STOPPED] Add a 'what it checks' sentence for {', '.join(missing)} in CHECKS, then run again.")
    body = ('<h3 id="distress-indicators">Distress indicators</h3>\n<p class="muted" style="margin-bottom:var(--s4)">How much financial trouble is the business in right now? Higher is worse.</p>\n'
            + table(inds, "distress", "Distress indicators") +
            '\n<h3 id="viability-indicators" style="margin-top:var(--s8)">Viability indicators</h3>\n<p class="muted" style="margin-bottom:var(--s4)">If the cash problem were fixed, would the business make money? Higher is better.</p>\n'
            + table(inds, "viability", "Viability indicators") + "\n")
    (SITE / "partials" / "indicator-table.html").write_text(body, encoding="utf-8", newline="\n")
    print(f"[DONE] Wrote partials\\indicator-table.html ({len(inds)} indicators). Now run  py build.py")


if __name__ == "__main__":
    main()
