import json
import statistics
from pathlib import Path

data_directory = Path("data")
markets_file = data_directory / "cleaned" / "cleaned_timed_markets.json"

print(f"Loading {markets_file}...")
with open(markets_file, "r", encoding="utf-8") as f:
    markets = json.load(f)

volumes = sorted([float(m["volume_fp"]) for m in markets if m.get("volume_fp")])
total = len(volumes)


def percentile(data, p):
    idx = (len(data) - 1) * p / 100
    lo, hi = int(idx), min(int(idx) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (idx - lo)


print(f"\nVolume distribution across {total:,} markets:\n")
print(f"  Min:     {volumes[0]:>20,.2f}")
print(f"  Q1:      {percentile(volumes, 25):>20,.2f}")
print(f"  Median:  {percentile(volumes, 50):>20,.2f}")
print(f"  Mean:    {statistics.mean(volumes):>20,.2f}")
print(f"  Q3:      {percentile(volumes, 75):>20,.2f}")
print(f"  P90:     {percentile(volumes, 90):>20,.2f}")
print(f"  P95:     {percentile(volumes, 95):>20,.2f}")
print(f"  P99:     {percentile(volumes, 99):>20,.2f}")
print(f"  Max:     {volumes[-1]:>20,.2f}")
print(f"  Std dev: {statistics.stdev(volumes):>20,.2f}")

thresholds = [10, 100, 500, 1000, 2500, 5000, 10000, 20000, 50000, 100000]

print(f"\n  {'Threshold':>10}  {'Markets kept':>15}  {'% kept':>8}  {'% dropped':>10}")
print(f"  {'-'*10}  {'-'*15}  {'-'*8}  {'-'*10}")

for t in thresholds:
    kept = sum(1 for v in volumes if v >= t)
    print(f"  {t:>10,.0f}  {kept:>15,}  {kept/total*100:>7.1f}%  {(1-kept/total)*100:>9.1f}%")