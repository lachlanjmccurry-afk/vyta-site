r"""
Make the website's charts from the dashboard's made-up "Stressed Co" test business, scored by the real engine.

Run with the dashboard's Python, from anywhere:
    ..\vyta\.venv\Scripts\python.exe tools\make_charts.py

Writes charts\*.svg (distress and viability history, creditor days, month-end cash, the cash waterfall).
Then run  py build.py  to copy them into the pages. Needs data_stressed built in the vyta folder
(py make_test_data.py, then py sync.py data_stressed). Never point this at real business data.
"""
import sys, io, contextlib
from pathlib import Path
sys.path.insert(0, r"C:\Users\LMcCurry\vyta")
import os; os.chdir(r"C:\Users\LMcCurry\vyta")
import score, trends, cashflow
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "charts"
with contextlib.redirect_stdout(io.StringIO()):
    run = score.compute("data_stressed")
d = run["d"]; n = len(d["months"])
months = [m["month"] for m in d["months"][n-12:]]
hist = []
for i in range(n-12, n):
    with contextlib.redirect_stdout(io.StringIO()):
        r = score.score_data(trends.as_at(d, i), run["cfg"], run["wording"])
    hist.append((round(r["scores"]["distress"][0]), round(r["scores"]["viability"][0])))

def mlab(m, year=False):
    return m.strftime("%b") + (" " + m.strftime("%y") if year else "")

def line_chart(values, zones, ymax, ymin=0, w=640, h=260, ticks=(), label_fmt=str, name="", hl=None, endlabel=True):
    L, R, T, B = 44, 16, 16, 30
    pw, ph = w-L-R, h-T-B
    X = lambda i: L + pw * i / (len(values)-1)
    Y = lambda v: T + ph * (1 - (v-ymin)/(ymax-ymin))
    s = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="{name}">']
    for lo, hi, cls in zones:
        s.append(f'<rect class="z-{cls}" x="{L}" y="{Y(hi):.1f}" width="{pw}" height="{Y(lo)-Y(hi):.1f}"/>')
    for t in ticks:
        s.append(f'<line class="grid" x1="{L}" x2="{w-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>')
        s.append(f'<text class="tick" x="{L-8}" y="{Y(t)+4:.1f}" text-anchor="end">{label_fmt(t)}</text>')
    for i, m in enumerate(months):
        if i % 2 == 0 or i == len(months)-1:
            s.append(f'<text class="tick" x="{X(i):.1f}" y="{h-8}" text-anchor="middle">{mlab(m, i in (0, len(months)-1))}</text>')
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(values))
    area = f"{X(0):.1f},{Y(max(ymin,0) if ymin<0 else ymin):.1f} " + pts + f" {X(len(values)-1):.1f},{Y(max(ymin,0) if ymin<0 else ymin):.1f}"
    s.append(f'<polyline class="line" points="{pts}"/>')
    for i, v in enumerate(values):
        cls = "dot end" if i == len(values)-1 else "dot"
        s.append(f'<circle class="{cls}" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{5 if i==len(values)-1 else 3}"/>')
    if hl is not None:
        i, text = hl
        s.append(f'<line class="mark" x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{T}" y2="{T+ph}"/>')
        s.append(f'<text class="note" x="{X(i)+8:.1f}" y="{T+14}">{text}</text>')
    if endlabel:
        v = values[-1]
        s.append(f'<text class="endlab" x="{X(len(values)-1)-10:.1f}" y="{Y(v)-12:.1f}" text-anchor="end">{label_fmt(v)}</text>')
    s.append('</svg>')
    return "\n".join(s)

dist = [h_[0] for h_ in hist]; via = [h_[1] for h_ in hist]
first_high = next(i for i, v in enumerate(dist) if v >= 60)
(OUT/"distress_history.svg").write_text(line_chart(dist, [(0,30,"g"),(30,60,"a"),(60,100,"r")], 100, ticks=(0,30,60,100),
    name="Distress score each month for the made-up Stressed Co, rising from 33 in October 2025 to 89 in September 2026", hl=(first_high, f"High from {mlab(months[first_high], True)}")), encoding="utf-8")
(OUT/"viability_history.svg").write_text(line_chart(via, [(0,40,"r"),(40,65,"a"),(65,100,"g")], 100, ticks=(0,40,65,100),
    name="Viability score each month for the made-up Stressed Co, falling from 53 to 21"), encoding="utf-8")

