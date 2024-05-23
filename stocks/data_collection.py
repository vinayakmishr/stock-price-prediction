import requests
import pandas as pd
from .models import Stock, HistoricalData

API_KEY = 'your_alpha_vantage_api_key'
BASE_URL = 'https://www.alphavantage.co/query'

def fetch_stock_data(symbol):
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    timeseries = data['Time Series (Daily)']
    df = pd.DataFrame(timeseries).transpose()
    df.columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
    df.index = pd.to_datetime(df.index)
    return df

def save_stock_data(symbol):
    stock, created = Stock.objects.get_or_create(symbol=symbol, defaults={'name': symbol})
    df = fetch_stock_data(symbol)
    for date, row in df.iterrows():
        HistoricalData.objects.update_or_create(
            stock=stock,
            date=date,
            defaults={
                'open_price': row['open_price'],
                'close_price': row['close_price'],
                'high_price': row['high_price'],
                'low_price': row['low_price'],
                'volume': row['volume'],
            }
        )
