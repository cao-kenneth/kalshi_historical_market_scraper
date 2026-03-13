import json
import time
from pathlib import Path

import requests

base_url = "https://api.elections.kalshi.com/trade-api/v2"
data_directory = Path("data/raw")

series_file = data_directory / "series.json"
events_file = data_directory / "events.json"
historical_markets_file = data_directory / "historical_markets.json"


def make_request(url, params = None, timeout = 20, max_retries = 8):
    retries = 0

    while True:
        response = requests.get(url, params = params, timeout = timeout)

        if response.status_code == 429:
            wait_time = min(2 ** retries, 30)
            print(f"429 rate limit hit. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1

            if retries > max_retries:
                raise RuntimeError("Too many retries after rate limiting.")
            continue

        response.raise_for_status()
        return response


def fetch_paginated(endpoint, array_key, limit, extra_params = None, sleep_seconds = 0.15):
    url = f"{base_url}{endpoint}"
    all_items = []
    cursor = None
    seen_cursors = set()
    page = 0

    while True:
        params = {"limit": limit}
        if extra_params:
            params.update(extra_params)
        if cursor:
            params["cursor"] = cursor

        response = make_request(url, params = params)
        data = response.json()

        items = data.get(array_key, [])
        next_cursor = data.get("cursor")

        page += 1
        all_items.extend(items)

        print(
            f"{endpoint} | page {page} | got {len(items)} items | total {len(all_items)}"
        )

        if not next_cursor:
            print(f"{endpoint} complete: no more cursor.\n")
            break

        if next_cursor in seen_cursors:
            print(f"{endpoint} stopped: repeated cursor detected.\n")
            break

        seen_cursors.add(next_cursor)
        cursor = next_cursor
        time.sleep(sleep_seconds)

    return all_items


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    print(f"Saved {path}\n")


def fetch_all_series():
    return fetch_paginated(
        endpoint = "/series",
        array_key = "series",
        limit = 200,
    )


def fetch_all_events():
    return fetch_paginated(
        endpoint = "/events",
        array_key = "events",
        limit = 200,
    )


def fetch_all_historical_markets():
    return fetch_paginated(
        endpoint = "/historical/markets",
        array_key = "markets",
        limit = 200,
    )


def main():
    print("Fetching series...")
    series = fetch_all_series()
    save_json(series_file, series)

    print("Fetching events...")
    events = fetch_all_events()
    save_json(events_file, events)

    print("Fetching historical markets...")
    historical_markets = fetch_all_historical_markets()
    save_json(historical_markets_file, historical_markets)

    print("Done.")
    print(f"Series: {len(series):,}")
    print(f"Events: {len(events):,}")
    print(f"Historical markets: {len(historical_markets):,}")


if __name__ == "__main__":
    main()