import requests

base_url = "https://api.elections.kalshi.com/trade-api/v2"


def get_historical_cutoffs():
    url = f"{base_url}/historical/cutoff"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data


def main():
    cutoffs = get_historical_cutoffs()

    print("Historical Cutoff Timestamps:")

    print("Market settled cutoff:", cutoffs.get("market_settled_ts"))
    print("Trades created cutoff:", cutoffs.get("trades_created_ts"))
    print("Orders updated cutoff:", cutoffs.get("orders_updated_ts"))


if __name__ == "__main__":
    main()