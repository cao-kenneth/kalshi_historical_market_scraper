import json
from pathlib import Path

data_directory = Path("data")
raw_directory = data_directory / "raw"

series_file = raw_directory / "series.json"
events_file = raw_directory / "events.json"
markets_file = raw_directory / "historical_markets.json"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    series = load_json(series_file)
    events = load_json(events_file)
    markets = load_json(markets_file)

    unique_series = {s.get("ticker") for s in series if s.get("ticker")}
    unique_events = {e.get("event_ticker") for e in events if e.get("event_ticker")}
    unique_markets = {m.get("ticker") for m in markets if m.get("ticker")}

    print("RAW DATA SUMMARY")
    print("----------------------------")

    print(f"Series rows: {len(series)}")
    print(f"Unique series tickers: {len(unique_series)}")

    print()

    print(f"Events rows: {len(events)}")
    print(f"Unique event tickers: {len(unique_events)}")

    print()

    print(f"Markets rows: {len(markets)}")
    print(f"Unique market tickers: {len(unique_markets)}")


if __name__ == "__main__":
    main()