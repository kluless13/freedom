import pandas as pd
import yaml
import os

def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

def calculate_dynamic_returns():
    # Load processed data
    large = pd.read_csv("processed_data/processed_nifty_large.csv", parse_dates=["Date"])
    mid = pd.read_csv("processed_data/processed_nifty_mid.csv", parse_dates=["Date"])

    # Ensure data is aligned by Date
    data = large[["Date", "Close"]].rename(columns={"Close": "Large"})
    data = data.merge(mid[["Date", "Close"]].rename(columns={"Close": "Mid"}), on="Date")

    # Normalize prices to 1 at the start
    data[["Large", "Mid"]] /= data[["Large", "Mid"]].iloc[0]

    # Load allocation rules
    config = load_config()
    allocation_rules = config["allocation_rules"]

    # Calculate dynamic allocation
    data["Portfolio"] = 0
    for i, row in data.iterrows():
        # Evaluate conditions
        for rule in allocation_rules:
            if eval(rule["condition"], None, {"large": row["Large"], "mid": row["Mid"]}):
                weights = rule["allocation"]
                break
        else:
            weights = [0.5, 0.5]  # Default to equal allocation

        # Compute portfolio value
        data.at[i, "Portfolio"] = (
            row["Large"] * weights[0] + row["Mid"] * weights[1]
        )

    # Save results
    os.makedirs("results", exist_ok=True)
    data.to_csv("results/dynamic_profit_curve.csv", index=False)
    print("Dynamic strategy profit curve saved to results/dynamic_profit_curve.csv")

if __name__ == "__main__":
    calculate_dynamic_returns()
