'''
Optimization Results:
Best SMA Period: 18
Best Buy Percentage: 0.9
Best Sell Percentage: 2.1

Full Stats:
Start                     2024-04-28 00:00:00
End                       2024-06-11 08:00:00
Duration                     44 days 08:00:00
Exposure Time [%]                   56.928839
Equity Final [$]                121076.198959
Equity Peak [$]                 153413.283814
Return [%]                          21.076199 <-
Buy & Hold Return [%]              -28.451256 <-
Return (Ann.) [%]                  371.735956
Volatility (Ann.) [%]             2042.186517
Sharpe Ratio                         0.182028
Sortino Ratio                        3.719822
Calmar Ratio                         9.000908
Max. Drawdown [%]                  -41.299829
Avg. Drawdown [%]                  -19.431485
Max. Drawdown Duration       22 days 04:00:00
Avg. Drawdown Duration        9 days 13:00:00
# Trades                                   13
Win Rate [%]                        61.538462
Best Trade [%]                      26.377664
Worst Trade [%]                    -17.472217
Avg. Trade [%]                        1.42636
Max. Trade Duration           4 days 08:00:00
Avg. Trade Duration           1 days 23:00:00
Profit Factor                        1.536176
Expectancy [%]                       2.171572
SQN                                  0.363343
_strategy                 SMABuySellStrate...
_equity_curve                             ...
_trades                         Size  Entr...
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
data_path = '/Users/kluless/freedom/backtest/sma/POPCAT_4h_5000.csv'  
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