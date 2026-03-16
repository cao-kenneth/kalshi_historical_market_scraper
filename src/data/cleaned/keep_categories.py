import json
import csv
from collections import defaultdict
from pathlib import Path

data_directory = Path("data")

series_file  = data_directory / "timed" / "timed_series_markets.json"
events_file  = data_directory / "timed" / "timed_events_markets.json"
markets_file = data_directory / "cleaned" / "cleaned_timed_markets.json"
output_file  = data_directory / "cleaned" / "politics_elections_markets.csv"

KEEP_CATEGORIES = {"Politics", "Elections"}

print(f"Loading files...")
with open(series_file, "r", encoding="utf-8") as f:
    series = json.load(f)
with open(events_file, "r", encoding="utf-8") as f:
    events = json.load(f)
with open(markets_file, "r", encoding="utf-8") as f:
    markets = json.load(f)

event_to_series = {
    e["event_ticker"]: e["series_ticker"]
    for e in events
    if e.get("event_ticker") and e.get("series_ticker")
}

series_to_category = {
    s["ticker"]: s.get("category") or "Unknown"
    for s in series
    if s.get("ticker")
}

filtered = []
for market in markets:
    event_ticker  = market.get("event_ticker")
    series_ticker = event_to_series.get(event_ticker)
    category      = series_to_category.get(series_ticker, "Unknown") if series_ticker else "Unknown"

    if category in KEEP_CATEGORIES:
        filtered.append({
            "title":      market.get("title", ""),
            "ticker":     market.get("ticker", ""),
            "event_ticker": market.get("event_ticker", ""),
            "category":   category,
            "volume_fp":  market.get("volume_fp", "0"),
            "close_time": market.get("close_time", ""),
        })

filtered.sort(key=lambda x: float(x["volume_fp"]), reverse=True)

print(f"Filtered to {len(filtered):,} markets in {KEEP_CATEGORIES}")

print(f"Saving {output_file}...")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "ticker", "event_ticker", "category", "volume_fp", "close_time"])
    writer.writeheader()
    writer.writerows(filtered)

print("Done.")