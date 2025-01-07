import pandas as pd

# Load the original CSV file
input_file = '/Users/kluless/freedom/backtest/HFT/BTC-USD-5m-2022-2-02T00_00.csv'
output_file = '/Users/kluless/freedom/backtest/echimoku/btc5min.csv'

# Read the CSV file and clean up column names
data = pd.read_csv(input_file)

# Strip any whitespace from column names
data.columns = data.columns.str.strip()

# Drop unnamed columns that might appear due to trailing commas
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

# Rename columns to match the desired format
data.rename(
    columns={
        'datetime': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    },
    inplace=True
)

# Save the cleaned and transformed data to a new CSV file
data.to_csv(output_file, index=False)

print(f"Transformed CSV saved to {output_file}")
