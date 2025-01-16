import pandas as pd
import os

def calculate_vanilla_returns():
    # Load processed data
    large = pd.read_csv("processed_data/processed_nifty_large.csv", parse_dates=["Date"])
    mid = pd.read_csv("processed_data/processed_nifty_mid.csv", parse_dates=["Date"])

    # Ensure data is aligned by Date
    data = large[["Date", "Close"]].rename(columns={"Close": "Large"})
    data = data.merge(mid[["Date", "Close"]].rename(columns={"Close": "Mid"}), on="Date")

    # Normalize prices to 1 at the start
    data[["Large", "Mid"]] /= data[["Large", "Mid"]].iloc[0]

    # Calculate returns with equal allocation
    data["Portfolio"] = (data["Large"] + data["Mid"]) / 2

    # Save results
    os.makedirs("results", exist_ok=True)
    data.to_csv("results/vanilla_profit_curve.csv", index=False)
    print("Vanilla strategy profit curve saved to results/vanilla_profit_curve.csv")

if __name__ == "__main__":
    calculate_vanilla_returns()
