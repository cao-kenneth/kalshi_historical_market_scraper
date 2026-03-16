# kalshi_scraper
Kalshi data scraper for analyzing political markets and resolutions.

Raw data and other data is not included in this repo due to size. 
- Data was gathered end-of-day on Mar 12th, 2026. Included: 9,013 series, 201,496 events, and 965,055 markets.

Running code to clean will create a cleaned folder (with only 2025 data) and a raw folder with data up to kalshi's historical data date.
- Running the api to gather all raw data took around 20 mins (market data ~2gb, events data ~94mb, series data ~14mb)

Getting full data goes from get_full_data.py -> raw data -> running all timed data scripts -> timed data -> running all cleaned scripts -> cleaned data.
- Kalshi is formatted: series -> events -> markets where each market is what people trade. 

project-root/
│
src/
├── get_full_data.py # get all historical data
├── get_series_names.py # get all possible categories from each series
├── get_category_volume.py # get total volume for each category
└── market_volume.py # script to get daily volume from all markets in cleaned_timed_markets.json
│
├── testing/
│   ├── check_numbers.py # used to check num unique markets, events, series
│   ├── historical_cutoffs.py # used to check when historical cutoff day is (usually 1 year from current day)
│   └── market_number_checker.py # check number of markets by total volume
│
└── data/
    ├── raw/
    │   └── events.json
    │   └── historical_markets.json
    │   └── series.json
    │
    ├── cleaned/
    │   ├── category_volume.json # total volume of each category
    │   ├── markets_above_10k.json # markets above 10k total volume (mar12 - mar12)
    │   ├── cleaned_timed_markets.json # all markets between 12mar2024 - 12mar2025
    │   ├── cleaned_timed_markets.py # creating .json above
    │   └── markets_10k.py # creating .json above
    │
    └── timed/
        ├── timed_historical_markets.json # historical_markets.json (mar12 - mar12)
        ├── timed_events_markets.json # only events from timed_historical_markets.json
        ├── timed_series_markets.json # only series from timed_events_markets.json
        ├── timed_market_daily_volume.json 
        ├── timed_aggregate_daily_volume.json 
        ├── time_events_data.py # used to create .json above
        ├── time_historical_data.py # used to create .json above
        ├── time_series_data.py # used to create .json above
        └── checkpoint.json # used to keep track of markets in case api crashes

