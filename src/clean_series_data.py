import json
from pathlib import Path

data_directory = Path("data")

events_file = data_directory / "cleaned/2025_events_markets.json"
series_file = data_directory / "raw/series.json"
output_file = data_directory / "cleaned/2025_series_markets.json"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    events = load_json(events_file)
    series = load_json(series_file)

    event_series_tickers = {
        event.get("series_ticker")
        for event in events
        if event.get("series_ticker") is not None
    }

    filtered_series = [
        s
        for s in series
        if s.get("ticker") in event_series_tickers
    ]

    save_json(filtered_series, output_file)

    print(f"Events loaded: {len(events)}")
    print(f"Series loaded: {len(series)}")
    print(f"Unique event series_tickers: {len(event_series_tickers)}")
    print(f"Filtered series saved: {len(filtered_series)}")


if __name__ == "__main__":
    main()