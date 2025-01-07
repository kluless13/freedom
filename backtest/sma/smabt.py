'''
RANK 5
Return (%): 107.90%
Sharpe Ratio: 1.355
Win Rate (%): 81.48% (highest among the strategies)
Profit Factor: 3.48
'''

# Fine.

'''
Optimization Results:
Best SMA Period: 10
Best Buy Percentage: 0.5
Best Sell Percentage: 2.1

Full Stats:
Start                     2023-01-01 00:00:00
End                       2023-11-20 19:15:00
Duration                    323 days 19:15:00
Exposure Time [%]                   95.284234 <-
Equity Final [$]                  207900.4642
Equity Peak [$]                   209623.1642
Return [%]                         107.900464 <-
Buy & Hold Return [%]                127.7687
Return (Ann.) [%]                  128.075118
Volatility (Ann.) [%]               94.479903
Sharpe Ratio                         1.355581 <-
Sortino Ratio                        5.783343
Calmar Ratio                         6.094142
Max. Drawdown [%]                  -21.016104
Avg. Drawdown [%]                   -1.510273
Max. Drawdown Duration      102 days 01:00:00
Avg. Drawdown Duration        2 days 10:40:00
# Trades                                   27 <-
Win Rate [%]                        81.481481 <-
Best Trade [%]                         20.752
Worst Trade [%]                    -15.016249
Avg. Trade [%]                       3.066279
Max. Trade Duration          66 days 19:15:00
Avg. Trade Duration          11 days 10:02:00
Profit Factor                        3.475599
Expectancy [%]                       3.295772
SQN                                  2.210345
_strategy                 SMABuySellStrate...
_equity_curve                             ...
_trades                       Size  EntryB...
'''

import numpy as np
from backtesting import Backtest, Strategy
from backtesting.test import SMA
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class SMABuySellStrategy(Strategy):
    sma_period = 14  # Default SMA period, will be optimized
    buy_pct = 1.0    # Default buy percentage below SMA, will be optimized
    sell_pct = 1.0   # Default sell percentage above SMA, will be optimized


    def init(self):
        # Calculate the SMA using the Close price and the sma_period
        self.sma = self.I(SMA, self.data.Close, self.sma_period)


    def next(self):
        # Calculate the buying and selling thresholds
        buy_threshold = self.sma[-1] * (1 - self.buy_pct / 100)
        sell_threshold = self.sma[-1] * (1 + self.sell_pct / 100)


        # If the Close price is below the buy threshold, buy
        if len(self.data.Close) > 0 and self.data.Close[-1] < buy_threshold:
            self.buy()


        # If the Close price is above the sell threshold, sell
        elif len(self.data.Close) > 0 and self.data.Close[-1] > sell_threshold:
            self.position.close()


# Load the data
data_path = '/Users/kluless/freedom/backtest/sma/BTC-USD-15m-2023-1-01T00_00 (1).csv'  
#data_path = '/Users/md/Dropbox/dev/github/hyper-liquid-trading-bots/data/POPCAT_4h_5000.csv' # popcat
data = pd.read_csv(data_path, index_col=0, parse_dates=True, skipinitialspace=True)


# Correct the column names to match the DataFrame
data = data[['open', 'high', 'low', 'close', 'volume']]
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']


# Sort the data index in ascending order
data = data.sort_index()


# Create and configure the backtest
bt = Backtest(data, SMABuySellStrategy, cash=100000, commission=0.002)


# Optimization with heatmap
opt_stats, heatmap = bt.optimize(
    sma_period=range(10, 30, 2),            # SMA periods from 10 to 30 in steps of 2
    buy_pct=[float(x)/10 for x in range(5, 25, 2)],    # Buy percentages from 0.5% to 2.5%
    sell_pct=[float(x)/10 for x in range(5, 25, 2)],   # Sell percentages from 0.5% to 2.5%
    maximize='Return [%]',
    constraint=lambda p: True,  # Remove constraint for now to debug
    return_heatmap=True
)

# Print the optimization results
print("\nOptimization Results:")
print(f"Best SMA Period: {opt_stats._strategy.sma_period}")
print(f"Best Buy Percentage: {opt_stats._strategy.buy_pct}")
print(f"Best Sell Percentage: {opt_stats._strategy.sell_pct}")
print("\nFull Stats:")
print(opt_stats)

# Convert heatmap data to a 2D DataFrame for plotting
heatmap_df = heatmap.unstack(level='buy_pct').T

# Plot the heatmap for the optimization results
plt.figure(figsize=(10, 8))
sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap='viridis')
plt.title("Optimization Heatmap")
plt.xlabel("Sell Percentage (%)")
plt.ylabel("Buy Percentage (%)")
plt.show()

# Run the backtest with the best parameters
# Run the backtest with the best parameters
results = bt.run(
    sma_period=opt_stats._strategy.sma_period,
    buy_pct=opt_stats._strategy.buy_pct,
    sell_pct=opt_stats._strategy.sell_pct
)
print(results)

# Plot with specific resample period
try:
    bt.plot(resample='4H')  # Resample to 4-hour intervals
except TypeError as e:
    print("Warning: Plotting with default parameters failed. Trying alternative plot...")
    # Alternative basic plot
    plt.figure(figsize=(15, 7))
    plt.plot(results._equity_curve.Equity)
    plt.title('Backtest Results - Equity Curve')
    plt.xlabel('Date')
    plt.ylabel('Equity')
    plt.grid(True)
    plt.show()
