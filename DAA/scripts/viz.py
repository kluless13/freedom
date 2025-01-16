'''
python3 scripts/viz.py
2025-01-16 23:01:23.329 python3[30832:58988501] +[IMKClient subclass]: chose IMKClient_Modern
2025-01-16 23:01:23.329 python3[30832:58988501] +[IMKInputSession subclass]: chose IMKInputSession_Modern
  Strategy      CAGR  Volatility  Sharpe Ratio
0  Vanilla  0.128311    0.170247      0.753677
1  Dynamic  0.135345    0.175658      0.770501
'''

import pandas as pd
import matplotlib.pyplot as plt

# Load the data
dynamic_df = pd.read_csv("results/dynamic_profit_curve.csv", parse_dates=["Date"])
vanilla_df = pd.read_csv("results/vanilla_profit_curve.csv", parse_dates=["Date"])

# Calculate metrics
def calculate_metrics(data, strategy_name):
    data["Daily_Return"] = data["Portfolio"].pct_change()
    cagr = (data["Portfolio"].iloc[-1] ** (1 / (len(data) / 252))) - 1
    volatility = data["Daily_Return"].std() * (252 ** 0.5)
    sharpe_ratio = cagr / volatility
    return {"Strategy": strategy_name, "CAGR": cagr, "Volatility": volatility, "Sharpe Ratio": sharpe_ratio}

vanilla_metrics = calculate_metrics(vanilla_df, "Vanilla")
dynamic_metrics = calculate_metrics(dynamic_df, "Dynamic")

# Create a comparison table
metrics_df = pd.DataFrame([vanilla_metrics, dynamic_metrics])

# Plot the profit curves
plt.figure(figsize=(12, 6))
plt.plot(vanilla_df["Date"], vanilla_df["Portfolio"], label="Vanilla Strategy")
plt.plot(dynamic_df["Date"], dynamic_df["Portfolio"], label="Dynamic Strategy")
plt.title("Portfolio Performance Comparison")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (Normalized)")
plt.legend()
plt.grid()
plt.show()

# Display metrics
print(metrics_df)
