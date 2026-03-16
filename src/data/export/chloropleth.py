import csv
import re
from collections import defaultdict
from pathlib import Path

data_directory = Path("data")

input_file  = data_directory / "cleaned" / "politics_elections_markets.csv"
output_file = data_directory / "export" / "chloropleth_data.csv"

STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
}

# Build regex: longest names first to avoid "New" matching before "New York" etc.
states_sorted = sorted(STATES, key=len, reverse=True)
pattern = re.compile(
    r'\b(' + '|'.join(re.escape(s) for s in states_sorted) + r')\b',
    re.IGNORECASE
)

state_volume = defaultdict(float)
state_count  = defaultdict(int)

print(f"Loading {input_file}...")
with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        title  = row.get("title", "")
        volume = float(row.get("volume_fp", 0))

        matches = set(m.group(1).title() for m in pattern.finditer(title))
        for state in matches:
            state_volume[state] += volume
            state_count[state]  += 1

# Include all 50 states even if zero
rows = [
    {
        "state":        state,
        "total_volume": round(state_volume[state], 2),
        "market_count": state_count[state],
    }
    for state in STATES
]
rows.sort(key=lambda x: x["total_volume"], reverse=True)

print(f"\nResults:")
for row in rows:
    if row["market_count"] > 0:
        print(f"  {row['state']}: {row['total_volume']:,.2f} ({row['market_count']:,} markets)")

print(f"\nSaving {output_file}...")
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["state", "total_volume", "market_count"])
    writer.writeheader()
    writer.writerows(rows)

print("Done.")