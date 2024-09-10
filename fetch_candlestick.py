import requests
import pandas as pd
import time
import datetime

def fetch_klines(symbol, interval, start_time, end_time):
    base_url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 1000  
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if isinstance(data, list):
        df = pd.DataFrame(data, columns=[
            'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 
            'Quote Asset Volume', 'Number of Trades', 
            'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
        ])
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
        return df
    else:
        raise Exception(f"Failed to fetch data: {data}")

def fetch_data_chronologically(symbol, interval, start_date, end_date, max_minutes=1000):
    all_data = []
    start = start_date

    while start < end_date:
        end = start + datetime.timedelta(minutes=max_minutes)
        if end > end_date:
            end = end_date

        start_time = int(start.timestamp() * 1000)
        end_time = int(end.timestamp() * 1000)

        print(f"Fetching data from {start} to {end}...")
        df = fetch_klines(symbol, interval, start_time, end_time)
        all_data.append(df)

        start = end

        time.sleep(1)

    all_data_df = pd.concat(all_data)
    return all_data_df

symbol = "BTCUSDT"  
interval = "1m"  
start_date = datetime.datetime(2021, 1, 1)
end_date = datetime.datetime(2024, 7, 31)

data = fetch_data_chronologically(symbol, interval, start_date, end_date)

spot = True
if spot:
    data.to_csv(f"{symbol}_spot_{interval}.csv", index=False)
else:
    data.to_csv(f"{symbol}_{interval}.csv", index=False)

print("Data saved.")