# Creditor days (D7) with Amber at 60 and Red at 90
ind = next(r["ind"] for r in run["results"] if r["ind"]["id"] == "D7")
cd = [round(p[1]) for p in trends.indicator_series(d, ind)["points"]]
(OUT/"creditor_days.svg").write_text(line_chart(cd, [(0,60,"g"),(60,90,"a"),(90,120,"r")], 120, ticks=(0,60,90,120), label_fmt=lambda v: f"{v}", name="Creditor days rising from 45 to 99 over 12 months", endlabel=True), encoding="utf-8")

# Month-end cash line
cash = [round(m["cash"]) for m in d["months"][n-12:]]
k = lambda v: ("-" if v < 0 else "") + f"${abs(v)/1000:.0f}k"
(OUT/"cash_line.svg").write_text(line_chart(cash, [(-40000,0,"r")], 10000, ymin=-40000, ticks=(-40000,-20000,0,10000), label_fmt=k, name="Month-end cash falling from $5,940 to an overdraft of $30,000"), encoding="utf-8")

# Waterfall
b = cashflow.cash_bridge(d)
steps = [("Opening cash", b["opening"], "total")] + [(nm, v, "step") for nm, v in b["steps"]] + [("Closing cash", b["closing"], "total")]
w, h = 720, 300; L, R, T, B = 56, 12, 20, 56
lo = -160000; hi = 160000
running = 0; bars = []
for nm, v, kind in steps:
    if kind == "total":
        a0, a1 = 0, v; running = v
    else:
        a0, a1 = running, running + v; running += v
    bars.append((nm, v, kind, a0, a1))
lo = min(min(x[3], x[4]) for x in bars); hi = max(max(x[3], x[4]) for x in bars)
lo = -120000 if lo > -120000 else lo; hi = 120000
Y = lambda v: T + (h-T-B) * (1 - (v-lo)/(hi-lo))
bw = (w-L-R) / len(bars)
s = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="Where the cash went for the made-up Stressed Co: opening cash $8,680, operating loss $100,537, ATO debt grew $56,674, customers owe $34,081 more, suppliers owed $129,102 more, other $89,838 out, closing overdraft $30,000">']
for t in (-120000, -60000, 0, 60000, 120000):
    s.append(f'<line class="grid{" zero" if t==0 else ""}" x1="{L}" x2="{w-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>')
    s.append(f'<text class="tick" x="{L-8}" y="{Y(t)+4:.1f}" text-anchor="end">{k(t) if t else "$0"}</text>')
short = {"Opening cash":"Opening","Operating profit":"Profit","ATO movement":"ATO","Debt movement":"Bank debt","Change in debtors":"Debtors","Change in creditors":"Suppliers","Other":"Other","Closing cash":"Closing"}
prev_end = None
for i, (nm, v, kind, a0, a1) in enumerate(bars):
    x = L + i*bw + bw*0.18; bwid = bw*0.64
    top, bot = Y(max(a0, a1)), Y(min(a0, a1))
    cls = "total" if kind == "total" else ("up" if v >= 0 else "down")
    hgt = max(bot-top, 1.5)
    s.append(f'<rect class="wf-{cls}" x="{x:.1f}" y="{top:.1f}" width="{bwid:.1f}" height="{hgt:.1f}" rx="3"/>')
    if prev_end is not None:
        s.append(f'<line class="wf-link" x1="{x-bw*0.36:.1f}" x2="{x:.1f}" y1="{Y(prev_end):.1f}" y2="{Y(prev_end):.1f}"/>')
    prev_end = a1
    val = ("+" if v > 0 and kind=="step" else "") + k(round(v)) if abs(v) >= 500 else "$0"
    ly = top - 6 if (v >= 0 or kind=="total" and v>=0) else bot + 14
    if kind == "total" and v < 0: ly = bot + 14
    s.append(f'<text class="wf-val" x="{x+bwid/2:.1f}" y="{ly:.1f}" text-anchor="middle">{val}</text>')
    s.append(f'<text class="tick" x="{x+bwid/2:.1f}" y="{h-30}" text-anchor="middle">{short[nm]}</text>')
s.append('</svg>')
(OUT/"waterfall.svg").write_text("\n".join(s), encoding="utf-8")
print("hist", hist); print("cd", cd); print("cash", cash); print("bars", [(x[0], round(x[1])) for x in bars])
