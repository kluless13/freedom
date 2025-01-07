import pandas as pd

data_path = '/Users/kluless/freedom/backtest/HFT/btc.csv'

try:
    # Test reading the CSV
    data = pd.read_csv(data_path, parse_dates=['Date'])
    print(data.head())
    print(data.info())

    # Check for any issues with the Date column
    print(data['Date'].isnull().sum())  # Ensure no missing dates
except Exception as e:
    print(f"Error reading CSV: {e}")
