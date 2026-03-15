import json
from pathlib import Path

data_directory = Path("data")

cleaned_market_file = data_directory / "timed" / "timed_historical_markets.json"
events_file = data_directory / "raw" / "events.json"
output_file = data_directory / "timed" / "timed_events_markets.json"

def load_json(file_path):
    print(f"Loading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, file_path):
    print("Saving File")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    markets = load_json(cleaned_market_file)
    events = load_json(events_file)

    market_event_tickers = {
        market["event_ticker"]
        for market in markets
        if market.get("event_ticker") is not None
    }

    print("Filtering Data")
    filtered_events = [
        event
        for event in events
        if event.get("event_ticker") in market_event_tickers
    ]

    missing = market_event_tickers - {e["event_ticker"] for e in events}

    print("Missing events:", len(missing))
    print(list(missing)[:20])

    save_json(filtered_events, output_file)

    print(f"Markets loaded: {len(markets)}")
    print(f"Events loaded: {len(events)}")
    print(f"Unique market event_tickers: {len(market_event_tickers)}")
    print(f"Filtered events saved: {len(filtered_events)}")


if __name__ == "__main__":
    main()