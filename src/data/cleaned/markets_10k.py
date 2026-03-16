import json
from pathlib import Path

data_directory = Path("data")
markets_file = data_directory / "cleaned" / "cleaned_timed_markets.json"
output_file  = data_directory / "cleaned" / "markets_above_10k.json"

print(f"Loading {markets_file}...")
with open(markets_file, "r", encoding="utf-8") as f:
    markets = json.load(f)

original_count = len(markets)

filtered = [m for m in markets if float(m.get("volume_fp", 0)) >= 10000]

print(f"Original markets: {original_count:,}")
print(f"Kept markets (volume >= 10,000): {len(filtered):,}")
print(f"Removed: {original_count - len(filtered):,}")

print(f"Saving {output_file}...")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(filtered, f, indent=2)

print("Done.")