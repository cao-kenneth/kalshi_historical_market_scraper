import json
import csv
from pathlib import Path

data_directory = Path("data")

input_file  = data_directory / "timed" / "timed_aggregate_daily_volume.json"
output_file = data_directory / "export" / "aggregate_daily_volume.csv"

print(f"Loading {input_file}...")
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Saving {output_file}...")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "daily_volume", "cumulative_volume"])
    writer.writeheader()
    writer.writerows(data)

print(f"Done. {len(data):,} rows written.")