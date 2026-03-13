import requests

base_url = "https://api.elections.kalshi.com/trade-api/v2"

def get_all_series():
    url = f"{base_url}/series"
    response = requests.get(url, timeout = 10)
    response.raise_for_status()
    return response.json()["series"]

def get_unique_categories(series):
    
    categories = set()

    for s in series:
        category = s.get("category")
        if category:
            categories.add(category)

    return sorted(categories)

def main():
    series = get_all_series()
    categories = get_unique_categories(series)

    print("All series categories:\n")
    for c in categories:
        print(c)

if __name__ == "__main__":
    main()