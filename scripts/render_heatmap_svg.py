from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("assets/contribution-activity.svg")

PALETTE = ["#161B22", "#312E81", "#4C1D95", "#6D28D9", "#8B5CF6", "#A78BFA"]
BG = "#0D1117"
TEXT = "#C9D1D9"
MUTED = "#8B949E"
ACCENT = "#A78BFA"
BORDER = "#312E81"

CELL = 12
GAP = 4
LEFT = 54
TOP = 60
WEEKS = 53
DAYS = 7
WIDTH = 930
HEIGHT = 232
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    raw_days = payload["days"]
    stats = payload["stats"]

    by_date = {date.fromisoformat(item["date"]): item for item in raw_days}
    last = max(by_date)
    end = last + timedelta(days=(6 - last.weekday()) % 7)
    start = end - timedelta(days=WEEKS * 7 - 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<style>",
        ".mono{font-family:'SFMono-Regular',Consolas,'Liberation Mono',monospace}",
        ".cell{opacity:0;animation:reveal .30s ease-out forwards}",
        "@keyframes reveal{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}",
        "</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="16" fill="{BG}"/>',
        f'<rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="15" fill="none" stroke="{BORDER}"/>',
        f'<text x="22" y="28" class="mono" fill="{ACCENT}" font-size="13" font-weight="700">53-week contribution activity</text>',
    ]

    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = TOP + row * (CELL + GAP) + CELL - 1
        parts.append(f'<text x="17" y="{y}" class="mono" fill="{MUTED}" font-size="10">{label}</text>')

    last_month = None
    for week in range(WEEKS):
        week_start = start + timedelta(days=week * 7)
        if week_start.month != last_month:
            last_month = week_start.month
            x = LEFT + week * (CELL + GAP)
            if x < WIDTH - 55:
                parts.append(f'<text x="{x}" y="{TOP-12}" class="mono" fill="{MUTED}" font-size="10">{MONTHS[last_month-1]}</text>')

        for row in range(DAYS):
            day = start + timedelta(days=week * 7 + row)
            item = by_date.get(day, {"count": 0, "level": 0})
            level = max(0, min(5, int(item.get("level", 0))))
            count = int(item.get("count", 0))
            x = LEFT + week * (CELL + GAP)
            y = TOP + row * (CELL + GAP)
            delay = (week + row) * 0.01
            title = f"{count} contribution{'s' if count != 1 else ''} on {day.isoformat()}"
            parts.append(
                f'<g class="cell" style="animation-delay:{delay:.3f}s">'
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[level]}">'
                f'<title>{esc(title)}</title></rect></g>'
            )

    legend_x = WIDTH - 210
    legend_y = HEIGHT - 34
    parts.append(f'<text x="{legend_x}" y="{legend_y+10}" class="mono" fill="{MUTED}" font-size="10">Less</text>')
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{legend_x+34+i*18}" y="{legend_y}" width="11" height="11" rx="3" fill="{color}"/>')
    parts.append(f'<text x="{legend_x+148}" y="{legend_y+10}" class="mono" fill="{MUTED}" font-size="10">More</text>')

    footer = (
        f'{stats.get("total", 0):,} contributions · '
        f'current streak {stats.get("current_streak", 0)} days · '
        f'longest {stats.get("longest_streak", 0)} days'
    )
    parts.append(f'<text x="22" y="{HEIGHT-25}" class="mono" fill="{TEXT}" font-size="11">{esc(footer)}</text>')

    best = stats.get("best_day", {})
    if best.get("date"):
        best_text = f'Best day: {best.get("count", 0)} on {best["date"]}'
        parts.append(f'<text x="22" y="{HEIGHT-10}" class="mono" fill="{MUTED}" font-size="10">{esc(best_text)}</text>')

    parts.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
