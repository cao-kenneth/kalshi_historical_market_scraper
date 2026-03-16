import json
from collections import defaultdict
from pathlib import Path

data_directory = Path("data")

series_file  = data_directory / "timed" / "timed_series_markets.json"
events_file  = data_directory / "timed" / "timed_events_markets.json"
markets_file = data_directory / "cleaned" / "cleaned_timed_markets.json"
output_file  = data_directory / "cleaned" / "category_volume.json"

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

category_volume = defaultdict(float)
category_count  = defaultdict(int)

for market in markets:
    event_ticker = market.get("event_ticker")
    volume = float(market.get("volume_fp", 0))

    series_ticker = event_to_series.get(event_ticker)
    category = series_to_category.get(series_ticker, "Unknown") if series_ticker else "Unknown"

    category_volume[category] += volume
    category_count[category]  += 1

rows = [
    {
        "category": category,
        "total_volume": round(volume, 2),
        "market_count": category_count[category],
    }
    for category, volume in sorted(category_volume.items(), key=lambda x: x[1], reverse=True)
]

print(f"\nFound {len(rows)} categories:\n")
for row in rows:
    print(f"  {row['category']}: {row['total_volume']:,.2f} ({row['market_count']:,} markets)")

print(f"\nSaving {output_file}...")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)

print("Done.")