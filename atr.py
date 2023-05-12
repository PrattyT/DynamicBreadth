import pandas as pd
import json
from typing import Union

"""Calculate the Average True Range (ATR) of a stock."""
def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    
    df['High-Low'] = df['High'] - df['Low']
    df['High-PrevClose'] = abs(df['High'] - df['Close'].shift())
    df['PrevClose-Low'] = abs(df['Close'].shift() - df['Low'])
    df['TR'] = df[['High-Low', 'High-PrevClose', 'PrevClose-Low']].max(axis=1)
    atr = df['TR'].rolling(window=period).mean()
    return atr

def count_stocks_within_atr(data: dict, date: Union[str, pd.Timestamp], atr_multiplier: float = 2) -> int:
    count = 0
    if isinstance(date, str):
        date = pd.to_datetime(date)
    for stock in data.keys():
        if all(item in data[stock].columns for item in ['Close', 'ATR', '10-day High']) and date in data[stock].index:
            close_price = data[stock].loc[date, 'Close']
            high_price = data[stock].loc[date, '10-day High']
            atr = data[stock].loc[date, 'ATR']
            if close_price >= high_price - atr_multiplier * atr:
                count += 1
    return count

# Load data
with open("datajson") as f:
    data = json.load(f)

# Convert data to DataFrames and calculate ATR and 10-day high
for stock in data.keys():
    data[stock] = pd.DataFrame(data[stock])
    if 'Date' in data[stock].columns:
        data[stock]['Date'] = pd.to_datetime(data[stock]['Date'])
        data[stock].set_index('Date', inplace=True)
    if all(item in data[stock].columns for item in ['High', 'Low', 'Close']):
        data[stock]['ATR'] = calculate_atr(data[stock])
        data[stock]['10-day High'] = data[stock]['High'].rolling(window='10D').max()

# Calculate the number of stocks within 2 ATR of their 10-day high for each date
dates = pd.date_range(start='2022-01-01', end='2022-01-31')
counts = {date: count_stocks_within_atr(data, date) for date in dates}
