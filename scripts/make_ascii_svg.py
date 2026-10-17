from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

RAMP = " .`:-=+*cs#%@"
COLS = 100
ROWS = 53
CELL_W = 6.8
CELL_H = 10.2
FG = "#CBD5E1"
BG = "#050914"
CYAN = "#22D3EE"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def to_ascii(image: Image.Image) -> list[str]:
    image = ImageOps.autocontrast(image.convert("L"))
    image = image.resize((COLS, ROWS))
    arr = np.asarray(image)

    rows = []
    for row in arr:
        chars = []
        for value in row:
            idx = round((255 - int(value)) / 255 * (len(RAMP) - 1))
            chars.append(RAMP[idx])
        rows.append("".join(chars).rstrip())
    return rows


def render(rows: list[str], output: str = "avi-ascii.svg") -> None:
    width = int(COLS * CELL_W + 28)
    height = int(ROWS * CELL_H + 36)
    duration = 0.42
    stagger = 0.035

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        f".row{{font-family:'SFMono-Regular',Consolas,'Liberation Mono',monospace;font-size:9px;fill:{FG};white-space:pre}}",
        f".cursor{{fill:{CYAN};opacity:.8}}",
        "</style>",
        f'<rect width="100%" height="100%" rx="16" fill="{BG}"/>',
    ]

    for i, row in enumerate(rows):
        y = 24 + i * CELL_H
        clip_id = f"clip{i}"
        delay = i * stagger
        row_width = COLS * CELL_W
        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="14" y="{y-9}" width="0" height="{CELL_H+2}">'
            f'<animate attributeName="width" from="0" to="{row_width}" dur="{duration}s" begin="{delay}s" fill="freeze"/>'
            f'</rect></clipPath>'
        )
        parts.append(
            f'<text class="row" x="14" y="{y}" clip-path="url(#{clip_id})">{esc(row)}</text>'
        )
        parts.append(
            f'<rect class="cursor" x="14" y="{y-8}" width="3" height="9">'
            f'<animate attributeName="x" from="14" to="{14+row_width}" dur="{duration}s" begin="{delay}s" fill="freeze"/>'
            f'<animate attributeName="opacity" from=".8" to="0" dur=".08s" begin="{delay+duration}s" fill="freeze"/>'
            f'</rect>'
        )

    parts.append("</svg>")
    Path(output).write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    source = Path("source-prepped.png")
    if not source.exists():
        raise SystemExit("Missing source-prepped.png. Run scripts/prep_photo.py first.")
    render(to_ascii(Image.open(source)))
