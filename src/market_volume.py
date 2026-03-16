import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

data_directory  = Path("data")
markets_file    = data_directory / "cleaned" / "markets_above_10k.json"
output_file     = data_directory / "timed" / "timed_market_daily_volume.json"
agg_file        = data_directory / "timed" / "timed_aggregate_daily_volume.json"
checkpoint_file = data_directory / "timed" / "checkpoint.json"

START_TS = int(datetime(2024, 3, 12, tzinfo=timezone.utc).timestamp())
END_TS   = int(datetime(2025, 3, 12, tzinfo=timezone.utc).timestamp())

MAX_RETRIES   = 3
SLEEP_BETWEEN = 0.20
SLEEP_ON_429  = 5.0

session = requests.Session()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def load_checkpoint():
    if checkpoint_file.exists():
        return set(load_json(checkpoint_file))
    return set()


def save_checkpoint(done):
    save_json(checkpoint_file, list(done))


def fetch_candles(ticker):
    url = f"{BASE_URL}/historical/markets/{ticker}/candlesticks"
    candles = []
    cursor = None

    while True:
        params = {
            "start_ts": START_TS,
            "end_ts": END_TS,
            "period_interval": 1440,
        }
        if cursor:
            params["cursor"] = cursor

        attempt = 0
        while True:
            try:
                r = session.get(url, params=params, timeout=20)
                if r.status_code == 429:
                    print(f"  [{ticker}] Rate limited — sleeping {SLEEP_ON_429}s")
                    time.sleep(SLEEP_ON_429)
                    continue
                r.raise_for_status()
                body = r.json()
                break
            except requests.RequestException as e:
                attempt += 1
                if attempt >= MAX_RETRIES:
                    raise
                wait = attempt * 2
                print(f"  [{ticker}] Attempt {attempt} failed ({e}), retrying in {wait}s...")
                time.sleep(wait)

        candles.extend(body.get("candlesticks", []))
        cursor = body.get("cursor")
        if not cursor:
            break

    return candles


def main():
    print(f"Loading {markets_file}")
    markets = load_json(markets_file)
    print(f"Loaded {len(markets)} markets")

    done_tickers = load_checkpoint()
    tickers = [m["ticker"] for m in markets if m.get("ticker") and m["ticker"] not in done_tickers]
    print(f"After checkpoint: {len(tickers)} remaining")

    per_market_rows: list[dict] = []
    daily_totals: defaultdict[str, float] = defaultdict(float)

    if output_file.exists():
        print(f"Loading existing rows from {output_file}")
        existing = load_json(output_file)
        per_market_rows.extend(existing)
        for row in existing:
            daily_totals[row["date"]] += row["daily_volume"]
        print(f"Resumed {len(existing)} existing rows")

    total = len(tickers)

    for i, ticker in enumerate(tickers):
        try:
            candles = fetch_candles(ticker)
            cumulative = 0.0

            for c in candles:
                volume = float(c.get("volume", 0))
                cumulative += volume
                date = datetime.fromtimestamp(
                    c["end_period_ts"], tz=timezone.utc
                ).strftime("%Y-%m-%d")

                per_market_rows.append({
                    "ticker": ticker,
                    "date": date,
                    "daily_volume": volume,
                    "cumulative_volume": cumulative,
                })

                daily_totals[date] += volume

            done_tickers.add(ticker)

            if (i + 1) % 500 == 0:
                print(f"  Checkpointing at {i+1}/{total}...")
                save_checkpoint(done_tickers)
                save_json(output_file, per_market_rows)

            if candles:
                print(f"[{i+1}/{total}] {ticker} → {len(candles)} candles")

        except Exception as e:
            print(f"[{i+1}/{total}] FAILED {ticker}: {e}")

        time.sleep(SLEEP_BETWEEN)

    print("Building aggregate daily totals")
    agg_rows = []
    running = 0.0
    for date in sorted(daily_totals):
        running += daily_totals[date]
        agg_rows.append({
            "date": date,
            "daily_volume": daily_totals[date],
            "cumulative_volume": running,
        })

    print(f"Saving {output_file}")
    save_json(output_file, per_market_rows)

    print(f"Saving {agg_file}")
    save_json(agg_file, agg_rows)

    save_checkpoint(done_tickers)
    print(f"\nDone — {len(per_market_rows)} per-market rows, {len(agg_rows)} aggregate rows")


if __name__ == "__main__":
    main()