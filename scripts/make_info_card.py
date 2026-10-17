from pathlib import Path
import os

ROWS = [
    ("Now", "Process Automation · Systems Integration · Data & AI"),
    ("Education", "Telecommunications & Informatics Engineering · ISEP"),
    ("Stack", "Python · FastAPI · n8n · Make · PostgreSQL · Supabase"),
    ("Focus", "REST APIs · Webhooks · LLM Integration · Automation"),
    ("Featured", "InvoiceFlow AI · AI-powered invoice automation platform"),
]

WIDTH = 690
HEIGHT = 300
BG = "#050914"
PANEL = "#0B1220"
CYAN = "#22D3EE"
TEXT = "#CBD5E1"
MUTED = "#64748B"


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render(static: bool = False) -> str:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<style>",
        ".mono{font-family:'SFMono-Regular',Consolas,'Liberation Mono',monospace}",
        f".key{{fill:{CYAN};font-weight:700}}",
        f".value{{fill:{TEXT}}}",
        f".muted{{fill:{MUTED}}}",
        "</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="{BG}"/>',
        f'<rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="17" fill="{PANEL}" stroke="{CYAN}" stroke-opacity=".20"/>',
        f'<circle cx="26" cy="24" r="5" fill="#FF5F57"/><circle cx="44" cy="24" r="5" fill="#FEBC2E"/><circle cx="62" cy="24" r="5" fill="#28C840"/>',
        f'<text x="86" y="29" class="mono muted" font-size="13">pedro@github:~$ neofetch</text>',
        f'<line x1="20" y1="45" x2="{WIDTH-20}" y2="45" stroke="{CYAN}" stroke-opacity=".16"/>',
    ]

    y = 82
    for idx, (key, value) in enumerate(ROWS):
        delay = idx * 0.12
        group_open = f'<g transform="translate(0 0)">'
        if not static:
            group_open = (
                f'<g opacity="0" transform="translate(0 6)">'
                f'<animate attributeName="opacity" from="0" to="1" dur=".28s" begin="{delay}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="0 6" to="0 0" dur=".28s" begin="{delay}s" fill="freeze"/>'
            )
        out += [
            group_open,
            f'<text x="28" y="{y}" class="mono key" font-size="14">{esc(key)}</text>',
            f'<text x="135" y="{y}" class="mono value" font-size="14">{esc(value)}</text>',
            "</g>",
        ]
        y += 40

    out += [
        f'<text x="28" y="{HEIGHT-22}" class="mono muted" font-size="12">github.com/pedrocunha4</text>',
        "</svg>",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    static = os.getenv("STATIC") == "1"
    Path("info-card.svg").write_text(render(static), encoding="utf-8")
    print("Wrote info-card.svg")
