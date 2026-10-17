from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "pedrocunha4"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")


def parse_count(text: str) -> int:
    text = text.strip().lower()
    if text.startswith("no contributions"):
        return 0
    match = re.search(r"([\d,]+)\s+contribution", text)
    return int(match.group(1).replace(",", "")) if match else 0


def fetch_days() -> list[dict]:
    response = requests.get(
        URL,
        timeout=30,
        headers={"User-Agent": "pedrocunha4-profile-readme"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    days: list[dict] = []

    # Current GitHub markup exposes date + level on contribution day cells.
    for cell in soup.select("[data-date][data-level]"):
        day = cell.get("data-date")
        level = int(cell.get("data-level", "0"))

        count = None
        cell_id = cell.get("id")
        if cell_id:
            tooltip = soup.find("tool-tip", attrs={"for": cell_id})
            if tooltip:
                count = parse_count(tooltip.get_text(" ", strip=True))

        if count is None:
            count_attr = cell.get("data-count")
            if count_attr and str(count_attr).isdigit():
                count = int(count_attr)

        days.append({"date": day, "count": count or 0, "level": level})

    # Fallback for older markup.
    if not days:
        for cell in soup.select("td.ContributionCalendar-day[data-date]"):
            day = cell.get("data-date")
            level = int(cell.get("data-level", "0"))
            count = 0
            cell_id = cell.get("id")
            if cell_id:
                tooltip = soup.find("tool-tip", attrs={"for": cell_id})
                if tooltip:
                    count = parse_count(tooltip.get_text(" ", strip=True))
            days.append({"date": day, "count": count, "level": level})

    # De-duplicate while preserving the latest parsed version.
    merged = {item["date"]: item for item in days if item.get("date")}
    result = sorted(merged.values(), key=lambda item: item["date"])

    if not result:
        raise RuntimeError("No contribution days found in GitHub HTML.")

    return result


def derive_stats(days: list[dict]) -> dict:
    counts = {date.fromisoformat(item["date"]): int(item["count"]) for item in days}
    today = date.today()

    active_dates = sorted(day for day, count in counts.items() if count > 0)

    longest = 0
    run = 0
    previous = None
    for day in active_dates:
        if previous and day == previous + timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)
        previous = day

    cursor = today
    if counts.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)

    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    best = max(days, key=lambda item: int(item["count"]))
    monthly = defaultdict(int)
    total = 0

    for item in days:
        count = int(item["count"])
        total += count
        monthly[item["date"][:7]] += count

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main() -> None:
    days = fetch_days()
    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "days": days,
        "stats": derive_stats(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
