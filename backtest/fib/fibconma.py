'''
Start                     2023-08-12 00:00:00                                                                   
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00
Exposure Time [%]                        74.5
Equity Final [$]                  20532.57458
Equity Peak [$]                  21389.043094
Return [%]                         105.325746 <-
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                  271.714259
Volatility (Ann.) [%]              153.573366
Sharpe Ratio                          1.76928 <-
Sortino Ratio                       12.855901
Calmar Ratio                        15.770211 <-
Max. Drawdown [%]                  -17.229589
Avg. Drawdown [%]                   -3.697723
Max. Drawdown Duration       51 days 00:00:00
Avg. Drawdown Duration        9 days 00:00:00
# Trades                                  147 <-
Win Rate [%]                        91.156463 <-
Best Trade [%]                     130.066754
Worst Trade [%]                    -28.491588
Avg. Trade [%]                       45.25847
Max. Trade Duration         105 days 00:00:00
Avg. Trade Duration          46 days 00:00:00
Profit Factor                       60.088581
Expectancy [%]                      51.547178
SQN                                 12.320352
_strategy                 FibonacciMAConfl...
_equity_curve                             ...
_trades                        Size  Entry...
dtype: object
'''

from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load data
data = pd.read_csv('/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv', parse_dates=['Datetime'])

# Ensure column names are in the required format
data.rename(columns={
    'Datetime': 'Date', 
    'Open': 'Open', 
    'High': 'High', 
    'Low': 'Low', 
    'Close': 'Close', 
    'Volume': 'Volume'
}, inplace=True)
data.set_index('Date', inplace=True)

class FibonacciMAConfluenceStrategy(Strategy):
    lookback_period = 20
    ma_period = 50  # Moving average period
    atr_period = 14  # ATR period
    atr_multiplier = 1.5
    take_profit_multiplier = 2

    def init(self):
        # Precompute Fibonacci levels
        high = self.data.High
        low = self.data.Low
        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), high)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), low)
        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618

        # Compute ATR for dynamic stop-loss and position sizing
        self.atr = self.I(
            lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(),
            self.data.High, self.data.Low, self.data.Close
        )

        # Compute moving average
        self.ma = self.I(lambda x: pd.Series(x).rolling(window=self.ma_period).mean(), self.data.Close)

    def next(self):
        # Trend confirmation
        trend_up = self.data.Close[-1] > self.ma[-1]
        trend_down = self.data.Close[-1] < self.ma[-1]

        # Position sizing
        risk_per_trade = 0.02
        position_size = risk_per_trade

        # Buy conditions
        if self.data.Close[-1] > self.fib_618[-1] and trend_up:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell conditions
        elif self.data.Close[-1] < self.fib_382[-1] and trend_down:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = max(0.01, self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1])
            self.sell(size=position_size, sl=sl, tp=tp)

# Prepare data for backtesting
bt = Backtest(data, FibonacciMAConfluenceStrategy, cash=10000, commission=0.002)
results = bt.optimize(
    lookback_period=range(10, 50, 5),
    ma_period=range(20, 100, 10),
    atr_multiplier=[1, 1.5, 2, 2.5, 3],
    take_profit_multiplier=[2, 3, 4, 5],
    maximize='Equity Final [$]'
)

# Print performance metrics
print(results)

# Plot results
bt.plot()
