import json
from pathlib import Path
from datetime import datetime, timezone

data_directory = Path("data")

historical_markets_file = data_directory / "raw" / "historical_markets.json"
output_file = data_directory / "timed" / "timed_historical_markets.json"

start_time = datetime(2024, 3, 12, 0, 0, 0, tzinfo=timezone.utc)
end_time = datetime(2025, 3, 12, 0, 0, 0, tzinfo=timezone.utc)


def parse_close_time(close_time):
    if not close_time:
        return None
    try:
        return datetime.fromisoformat(close_time.replace("Z", "+00:00"))
    except ValueError:
        return None

print("Opening Raw Data File")

with open(historical_markets_file, "r", encoding="utf-8") as f:
    markets = json.load(f)

print("Filtering Markets")

filtered_markets = [
    market
    for market in markets
    if (dt := parse_close_time(market.get("close_time"))) is not None
    and start_time <= dt < end_time
]

print("Transferring Data")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(filtered_markets, f, indent=2)

print(f"Saved {len(filtered_markets)} markets that closed between 2024-03-12 00:00 UTC and 2025-03-12 00:00 UTC.")