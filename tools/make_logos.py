"""
Make the website's logo files from the dashboard's logo files.

Run with the dashboard's Python (it has Pillow):
    ..\\vyta\\.venv\\Scripts\\python.exe tools\\make_logos.py

Reads  ..\\vyta\\assets\\vyta_logo_dark.png  (white wordmark, transparent) and  vyta_mark.png, and writes:
  assets\\logo.png        navy wordmark on transparent (white header, light pages)
  assets\\logo-white.png  white wordmark on transparent (navy footer and bands)
  assets\\mark.png        the round mark on its own
  assets\\favicon.png     the round mark, 64px, for the browser tab
Run it again if the master logo changes (then run make_logo_assets.py in the vyta folder first).
"""

from pathlib import Path

from PIL import Image

SRC = Path(__file__).resolve().parents[2] / "vyta" / "assets"
OUT = Path(__file__).resolve().parents[1] / "assets"
NAVY = (21, 27, 61)  # sampled from the logo's circle


def main():
    OUT.mkdir(exist_ok=True)
    white = Image.open(SRC / "vyta_logo_dark.png").convert("RGBA")
    mark = Image.open(SRC / "vyta_mark.png").convert("RGBA")

    # The wordmark is white in the dark version; turn pure-white wordmark pixels navy, keep the mark as-is
    navy = white.copy()
    px = navy.load()
    w, h = navy.size
    mark_w = mark.size[0]
    for y in range(h):
        for x in range(mark_w + 2, w):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (*NAVY, a)

    white.save(OUT / "logo-white.png")
    navy.save(OUT / "logo.png")
    mark.save(OUT / "mark.png")
    mark.resize((64, 64), Image.LANCZOS).save(OUT / "favicon.png")
    print(f"[DONE] Saved logo.png, logo-white.png, mark.png and favicon.png in {OUT}")


if __name__ == "__main__":
    main()
