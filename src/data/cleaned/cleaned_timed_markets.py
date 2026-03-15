import json
from pathlib import Path

data_directory = Path("data")

historical_markets_file = data_directory / "timed" / "timed_historical_markets.json"
output_file = data_directory / "cleaned" / "cleaned_timed_markets.json"

print(f"Loading {historical_markets_file}...")

with open(historical_markets_file, "r", encoding="utf-8") as f:
    markets = json.load(f)

original_count = len(markets)

cleaned_markets = []
removed_count = 0

for market in markets:
    volume = market.get("volume_fp")

    if volume == "0.00":
        removed_count += 1
    else:
        cleaned_markets.append(market)

print(f"Original markets: {original_count}")
print(f"Removed markets with volume_fp == 0.00: {removed_count}")
print(f"Remaining markets: {len(cleaned_markets)}")

print(f"Saving cleaned file to {output_file}...")

output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned_markets, f, indent=2)

print("Done.")