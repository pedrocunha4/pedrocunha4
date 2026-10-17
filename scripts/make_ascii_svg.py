from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

RAMP = " .`:-=+*cs#%@"
COLS = 82
ROWS = 54
CELL_W = 6.7
CELL_H = 10.0
FG = "#CBD5E1"
BG = "#050914"
CYAN = "#22D3EE"

def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def to_ascii(image: Image.Image) -> list[str]:
    image = ImageOps.autocontrast(image.convert("L")).resize((COLS, ROWS))
    arr = np.asarray(image)
    result = []
    for row in arr:
        chars = []
        for value in row:
            idx = round((255 - int(value)) / 255 * (len(RAMP) - 1))
            chars.append(RAMP[idx])
        result.append("".join(chars).rstrip())
    return result

def render(rows: list[str], output: str = "avi-ascii.svg") -> None:
    width = int(COLS * CELL_W + 28)
    height = int(ROWS * CELL_H + 36)
    duration = 0.42
    stagger = 0.032
    row_width = COLS * CELL_W
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<style>.row{{font-family:'SFMono-Regular',Consolas,'Liberation Mono',monospace;font-size:9px;fill:{FG};white-space:pre}}.cursor{{fill:{CYAN};opacity:.82}}</style>",
        f'<rect width="100%" height="100%" rx="16" fill="{BG}"/>',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="15" fill="#0B1220" stroke="{CYAN}" stroke-opacity=".18"/>',
    ]
    for i, row in enumerate(rows):
        y = 24 + i * CELL_H
        delay = i * stagger
        clip = f"clip{i}"
        parts.append(f'<clipPath id="{clip}"><rect x="14" y="{y-9}" width="0" height="{CELL_H+2}"><animate attributeName="width" from="0" to="{row_width}" dur="{duration}s" begin="{delay:.3f}s" fill="freeze"/></rect></clipPath>')
        parts.append(f'<text class="row" x="14" y="{y}" clip-path="url(#{clip})">{esc(row)}</text>')
        parts.append(f'<rect class="cursor" x="14" y="{y-8}" width="3" height="9"><animate attributeName="x" from="14" to="{14+row_width}" dur="{duration}s" begin="{delay:.3f}s" fill="freeze"/><animate attributeName="opacity" from=".82" to="0" dur=".08s" begin="{delay+duration:.3f}s" fill="freeze"/></rect>')
    parts.append("</svg>")
    Path(output).write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output}")

if __name__ == "__main__":
    source = Path("source-prepped.png")
    if not source.exists():
        raise SystemExit("Missing source-prepped.png. Run scripts/prep_photo.py first.")
    render(to_ascii(Image.open(source)))
