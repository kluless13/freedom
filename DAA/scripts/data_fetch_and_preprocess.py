import os
import yfinance as yf
import pandas as pd

# Create required directories
os.makedirs("data", exist_ok=True)
os.makedirs("processed_data", exist_ok=True)

# Yahoo Finance tickers for indices
INDEX_TICKERS = {
    "nifty_large": "^NSEI",          # NIFTY 50
    "nifty_mid": "NIFTY_MIDCAP_100.NS",  # NIFTY Midcap 100
    # "nifty_small": "^CNXSC"        # Ignored for now
}

def fetch_index_data_yfinance(symbol, file_path):
    """
    Fetch index data from Yahoo Finance and save it as CSV.
    """
    print(f"Fetching data for {symbol} from Yahoo Finance...")
    try:
        # Fetch data
        data = yf.download(symbol, start="2010-01-01")  # Adjust start date as needed
        if not data.empty:
            data.to_csv(file_path, index=True)
            print(f"Data for {symbol} saved to {file_path}")
        else:
            print(f"No data found for {symbol}.")
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")

def preprocess_data(file_path, processed_file_path):
    """
    Preprocess raw data, clean headers, and save the processed data.
    """
    print(f"Processing data from {file_path}...")
    try:
        # Load data
        data = pd.read_csv(file_path)
        
        # Remove unnecessary rows
        data = data.iloc[2:].reset_index(drop=True)
        
        # Rename columns
        data.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
        
        # Convert date column
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        
        # Convert numeric columns
        numeric_cols = ["Close", "High", "Low", "Open", "Volume"]
        for col in numeric_cols:
            data[col] = pd.to_numeric(data[col], errors="coerce")
        
        # Drop rows with missing values
        data.dropna(subset=["Date", "Close"], inplace=True)
        
        # Save processed data
        data.to_csv(processed_file_path, index=False)
        print(f"Processed data saved to {processed_file_path}")
    except Exception as e:
        print(f"Error processing data from {file_path}: {e}")

def main():
    for name, ticker in INDEX_TICKERS.items():
        raw_file = f"data/{name}.csv"
        processed_file = f"processed_data/processed_{name}.csv"
        
        # Fetch data
        fetch_index_data_yfinance(ticker, raw_file)

        # Preprocess data
        if os.path.exists(raw_file):
            preprocess_data(raw_file, processed_file)
        else:
            print(f"Raw file {raw_file} does not exist. Skipping processing.")

if __name__ == "__main__":
    main()
