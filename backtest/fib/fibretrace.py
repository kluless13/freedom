''' 
/Users/kluless/freedom/backtest/rsi/Zata1h.csv
Start                     2024-10-01 00:00:00                                                                   
End                       2025-01-01 01:00:00
Duration                     92 days 01:00:00
Exposure Time [%]                   97.692308
Equity Final [$]                 12132.890896
Equity Peak [$]                  13320.369097
Return [%]                          21.328909
Buy & Hold Return [%]              175.542117
Return (Ann.) [%]                  113.568539
Volatility (Ann.) [%]                66.41484
Sharpe Ratio                         1.709987
Sortino Ratio                        7.186777
Calmar Ratio                        12.682972
Max. Drawdown [%]                   -8.954411
Avg. Drawdown [%]                   -1.701054
Max. Drawdown Duration       27 days 01:00:00
Avg. Drawdown Duration        2 days 15:00:00
# Trades                                 1846
Win Rate [%]                        37.811484
Best Trade [%]                      25.164928
Worst Trade [%]                    -13.142017
Avg. Trade [%]                       0.386814
Max. Trade Duration           3 days 22:00:00
Avg. Trade Duration           0 days 20:00:00
Profit Factor                        1.275813
Expectancy [%]                       0.542748
SQN                                  4.719766
_strategy                 EnhancedFibonacc...
_equity_curve                             ...
_trades                         Size  Entr...
dtype: object
'''

from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load data
data = pd.read_csv('/Users/kluless/freedom/backtest/rsi/Zata1h.csv', parse_dates=['Date'])

# Ensure column names are in the required format
data.rename(columns={
    'Date': 'Date', 
    'Open': 'Open', 
    'High': 'High', 
    'Low': 'Low', 
    'Close': 'Close', 
    'Volume': 'Volume'
}, inplace=True)
data.set_index('Date', inplace=True)

class EnhancedFibonacciRetracementStrategy(Strategy):
    lookback_period = 20  # Optimizable parameter
    atr_period = 14  # ATR period for dynamic stop-loss and position sizing
    atr_multiplier = 1.5  # Multiplier for ATR-based stop-loss
    take_profit_multiplier = 3  # Increased reward-to-risk ratio
    cooldown_period = 5  # Reduced cooldown to allow more trades

    def init(self):
        # Precompute Fibonacci levels
        high = self.data.High
        low = self.data.Low

        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), high)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), low)

        # Calculate Fibonacci levels
        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618

        # Calculate ATR for dynamic stop-loss and position sizing
        self.atr = self.I(lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(), high, low, self.data.Close)

        # Compute 50-period moving average for trend confirmation
        self.ma50 = self.I(lambda x: pd.Series(x).rolling(window=50).mean(), self.data.Close)

    def next(self):
        # Check cooldown
        if len(self.trades) > 0 and self.trades[-1].exit_bar is not None and len(self.data) - self.trades[-1].exit_bar < self.cooldown_period:
            return

        # Trend confirmation using precomputed moving average
        trend_up = self.data.Close[-1] > self.ma50[-1]

        # Position sizing as a fraction of equity
        risk_per_trade = 0.02  # Risk 2% of equity per trade
        position_size = risk_per_trade  # Trade 2% of equity as a fraction

        # Buy conditions
        if self.data.Close[-1] > self.fib_618[-1] and trend_up:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell conditions
        elif self.data.Close[-1] < self.fib_382[-1] and not trend_up:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.sell(size=position_size, sl=sl, tp=tp)

# Prepare data for backtesting
bt = Backtest(data, EnhancedFibonacciRetracementStrategy, cash=10000, commission=0.002)
results = bt.optimize(
    lookback_period=range(10, 50, 5),
    atr_period=range(10, 20, 2),
    atr_multiplier=[1, 1.5, 2, 2.5],
    take_profit_multiplier=[2, 3, 4],
    cooldown_period=range(3, 15, 2),
    maximize='Equity Final [$]'
)

# Print performance metrics
print(results)

# Plot results
bt.plot()
