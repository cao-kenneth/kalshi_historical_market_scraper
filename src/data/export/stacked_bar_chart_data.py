import json
import csv
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

data_directory = Path("data")

series_file  = data_directory / "timed" / "timed_series_markets.json"
events_file  = data_directory / "timed" / "timed_events_markets.json"
markets_file = data_directory / "cleaned" / "cleaned_timed_markets.json"
output_file  = data_directory / "export" / "category_volume_split.csv"

SPLIT_DATE = datetime(2024, 10, 2, tzinfo=timezone.utc)

print(f"Loading {series_file}...")
with open(series_file, "r", encoding="utf-8") as f:
    series = json.load(f)

print(f"Loading {events_file}...")
with open(events_file, "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"Loading {markets_file}...")
with open(markets_file, "r", encoding="utf-8") as f:
    markets = json.load(f)

# event_ticker -> series_ticker
event_to_series = {
    e["event_ticker"]: e["series_ticker"]
    for e in events
    if e.get("event_ticker") and e.get("series_ticker")
}

# series_ticker -> category
series_to_category = {
    s["ticker"]: s.get("category") or "Unknown"
    for s in series
    if s.get("ticker")
}

volume_before  = defaultdict(float)
volume_after   = defaultdict(float)
count_before   = defaultdict(int)
count_after    = defaultdict(int)

for market in markets:
    event_ticker = market.get("event_ticker")
    volume = float(market.get("volume_fp", 0))

    series_ticker = event_to_series.get(event_ticker)
    category = series_to_category.get(series_ticker, "Unknown") if series_ticker else "Unknown"

    close_time_str = market.get("close_time")
    if close_time_str:
        close_time = datetime.fromisoformat(close_time_str.replace("Z", "+00:00"))
        if close_time < SPLIT_DATE:
            volume_before[category] += volume
            count_before[category]  += 1
        else:
            volume_after[category] += volume
            count_after[category]  += 1
    else:
        # No close_time: bucket into "after" or handle as unknown
        volume_after[category] += volume
        count_after[category]  += 1

all_categories = sorted(set(volume_before) | set(volume_after))

rows = [
    {
        "category":      category,
        "volume_before": round(volume_before[category], 2),
        "volume_after":  round(volume_after[category], 2),
        "count_before":  count_before[category],
        "count_after":   count_after[category],
    }
    for category in all_categories
]

# Sort by total volume descending
rows.sort(key=lambda x: x["volume_before"] + x["volume_after"], reverse=True)

print(f"\nFound {len(rows)} categories:\n")
for row in rows:
    print(
        f"  {row['category']}: "
        f"before={row['volume_before']:,.2f} ({row['count_before']:,} mkts) | "
        f"after={row['volume_after']:,.2f} ({row['count_after']:,} mkts)"
    )

print(f"\nSaving {output_file}...")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["category", "volume_before", "volume_after", "count_before", "count_after"])
    writer.writeheader()
    writer.writerows(rows)

print("Done.")