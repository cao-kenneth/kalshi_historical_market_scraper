import json
from pathlib import Path
from datetime import datetime

data_directory = Path("data")

historical_markets_file = data_directory / "raw/historical_markets.json"
output_file = data_directory / "cleaned/2025_historical_markets.json"

# load data
with open(historical_markets_file, "r") as f:
    markets = json.load(f)

markets_2025 = []

for market in markets:
    close_time = market.get("close_time")

    if not close_time:
        print(f"Warning: market missing close_time: {market.get('id', '<no id>')}")
        continue

    try:
        dt = datetime.fromisoformat(close_time)
    except ValueError:
        print(f"Warning: unparseable close_time '{close_time}'")

    if dt.year == 2025:
        markets_2025.append(market)

# save filtered data
with open(output_file, "w") as f:
    json.dump(markets_2025, f, indent=2)

print(f"Saved {len(markets_2025)} markets that closed in 2025.")