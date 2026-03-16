import csv
import json
from collections import defaultdict
from pathlib import Path

data_directory = Path("data")

series_file  = data_directory / "timed" / "timed_series_markets.json"
events_file  = data_directory / "timed" / "timed_events_markets.json"
input_file   = data_directory / "cleaned" / "politics_markets.csv"
output_file  = data_directory / "export" / "politics_network_edges.csv"

VOLUME_THRESHOLD = 500000

with open(series_file, "r", encoding="utf-8") as f:
    series = json.load(f)
with open(events_file, "r", encoding="utf-8") as f:
    events = json.load(f)

event_to_series = {
    e["event_ticker"]: e["series_ticker"]
    for e in events
    if e.get("event_ticker") and e.get("series_ticker")
}

with open(input_file, "r", encoding="utf-8") as f:
    markets = [r for r in csv.DictReader(f) if float(r.get("volume_fp", 0)) >= VOLUME_THRESHOLD]

print(f"Markets above {VOLUME_THRESHOLD:,}: {len(markets)}")

series_volume = defaultdict(float)
event_volume  = defaultdict(float)

for m in markets:
    event_ticker  = m["event_ticker"]
    series_ticker = event_to_series.get(event_ticker, "Unknown")
    volume        = float(m["volume_fp"])
    event_volume[event_ticker]   += volume
    series_volume[series_ticker] += volume

edges = []

# Politics -> series
for series_ticker, volume in series_volume.items():
    edges.append({
        "from":      "Politics",
        "to":        series_ticker,
        "from_type": "root",
        "to_type":   "series",
        "volume":    round(volume, 2),
    })

# Series -> events
for event_ticker, volume in event_volume.items():
    series_ticker = event_to_series.get(event_ticker, "Unknown")
    edges.append({
        "from":      series_ticker,
        "to":        event_ticker,
        "from_type": "series",
        "to_type":   "event",
        "volume":    round(volume, 2),
    })

# Events -> markets
for m in markets:
    edges.append({
        "from":      m["event_ticker"],
        "to":        m["ticker"],
        "from_type": "event",
        "to_type":   "market",
        "volume":    round(float(m["volume_fp"]), 2),
    })

print(f"Total edges:   {len(edges)}")
print(f"  Root->Series:  {sum(1 for e in edges if e['from_type'] == 'root')}")
print(f"  Series->Event: {sum(1 for e in edges if e['from_type'] == 'series')}")
print(f"  Event->Market: {sum(1 for e in edges if e['from_type'] == 'event')}")

unique_nodes = len({"Politics"} |
    {e["to"] for e in edges if e["to_type"] == "series"} |
    {e["to"] for e in edges if e["to_type"] == "event"} |
    {e["to"] for e in edges if e["to_type"] == "market"})
print(f"Total nodes:   {unique_nodes}")

output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["from", "to", "from_type", "to_type", "volume"])
    writer.writeheader()
    writer.writerows(edges)

print(f"Saved to {output_file}")