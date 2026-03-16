import json
import csv
from pathlib import Path

data_directory = Path("data")

input_file  = data_directory / "cleaned" / "cleaned_timed_markets.json"
output_file = data_directory / "export" / "eighty_twenty_check.csv"

print(f"Loading {input_file}...")
with open(input_file, "r", encoding="utf-8") as f:
    markets = json.load(f)

markets_sorted = sorted(markets, key=lambda x: float(x.get("volume_fp", 0)), reverse=True)

total_volume = sum(float(m.get("volume_fp", 0)) for m in markets_sorted)
print(f"Total volume: {total_volume:,.2f} across {len(markets_sorted):,} markets")

rows = []
cumulative = 0.0
for market in markets_sorted:
    volume = float(market.get("volume_fp", 0))
    cumulative += volume
    rows.append({
        "title":      market.get("title", ""),
        "volume_fp":  round(volume, 2),
        "percent":    round(cumulative / total_volume * 100, 4),
    })

print(f"Saving {output_file}...")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "volume_fp", "percent"])
    writer.writeheader()
    writer.writerows(rows)

print("Done.")