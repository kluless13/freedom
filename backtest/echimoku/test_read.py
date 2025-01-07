import pandas as pd
import sys

def main():
    print(f"Python version: {sys.version}")
    print(f"Pandas version: {pd.__version__}")
    print("-" * 50)

    try:
        # Attempt to read the CSV file
        df = pd.read_csv('/Users/kluless/freedom/backtest/HFT/BTC-USD-5m-2022-2-02T00_00.csv')
        
        # Display basic information about the dataframe
        print("\nDataframe Info:")
        print(df.info())
        
        # Display the first few rows
        print("\nFirst few rows of the data:")
        print(df.head())
        
    except FileNotFoundError:
        print("Error: The CSV file was not found. Please check the file path.")
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
    except pd.errors.ParserError:
        print("Error: Unable to parse the CSV file. Please check if it's properly formatted.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()

